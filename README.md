# Python Scraping Benchmark: Requests vs. HTTPX vs. Requests-HTML vs. AIOHTTP

This repository provides a side-by-side comparison of four popular Python libraries used for web scraping and making HTTP requests. By implementing the same scraping task—extracting book data from [books.toscrape.com](https://books.toscrape.com)—this project highlights the syntax, features, and performance differences between synchronous and asynchronous clients.

## 🚀 Libraries Included:
- **Requests**: The industry standard for synchronous HTTP requests.
- **HTTPX**: A modern, fully featured HTTP client for Python 3 with support for both sync and async.
- **Requests-HTML**: A powerful library for HTML parsing and JavaScript rendering.
- **AIOHTTP**: An asynchronous HTTP client/server for asyncio.

## 📊 Features:
- **Consistent Extraction**: All scripts perform the exact same data extraction logic.
- **Performance Benchmarking**: Integrated timing to compare execution speeds between synchronous and asynchronous implementations.
- **Robustness**: Includes error handling, logging, and pagination management.
- **Standardized Output**: Scraped data is saved to a unified JSON format in the `scraped-data/` directory.

## 🛠️ Getting Started

### Prerequisites
- Python 3.7+
- A virtual environment (recommended)

### Installation
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install requests httpx requests-html aiohttp beautifulsoup4
```

### Running the benchmarks
You can run each script individually to compare their output and performance:

```bash
python requests_main.py
python httpx_main.py
python requests-html_main.py
python aiohttp_main.py
```

## 📝 Project Structure
- `requests_main.py`: Implementation using the `requests` library.
- `httpx_main.py`: Implementation using the `httpx` (async) library.
- `requests-html_main.py`: Implementation using `requests-html`.
- `aiohttp_main.py`: Implementation using `aiohttp`.
- `scraped-data/`: Directory where the resulting data is stored.
- `.gitignore`: Configured to exclude virtual environments and cache files.
