import json
import logging

from app.schemas.pdp_audit import PDPAuditEvent
from app.audit.pdp_audit_repository import insert_pdp_audit_event

audit_logger = logging.getLogger("pdp_audit")
audit_logger.setLevel(logging.INFO)



def record_pdp_audit_event(event: PDPAuditEvent) -> None:
    """
     Records a PDP audit event by inserting it into the database and logging it.

     Args:
         event (PDPAuditEvent): The PDP audit event to record.
     """
    insert_pdp_audit_event(event)

    audit_logger.info(
        "pdp_audit_event=%s",
        json.dumps(event.model_dump(mode="json")),
    )
    
    