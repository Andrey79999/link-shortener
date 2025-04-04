from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
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
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="links")
    stats = relationship("LinkStats", back_populates="link")

class LinkStats(Base):
    __tablename__ = "links_stats"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"))
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    ip = Column(String(45))
    country = Column(String(100))
    city = Column(String(100))
    user_agent = Column(String(256))
    link = relationship("Link", back_populates="stats")
