
# Jumia Price Scraper & Currency Converter

A Python-based web scraper that extracts product information from Jumia Kenya, converts the local currency (KES) into United States Dollars (USD) using a live exchange rate API, and exports the structured data into a clean JSON file.

## Features

- **Web Scraping:** Safely bypasses basic bot detection on Jumia Kenya using custom browser headers to extract product titles and prices.
- **Live Currency Conversion:** Connects to the ExchangeRate-API to fetch real-time KES to USD exchange rates, with a reliable built-in fallback rate.
- **Data Structuring:** Cleans raw string price data (e.g., handling "KSh" prefixes and range prices) and processes it using `pandas`.
- **Beautiful Output:** Displays the data in a highly readable tabular format directly in the terminal and automatically exports a formatted `jumia_converted_prices.json` file.


## File Structure

- scraper.py              [**Main Python scraping script** ]
- requirements.txt            [**Project library dependencies**]
- README.md                   [**Project documentation**]
- jumia_converted_prices.json  [**Generated output file (created after running)**]

## Prerequisites & Installation

1. Clone or navigate to the project directory
2. Install the required third-party libraries

## Technologies Used

1. Python 3

2. Requests: For making HTTP connections to Jumia and the exchange rate API.

3. BeautifulSoup4: For parsing the HTML structure of the e-commerce site.

4. Pandas: For data alignment, terminal table formatting, and structured output.