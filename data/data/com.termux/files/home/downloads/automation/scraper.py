import requests

def get_trends():
    url = "https://trends.google.com/trends/trendingsearches/daily/rss"
    return requests.get(url).text
