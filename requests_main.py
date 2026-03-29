import time
import json
import logging
import requests

from pathlib import Path
from bs4 import BeautifulSoup as bs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
LOG = logging.getLogger(__name__)


def get_category_urls(homepage, session):
    """Collects all the category urls from the homepage."""
    try:
        with session.get(homepage) as r:
            r.raise_for_status()
            LOG.info("Successfully connected to homepage...")
            soup = bs(r.text, "html.parser")
            cat_links = [homepage + "/" + a.get("href") for a in soup.select(".nav-list ul li a")]
            LOG.info(f"Found {len(cat_links)} category links")
            return cat_links

    except Exception as err:
        LOG.error(f"Error getting category URLs: {err}")
        return []


def get_book_urls(category_url, session):
    """Collects all book URLs from a category, handling pagination."""
    book_urls = []
    # Normalize: strip the filename so we have the base directory
    base_url = category_url.rsplit("/", 1)[0]
    current_url = category_url
    while current_url:
        try:
            with session.get(current_url) as r:
                r.raise_for_status()
                soup = bs(r.text, "html.parser")
                # Collect book URLs from the current page
                for a in soup.select("ol.row li article.product_pod h3 a"):
                    book_urls.append("https://books.toscrape.com/catalogue/" + a["href"].replace("../", ""))
                # Check for a "next" page button
                next_btn = soup.select_one("li.next a")
                if next_btn:
                    current_url = base_url + "/" + next_btn["href"]
                    LOG.info(f"Moving to next page: {current_url}")
                else:
                    current_url = None  # No more pages, stop the loop

        except Exception as err:
            LOG.error(f"Error getting book URLs from {current_url}: {err}")
            current_url = None
                
    LOG.info(f"Total books found in category {category_url}: {len(book_urls)}")
    return book_urls
                
    LOG.info(f"Total books found in category: {len(book_urls)}")
    return book_urls


def get_book_details(book_url, session):
    """Scrapes the details of a single book."""
    try:
        with session.get(book_url) as r:
            r.raise_for_status()
            LOG.info(f"Scraping book: {book_url}")
            soup = bs(r.text, "html.parser")
            data = {}
            title_elem = soup.select_one(".product_main h1")
            price_elem = soup.select_one(".product_main p.price_color")
            
            data['title'] = title_elem.text if title_elem else "N/A"
            data['price'] = price_elem.text if price_elem else "N/A"
            
            table = soup.find('table', class_='table table-striped')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    header = row.find('th')
                    value = row.find('td')
                    if header and value:
                        data[header.text] = value.text
            return data

    except Exception as err:
        LOG.error(f"Error scraping book details for {book_url}: {err}")
        return None


def save_data(data):
    """Saves the scraped data to a JSON file."""
    output_dir = Path("scraped-data")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "data.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    LOG.info(f"Data saved to {filepath}")


def main():
    """Main function to orchestrate the scraping process."""
    homepage = "https://books.toscrape.com"
    with requests.Session() as session:
        try:
            start = time.perf_counter()
            
            # 1. Get all category URLs
            cat_urls = get_category_urls(homepage, session)
            
            # 2. Get all book URLs from all categories
            book_urls = []
            for url in cat_urls:
                book_urls.extend(get_book_urls(url, session))
            
            # Remove duplicates
            book_urls = list(set(book_urls))
            LOG.info(f"Total unique book URLs found: {len(book_urls)}")
            
            # 3. Get details for each book
            data = []
            for url in book_urls:
                details = get_book_details(url, session)
                if details:
                    data.append(details)
            
            # 4. Save the data
            save_data(data)
            
            end = time.perf_counter()
            LOG.info(f"Time taken to get data: {end - start:.2f} seconds")

        except Exception as err:
            LOG.error(f"Unexpected error in main: {err}")


if __name__ == '__main__':
    main()