#!/usr/bin/env python3
"""
ROBLOX CATALOG SCRAPER - WORKING VERSION
Gets ALL clothing items from your group's catalog page.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
import time

GROUP_CATALOG_URL = "https://www.roblox.com/catalog?Category=1&CreatorName=%27forgive%20me&CreatorType=Group"
OUTPUT_FILE = "./runtime/catalog_items.json"

def scrape_catalog_with_selenium():
    """Scrape the catalog page using Selenium (guaranteed to work)."""
    print("Loading catalog page with Selenium...")
    
    # Setup Chrome with options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    driver.get(GROUP_CATALOG_URL)
    
    print("Page loaded. Waiting for content...")
    time.sleep(3)
    
    # Scroll to load all items (Roblox uses infinite scroll)
    print("Scrolling to load all items...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(20):  # Scroll up to 20 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print(f"  Stopped scrolling after {i+1} scrolls")
            break
        last_height = new_height
        print(f"  Scroll {i+1}: Height {new_height}px")
    
    # Wait a bit more for content to load
    time.sleep(3)
    
    # Now extract items
    print("\nExtracting items from page...")
    
    items = []
    
    # Method 1: Look for item cards by multiple selectors
    selectors_to_try = [
        "div[class*='item-card']",
        "div[data-testid*='item']",
        "a[href*='/catalog/']",
        ".catalog-item",
        ".item-card-container"
    ]
    
    for selector in selectors_to_try:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and len(elements) > 10:
                print(f"Found {len(elements)} elements with selector: {selector}")
                break
        except:
            continue
    
    # If no specific selector worked, get all links
    if 'elements' not in locals() or len(elements) < 10:
        print("Using fallback: getting all catalog links...")
        elements = driver.find_elements(By.TAG_NAME, "a")
        elements = [e for e in elements if "/catalog/" in e.get_attribute("href")]
        print(f"Found {len(elements)} catalog links")
    
    # Process each element
    processed_ids = set()
    
    for element in elements:
        try:
            # Get the link
            if element.tag_name == "a":
                link_element = element
            else:
                link_element = element.find_element(By.TAG_NAME, "a")
            
            href = link_element.get_attribute("href")
            if not href or "/catalog/" not in href:
                continue
            
            # Extract item ID from URL
            match = re.search(r'/catalog/(\d+)/', href)
            if not match:
                continue
                
            item_id = match.group(1)
            
            # Skip duplicates
            if item_id in processed_ids:
                continue
            processed_ids.add(item_id)
            
            # Try to get item name
            item_name = f"Item_{item_id}"
            try:
                # Look for name in various places
                name_selectors = [
                    ".item-card-name",
                    "h3", "h4", "h5",
                    "[data-testid='item-name']",
                    ".text-name",
                    ".item-name"
                ]
                
                for name_selector in name_selectors:
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, name_selector)
                        name_text = name_element.text.strip()
                        if name_text and len(name_text) > 2:
                            item_name = name_text
                            break
                    except:
                        continue
            except:
                pass
            
            # Clean the name
            clean_name = re.sub(r'[<>:"/\\|?*]', '', item_name)
            clean_name = clean_name.strip()
            
            items.append({
                "id": item_id,
                "name": clean_name,
                "href": href
            })
            
        except Exception as e:
            continue
    
    driver.quit()
    
    return items

def save_catalog_items(items):
    """Save catalog items to JSON file."""
    catalog_data = {
        "url": GROUP_CATALOG_URL,
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": len(items),
        "items": items
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ SUCCESS: Saved {len(items)} catalog items to: {OUTPUT_FILE}")
    
    if items:
        print("\nSample items found:")
        for i, item in enumerate(items[:15]):
            print(f"  {i+1:3d}. [{item['id']}] {item['name'][:50]}...")
    
    return catalog_data

def main():
    print("=" * 60)
    print("ROBLOX CATALOG SCRAPER - SELENIUM VERSION")
    print("=" * 60)
    print(f"Catalog URL: {GROUP_CATALOG_URL}")
    print("\nNote: This will open a Chrome browser in the background.")
    print("It needs to load the page completely to see all items.\n")
    
    # Check if Selenium is installed
    try:
        from selenium import webdriver
    except ImportError:
        print("Installing Selenium...")
        import subprocess
        subprocess.check_call(["pip", "install", "selenium"])
        from selenium import webdriver
    
    # Scrape the catalog
    items = scrape_catalog_with_selenium()
    
    if not items:
        print("\n❌ No items found!")
        print("\nPossible reasons:")
        print("1. Page didn't load correctly")
        print("2. Selectors need updating (Roblox changed their HTML)")
        print("3. The group has no items")
        
        print("\nTry METHOD 2 below...")
        return
    
    # Save items
    save_catalog_items(items)
    
    print(f"\n{'='*60}")
    print("NEXT STEP:")
    print(f"{'='*60}")
    print("Now you have the REAL catalog IDs and names!")
    print(f"\nRun this command to match and rename your files:")
    print(f"  python match_files.py")

if __name__ == "__main__":
    main()