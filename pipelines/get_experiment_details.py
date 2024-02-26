import os
from bs4 import BeautifulSoup
from requests import request
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def get_simulator_link(url):
    with requests.get(url) as response:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.iframe:
            return "https:" + str(soup.iframe["src"])

    return ""


def get_experiment_details(driver: Chrome, url: str) -> dict[str, str]:
    driver.implicitly_wait(10)
    driver.get(url)

    all_tabs = driver.find_elements(
        By.XPATH, "//nav[@id='mcurve']/div[@id='myNavbar']/ul[@id='tab']/li/a"
    )

    req_tabs: dict[str, str] = {}

    for tab in all_tabs:
        p = tab.find_element(By.XPATH, "./p")
        innerText = p.get_attribute("innerText")
        if innerText and (tabTitle := innerText.strip().lower()) in [
            "theory",
            "procedure",
            "simulator",
            "viva voce",
        ]:
            req_tabs[tabTitle] = tab.get_attribute("href") or ""
            if tabTitle == "simulator":
                req_tabs[tabTitle] = get_simulator_link(req_tabs[tabTitle])

    return req_tabs
