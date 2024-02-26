import json
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def save_viva(driver: Chrome, url: str, filename: str):
    driver.implicitly_wait(10)
    driver.get(url)

    content = driver.find_element(By.XPATH, "//div[@id='displayQuiz']/form")
    innerHTML = content.get_attribute("innerHTML")

    if not innerHTML:
        return

    soup = BeautifulSoup(innerHTML, "html.parser")

    tables = soup.find_all("table")

    questions: list[dict[str, str | list[str]]] = []

    for table in tables:
        question = table.find("span", id="question").text
        options_elements = table.find_all("label")
        options = [option.text.strip() for option in options_elements]
        questions.append({"question": question, "options": options})

    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(questions, indent=4))
