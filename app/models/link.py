from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func
from db.session import Base

class Link(Base):
    __tablename__ = "links"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0)
    created = Column(DateTime(timezone=True), server_default=func.now())
