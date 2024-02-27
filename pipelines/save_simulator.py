import os
from pathlib import Path
import re
import time
from bs4 import BeautifulSoup
import requests

from selenium.webdriver import Chrome
import urllib.parse


def download_file(url, directory):
    local_filename = os.path.join(directory, url.split("/")[-1])
    with requests.get(url, stream=True) as response:
        with open(local_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return local_filename


def extract_assets_from_css(css_url: str, original_url: str, directory: Path):
    css_file_name = css_url.split("/")[-1]
    response = requests.get(css_url)
    css_content = response.text

    # Find all URLs in the CSS content
    urls = re.findall(r"url\((.*?)\)", css_content)

    for url in urls:
        # Remove quotes and whitespace from the URL
        url = url.strip(" '\"")
        if not (url.startswith("data:") or url.startswith("http")):
            remote_url = urllib.parse.urljoin(css_url, url)
            local_url = download_file(
                remote_url, os.path.join(directory, "css", "assets")
            )
            # Replace the original URL with the local path
            css_content = css_content.replace(
                url,
                "./" + os.path.relpath(local_url, directory / "css").replace("\\", "/"),
            )

    # Save the updated CSS content to a new file
    with open(
        os.path.join(directory, "css", css_file_name), "w", encoding="utf-8"
    ) as f:
        f.write(css_content)

    return os.path.join(directory, "css", css_file_name)


def extract_assets(soup: BeautifulSoup, original_url: str, directory: Path):
    # Extracting image assets
    img_tags = soup.find_all("img")
    for img in img_tags:
        img_url = img.get("src")
        if img_url and not str(img_url).startswith("http"):
            img_url = urllib.parse.urljoin(original_url, img_url)
            local_file = download_file(img_url, directory / "assets")
            img["src"] = os.path.relpath(local_file, directory).replace("\\", "/")

    # Extract JS files
    js_tags = soup.find_all("script", {"src": True})
    for js in js_tags:
        js_url = js.get("src")
        if js_url and not str(js_url).startswith("http"):
            js_url = urllib.parse.urljoin(original_url, js_url)
            local_file = download_file(js_url, directory / "js")
            js["src"] = os.path.relpath(local_file, directory).replace("\\", "/")

    # Extract CSS files along with embedded assets
    css_tags = soup.find_all("link", {"rel": "stylesheet", "href": True})
    for css in css_tags:
        css_url = css.get("href")
        if css_url and not str(css_url).startswith("http"):
            css_url = urllib.parse.urljoin(original_url, css_url)
            local_file = extract_assets_from_css(css_url, original_url, directory)
            css["href"] = os.path.relpath(local_file, directory).replace("\\", "/")

    # Extracting audio files
    other_tags = soup.find_all(["audio", "source"])
    for other in other_tags:
        audio_url = other.get("src")
        if audio_url:
            audio_url = urllib.parse.urljoin(original_url, audio_url)
            local_file = download_file(audio_url, directory / "assets")
            other["src"] = os.path.relpath(local_file, directory).replace("\\", "/")

    if soup.footer:
        soup.footer.decompose()

    return soup


def create_directories(directory):
    folders = ["css", "css/assets", "js", "assets"]
    for folder in folders:
        os.makedirs(os.path.join(directory, folder), exist_ok=True)


def save_simulator(driver: Chrome, url: str, directory: Path):
    driver.implicitly_wait(10)
    driver.get(url)

    html = driver.execute_script(
        "return document.getElementsByTagName('html')[0].outerHTML;"
    )
    html = BeautifulSoup(html, "html.parser")

    if not os.path.exists(directory):
        os.makedirs(directory)
    create_directories(directory)
    html = extract_assets(html, url, directory)

    html = html.prettify()
    html = html.replace(
        'var simPath="../', 'var simPath="https://amrita.olabs.edu.in/olab/'
    )

    with open(os.path.join(directory, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
