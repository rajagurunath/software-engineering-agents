import asyncio
import time

from crawl4ai import CrawlerRunConfig, AsyncWebCrawler, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter,
    ContentRelevanceFilter,
    SEOFilter,
)
from crawl4ai.deep_crawling.scorers import (
    KeywordRelevanceScorer,
)
import os
MARKDOWN_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'markdown4')

# 1️⃣ Basic Deep Crawl Setup
async def basic_deep_crawl():
    """
    PART 1: Basic Deep Crawl setup - Demonstrates a simple two-level deep crawl.

    This function shows:
    - How to set up BFSDeepCrawlStrategy (Breadth-First Search)
    - Setting depth and domain parameters
    - Processing the results to show the hierarchy
    """
    print("\n===== BASIC DEEP CRAWL SETUP =====")

    # Configure a 2-level deep crawl using Breadth-First Search strategy
    # max_depth=2 means: initial page (depth 0) + 2 more levels
    # include_external=False means: only follow links within the same domain
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=2, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,  # Show progress during crawling
    )

    async with AsyncWebCrawler() as crawler:
        start_time = time.perf_counter()
        print("Crawling guru...")
        results = await crawler.arun(url="https://docs.io.net/docs/block-rewards", config=config)
      
        # Group results by depth to visualize the crawl tree
        pages_by_depth = {}
        for result in results:
            depth = result.metadata.get("depth", 0)
            if depth not in pages_by_depth:
                pages_by_depth[depth] = []
            pages_by_depth[depth].append(result.url)
            print(result.markdown)
            link = result.links
            print(link.get('text'))
            file_name = f"{link.get('text').replace(' ', '_').replace('/', '_')}.md"
            file_path = os.path.join(MARKDOWN_DATA_DIR, file_name)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(result.markdown)
            print(f"Markdown file saved to {file_path}")

        print(f"✅ Crawled {len(results)} pages total")

        # Display crawl structure by depth
        for depth, urls in sorted(pages_by_depth.items()):
            print(urls)
            print(f"\nDepth {depth}: {len(urls)} pages")
            # Show first 3 URLs for each depth as examples
            for url in urls[:3]:
                print(f"  → {url}")
            if len(urls) > 3:
                print(f"  ... and {len(urls) - 3} more")

        print(
            f"\n✅ Performance: {len(results)} pages in {time.perf_counter() - start_time:.2f} seconds"
        )

if __name__ == "__main__":
    asyncio.run(basic_deep_crawl())