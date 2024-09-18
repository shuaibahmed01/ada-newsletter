from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
from collections import defaultdict

def generate_newsletter(articles):
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('newsletter_template.html')

    # Get the current date
    current_date = datetime.now()
    
    # Calculate the start of the week (Monday)
    start_of_week = current_date - timedelta(days=7)
    
    # Format the date range
    formatted_date_range = f"{start_of_week.strftime('%B %d')} - {current_date.strftime('%B %d, %Y')}"

    # Group articles by topic
    articles_by_topic = defaultdict(list)
    for article in articles:
        articles_by_topic[article['topic']].append(article)

    # Render the template with the grouped articles data
    newsletter_html = template.render(
        articles_by_topic=articles_by_topic,
        date_range=formatted_date_range
    )

    # Write the output to a file
    with open('newsletter.html', 'w') as f:
        f.write(newsletter_html)

    print("Newsletter generated successfully!")
    return newsletter_html
