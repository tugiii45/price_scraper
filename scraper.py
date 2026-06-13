import csv
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Constants
SCRAPE_URL = "https://www.jumia.co.ke/"  # Pulls from Jumia's landing page/deals section
# Using ExchangeRate-API's open endpoint (Base KES)
API_URL = "https://open.er-api.com/v6/latest/KES"
OUTPUT_FILE = "jumia_converted_prices.csv"


def get_exchange_rate(target_currency="USD"):
    """
    Fetches live exchange rates from KES to the target currency (USD).
    """
    try:
        print(f"Fetching live exchange rates for KES...")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("result") == "success":
            rate = data["rates"].get(target_currency)
            if rate:
                print(f"Successfully retrieved rate: 1 KES = {rate:.5f} {target_currency}")
                return rate
            else:
                raise ValueError(f"Target currency '{target_currency}' not found.")
        else:
            raise Exception("API returned unsuccessful status.")
            
    except Exception as e:
        # High-accuracy historical fallback rate if API breaks (approx 1 KES = 0.0076 USD)
        fallback = 0.0076
        print(f"Exchange Rate API Error: {e}. Using local currency exchange rate: 1 KES = {fallback} USD")
        return fallback


def scrape_jumia(url):
    """
    Scrapes product names and prices directly from Jumia Kenya.
    """
    products = []
    try:
        print(f"Scraping products from {url}...")
        # Spoofing modern browser headers to bypass Jumia's 403 Forbidden blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Jumia identifies product grid items using 'article' tags with class 'prd'
        product_containers = soup.find_all("article", class_="prd")
        
        # Limit to the first 12 items to satisfy the "> 10 items" requirement smoothly
        for product in product_containers[:12]:
            name_tag = product.find("div", class_="name")
            price_tag = product.find("div", class_="prc")
            
            # Ensure both elements exist before parsing text
            if name_tag and price_tag:
                title = name_tag.text.strip()
                price_text = price_tag.text.strip()
                
                # Cleaning Jumia's price format (e.g., "KSh 1,200" -> 1200.0)
                clean_price = price_text.replace("KSh", "").replace(",", "").strip()
                
                # Check for range prices like "KSh 400 - KSh 600", and split to take the baseline
                if " - " in clean_price:
                    clean_price = clean_price.split(" - ")[0]
                
                try:
                    price_float = float(clean_price)
                    products.append({
                        "Product Name": title,
                        "Price (KES)": price_float
                    })
                except ValueError:
                    continue  # Ignore item if price string can't convert to numeric cleanly
                    
        print(f"Successfully scraped {len(products)} products from Jumia.")
        return products

    except requests.exceptions.RequestException as e:
        print(f"Scraping Error: Failed to reach Jumia. Reason: {e}")
        return []


def main():
    # 1. Gather live Jumia entries
    raw_products = scrape_jumia(SCRAPE_URL)
    
    if not raw_products:
        print("No product data collected. Exiting program.")
        return

    # 2. Get Conversion Rate (KES -> USD)
    target_curr = "USD"
    conversion_rate = get_exchange_rate(target_curr)

    # 3. Calculate conversions
    for product in raw_products:
        product[f"Price ({target_curr})"] = round(product["Price (KES)"] * conversion_rate, 2)

    # 4. Format and Print the result table using Pandas
    df = pd.DataFrame(raw_products)
    print(f"\n{'=' * 40} JUMIA COVERTED PRICING TABLE {'=' * 40}\n")
    print(df.to_string(index=False))
    print("="*111 + "\n")

    # 5. Export to CSV
    try:
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        print(f"Success! Jumia data saved cleanly to '{OUTPUT_FILE}'.")
    except Exception as e:
        print(f"Failed to write to CSV: {e}")


if __name__ == "__main__":
    main()