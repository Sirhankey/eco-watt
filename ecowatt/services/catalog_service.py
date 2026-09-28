"""User catalog creation and moderation workflows."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List
from uuid import uuid4

from ecowatt.models.catalog import CatalogAppliance, CatalogPCComponent, CatalogSubmission
from ecowatt.services.catalog_validation import (
    duplicate_key,
    find_duplicate,
    validate_submission_payload,
)

LOGGER = logging.getLogger("ecowatt.catalog")


@dataclass
class CatalogStore:
    personal_items: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    submissions: Dict[str, CatalogSubmission] = field(default_factory=dict)
    moderation_audit: List[Dict[str, Any]] = field(default_factory=list)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_personal_item(store: CatalogStore, participant_id: str, kind: str, payload: Dict[str, Any], created_by_name: str | None = None) -> CatalogAppliance | CatalogPCComponent:
    validated = validate_submission_payload(kind, payload)
    existing = find_duplicate(store.personal_items.get(participant_id, []), validated, kind, participant_id)
    if existing is not None:
        LOGGER.info("catalog_duplicate kind=%s owner_scope=%s", kind, participant_id[:8])
        raise ValueError("Este item ja foi criado na sua conta.")

    item_id = str(uuid4())
    item = {**validated, "id": item_id, "participant_id": participant_id, "created_by_name": created_by_name, "created_at": _now()}
    store.personal_items.setdefault(participant_id, []).append(item)
    if kind == "appliance":
        return CatalogAppliance(**item)
    if kind == "pc_component":
        return CatalogPCComponent(**item)
    raise ValueError("Apenas aparelhos e componentes podem ser itens pessoais.")


def submit_catalog_item(store: CatalogStore, participant_id: str, kind: str, payload: Dict[str, Any], submitted_by_name: str | None = None) -> CatalogSubmission:
    validated = validate_submission_payload(kind, payload)
    if any(submission.status == "pending" and duplicate_key(submission.payload, kind, participant_id) == duplicate_key(validated, kind, participant_id) for submission in store.submissions.values()):
        LOGGER.info("catalog_duplicate_submission kind=%s owner_scope=%s", kind, participant_id[:8])
        raise ValueError("Ja existe uma submissao pendente equivalente.")
    submission = CatalogSubmission(
        id=str(uuid4()),
        kind=kind,
        payload=validated,
        participant_id=participant_id,
        submitted_by_name=submitted_by_name,
    )
    store.submissions[submission.id] = submission
    LOGGER.info("catalog_submission_created kind=%s submission_scope=%s", kind, submission.id[:8])
    return submission


def moderate_submission(store: CatalogStore, submission_id: str, moderator_id: str, decision: str, reason: str | None = None) -> CatalogSubmission:
    if decision not in {"approved", "rejected", "archived"}:
        raise ValueError("Decisao de moderacao invalida.")
    submission = store.submissions.get(submission_id)
    if submission is None:
        raise KeyError("Submissao nao encontrada.")
    if submission.status != "pending":
        raise ValueError("A submissao ja foi decidida.")
    submission.status = decision
    submission.moderator_id = moderator_id
    submission.moderation_reason = reason
    store.moderation_audit.append({
        "submission_id": submission.id,
        "moderator_id": moderator_id,
        "decision": decision,
        "occurred_at": _now(),
    })
    LOGGER.info("catalog_submission_moderated decision=%s submission_scope=%s", decision, submission.id[:8])
    return submission
