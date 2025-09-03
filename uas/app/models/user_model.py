from app.configuration.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship


class User(Base):
    """
    User model for the UAS application.
    """

    __tablename__ = "users"

    # Account Fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Status Fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="user")

    # Timestamp Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Security Fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    logs = relationship(
        "UserActivityLog", back_populates="user", cascade="all, delete-orphan"
    )


class UserSession(Base):
    """
    User session model for the UAS application.
    """

    __tablename__ = "user_sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(Text, unique=True, nullable=False, index=True)
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")


class UserActivityLog(Base):
    """
    User activicty log model
    """

    __tablename__ = "user_activity_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_email = Column(String(255), unique=True, nullable=False, index=True)
    action = Column(String, nullable=False)
    ip_address = Column(String(45), nullable=True)
    device_info = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    count = Column(Integer, default=1)

    user = relationship("User", back_populates="logs")
