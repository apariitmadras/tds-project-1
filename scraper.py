import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

context = []

# Utility to scrape a single URL and extract readable text
async def scrape_page(playwright, url):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(2000)  # let content load
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n").strip()
        return text
    finally:
        await browser.close()

# Scrape the TDS course website (single page)
async def scrape_course_content(playwright):
    print("Scraping course content...")
    url = "https://tds.s-anand.net/#/2025-01/"
    text = await scrape_page(playwright, url)
    context.append({"text": text[:3000], "url": url})

# Scrape 5 recent Discourse threads
async def scrape_discourse_threads(playwright):
    print("Scraping Discourse posts...")
    base = "https://discourse.onlinedegree.iitm.ac.in"
    list_url = f"{base}/c/courses/tds-kb/34.json"
    
    import requests
    res = requests.get(list_url)
    topics = res.json()["topic_list"]["topics"][:5]  # get top 5 topics

    for topic in topics:
        slug = topic["slug"]
        id_ = topic["id"]
        url = f"{base}/t/{slug}/{id_}"
        text = await scrape_page(playwright, url)
        context.append({"text": text[:3000], "url": url})

# Main scraper runner
async def main():
    async with async_playwright() as playwright:
        await scrape_course_content(playwright)
        await scrape_discourse_threads(playwright)
        
        with open("context.json", "w") as f:
            json.dump(context, f, indent=2)
        print("✅ Saved context.json with", len(context), "chunks.")

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
