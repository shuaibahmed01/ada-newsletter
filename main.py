import os
from site_scraper import setup_driver, scrape_website, extract_article_links, get_article_info, is_within_last_week, extract_body_content, clean_body_content
from nl_agent import summarize_chain
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class PrettyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)

def main():
    # Step 1: Scrape articles
    base_url = "https://adanews.ada.org/topic/"
    topics = {
        "Government": "government", 
        "Practice": "practice", 
        "Access To Care": "access-to-care",
        "Education": "education",
        "Science": "science",
        "Around the ADA": "around-the-ada"
    }
    
    driver = setup_driver()
    articles_data = []

    for topic, url_suffix in topics.items():
        target_url = base_url + url_suffix
        main_page_content = scrape_website(driver, target_url)
        article_links = extract_article_links(main_page_content, target_url)
        
        filtered_categorized_links = []
        for link in article_links:
            publish_date = get_article_info(driver, link)
            if publish_date and is_within_last_week(publish_date):
                filtered_categorized_links.append((link, publish_date))
        
        for link, publish_date in filtered_categorized_links:
            html = scrape_website(driver, link)
            body = extract_body_content(html)
            author, title, cleaned_content, image_url = clean_body_content(body)
            
            article_data = {
                "url": link,
                "publish_date": publish_date,
                "title": title,
                "content": cleaned_content,
                "topic": topic,
                "author": author,
                "image_url": image_url
            }
            articles_data.append(article_data)
        print(f"Finished article extraction for {topic}")

    driver.quit()

    # Save scraped articles
    with open("scraped_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2, cls=PrettyJSONEncoder)

    print(f"Scraped and saved {len(articles_data)} articles from the past week.")

    # Step 2: Generate summaries
    for article in articles_data:
        if isinstance(article['publish_date'], str):
            article['publish_date'] = datetime.strptime(article['publish_date'], '%Y-%m-%d')
        summary = summarize_chain.invoke({"article_content": article["content"]})
        article["summary"] = summary.strip()

    # Save articles with summaries
    with open("scraped_articles_with_summaries.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2, cls=PrettyJSONEncoder)
    

    print("Summaries generated and added to scraped_articles_with_summaries.json")

    generate_newsletter(articles_data)

def generate_newsletter(articles):
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('newsletter_template.html')

    # Format the date
    formatted_date = datetime.now().strftime("%B %d, %Y")

    # Render the template with the articles data
    newsletter_html = template.render(
        articles=articles,
        date=formatted_date
    )

    # Write the output to a file
    with open('newsletter.html', 'w') as f:
        f.write(newsletter_html)

    print("Newsletter generated successfully!")

if __name__ == "__main__":
    main()
