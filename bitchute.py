import requests
from bs4 import BeautifulSoup


def get_bitchute_video_url(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    video_source = soup.find('source', {'type': 'video/mp4'})
    if video_source:
        video_url = video_source['src']
        return video_url
    return None
