from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.connection import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    resolution_suggestion = Column(Text, nullable=True)
    priority = Column(String(20), nullable=True)
    sla_deadline = Column(DateTime,nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)