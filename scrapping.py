from playwright.sync_api import sync_playwright
import requests

def check_response(url):
    try:
        return requests.get(url, timeout=5).status_code == 200
    except:
        return False

def scrape(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=5000)
            page.wait_for_load_state("networkidle")

            content = page.evaluate("""() => document.body.innerText""")
            browser.close()

            return content
    except Exception as e:
        print(f"Playwright error: {e}")
        return ""

def scraper_agent(urls):
    results = []
    for url in urls:
        if not check_response(url):
            continue

        content = scrape(url)
        if content and len(content) > 500:
            results.append({"url": url, "content": content[:5000]})

        if len(results) >=3:
            break

    return results
