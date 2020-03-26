"""Module for actually getting data and downloading videos from Pornhub."""
import os
import http
import time
import traceback
import requests
import youtube_dl
from youtube_dl.utils import DownloadError
from bs4 import BeautifulSoup


def get_cookies():
    """Get the cookies from the cookie_file"""
    if not os.path.exists('http_cookie_file'):
        return None

    cookies_jar = {}
    with open('http_cookie_file') as f:
        cookie_data = f.read()

    cookies = cookie_data.split(';')
    for cookie in cookies:
        [key, value] = cookie.strip().split('=', 1)
        cookies_jar[key] = value

    return cookies_jar

def get_soup(url):
    """Get new soup instance from url."""
    tries = 0
    while True:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
            }
            cookies = get_cookies()
            response = requests.get(url, headers=headers, cookies=cookies)

            # Couldn't find the site. Stop and return None
            if response.status_code == 404:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
        except BaseException as e:
            print('Got exception during html fetch.')
            traceback.print_exc()
            time.sleep(60)
            tries += 1

            if tries > 3:
                raise e
            continue

        return soup


def download_video(viewkey, name='single_videos'):
    """Download the video."""
    # Decide which domain should be used, depending if the user has a premium account
    is_premium = os.path.exists('cookie_file')
    if is_premium:
        video_url = f"https://www.pornhubpremium.com/view_video.php?viewkey={viewkey}"
    else:
        video_url = f"https://www.pornhub.com/view_video.php?viewkey={viewkey}"

    options = {
        'outtmpl': f'~/pornhub/{name}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
    }
    if is_premium:
        options['cookiefile'] = 'cookie_file'

    ydl = youtube_dl.YoutubeDL(options)
    tries = 0
    while True:
        try:
            print(f'Start downloading: {video_url}')
            info = ydl.extract_info(video_url)
            info['out_path'] = f'~/pornhub/{name}/{info["title"]}.{info["ext"]}'
            return True, info
        except TypeError:
            # This is an error that seems to occurr from time to time
            # A short wait and retry often seems to fix the problem
            # This is something about pornhub not properly loading the video.
            print('Got TypeError bug')
            time.sleep(20)
            tries += 1

            # If this happens too many times, something else must be broken.
            if tries > 10:
                return False, None
            continue
        except DownloadError:
            # We got a download error.
            # Ignore for now and continue downloading the other videos
            print("DownloadError: Failed to download video.")
            return False, None

        time.sleep(6)
    return False, None