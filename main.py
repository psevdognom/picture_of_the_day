from bs4 import BeautifulSoup
import requests
import shutil
from datetime import datetime, timedelta
import os

path_to_file = '/Users/kostantin/Library/Application Support/zoom.us/data/VirtualBkgnd_Custom/' \
               '956B6684-68CA-44AF-861C-07E57B34C2D9'

headers = {
    "User-Agent": "MyWikiScript/1.0 (your_email@example.com)"
}

# Number of previous days to cycle through
DAYS_TO_CYCLE = 30


def get_html(url):
    r = requests.get(url, headers=headers)
    text = r.text
    return text


def get_potd_archive_url(date):
    """Generate URL for Picture of the Day archive page for a specific date."""
    date_str = date.strftime("%Y-%m-%d")
    return f"https://uk.wikipedia.org/wiki/Вікіпедія:Вибране_зображення/{date_str}"


def find_photo_from_archive(html):
    """Find the photo link from a POTD archive page."""
    soup = BeautifulSoup(html, 'html.parser')
    # Try to find the main image in the archive page
    # Archive pages typically have the image in various locations
    img = soup.find('img', class_='mw-file-element')
    if img and img.get('src'):
        return img.get('src')
    # Fallback: find any image in thumbinner
    thumbinner = soup.find('div', class_='thumbinner')
    if thumbinner:
        img = thumbinner.find('img')
        if img and img.get('src'):
            return img.get('src')
    # Another fallback: find image in floatnone
    floatnone = soup.find('div', class_='floatnone')
    if floatnone:
        img = floatnone.find('img')
        if img and img.get('src'):
            return img.get('src')
    return None


def get_current_picture_index():
    """Calculate which picture to show based on current time (rotating every 5 minutes)."""
    now = datetime.now()
    # Calculate minutes since midnight, then divide by 5 to get 5-minute intervals
    minutes_since_midnight = now.hour * 60 + now.minute
    return (minutes_since_midnight // 5) % DAYS_TO_CYCLE


def get_date_for_index(index):
    """Get the date for a specific index (days ago from today)."""
    today = datetime.now().date()
    return today - timedelta(days=index + 1)


def download_image(url):
    response = requests.get(url, headers=headers)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "image.jpg")
    with open(image_path, "wb") as f:
        f.write(response.content)


def change_wallpaper():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "image.jpg")
    shutil.copy2(image_path, path_to_file)


def main():
    # Get the index of which previous day's picture to show
    picture_index = get_current_picture_index()
    target_date = get_date_for_index(picture_index)
    
    # Get the archive page for the target date
    archive_url = get_potd_archive_url(target_date)
    html = get_html(archive_url)
    
    # Find the photo link
    photo_link = find_photo_from_archive(html)
    
    if photo_link:
        # Make sure the URL is properly formatted
        if photo_link.startswith('//'):
            photo_link = 'https:' + photo_link
        elif not photo_link.startswith('http'):
            photo_link = 'https://uk.wikipedia.org' + photo_link
        
        download_image(photo_link)
        change_wallpaper()
    else:
        print(f"Could not find picture for date: {target_date}")


if __name__ == '__main__':
    main()


