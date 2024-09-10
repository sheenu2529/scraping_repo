from crewai import Agent
from langchain_groq import ChatGroq

# LLM setup (ChatGroq)
my_llm = ChatGroq(
    api_key="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",
    model="llama3-8b-8192",
)

def create_web_scraper_agent():
    return Agent(
        role="Web Scraper Specialist",
        goal="Efficiently scrape and organize web content, including text, images, audio, and videos from websites.",
        backstory="I am an AI agent designed for comprehensive web scraping. I can navigate websites, extract various types of content, and organize the data into easily accessible formats.",
        llm=my_llm,
        verbose=True,
    )