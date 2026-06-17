import discord
from discord.ext import commands, tasks
from src.database.session import AsyncSessionLocal
from src.database.models import Reminder, ForestSession, User, Participant, GuildSettings
from sqlalchemy import select, update
from datetime import datetime, timedelta
import logging

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
        self.check_sessions.start()
        self.logger = logging.getLogger("forest_bot.reminders")

    def cog_unload(self):
        self.check_reminders.cancel()
        self.check_sessions.cancel()

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        """Checks for reminders that need to be sent."""
        now = datetime.utcnow()
        async with AsyncSessionLocal() as db:
            stmt = select(Reminder).where(Reminder.remind_at <= now, Reminder.status == "pending")
            result = await db.execute(stmt)
            reminders = result.scalars().all()
            
            for reminder in reminders:
                user = self.bot.get_user(reminder.user_id)
                if user:
                    try:
                        # Fetch session info for context
                        session_stmt = select(ForestSession).where(ForestSession.id == reminder.session_id)
                        session_result = await db.execute(session_stmt)
                        session = session_result.scalar_one_or_none()
                        
                        if session:
                            await user.send(f"⏰ **Reminder:** The Forest session for **{session.plant_name}** is starting {session.start_time.strftime('%H:%M')} UTC! (Room: `{session.room_code}`)")
                        
                        reminder.status = "sent"
                    except discord.Forbidden:
                        self.logger.warning(f"Could not send DM to {reminder.user_id}")
                
            await db.commit()

    @tasks.loop(minutes=5)
    async def check_sessions(self):
        """Checks for sessions that have ended and updates user stats."""
        now = datetime.utcnow()
        async with AsyncSessionLocal() as db:
            # Find active sessions that have passed their end_time
            stmt = select(ForestSession).where(ForestSession.end_time <= now, ForestSession.status != "completed")
            result = await db.execute(stmt)
            sessions = result.scalars().all()
            
            for session in sessions:
                # Mark as completed
                session.status = "completed"
                
                # Update host stats
                host_stmt = select(User).where(User.user_id == session.host_id)
                host_result = await db.execute(host_stmt)
                host = host_result.scalar_one_or_none()
                if host:
                    host.focus_minutes += session.duration
                    host.sessions_hosted += 1
                    self.update_streak(host, now)

                # Update participants stats
                part_stmt = select(Participant).where(Participant.session_id == session.id)
                part_result = await db.execute(part_stmt)
                participants = part_result.scalars().all()
                
                for participant in participants:
                    # Skip host as already handled
                    if participant.user_id == session.host_id:
                        continue
                        
                    user_stmt = select(User).where(User.user_id == participant.user_id)
                    user_result = await db.execute(user_stmt)
                    user = user_result.scalar_one_or_none()
                    if user:
                        user.focus_minutes += session.duration
                        user.sessions_joined += 1
                        self.update_streak(user, now)
                
            await db.commit()

    def update_streak(self, user: User, now: datetime):
        if not user.last_session_at:
            user.current_streak = 1
        else:
            diff = now - user.last_session_at
            if diff < timedelta(hours=36): # Within ~1.5 days to keep streak alive
                user.current_streak += 1
            elif diff > timedelta(hours=48):
                user.current_streak = 1
        
        user.last_session_at = now
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak

async def setup(bot):
    await bot.add_cog(Reminders(bot))
