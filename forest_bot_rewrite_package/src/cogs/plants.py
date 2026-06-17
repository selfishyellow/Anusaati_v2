import discord
from discord.ext import commands
from discord import app_commands
from src.database.session import AsyncSessionLocal
from src.database.models import ForestSession
from sqlalchemy import select, func
from typing import Optional

class Plants(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="plant", description="Show information about a plant")
    @app_commands.describe(name="The name of the plant")
    async def plant_info(self, interaction: discord.Interaction, name: str):
        filename, score = self.bot.asset_manager.get_plant_image(name)
        
        if not filename:
            await interaction.response.send_message(f"Could not find a plant matching '{name}'.", ephemeral=True)
            return

        display_name = filename.replace(".png", "").replace("_", " ").title()
        
        embed = discord.Embed(
            title=f"🌿 {display_name}",
            color=discord.Color.from_rgb(114, 137, 118)
        )
        
        # Statistics (how many times this plant was used)
        async with AsyncSessionLocal() as db:
            count_stmt = select(func.count(ForestSession.id)).where(ForestSession.plant_name == display_name)
            result = await db.execute(count_stmt)
            count = result.scalar()
            
            embed.add_field(name="Total Times Planted", value=str(count))

        file = discord.File(self.bot.asset_manager.get_asset_path(filename), filename=filename)
        embed.set_image(url=f"attachment://{filename}")
        
        await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(name="plants", description="Gallery of all available plants")
    async def plants_gallery(self, interaction: discord.Interaction):
        plants = sorted(list(self.bot.asset_manager.plants.keys()))
        
        # Simple pagination: 10 per page
        pages = []
        for i in range(0, len(plants), 15):
            page_plants = plants[i:i+15]
            embed = discord.Embed(
                title="🌿 Plant Gallery",
                description="\n".join([f"• {p.title()}" for p in page_plants]),
                color=discord.Color.from_rgb(114, 137, 118)
            )
            embed.set_footer(text=f"Showing {i+1} - {min(i+15, len(plants))} of {len(plants)} plants")
            pages.append(embed)
            
        if not pages:
            await interaction.response.send_message("No plants found in assets!")
            return

        await interaction.response.send_message(embed=pages[0])
        # In a real bot, I'd add pagination buttons here

async def setup(bot):
    await bot.add_cog(Plants(bot))
