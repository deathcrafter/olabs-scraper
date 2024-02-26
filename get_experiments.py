import os
import json

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from pipelines.get_experiment_details import get_experiment_details

options = ChromeOptions()
options.add_argument("--headless")
driver = Chrome(options)
driver.implicitly_wait(10)

driver.get("https:https://amrita.olabs.edu.in/?sub=1")

all_galleries = driver.find_elements(
    By.XPATH,
    "//div[@class='experiment-gallery-new']/span[@class='class-title']/a",
)

req_galleries: dict[str, WebElement] = {}

for gallery in all_galleries:
    innerText = gallery.get_attribute("innerText")
    if not innerText:
        continue
    if innerText.strip().lower() in ["class 9", "class 10"]:
        req_galleries[innerText.strip().lower()] = gallery.find_element(
            By.XPATH, "./../.."
        )

experiments: dict[str, list[tuple[str, str]]] = {}

for className in req_galleries:
    gallery = req_galleries[className]
    items = gallery.find_elements(
        By.XPATH,
        "./div[@class='experiment-gallery-new']/div[@class='row']/div/p/a",
    )

    experiments[className] = []

    for item in items:
        href = item.get_attribute("href")
        title = item.get_attribute("innerText")
        if href and title:
            experiments[className].append((title.strip(), href.strip()))

experiment_tabs: dict[str, list[dict[str, str]]] = {}

for className in experiments:
    experiment_tabs[className] = []
    for experiment in experiments[className]:
        experiment_tabs[className].append(
            {
                "title": experiment[0],
                **get_experiment_details(driver, experiment[1]),
            }
        )

for className in experiment_tabs:
    os.makedirs(className, exist_ok=True)
    with open(f"{className}/experiments.json", "w") as f:
        json.dump(experiment_tabs[className], f, indent=4)

driver.close()
