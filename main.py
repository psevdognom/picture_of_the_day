import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup
import requests
import shutil
from datetime import datetime, timedelta
import os

wiki_url = "https://uk.wikipedia.org/wiki/%D0%93%D0%BE%D0%BB%D0%BE%D0%B2%D0%BD%D0%B0_%D1%81%D1%82%D0%BE%D1%80%D1%96%D0%BD%D0%BA%D0%B0"
path_to_file = '/Users/kostantin/Library/Application Support/zoom.us/data/VirtualBkgnd_Custom/' \
               '853FBC6B-84A9-4D1F-9BD6-21F823AF0E2F'

headers = {
    "User-Agent": "MyWikiScript/1.0 (your_email@example.com)",
    'Accept-Encoding': 'gzip',
}
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
    open('file2.txt', 'w').close()

def change_wallpaper():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "image.jpg")
    shutil.copy2(image_path, path_to_file)


class SlidingWindowLimiter:
    # Global bytes budget within last `window_s` seconds
    def __init__(self, max_bytes_per_window: int, window_s: float):
        self.max_bytes = max_bytes_per_window
        self.window_s = window_s
        self.events = deque()  # (t_monotonic, nbytes)
        self.used = 0
        self.lock = threading.Lock()

    def _prune(self, now: float):
        cutoff = now - self.window_s
        while self.events and self.events[0][0] <= cutoff:
            _, n = self.events.popleft()
            self.used -= n

    def acquire(self, nbytes: int):
        if nbytes <= 0:
            return
        while True:
            with self.lock:
                now = time.monotonic()
                self._prune(now)

                if self.used + nbytes <= self.max_bytes:
                    self.events.append((now, nbytes))
                    self.used += nbytes
                    return

                # wait until enough falls out of window
                need_free = (self.used + nbytes) - self.max_bytes
                freed = 0
                wait_until = None
                for ts, b in self.events:
                    freed += b
                    if freed >= need_free:
                        wait_until = ts + self.window_s
                        break
                if wait_until is None:
                    wait_until = now + 0.05
                sleep_for = max(0.0, wait_until - now)

            time.sleep(min(sleep_for, 0.5))


def download2(url, out_path, session, limiter):
    headers = {
        "User-Agent": 'UA',
        # інколи корисно додати:
        "Accept": "*/*",
    }

    with session.get(url, stream=True, timeout=(10, 60), headers=headers) as r:
        if r.status_code == 403:
            # подивитись реальну причину (часто там текст про User-Agent policy)
            print("UA sent:", r.request.headers.get("User-Agent"))
            print("403 body (first 500 chars):", r.text[:500])
        r.raise_for_status()

        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=256 * 1024):
                if not chunk:
                    continue
                limiter.acquire(len(chunk))
                f.write(chunk)


def main():
    html = get_html(wiki_url)
    download_image('https://' + find_photo_of_the_day_link(html)[2:])
    change_wallpaper()

if __name__ == '__main__':
    main()


