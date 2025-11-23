from bs4 import BeautifulSoup
import requests
import shutil

wiki_url = "https://uk.wikipedia.org/wiki/%D0%93%D0%BE%D0%BB%D0%BE%D0%B2%D0%BD%D0%B0_%D1%81%D1%82%D0%BE%D1%80%D1%96%D0%BD%D0%BA%D0%B0"
path_to_file = '/Users/kostantin/Library/Application Support/zoom.us/data/VirtualBkgnd_Custom/' \
               '956B6684-68CA-44AF-861C-07E57B34C2D9'

headers = {
    "User-Agent": "MyWikiScript/1.0 (your_email@example.com)"
}
def get_html(url):
    r = requests.get(url, headers=headers)
    text = r.text
    return text

def find_photo_of_the_day_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    photo_of_the_day_source = soup.find('div', id='feat-pic')\
        .\
        find('div', class_='main-block-content').\
        find('img').get('src')
    return photo_of_the_day_source

def download_image(url):
    response = requests.get(url, headers=headers)
    with open("image.jpg", "wb") as f:
        f.write(response.content)
    with open("image2.jpg", "rb") as f:
        f.write(response.content)

def change_wallpaper():
    shutil.copy2('image.jpg', path_to_file)


def main():
    html = get_html(wiki_url)
    download_image('https://' + find_photo_of_the_day_link(html)[2:])
    change_wallpaper()

if __name__ == '__main__':
    main()


