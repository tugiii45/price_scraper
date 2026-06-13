import csv
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Constants
SCRAPE_URL = "https://www.jumia.co.ke/"
# Base API URL tracking KES
API_URL = "https://open.er-api.com/v6/latest/KES"
OUTPUT_FILE = "jumia_converted_prices.json"


def get_exchange_rate(target_currency):
    """
    Fetches live exchange rates from KES to the user-selected target currency.
    """
    try:
        print(f"\nFetching live exchange rates for KES to {target_currency}...")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("result") == "success":
            # Get the rate for the currency the user typed in
            rate = data["rates"].get(target_currency.upper())
            if rate:
                print(f"Live Rate Found: 1 KES = {rate:.5f} {target_currency.upper()}")
                return rate, target_currency.upper()
            else:
                print(f"Currency '{target_currency}' not recognized by the API.")
                print("Falling back to USD.")
                return data["rates"]["USD"], "USD"
        else:
            raise Exception("API returned unsuccessful status.")
            
    except Exception as e:
        # Emergency fallbacks if internet/API drops
        fallbacks = {"USD": 0.0076, "EUR": 0.0070, "GBP": 0.0060}
        fallback_rate = fallbacks.get(target_currency.upper(), 0.0076)
        print(f"API Error: {e}. Using a fallback rate (1 KES = {fallback_rate}).")
        return fallback_rate, target_currency.upper()


def scrape_jumia(url):
    """
    Scrapes product names and prices directly from Jumia Kenya.
    """
    products = []
    try:
        print(f"Scraping products from {url}...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        product_containers = soup.find_all("article", class_="prd")
        
        for product in product_containers[:12]:
            name_tag = product.find("div", class_="name")
            price_tag = product.find("div", class_="prc")
            
            if name_tag and price_tag:
                title = name_tag.text.strip()
                price_text = price_tag.text.strip()
                
                # Cleaning Jumia's price format (e.g., "KSh 1,200" -> 1200.0)
                clean_price = price_text.replace("KSh", "").replace(",", "").strip()
                
                if " - " in clean_price:
                    clean_price = clean_price.split(" - ")[0]
                
                try:
                    price_float = float(clean_price)
                    products.append({
                        "Product Name": title,
                        "Price (KES)": price_float
                    })
                except ValueError:
                    continue
                    
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

    # 2. INTERACTIVE USER INPUT FOR CURRENCY
    print("\n" + "="*50)
    print("WELCOME TO THE JUMIA CURRENCY CONVERTER")
    print("="*50)
    print("Popular options: USD, EUR, GBP, UGX, TZS, ZAR, NGN")
    
    user_choice = input("Enter the 3-letter currency code you want to convert to: ").strip()
    
    # If the user hits enter without typing, default to USD
    if not user_choice:
        user_choice = "USD"

    # 3. Get Custom Conversion Rate
    conversion_rate, target_curr = get_exchange_rate(user_choice)

    # 4. Calculate conversions dynamically using the selected currency
    for product in raw_products:
        product[f"Price ({target_curr})"] = round(product["Price (KES)"] * conversion_rate, 2)

    # 5. Format and Print the result table using Pandas
    df = pd.DataFrame(raw_products)
    print("\n" + "="*35 + f" JUMIA PRICING TABLE ({target_curr}) " + "="*35)
    print(df.to_string(index=False))
    print("=" * (86 + len(target_curr)) + "\n")

    # 6. Export automatically to JSON
    try:
        df.to_json(OUTPUT_FILE, orient="records", indent=4)
        print(f"Success! Data converted to {target_curr} and saved to '{OUTPUT_FILE}'.")
    except Exception as e:
        print(f"Failed to write to JSON: {e}")


if __name__ == "__main__":
    main()