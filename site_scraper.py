from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
from datetime import datetime, timedelta

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    service = Service("chromedriver-mac-arm64/chromedriver")  # Update path as needed
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_website(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return driver.page_source

def is_article_link(url):
    # Adjust these patterns based on the website's URL structure for articles
    article_indicators = ['/ada-news']
    return any(indicator in url for indicator in article_indicators)

def extract_article_links(html_content, base_url, num_links=10):
    soup = BeautifulSoup(html_content, 'html.parser')
    article_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if is_article_link(full_url) and full_url not in article_links:
            article_links.add(full_url)
            if len(article_links) == num_links:
                break
    return article_links

def parse_date(date_string):
    return datetime.strptime(date_string, '%B %d, %Y')

def is_within_last_week(publish_date):
    current_date = datetime.now()
    one_week_ago = current_date - timedelta(days=7)
    return publish_date >= one_week_ago

def get_article_info(driver, link):
    driver.get(link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract publish date
    date_span = soup.find('span', class_='publish-date')
    if date_span:
        publish_date = parse_date(date_span.text)
    else:
        publish_date = None
    
    # Extract category (you can keep your existing categorization logic here)
    category = categorize_article(soup, link)
    
    return publish_date, category

def categorize_article(soup, link):
    if soup.find('meta', property='article:section'):
        return soup.find('meta', property='article:section')['content']
    elif soup.find('span', class_='category'):
        return soup.find('span', class_='category').text.strip()
    elif re.search(r'(news|article|story)', link, re.I):
        return 'General Article'
    else:
        return 'Uncategorized'

if __name__ == "__main__":
    target_url = "https://adanews.ada.org/topic/government"
    driver = setup_driver()
    
    # Scrape the main page
    main_page_content = scrape_website(driver, target_url)
    article_links = extract_article_links(main_page_content, target_url)
    
    # Filter and categorize articles
    filtered_categorized_links = []
    for link in article_links:
        publish_date, category = get_article_info(driver, link)
        if publish_date and is_within_last_week(publish_date):
            filtered_categorized_links.append((link, category, publish_date))
    
    # Save filtered and categorized links to file
    with open("filtered_categorized_links.txt", "w", encoding="utf-8") as f:
        for link, category, publish_date in filtered_categorized_links:
            f.write(f"{category} - {publish_date.strftime('%Y-%m-%d')}: {link}\n")
    
    print(f"Scraped, filtered, and categorized {len(filtered_categorized_links)} article links from the past week.")
    driver.quit()