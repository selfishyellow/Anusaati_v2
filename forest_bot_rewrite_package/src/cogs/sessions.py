import discord
from discord.ext import commands
from discord import app_commands
from src.database.session import AsyncSessionLocal
from src.database.models import ForestSession, User, GuildSettings, Participant
from src.ui.embeds import ForestEmbeds
from src.ui.views import SessionView
from datetime import datetime, timedelta
from sqlalchemy import select
from typing import Optional
import logging

class Sessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("forest_bot.sessions")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Check guild settings for parse channel
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(GuildSettings).where(GuildSettings.guild_id == message.guild.id))
            settings = result.scalar_one_or_none()
            
            if settings and settings.parse_channel_id:
                if message.channel.id != settings.parse_channel_id:
                    return

        # Attempt to parse the message for a Forest invite
        parsed_data = self.bot.forest_parser.parse_message(message.content)
        if not parsed_data:
            return

        await self.create_session(message, parsed_data)

    async def create_session(self, message: discord.Message, data: dict):
        room_code = data["room_code"]
        plant_name = data["plant_name"]
        duration = data["duration"]
        join_url = data["join_url"]
        
        # Default duration if not parsed
        if duration == 0:
            duration = 10 # Default to 10 min if unknown

        # Find plant image
        filename, score = self.bot.asset_manager.get_plant_image(plant_name)
        image_file = None
        image_url = None
        if filename:
            image_file = discord.File(self.bot.asset_manager.get_asset_path(filename), filename=filename)
            image_url = f"attachment://{filename}"
            # Update plant name to the one found in assets if score is high
            if score > 80:
                plant_name = filename.replace(".png", "").replace("_", " ").title()

        start_time = datetime.utcnow() + timedelta(minutes=5) # Default 5 min countdown
        end_time = start_time + timedelta(minutes=duration)

        embed = ForestEmbeds.session_card(
            plant_name=plant_name,
            duration=duration,
            room_code=room_code,
            start_time=start_time,
            end_time=end_time,
            image_url=image_url,
            host_name=message.author.display_name
        )

        view = SessionView(room_url=join_url)
        
        # Check guild settings for role ping and channel
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(GuildSettings).where(GuildSettings.guild_id == message.guild.id))
            settings = result.scalar_one_or_none()
            
            target_channel = message.channel
            ping_content = ""
            
            if settings:
                if settings.session_channel_id:
                    chan = self.bot.get_channel(settings.session_channel_id)
                    if chan:
                        target_channel = chan
                if settings.forest_role_id:
                    ping_content = f"<@&{settings.forest_role_id}>"

            sent_msg = await target_channel.send(content=ping_content, embed=embed, view=view, file=image_file)
            
            # Save to database
            # Ensure user exists
            user_result = await db.execute(select(User).where(User.user_id == message.author.id))
            user = user_result.scalar_one_or_none()
            if not user:
                user = User(user_id=message.author.id)
                db.add(user)
            
            new_session = ForestSession(
                guild_id=message.guild.id,
                host_id=message.author.id,
                room_code=room_code,
                plant_name=plant_name,
                duration=duration,
                start_time=start_time,
                end_time=end_time,
                message_id=sent_msg.id
            )
            db.add(new_session)
            await db.commit()

            if settings and settings.delete_raw:
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass

    @app_commands.command(name="setup", description="Configure Forest Bot for this server")
    @app_commands.describe(
        role="The role to ping for new sessions", 
        post_channel="The channel where session cards will be posted",
        parse_channel="The ONLY channel where the bot will listen for Forest invite links"
    )
    @commands.has_permissions(manage_guild=True)
    async def setup(
        self, 
        interaction: discord.Interaction, 
        role: Optional[discord.Role] = None, 
        post_channel: Optional[discord.TextChannel] = None,
        parse_channel: Optional[discord.TextChannel] = None
    ):
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(GuildSettings).where(GuildSettings.guild_id == interaction.guild.id))
            settings = result.scalar_one_or_none()
            
            if not settings:
                settings = GuildSettings(guild_id=interaction.guild.id)
                db.add(settings)
            
            if role:
                settings.forest_role_id = role.id
            if post_channel:
                settings.session_channel_id = post_channel.id
            if parse_channel:
                settings.parse_channel_id = parse_channel.id
                
            await db.commit()
            
            # Onboarding ping/notification
            ping_msg = f" {role.mention}" if role else ""
            response_text = (
                f"✅ **Forest Bot Setup Complete!**{ping_msg}\n\n"
                f"📍 **Parse Channel:** {parse_channel.mention if parse_channel else (interaction.channel.mention if not settings.parse_channel_id else f'<#{settings.parse_channel_id}>')}\n"
                f"📢 **Post Channel:** {post_channel.mention if post_channel else (interaction.channel.mention if not settings.session_channel_id else f'<#{settings.session_channel_id}>')}\n"
                f"🔔 **Session Role:** {role.mention if role else (f'<@&{settings.forest_role_id}>' if settings.forest_role_id else 'None')}\n\n"
                "The bot is now ready to track your Forest sessions!"
            )
            
            await interaction.response.send_message(response_text)
            
            # If a role was provided, also send a public message to "onboard" the server
            if role:
                await interaction.channel.send(f"📢 {role.mention}, Forest Bot has been configured for this server! Start sharing your invite links in the parse channel to begin.")

async def setup(bot):
    await bot.add_cog(Sessions(bot))
