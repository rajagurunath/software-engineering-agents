import asyncio
import logging
from core.bot import SlackBotHandler
from core.workflows import PRWorkflows
from dbos import DBOS, DBOSConfig
from dotenv import load_dotenv
import os

load_dotenv(override=True) 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    logger.info("Starting Slack Bot System")
    
    # Initialize DBOS
    config: DBOSConfig= dict(
        name="kkk",
        database_url="postgresql://postgres:postgres@localhost:5432/agent_team",

        # Add other DBOS configuration as needed
    )
    DBOS(config=config)
    DBOS.launch()
    
    # Initialize and start the bot
    bot_handler = SlackBotHandler()
    
    # Start the bot
    await bot_handler.start()

if __name__ == "__main__":
    asyncio.run(main())