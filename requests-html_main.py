import time
import json
import asyncio
import logging
from pathlib import Path
from requests_html import AsyncHTMLSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
LOG = logging.getLogger(__name__)


async def get_category_urls(homepage, asession):
    """Collects all the category urls from the homepage."""
    try:
        r = await asession.get(homepage)
        r.raise_for_status()
        LOG.info("Successfully connected to homepage...")
        
        # requests-html makes absolute links easy
        cat_links = [link for a in r.html.find(".nav-list ul li a") for link in a.absolute_links]
        LOG.info(f"Found {len(cat_links)} category links")
        return cat_links

    except Exception as err:
        LOG.error(f"Error getting category URLs: {err}")
        return []


async def get_book_urls(category_url, asession, semaphore):
    """Collects all book URLs from a category, handling pagination."""
    book_urls = []
    current_url = category_url
    
    async with semaphore:
        while current_url:
            try:
                r = await asession.get(current_url)
                r.raise_for_status()
                
                # Get all book links on the current page
                for article in r.html.find("ol.row li article.product_pod"):
                    link_element = article.find("h3 a", first=True)
                    if link_element:
                        book_urls.extend(link_element.absolute_links)
                
                # Check for a "next" page button
                next_btn = r.html.find("li.next a", first=True)
                if next_btn:
                    current_url = list(next_btn.absolute_links)[0]
                    LOG.info(f"Moving to next page: {current_url}")
                else:
                    current_url = None  # No more pages

            except Exception as err:
                LOG.error(f"Error getting book URLs from {current_url}: {err}")
                current_url = None

    LOG.info(f"Total books found in category {category_url}: {len(book_urls)}")
    return book_urls


async def get_book_details(book_url, asession, semaphore):
    """Scrapes the details of a single book."""
    async with semaphore:
        try:
            r = await asession.get(book_url)
            r.raise_for_status()
            LOG.info(f"Scraping book: {book_url}")

            data = {}
            title_elem = r.html.find(".product_main h1", first=True)
            price_elem = r.html.find(".product_main p.price_color", first=True)
            
            data['title'] = title_elem.text if title_elem else "N/A"
            data['price'] = price_elem.text if price_elem else "N/A"
            
            table = r.html.find('table.table-striped', first=True)
            if table:
                rows = table.find('tr')
                for row in rows:
                    header = row.find('th', first=True)
                    value = row.find('td', first=True)
                    if header and value:
                        data[header.text] = value.text
            
            return data

        except Exception as err:
            LOG.error(f"Error scraping book details for {book_url}: {err}")
            return None


async def save_data(data):
    """Saves the scraped data to a JSON file."""
    output_dir = Path("scraped-data")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "data.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    LOG.info(f"Data saved to {filepath}")


async def main():
    homepage = "https://books.toscrape.com"
    asession = AsyncHTMLSession()
    semaphore = asyncio.Semaphore(5)  # Max 5 parallel requests at a time

    try:
        start = time.perf_counter()
        
        # 1. Get all category URLs
        cat_urls = await get_category_urls(homepage, asession)
        
        # 2. Get all book URLs from all categories
        nested_book_urls = await asyncio.gather(*[get_book_urls(url, asession, semaphore) for url in cat_urls])
        book_urls = [url for sublist in nested_book_urls for url in sublist]
        
        # Remove duplicates if any
        book_urls = list(set(book_urls))
        LOG.info(f"Total unique book URLs found: {len(book_urls)}")
        
        # 3. Get details for each book
        data = await asyncio.gather(*[get_book_details(url, asession, semaphore) for url in book_urls])
        
        # Filter out failed requests
        data = [item for item in data if item is not None]
        
        # 4. Save the data
        await save_data(data)
        
        end = time.perf_counter()
        LOG.info(f"Time taken to get data: {end - start:.2f} seconds")

    finally:
        await asession.close()


if __name__ == '__main__':
    asyncio.run(main())