from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    websites = relationship("BlockedWebsite", back_populates="user")
    focus_sessions = relationship("FocusSession", back_populates="user")


class BlockedWebsite(Base):
    __tablename__ = "blocked_websites"

    id = Column(Integer, primary_key=True, index=True)
    website = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="websites")


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="focus_sessions")
