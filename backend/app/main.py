from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .knowledge import KNOWLEDGE_BASE
from .models import Ticket
from .schemas import TicketAnalysis, TicketCreate, TicketListItem
from .services.copilot import analyze

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SignalDesk AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local development only; lock this down before deployment.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "signaldesk-ai"}


@app.get("/api/knowledge")
def knowledge():
    return KNOWLEDGE_BASE


@app.post("/api/analyze", response_model=TicketAnalysis)
def analyze_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    result = analyze(payload.title, payload.description)
    row = Ticket(
        title=payload.title,
        description=payload.description,
        category=result["category"],
        severity=result["severity"],
        confidence=result["confidence"],
        escalation="true" if result["escalation"] else "false",
        summary=result["summary"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "title": row.title,
        **result,
        "created_at": row.created_at,
    }


@app.get("/api/tickets", response_model=list[TicketListItem])
def list_tickets(db: Session = Depends(get_db)):
    rows = db.scalars(select(Ticket).order_by(Ticket.created_at.desc())).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "category": row.category,
            "severity": row.severity,
            "confidence": row.confidence,
            "escalation": row.escalation == "true",
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.get("/api/tickets/{ticket_id}", response_model=TicketAnalysis)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    row = db.get(Ticket, ticket_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    result = analyze(row.title, row.description)
    return {
        "id": row.id,
        "title": row.title,
        **result,
        "created_at": row.created_at,
    }
