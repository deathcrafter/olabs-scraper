from pathlib import Path
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import re


def download_file(url, directory):
    local_filename = os.path.join(directory, url.split("/")[-1])
    with requests.get(url, stream=True) as response:
        with open(local_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return local_filename


def create_directories(directory):
    folders = ["css", "css/assets", "js", "assets"]
    for folder in folders:
        os.makedirs(os.path.join(directory, folder), exist_ok=True)


def extract_assets_from_css(css_url, original_url, directory):
    css_file_name = css_url.split("/")[-1]
    response = requests.get(css_url)
    css_content = response.text

    # Find all URLs in the CSS content
    urls = re.findall(r"url\((.*?)\)", css_content)

    for url in urls:
        # Remove quotes and whitespace from the URL
        url = url.strip(" '\"")
        if not (url.startswith("data:") or url.startswith("http")):
            remote_url = urllib.parse.urljoin(original_url, url)
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


def extract_assets(url, directory: Path):
    response = requests.get(url)
    original_url = response.url
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    # Extracting image assets
    img_tags = soup.find_all("img")
    for img in img_tags:
        img_url = img.get("src")
        if img_url:
            img_url = urllib.parse.urljoin(url, img_url)
            local_file = download_file(img_url, directory / "assets")
            img["src"] = os.path.relpath(local_file, directory).replace("\\", "/")

    # Extract assets from CSS files
    css_tags = soup.find_all("link", {"rel": "stylesheet", "href": True})
    for css in css_tags:
        css_url = css.get("href")
        if css_url:
            css_url = urllib.parse.urljoin(original_url, css_url)
            local_file = extract_assets_from_css(css_url, original_url, directory)
            css_href = os.path.relpath(local_file, directory)
            css["href"] = css_href.replace("\\", "/")

    # Extracting JS assets
    js_tags = soup.find_all("script", {"src": True})
    for js in js_tags:
        js_url = js.get("src")
        if js_url:
            js_url = urllib.parse.urljoin(url, js_url)
            local_file = download_file(js_url, directory / "js")
            js["src"] = os.path.relpath(
                local_file,
                directory,
            ).replace("\\", "/")

    # Extracting audio files and other assets (modify as needed)
    other_tags = soup.find_all(["audio", "source"])
    for other in other_tags:
        other_url = other.get("src")
        if other_url:
            other_url = urllib.parse.urljoin(url, other_url)
            local_file = download_file(other_url, directory / "assets")
            other["src"] = os.path.relpath(local_file, directory).replace("\\", "/")

    if soup.footer:
        soup.footer.decompose()

    text_html = soup.prettify()
    text_html = text_html.replace(
        'var simPath="../', 'var simPath="https:https://amrita.olabs.edu.in/olab/'
    )

    # Save updated HTML content to a new file
    with open(os.path.join(directory, "index.html"), "w", encoding="utf-8") as f:
        f.write(text_html)


def save_simulator(url: str, directory: Path):
    if not os.path.exists(directory):
        os.makedirs(directory)
    create_directories(directory)
    extract_assets(url, directory)
