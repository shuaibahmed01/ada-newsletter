from jinja2 import Environment, FileSystemLoader
from datetime import datetime

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
    return newsletter_html
