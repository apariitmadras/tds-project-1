# scraper.py
import requests
from bs4 import BeautifulSoup
import json

def scrape_course_page():
    url = "https://tds.s-anand.net/#/2025-01/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator="\n")
    return text[:5000]  # keep content short for now

def scrape_discourse():
    url = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator="\n")
    return text[:5000]

def save_combined_context():
    course = scrape_course_page()
    discourse = scrape_discourse()
    with open("context.json", "w") as f:
        json.dump({"context": course + "\n\n" + discourse}, f)
