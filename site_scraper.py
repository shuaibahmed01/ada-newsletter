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
import json

class PrettyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)

    def encode(self, obj):
        return super().encode(obj)

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    service = Service("chromedriver-mac-arm64/chromedriver")  # Update path as needed
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_website(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return driver.page_source

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    articles = soup.find_all('article')
    
    if articles:
        cleaned_content = []
        title = ""
        for article in articles:
            # Extract title
            h1_tag = article.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            
            strong_tag = article.find('strong')
            if strong_tag:
                author = strong_tag.get_text(strip = True)
            
            # Remove script and style elements
            for script_or_style in article(["script", "style"]):
                script_or_style.extract()
            
            # Get text from the article
            article_text = article.get_text(separator=' ')
            cleaned_article = ' '.join(article_text.split())
            cleaned_content.append(cleaned_article)
        
        return author,title, ' '.join(cleaned_content)
    else:
        # If no article tags are found, fall back to the original method
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        h1_tag = soup.find('h1')
        title = h1_tag.get_text(strip=True) if h1_tag else ""

        cleaned_content = soup.get_text(separator=' ')
        cleaned_content = ' '.join(cleaned_content.split())

        return title, cleaned_content

def is_article_link(url):
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
    one_week_ago = current_date - timedelta(days=8)
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
    
    
    return publish_date


if __name__ == "__main__":
    base_url = "https://adanews.ada.org/topic/"
    topics = {"Government": "government", 
              "Practice": "practice", 
              "Access To Care": "access-to-care",
              "Education": "education",
              "Science": "science",
              "Around the ADA": "around-the-ada"}
    driver = setup_driver()
    articles_data = []
    for topic, url_suffix in topics.items():
        target_url = base_url + url_suffix
        # Scrape the main page
        main_page_content = scrape_website(driver, target_url)
        article_links = extract_article_links(main_page_content, target_url)
        
        # Filter and categorize articles
        filtered_categorized_links = []
        for link in article_links:
            publish_date = get_article_info(driver, link)
            if publish_date and is_within_last_week(publish_date):
                filtered_categorized_links.append((link, publish_date))

        
        for link, publish_date in filtered_categorized_links:
            html = scrape_website(driver, link)
            body = extract_body_content(html)
            author, title, cleaned_content = clean_body_content(body)
            
            article_data = {
                "url": link,
                "publish_date": publish_date,
                "title": title,
                "content": cleaned_content,
                "topic": topic,
                "author": author
            }
            articles_data.append(article_data)
        print(f"Finished article extraction for {topic}")

    # Save articles data as JSON
    with open("scraped_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2, cls=PrettyJSONEncoder)

    print(f"Scraped and saved {len(articles_data)} articles from the past week.")
    driver.quit()