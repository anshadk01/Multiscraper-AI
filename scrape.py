from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


def scrape_website(website):
    print("Launching Chrome browser...")

    # Chrome options
    options = Options()
    options.add_argument("--headless=new")   # better headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    # Auto-manage ChromeDriver (no need for chromedriver.exe)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        print("Navigating to website...")
        driver.get(website)

        # ⏳ wait for page to load properly
        time.sleep(3)

        print("Taking screenshot...")
        driver.save_screenshot("page.png")

        print("Scraping page content...")
        html = driver.page_source

        return html

    finally:
        driver.quit()


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=4000):
    return [
        dom_content[i:i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]