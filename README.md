# Vélib' Métropole Scraping

## Purpose
This script scrapes data from your own Vélib' Métropole account and gets basic information in a CSV file for analysis.

## Preparing
1. Clone this repo and `cd` into it
2. Get your credentials for the Vélib' Métropole portal, create a `cp template.env .env` then add your username and password to the corresponding fields inside it
3. Install required modules: `pip install -r requirements.txt`
4. Install the [Chrome driver](https://chromedriver.chromium.org/getting-started) for Selenium

## Running
`python scrape.py` will run the scraper and output results to the `runs.csv` file. Please use Python 3.
