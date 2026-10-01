from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.models import Ticket
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate
)

from app.ml.predictor import predict_category
from app.ml.priority import predict_priority
from app.ml.resolution import get_resolution_suggestion

from app.services.sla_service import calculate_sla_status
from app.services.duplicate_service import find_best_duplicate


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# ============================================================
# DUPLICATE CHECK REQUEST
# ============================================================

class DuplicateCheckRequest(BaseModel):
    title: str
    description: str


# ============================================================
# CREATE TICKET
# ============================================================

@router.post("/", response_model=dict, status_code=201)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db)
):
    ticket_text = f"{ticket.title}. {ticket.description}"

    predicted_category = predict_category(ticket_text)

    predicted_priority = predict_priority(ticket_text)

    sla_hours = {
        "CRITICAL": 4,
        "HIGH": 8,
        "MEDIUM": 24,
        "LOW": 72
    }

    sla_deadline = datetime.utcnow() + timedelta(
        hours=sla_hours[predicted_priority]
    )

    resolution_suggestion = get_resolution_suggestion(
        predicted_category
    )

    existing_tickets = db.query(Ticket).all()

    duplicate_result = find_best_duplicate(
        ticket_text,
        existing_tickets
    )

    duplicate_ticket_id = duplicate_result["ticket_id"]
    duplicate_similarity = duplicate_result["similarity"]
    duplicate_detected = duplicate_result["is_duplicate"]

    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=predicted_category,
        priority=predicted_priority,
        sla_deadline=sla_deadline,
        resolution_suggestion=resolution_suggestion,
        status="OPEN"
    )

    db.add(new_ticket)

    db.commit()

    db.refresh(new_ticket)

    return {
        "ticket": {
            "id": new_ticket.id,
            "title": new_ticket.title,
            "description": new_ticket.description,
            "category": new_ticket.category,
            "priority": new_ticket.priority,
            "sla_deadline": new_ticket.sla_deadline,
            "resolution_suggestion": new_ticket.resolution_suggestion,
            "status": new_ticket.status,
            "created_at": new_ticket.created_at
        },
        "duplicate_detected": duplicate_detected,
        "duplicate_ticket_id": duplicate_ticket_id,
        "duplicate_similarity": duplicate_similarity
    }


# ============================================================
# CHECK DUPLICATE BEFORE CREATION
# ============================================================

@router.post("/check-duplicate")
def check_duplicate(
    request: DuplicateCheckRequest,
    db: Session = Depends(get_db)
):
    ticket_text = (
        f"{request.title}. "
        f"{request.description}"
    )

    existing_tickets = db.query(Ticket).all()

    duplicate_result = find_best_duplicate(
        ticket_text,
        existing_tickets
    )

    return {
        "title": request.title,
        "description": request.description,
        "duplicate_detected": duplicate_result["is_duplicate"],
        "duplicate_ticket_id": duplicate_result["ticket_id"],
        "similarity": duplicate_result["similarity"]
    }


# ============================================================
# GET ALL TICKETS
# ============================================================

# ============================================================
# GET ALL TICKETS / FILTER TICKETS
# ============================================================

@router.get("/", response_model=list[TicketResponse])
def get_tickets(
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    if status is not None:
        query = query.filter(
            Ticket.status == status
        )

    if priority is not None:
        query = query.filter(
            Ticket.priority == priority
        )

    if category is not None:
        query = query.filter(
            Ticket.category == category
        )

    return (
        query
        .order_by(Ticket.id.desc())
        .all()
    )


# ============================================================
# TICKET STATISTICS
# ============================================================

@router.get("/stats/summary")
def ticket_statistics(
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).all()

    total = len(tickets)

    open_count = sum(
        1
        for ticket in tickets
        if ticket.status == "OPEN"
    )

    in_progress_count = sum(
        1
        for ticket in tickets
        if ticket.status == "IN_PROGRESS"
    )

    resolved_count = sum(
        1
        for ticket in tickets
        if ticket.status == "RESOLVED"
    )

    critical_count = sum(
        1
        for ticket in tickets
        if ticket.priority == "CRITICAL"
    )

    high_count = sum(
        1
        for ticket in tickets
        if ticket.priority == "HIGH"
    )

    on_track_count = 0
    at_risk_count = 0
    breached_count = 0

    for ticket in tickets:

        sla_result = calculate_sla_status(
            ticket.sla_deadline
        )

        if sla_result["sla_status"] == "ON_TRACK":
            on_track_count += 1

        elif sla_result["sla_status"] == "AT_RISK":
            at_risk_count += 1

        elif sla_result["sla_status"] == "BREACHED":
            breached_count += 1

    return {
        "total_tickets": total,
        "open_tickets": open_count,
        "in_progress_tickets": in_progress_count,
        "resolved_tickets": resolved_count,
        "critical_tickets": critical_count,
        "high_tickets": high_count,
        "on_track_tickets": on_track_count,
        "at_risk_tickets": at_risk_count,
        "breached_tickets": breached_count
    }

# ============================================================
# TICKET COUNTS BY CATEGORY
# ============================================================

@router.get("/stats/categories")
def ticket_category_statistics(
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).all()

    category_counts = {}

    for ticket in tickets:
        category = ticket.category or "Uncategorized"

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    return {
        "categories": category_counts
    }

# ============================================================
# TICKET COUNTS BY PRIORITY
# ============================================================

@router.get("/stats/priorities")
def ticket_priority_statistics(
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).all()

    priority_counts = {}

    for ticket in tickets:
        priority = ticket.priority or "Uncategorized"

        priority_counts[priority] = (
            priority_counts.get(priority, 0) + 1
        )

    return {
        "priorities": priority_counts
    }
@router.get("/stats/statuses")
def ticket_status_statistics(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    status_counts = {}

    for ticket in tickets:
        status = ticket.status or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1

    return {"statuses": status_counts}
# ============================================================
# GET TICKET SLA
# ============================================================

@router.get("/{ticket_id}/sla")
def get_ticket_sla(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    sla_result = calculate_sla_status(
        ticket.sla_deadline
    )

    return {
        "ticket_id": ticket_id,
        "sla_deadline": ticket.sla_deadline,
        **sla_result
    }


# ============================================================
# GET SINGLE TICKET
# ============================================================

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket


# ============================================================
# DELETE TICKET
# ============================================================

@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    db.delete(ticket)

    db.commit()

    return {
        "message": "Ticket deleted successfully",
        "ticket_id": ticket_id
    }


# ============================================================
# UPDATE TICKET
# ============================================================

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db)
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if ticket_update.category is not None:
        ticket.category = ticket_update.category

    if ticket_update.priority is not None:
        ticket.priority = ticket_update.priority

    if ticket_update.status is not None:
        ticket.status = ticket_update.status

    db.commit()

    db.refresh(ticket)

    return ticket