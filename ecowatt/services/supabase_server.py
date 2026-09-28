"""Small server-only PostgREST client for private EcoWatt data."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import streamlit as st


class SupabaseServerError(RuntimeError):
    """Raised when the server-side Supabase connection is unavailable."""


class SupabaseServerClient:
    def __init__(self, timeout: float = 3.0) -> None:
        self.timeout = timeout

    @staticmethod
    def _secret(name: str) -> str | None:
        value = os.getenv(name)
        if value:
            return value.strip()
        try:
            secret = st.secrets.get(name)
        except Exception:
            return None
        return str(secret).strip() if secret else None

    def request(
        self,
        method: str,
        table: str,
        *,
        filters: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        prefer: str | None = None,
    ) -> tuple[int, Any]:
        base_url = self._secret("SUPABASE_URL")
        service_key = self._secret("SUPABASE_SERVICE_ROLE_KEY")
        if not base_url or not service_key:
            raise SupabaseServerError("A conexão privada com o Supabase não está configurada no servidor.")

        query = urllib.parse.urlencode(filters or {})
        url = f"{base_url.rstrip('/')}/rest/v1/{table}"
        if query:
            url = f"{url}?{query}"
        body = json.dumps(payload, ensure_ascii=True, default=str).encode("utf-8") if payload is not None else None
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        if prefer:
            headers["Prefer"] = prefer
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, self._decode(response.read())
        except urllib.error.HTTPError as error:
            return error.code, self._decode(error.read())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise SupabaseServerError("Não foi possível acessar o Supabase.") from error

    @staticmethod
    def _decode(raw: bytes) -> Any:
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SupabaseServerError("O Supabase retornou uma resposta inválida.") from error