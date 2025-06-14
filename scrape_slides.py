import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://tds.s-anand.net/2025-01/"
SLIDES = [
    "intro", "excel", "sql", "python", "python-quiz", "regex",
    "html", "xpath", "unix", "git", "jupyter", "colab"
]

slides_data = {}

for slide in SLIDES:
    url = BASE_URL + slide
    print(f"Scraping: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract slide content
    text_elements = soup.find_all(["h1", "h2", "h3", "p", "li"])
    text = "\n".join([el.get_text() for el in text_elements])
    slides_data[slide] = text

# Save to file
with open("tds_course_slides.json", "w", encoding="utf-8") as f:
    json.dump(slides_data, f, indent=2, ensure_ascii=False)

print("✅ Slides saved to tds_course_slides.json")
