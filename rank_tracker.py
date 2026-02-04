import asyncio
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
# Add your Extension Name (exactly as it appears in the store) 
# and the Keywords you want to track.
MY_EXTENSIONS = {
    "WordBridge": ["Learn English", "ESL Flashcards", "Vocabulary"],
    "Local Schema Helper": ["Local SEO", "Schema Generator", "JSON-LD"],
    "Citation Manager": ["Local SEO", "Google Maps Audit", "Citations"]
}
CSV_FILENAME = 'extension_rankings.csv'

async def check_rankings():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        all_results = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        print(f"🚀 Starting rank check at {timestamp}...")

        for ext_name, keywords in MY_EXTENSIONS.items():
            for kw in keywords:
                print(f"Checking '{ext_name}' for keyword: '{kw}'...")
                search_url = f"https://chromewebstore.google.com/search/{kw.replace(' ', '%20')}"
                
                try:
                    await page.goto(search_url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_selector('h2', timeout=5000)
                    
                    # Scrape all titles in the results
                    titles = await page.eval_on_selector_all('h2', 'elements => elements.map(e => e.innerText)')
                    
                    try:
                        # Find index of your extension in the list
                        rank = [i for i, t in enumerate(titles) if ext_name.lower() in t.lower()][0] + 1
                    except IndexError:
                        rank = ">20" # Not found in the top tier
                except Exception as e:
                    print(f"Error checking {kw}: {e}")
                    rank = "Error"
                
                all_results.append([timestamp, ext_name, kw, rank])
        
        await browser.close()
        return all_results

def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Extension', 'Keyword', 'Rank'])
        writer.writerows(data)
    print(f"✅ Results saved to {CSV_FILENAME}")

if __name__ == "__main__":
    # Ensure Playwright browsers are installed: python -m playwright install chromium
    results = asyncio.run(check_rankings())
    save_to_csv(results)