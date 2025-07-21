import asyncio
import logging
from core.architect_bot import ArchitectBotHandler
from core.developer_bot import DeveloperBotHandler
from core.data_analyst_bot import DataAnalystBotHandler
from core.sentry_bot import SentryBotHandler
from core.main_dispatcher_bot import MainDispatcherBotHandler
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
    """Main application entry point for multiple specialized bots"""
    logger.info("Starting Multi-Bot Agent Team System")
    
    # Initialize DBOS
    config: DBOSConfig = dict(
        name="agent-team-multi-bot",
        database_url="postgresql://postgres:postgres@localhost:5432/agent_team",
    )
    DBOS(config=config)
    DBOS.launch()
    
    # Initialize all bot handlers
    try:
        architect_bot = ArchitectBotHandler()
        developer_bot = DeveloperBotHandler()
        data_analyst_bot = DataAnalystBotHandler()
        sentry_bot = SentryBotHandler()
        main_dispatcher_bot = MainDispatcherBotHandler()
        
        logger.info("All bot handlers initialized successfully")
        
        # Start all bots concurrently
        await asyncio.gather(
            architect_bot.start(),
            developer_bot.start(),
            data_analyst_bot.start(),
            sentry_bot.start(),
            main_dispatcher_bot.start(),
            return_exceptions=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start bot system: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())