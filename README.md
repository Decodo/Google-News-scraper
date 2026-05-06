# Google News Scraper
![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![License](https://img.shields.io/github/license/decodo/Google-News-scraper)

<p align="center">
<a href="https://dashboard.decodo.com/scrapers/pricing?utm_source=github&utm_medium=social&utm_campaign=googlenewsscraper"><img src="https://github.com/user-attachments/assets/13b08523-32b0-4c85-8e99-580d7c2a9055"></a>
</p>

[![](https://dcbadge.vercel.app/api/server/Ja8dqKgvbZ)](https://discord.gg/Ja8dqKgvbZ)

## What is Google News?
[Google News](https://news.google.com/) is a powerful news aggregator that collects and organizes news articles from various news sources worldwide. You can browse articles directly on the Google News web page or access specific categories, like business, technology, or sports, based on your interests.

## What is a Google News scraper?
This is a Google News scraper that lets you extract headlines, summaries, sources, and publication dates from Google News search results using automated scripts.

Built for developers, data teams, and businesses, it’s ideal for scraping Google News at scale for media monitoring, market research, and trend analysis.

## Features

- **Rotating proxy support**. Utilizes proxy rotation to prevent IP blocking and maintain uninterrupted access to Google News.
- **Extract headlines, summaries, sources, and publication dates**. Gathers essential article details for comprehensive news data analysis. 
- **Parse HTML content using Beautiful Soup**. Employs BeautifulSoup to navigate and extract structured data from Google News pages.
- **Automate data collection with Python scripts**:. Uses Python for scripting automated news data extraction processes.

## Installation

Before you start scraping, let’s make sure you have the right tools for the job. In this case, your essentials are 
[Python](https://www.python.org/) and a few powerful libraries that will help you dig through the data with ease:

1. **Install Python**. Make sure that you have the latest Python version should be installed on your machine. You can get it from the [official downloads page](https://www.python.org/downloads/). 
2. **Install the required libraries**. Requests and Beautiful Soup are the usual staples when it comes to scraping and parsing websites:

```
pip install requests beautifulsoup4
```

3. **Install Playwright**. Run the following command to get the [Playwright](https://playwright.dev/) library in your Python environment. It allows you to use Playwright’s Python API to interact with browsers:

```
pip install playwright
```

4. **Install the necessary browsers**. Get the necessary browser binaries (Chromium, Firefox, and WebKit) that Playwright uses to automate browsers. Playwright needs these binaries to run browser automation tasks, but they're not included with the initial library installation:

```
python -m playwright install
```
5. **Get proxy authentication detail**s. You'll need a username, password, and endpoint information that can be found on the [Decodo dashboard](https://dashboard.decodo.com/residential-proxies/proxy-setup).
6. **Run the script file**. Run the `google-news-scraper.py` file with the following command:
```
python path/to/your/file/google-news-scraper.py
```
Here's the breakdown of what the code does:

1. Loads the Google News website.
2. Clicks the "Accept all" button to accept cookies.
3. Finds the URL of the article by its class name.
4. Finds the title of the article by its class name.
5. Adds a counter from 0 to count mentions of specified phrases and links scraped.
6. Iterates over the URLs and access each website.
7. Finds "proxy" or "proxies" phrases in the websites.
8. Prints the title, URL, and whether the phrases were found.
9. Prints the total number of mentions found and links scraped.
10. Stores the data in a CSV file named `scraped_articles.csv`
11. Closes the browser.

You should see the title, URL, and whether the phrases were printed in the terminal. As a final note, you can change the headless variable value to *True* to save resources and time, as graphically loading each website can be resource-intensive.

## Output example
![Google Maps scraper output example](https://images.decodo.com/Google_news_data_d71cfb1cb2/Google_news_data_d71cfb1cb2.png)

## Further reading
For a more in-depth tutorial on how to create your own Google News scraper with Python, read the [full blog post](https://decodo.com/blog/how-to-scrape-google-news). 

## Related repositories
[Google Maps scraper](https://github.com/Decodo/google-maps-scraper/tree/main)

[Python scraper tutorial](https://github.com/Decodo/Python-scraper-tutorial)
