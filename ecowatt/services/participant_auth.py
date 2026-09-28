"""Participant accounts and persistent server-validated login sessions."""
import hashlib
import re
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from ecowatt.services.supabase_server import SupabaseServerClient, SupabaseServerError


SESSION_TTL = timedelta(days=30)
USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]{3,24}$")
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128
LOGIN_FAILURE_LIMIT = 5
LOGIN_WINDOW_SECONDS = 60
LOGIN_LOCK_SECONDS = 60


class AuthStorageUnavailable(RuntimeError):
    """Raised when private authentication storage is not configured or reachable."""


class UsernameAlreadyTaken(ValueError):
    """Raised when another account already uses the normalized username."""


class LoginRateLimited(RuntimeError):
    """Raised when too many invalid login attempts occur in a short period."""


@dataclass(frozen=True)
class AuthenticatedParticipant:
    participant_id: str
    username: str
    session_token: str
    expires_at: datetime
    must_change_password: bool = False


@dataclass
class _FailureWindow:
    started_at: float
    failures: int = 0
    locked_until: float = 0


class LoginAttemptLimiter:
    """Small process-local throttle suitable for the single-process event app."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._windows: dict[str, _FailureWindow] = {}
        self._lock = threading.Lock()

    def check(self, username: str) -> None:
        now = self._clock()
        with self._lock:
            window = self._windows.get(username)
            if window and window.locked_until > now:
                raise LoginRateLimited("Muitas tentativas. Aguarde um minuto e tente novamente.")

    def failed(self, username: str) -> None:
        now = self._clock()
        with self._lock:
            window = self._windows.get(username)
            if window is None or now - window.started_at >= LOGIN_WINDOW_SECONDS:
                window = _FailureWindow(started_at=now)
                self._windows[username] = window
            window.failures += 1
            if window.failures >= LOGIN_FAILURE_LIMIT:
                window.locked_until = now + LOGIN_LOCK_SECONDS

    def succeeded(self, username: str) -> None:
        with self._lock:
            self._windows.pop(username, None)


def normalize_username(username: str) -> str:
    if not isinstance(username, str):
        raise ValueError("Use de 3 a 24 caracteres: letras sem acento, números, ponto, hífen ou sublinhado.")
    normalized = username.strip().lower()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError("Use de 3 a 24 caracteres: letras sem acento, números, ponto, hífen ou sublinhado.")
    return normalized


def validate_password(password: str) -> None:
    if not isinstance(password, str) or not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH:
        raise ValueError("A senha deve ter entre 6 e 128 caracteres.")


def hash_password(password: str) -> str:
    validate_password(password)
    return PasswordHasher(type=Type.ID).hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return PasswordHasher(type=Type.ID).verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class SupabaseParticipantRepository:
    """Server-side PostgREST access; never instantiate in browser code."""

    def __init__(self, timeout: float = 3.0) -> None:
        self.client = SupabaseServerClient(timeout=timeout)

    def _request(
        self,
        method: str,
        table: str,
        *,
        filters: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        prefer: str | None = None,
    ) -> tuple[int, Any]:
        try:
            status, data = self.client.request(method, table, filters=filters, payload=payload, prefer=prefer)
        except SupabaseServerError as error:
            raise AuthStorageUnavailable("Nao foi possivel acessar o armazenamento de autenticacao.") from error
        if (status < 200 or status >= 300) and status != 409:
            raise AuthStorageUnavailable("A operação de autenticação foi rejeitada pelo armazenamento.")
        return status, data

    def find_participant(self, username_normalized: str) -> dict[str, Any] | None:
        _, rows = self._request(
            "GET",
            "participants",
            filters={
                "select": "id,username,username_normalized,password_hash,must_change_password",
                "username_normalized": f"eq.{username_normalized}",
                "limit": "1",
            },
        )
        return rows[0] if rows else None

    def create_participant(self, values: dict[str, Any]) -> dict[str, Any]:
        status, rows = self._request(
            "POST", "participants", payload=values, prefer="return=representation"
        )
        if status == 409:
            raise UsernameAlreadyTaken("Esse nome de usuario ja esta em uso.")
        if status < 200 or status >= 300 or not rows:
            raise AuthStorageUnavailable("Nao foi possivel criar a conta.")
        return rows[0]

    def create_session(self, participant_id: str, token_hash: str, expires_at: datetime) -> None:
        status, _ = self._request(
            "POST",
            "participant_sessions",
            payload={
                "participant_id": participant_id,
                "token_hash": token_hash,
                "expires_at": expires_at.isoformat(),
            },
            prefer="return=minimal",
        )
        if status < 200 or status >= 300:
            raise AuthStorageUnavailable("Nao foi possivel iniciar a sessao.")

    def find_session(self, token_hash: str, now: datetime) -> dict[str, Any] | None:
        _, rows = self._request(
            "GET",
            "participant_sessions",
            filters={
                "select": "id,participant_id,expires_at",
                "token_hash": f"eq.{token_hash}",
                "revoked_at": "is.null",
                "expires_at": f"gt.{now.isoformat()}",
                "limit": "1",
            },
        )
        return rows[0] if rows else None

    def revoke_session(self, token_hash: str, revoked_at: datetime) -> None:
        status, _ = self._request(
            "PATCH",
            "participant_sessions",
            filters={"token_hash": f"eq.{token_hash}", "revoked_at": "is.null"},
            payload={"revoked_at": revoked_at.isoformat()},
            prefer="return=minimal",
        )
        if status < 200 or status >= 300:
            raise AuthStorageUnavailable("Nao foi possivel encerrar a sessao.")

    def get_participant(self, participant_id: str) -> dict[str, Any] | None:
        _, rows = self._request(
            "GET",
            "participants",
            filters={
                "select": "id,username,must_change_password",
                "id": f"eq.{participant_id}",
                "limit": "1",
            },
        )
        return rows[0] if rows else None

    def update_password(self, participant_id: str, password_hash: str) -> None:
        status, _ = self._request(
            "PATCH",
            "participants",
            filters={"id": f"eq.{participant_id}"},
            payload={"password_hash": password_hash, "must_change_password": False},
            prefer="return=minimal",
        )
        if status < 200 or status >= 300:
            raise AuthStorageUnavailable("Nao foi possivel atualizar a senha.")


class ParticipantAuthService:
    def __init__(
        self,
        repository: SupabaseParticipantRepository | Any | None = None,
        *,
        ttl: timedelta = SESSION_TTL,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        limiter: LoginAttemptLimiter | None = None,
    ) -> None:
        self.repository = repository or SupabaseParticipantRepository()
        self.ttl = ttl
        self.clock = clock
        self.limiter = limiter or _PROCESS_LOGIN_LIMITER

    def username_available(self, username: str) -> bool:
        normalized = normalize_username(username)
        return self.repository.find_participant(normalized) is None

    def register(self, username: str, password: str) -> AuthenticatedParticipant:
        normalized = normalize_username(username)
        validate_password(password)
        created = self.repository.create_participant({
            "username": username.strip(),
            "username_normalized": normalized,
            "password_hash": hash_password(password),
            "must_change_password": False,
        })
        return self._new_session(created)

    def login(self, username: str, password: str) -> AuthenticatedParticipant | None:
        username_valid = True
        try:
            normalized = normalize_username(username)
        except ValueError:
            normalized = "__invalid_username__"
            username_valid = False
        self.limiter.check(normalized)
        participant = self.repository.find_participant(normalized) if username_valid else None
        valid = bool(participant and verify_password(participant["password_hash"], password))
        if not valid:
            self.limiter.failed(normalized)
            return None
        self.limiter.succeeded(normalized)
        return self._new_session(participant)

    def restore(self, token: str | None) -> AuthenticatedParticipant | None:
        if not token:
            return None
        now = self.clock()
        session = self.repository.find_session(hash_session_token(token), now)
        if not session:
            return None
        participant = self.repository.get_participant(session["participant_id"])
        if not participant:
            return None
        expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
        return AuthenticatedParticipant(
            participant_id=str(participant["id"]),
            username=participant["username"],
            session_token=token,
            expires_at=expires_at,
            must_change_password=bool(participant.get("must_change_password", False)),
        )

    def logout(self, token: str) -> None:
        self.repository.revoke_session(hash_session_token(token), self.clock())

    def change_password(self, participant_id: str, password: str) -> None:
        validate_password(password)
        self.repository.update_password(participant_id, hash_password(password))

    def _new_session(self, participant: dict[str, Any]) -> AuthenticatedParticipant:
        now = self.clock()
        token = secrets.token_urlsafe(32)
        expires_at = now + self.ttl
        self.repository.create_session(str(participant["id"]), hash_session_token(token), expires_at)
        return AuthenticatedParticipant(
            participant_id=str(participant["id"]),
            username=participant["username"],
            session_token=token,
            expires_at=expires_at,
            must_change_password=bool(participant.get("must_change_password", False)),
        )


_PROCESS_LOGIN_LIMITER = LoginAttemptLimiter()