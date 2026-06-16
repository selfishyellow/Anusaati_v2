import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from aiohttp import web
from src.services.asset_manager import AssetManager
from src.services.forest_parser import ForestParser
from src.ui.views import SessionView
from src.database.session import init_db

load_dotenv()

class ForestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None
        )
        
        self.asset_manager = AssetManager()
        self.forest_parser = ForestParser()
        self.logger = logging.getLogger("forest_bot")

    async def setup_hook(self):
        # Initialize database
        await init_db()
        
        # Register persistent views
        self.add_view(SessionView())
        
        # Load cogs
        for filename in os.listdir("./src/cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                await self.load_extension(f"src.cogs.{filename[:-3]}")
                self.logger.info(f"Loaded extension: {filename}")

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Forest Bot is online!")

async def health_check(request):
    return web.Response(text="Bot is alive!")

async def run_bot():
    bot = ForestBot()
    
    # Setup web server for Render health checks
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Use PORT env var provided by Render, default to 8080
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logging.error("DISCORD_TOKEN is not set in environment variables.")
        return

    # Start web server and bot
    await site.start()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
