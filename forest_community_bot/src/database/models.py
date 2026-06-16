from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, Boolean, Float
from datetime import datetime
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class GuildSettings(Base):
    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    forest_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    session_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    parse_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    reminder_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    delete_raw: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    focus_minutes: Mapped[int] = mapped_column(Integer, default=0)
    sessions_hosted: Mapped[int] = mapped_column(Integer, default=0)
    sessions_joined: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_session_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    favorite_plant_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

class ForestSession(Base):
    __tablename__ = "forest_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id"))
    host_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    room_code: Mapped[str] = mapped_column(String(20))
    plant_name: Mapped[str] = mapped_column(String(100))
    duration: Mapped[int] = mapped_column(Integer) # in minutes
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, active, completed, cancelled
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    participants: Mapped[List["Participant"]] = relationship(back_populates="session")

class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("forest_sessions.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    session: Mapped["ForestSession"] = relationship(back_populates="participants")

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("forest_sessions.id"))
    remind_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, sent
