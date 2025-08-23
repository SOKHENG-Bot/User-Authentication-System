from sqlalchemy import Integer, String, Boolean, Column

from app.configuration.database import Base


class User(Base):
    """
    User model for the UAS application.
    """

    __tablename__ = "users"

    # Account fields
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)

    # Role and verification fields
    role = Column(String(20), default="user", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # String representation of the User model
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
