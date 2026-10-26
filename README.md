# Google News Scraper
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/github/license/decodo/Google-News-scraper)

<p align="center">
<a href="https://dashboard.decodo.com/?page=residential-proxies&utm_source=socialorganic&utm_medium=social&utm_campaign=resi_trial_GITHUB"><img src="https://github.com/user-attachments/assets/60bb48bd-8dcc-48b2-82c9-a218e1e4449c"></a>
</p>

[![](https://dcbadge.vercel.app/api/server/Ja8dqKgvbZ)](https://discord.gg/Ja8dqKgvbZ)

## What is Google News?
[Google News](https://news.google.com/) is a powerful news aggregator that collects and organizes news articles from various news sources worldwide. You can browse articles directly on the Google News web page or access specific categories, like business, technology, or sports, based on your interests.

## What is a Google News scraper?
This Python scraper collects article listings from a selected Google News category or subcategory. It extracts headlines, Google News URLs, publishers, publication dates, and authors when available. It can also capture related-story group information.

The script uses Requests and BeautifulSoup to process the HTML returned by a single request. It **does not** search Google News by keyword, scroll for more results, or visit individual publishers to retrieve full articles.

## Features

- **Category and subcategory selection**. Paste a Google News URL under `/topics/`, including `/topics/.../sections/...` subcategory URLs.
- **Residential proxy support**. Send requests through Decodo proxies using credentials stored in `.env`.
- **Article metadata extraction**. Collect titles, links, publishers, publication timestamps, authors, and related-story information when available.
- **Configurable output**. Choose a result limit, filter articles by publication age, and optionally keep only the lead article from each identified story group.
- **CSV export**. Save the results to `scraped_articles.csv` for further analysis.

## Installation

1. **Install Python**. Download Python 3.9 or later from the [official website](https://www.python.org/downloads/).
2. **Install dependencies**:

   ```bash
   pip install requests beautifulsoup4 python-dotenv
   ```

3. **Configure your Decodo residential proxy**. Create a `.env` file in the same directory as `google-news-topic-with-proxies.py` and provide your [proxy credentials](https://dashboard.decodo.com/residential-proxies/proxy-setup):

   ```dotenv
   PROXY_SERVER=http://gate.decodo.com:7000
   PROXY_USERNAME=your_username
   PROXY_PASSWORD=your_password
   ```

   Alternatively, set a single `PROXY_URL` with the credentials included. Never commit your `.env` file to GitHub.

4. **Choose a category or subcategory**. Open [Google News](https://news.google.com/), select a category or subcategory, and paste its full URL into `TOPIC_URL` in `google-news-topic-with-proxies.py`. Subcategory URLs include `/sections/`.

5. **Adjust the optional settings**:

   ```python
   MAX_ITEMS = 50                   # Set to None for all articles in the initial HTML.
   MAX_AGE_DAYS = None              # Set to 1, 7, or 30 to filter by publication age.
   INCLUDE_RELATED_ARTICLES = True  # False keeps only the first article per story group.
   ```

6. **Run the script**:

   ```bash
   python google-news-topic-with-proxies.py
   ```

## How it works

1. Fetches the selected Google News topic page through the configured proxy.
2. Parses the returned HTML using BeautifulSoup and finds article links and their metadata.
3. Applies publication-date and related-story filters, followed by the result limit.
4. Saves the selected records to `scraped_articles.csv` and prints a summary of the extracted fields and output path.

It uses only the initial HTML response, so increasing `MAX_ITEMS` won't trigger infinite scrolling or retrieve further pages. Some articles do not include author or related-story details.

## Output example

The output CSV includes these columns:

| Title | URL | Source | Published | Author | Story Group | Story URL |
| --- | --- | --- | --- | --- | --- | --- |
| Article headline | Google News `/read/` link | Publisher | ISO 8601 timestamp | If available | If available | Google News `/stories/` link, if available |

**Access restrictions**: As checked in October 2026, Google News' [robots.txt](https://news.google.com/robots.txt) allowed `/topics/` pages but disallowed its search and RSS search endpoints. Check the current robots.txt and [Google's Terms of Service](https://policies.google.com/terms) before scraping. Proxies do not override access restrictions.

## Further reading
For a more in-depth tutorial on how to create your own Google News scraper with Python, read the [full blog post](https://decodo.com/blog/how-to-scrape-google-news). 

## Related repositories
[Google Maps scraper](https://github.com/Decodo/google-maps-scraper/tree/main)

[Python scraper tutorial](https://github.com/Decodo/Python-scraper-tutorial)
