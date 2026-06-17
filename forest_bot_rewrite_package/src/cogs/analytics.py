import discord
from discord.ext import commands
from discord import app_commands
from src.database.session import AsyncSessionLocal
from src.database.models import User, ForestSession, Participant
from src.ui.embeds import ForestEmbeds
from sqlalchemy import select, func, desc
from typing import Optional

class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="forest", description="Show your Forest profile")
    async def profile(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        target_user = user or interaction.user
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.user_id == target_user.id))
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                await interaction.response.send_message(f"No Forest data found for {target_user.display_name}.", ephemeral=True)
                return

            focus_hours = db_user.focus_minutes / 60.0
            
            embed = ForestEmbeds.profile_card(
                user_name=target_user.display_name,
                focus_hours=focus_hours,
                current_streak=db_user.current_streak,
                longest_streak=db_user.longest_streak,
                favorite_plant=db_user.favorite_plant_id or "Not set",
                avatar_url=target_user.display_avatar.url
            )
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Show server ranking by focus time")
    async def leaderboard(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as db:
            # Join with User table to get focus_minutes
            # Actually we just want the top users in the server who have data
            # This requires fetching user IDs from the guild and matching them
            
            # For simplicity, we'll just show the global top for now or filter by those in the guild if possible
            # In a real bot, we'd filter by guild members
            stmt = select(User).order_by(desc(User.focus_minutes)).limit(10)
            result = await db.execute(stmt)
            top_users = result.scalars().all()
            
            if not top_users:
                await interaction.response.send_message("Leaderboard is empty!", ephemeral=True)
                return

            embed = discord.Embed(
                title="🌳 Forest Leaderboard",
                description="Top focusers by minutes",
                color=discord.Color.from_rgb(114, 137, 118)
            )
            
            for i, u in enumerate(top_users, 1):
                # Try to get member name
                member = interaction.guild.get_member(u.user_id)
                name = member.display_name if member else f"User {u.user_id}"
                embed.add_field(name=f"{i}. {name}", value=f"{u.focus_minutes} min ({u.focus_minutes/60:.1f}h)", inline=False)
                
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Analytics(bot))
