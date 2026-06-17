import discord
from typing import Optional
from src.database.session import AsyncSessionLocal
from src.database.models import Participant, ForestSession, User, Reminder
from sqlalchemy import select
from datetime import datetime, timedelta

class SessionView(discord.ui.View):
    def __init__(self, room_url: Optional[str] = None):
        super().__init__(timeout=None)
        if room_url:
            self.add_item(discord.ui.Button(label="Join Room", url=room_url, style=discord.ButtonStyle.link))

    @discord.ui.button(label="Notify Me", style=discord.ButtonStyle.primary, custom_id="forest:notify")
    async def notify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ReminderSelectView()
        await interaction.response.send_message("When should I remind you?", view=view, ephemeral=True)

    @discord.ui.button(label="Interested", style=discord.ButtonStyle.secondary, custom_id="forest:interested")
    async def interested_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with AsyncSessionLocal() as db:
            # Find the session associated with this message
            stmt = select(ForestSession).where(ForestSession.message_id == interaction.message.id)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                await interaction.response.send_message("Could not find this session in the database.", ephemeral=True)
                return

            # Check if user already interested
            part_stmt = select(Participant).where(Participant.session_id == session.id, Participant.user_id == interaction.user.id)
            part_result = await db.execute(part_stmt)
            if part_result.scalar_one_or_none():
                await interaction.response.send_message("You've already marked your interest!", ephemeral=True)
                return

            # Add participant
            # Ensure user exists
            user_stmt = select(User).where(User.user_id == interaction.user.id)
            user_result = await db.execute(user_stmt)
            if not user_result.scalar_one_or_none():
                db.add(User(user_id=interaction.user.id))
            
            db.add(Participant(session_id=session.id, user_id=interaction.user.id))
            await db.commit()
            
            await interaction.response.send_message("Marked as interested! You'll be included in the session analytics.", ephemeral=True)

    @discord.ui.button(label="Plant Info", style=discord.ButtonStyle.secondary, custom_id="forest:plant_info")
    async def plant_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with AsyncSessionLocal() as db:
            stmt = select(ForestSession).where(ForestSession.message_id == interaction.message.id)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                await interaction.response.send_message(f"This is a session for **{session.plant_name}** ({session.duration} min).", ephemeral=True)
            else:
                await interaction.response.send_message("Could not find plant info for this session.", ephemeral=True)

class ReminderSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(
        placeholder="Choose reminder time",
        options=[
            discord.SelectOption(label="5 minutes before", value="5"),
            discord.SelectOption(label="10 minutes before", value="10"),
            discord.SelectOption(label="15 minutes before", value="15"),
        ],
        custom_id="forest:reminder_select"
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        minutes_before = int(select.values[0])
        
        async with AsyncSessionLocal() as db:
            # Find the session
            stmt = select(ForestSession).where(ForestSession.message_id == interaction.message.id)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                await interaction.response.send_message("Could not find this session.", ephemeral=True)
                return

            remind_at = session.start_time - timedelta(minutes=minutes_before)
            
            if remind_at < datetime.utcnow():
                await interaction.response.send_message("It's too late to set this reminder!", ephemeral=True)
                return

            # Add reminder
            db.add(Reminder(user_id=interaction.user.id, session_id=session.id, remind_at=remind_at))
            await db.commit()
            
            await interaction.response.send_message(f"Reminder set for {minutes_before} minutes before start!", ephemeral=True)
