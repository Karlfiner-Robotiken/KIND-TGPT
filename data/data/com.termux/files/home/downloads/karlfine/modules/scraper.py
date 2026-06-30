
import requests
from bs4 import BeautifulSoup

def scrape(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    text = soup.get_text()[:2000]
    print("\n--- Scraped Content ---\n")
    print(text)
