from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.session import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    user_name = Column(String, nullable=False)
    auth_methods = relationship("AuthMethod", back_populates="user")
    links = relationship("Link", back_populates="user")


class AuthMethod(Base):
    __tablename__ = "auth_methods"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="auth_methods")
