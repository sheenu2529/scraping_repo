from crewai import Task
from tools.web_scraper_tool import web_scraper

def create_web_scraper_task(website_url, content_type, output_directory, agent):
    return Task(
        description=f"Scrape the website '{website_url}' for all URLs and save the following content types: {content_type}.",
        expected_output=f"All scraped content from {website_url} saved in {output_directory}.",
        agent=agent,
        tools=[web_scraper],
    )