from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_website(url):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

    # Set up the Chrome driver
    service = Service("chromedriver-mac-arm64/chromedriver")  # Replace with your chromedriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load (adjust timeout as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Scroll to load any lazy-loaded content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract all text from the page
        text_content = soup.get_text(separator='\n', strip=True)

        return text_content

    finally:
        driver.quit()

if __name__ == "__main__":
    target_url = "https://adanews.ada.org/topic/government"  # Replace with the website you want to scrape
    scraped_text = scrape_website(target_url)
    print(scraped_text)

    # Optionally, save the scraped text to a file
    with open("scraped_content.txt", "w", encoding="utf-8") as f:
        f.write(scraped_text)
