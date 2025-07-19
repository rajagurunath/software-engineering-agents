# Uses the crawl4ai Python library to scrape website content into Markdown files
import os
import logging
import asyncio
from crawl4ai import AsyncWebCrawler # Assuming this is the correct import
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, BestFirstCrawlingStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the output directory at the module level so it can be imported
MARKDOWN_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'markdown4')

async def scrape_website_with_crawl4ai_lib(start_url: str, output_dir: str):
    """
    Uses the crawl4ai library (async) to scrape the website into Markdown files.
    """
    logging.info(f"Starting crawl4ai library scrape for {start_url}")
    logging.info(f"Output directory: {output_dir}")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=2, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,  # Show progress during crawling
    )


    try:
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(
                url=start_url,
                output_folder=output_dir,
                output_format="markdown",
                crawl_depth=1000,  # Adjust as needed,
                max_links=1000,  # Adjust as needed
                config=config,
            )
            for result in results:
                if result:
                    logging.info(f"crawl4ai arun() returned: {type(result)}")
                    if hasattr(result, 'links'):
                        logging.info(f"Links extracted: {result.links}")
                        for link_type in ['internal', 'external']:
                            if link_type in result.links:
                                for link in result.links[link_type]:
                                    link_url = link.get('href')
                                    print(f"Link URL: {link}")
                                    if link_url:
                                        try:
                                            # Crawl each link and save as Markdown
                                            result = await crawler.arun(
                                                url=link_url,
                                                output_folder=output_dir,
                                                output_format="markdown"
                                            )
                                            print(link.get('title'))
                                            if result and hasattr(result, 'markdown') and 'text' in link:
                                                # Use the title as the file name
                                                file_name = f"{link.get('text').replace(' ', '_').replace('/', '_')}.md"
                                                file_path = os.path.join(output_dir, file_name)
                                                file_name2 = f"{link.get('text').replace(' ', '_').replace('/', '_')}.json"
                                                file_path2 = os.path.join(output_dir, file_name2)
                                                # Save the markdown content to the file
                                                with open(file_path, 'w', encoding='utf-8') as file:
                                                    file.write(result.markdown)
                                                with open(file_path2, 'w', encoding='utf-8') as file:
                                                    file.write(result.json())

                                                logging.info(f"Saved Markdown file: {file_path}")
                                            else:
                                                logging.warning(f"Result missing 'markdown' or 'title' attributes for {link_url}")
                                        except Exception as e:
                                            logging.error(f"Failed to crawl {link_url}: {e}")
            else:
                logging.info("crawl4ai arun() completed (return value might be None or missing expected attributes).")

        logging.info("crawl4ai library crawl finished successfully.")
        return True

    except ImportError:
        logging.error("Failed to import AsyncWebCrawler from crawl4ai.")
        logging.error("Please ensure the crawl4ai library is installed correctly (`pip install crawl4ai`).")
        return False
    except AttributeError as e:
         logging.error(f"crawl4ai library usage error: {e}. The assumed parameters (e.g., output_folder) might be incorrect.")
         logging.error("Please check the crawl4ai library documentation for correct usage.")
         return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while running crawl4ai library: {e}", exc_info=True)
        return False

async def main_async():
    """Async entry point for running the scraper directly."""
    TARGET_URL = "https://docs.io.net/docs/block-rewards"
    logging.info(f"Markdown files will be saved in: {MARKDOWN_DATA_DIR}")
    if await scrape_website_with_crawl4ai_lib(TARGET_URL, MARKDOWN_DATA_DIR):
        logging.info("Scraping process initiated successfully via crawl4ai library.")
    else:
        logging.error("Scraping process failed.")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main_async())
