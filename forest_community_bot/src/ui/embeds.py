import discord
from datetime import datetime, timedelta
from typing import Optional

class ForestEmbeds:
    @staticmethod
    def session_card(
        plant_name: str,
        duration: int,
        room_code: str,
        start_time: datetime,
        end_time: datetime,
        image_url: Optional[str] = None,
        host_name: str = "Unknown"
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"🌳 {plant_name}",
            color=discord.Color.from_rgb(114, 137, 118), # Forest green
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Plant", value=plant_name, inline=True)
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        embed.add_field(name="Room Code", value=f"`{room_code}`", inline=False)
        
        # Discord relative timestamps
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())
        
        embed.add_field(name="Starts", value=f"<t:{start_ts}:R>", inline=True)
        embed.add_field(name="Ends", value=f"<t:{end_ts}:R>", inline=True)
        
        embed.set_footer(text=f"Hosted by {host_name}")
        
        if image_url:
            embed.set_thumbnail(url=image_url)
            
        return embed

    @staticmethod
    def profile_card(
        user_name: str,
        focus_hours: float,
        current_streak: int,
        longest_streak: int,
        favorite_plant: str,
        avatar_url: Optional[str] = None
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"{user_name}'s Forest Profile",
            color=discord.Color.from_rgb(114, 137, 118)
        )
        
        embed.add_field(name="Focus Hours", value=f"⏱️ {focus_hours:.1f}h", inline=True)
        embed.add_field(name="Current Streak", value=f"🔥 {current_streak} days", inline=True)
        embed.add_field(name="Longest Streak", value=f"🏆 {longest_streak} days", inline=True)
        embed.add_field(name="Favorite Plant", value=f"🌿 {favorite_plant}", inline=False)
        
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
            
        return embed
