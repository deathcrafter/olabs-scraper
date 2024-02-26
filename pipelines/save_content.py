import os
import re
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
from markdownify import markdownify, MarkdownConverter


def save_content(driver: Chrome, url: str, filename: str):
    driver.implicitly_wait(10)
    driver.get(url)

    content = driver.find_element(By.XPATH, "//div[@class='divContent']")
    innerHTML = content.get_attribute("innerHTML")

    if not innerHTML:
        return

    soup = BeautifulSoup(innerHTML, "html.parser")
    h1_with_img = soup.find_all(
        "h1", recursive=False
    )  # Set recursive to False to only look for immediate children

    for h1 in h1_with_img:
        img_tag = h1.find("img")
        if img_tag:
            div = soup.new_tag("div")
            for content in h1.contents:
                div.append(content)
            h1.replaceWith(div)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(MarkdownConverter().convert(soup.prettify()))
