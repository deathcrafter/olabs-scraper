import json
import os
from pathlib import Path

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from slugify import slugify

from pipelines.save_content import save_content
from pipelines.save_simulator import save_simulator
from pipelines.save_viva import save_viva

C9_PATH = Path(__file__).parent / "class 9"
C10_PATH = Path(__file__).parent / "class 10"


def create_directories(statndard, title):
    title = slugify(title)
    folders = ["theory", "procedure", "simulator", "viva-voce"]
    for folder in folders:
        os.makedirs(os.path.join(statndard, title, folder), exist_ok=True)


def main():
    c9_experiments = []
    c10_experiments = []

    with open(os.path.join(C9_PATH, "experiments.json")) as f:
        c9_experiments = json.load(f)

    with open(os.path.join(C10_PATH, "experiments.json")) as f:
        c10_experiments = json.load(f)

    options = ChromeOptions()
    options.add_argument("--headless")
    driver = Chrome(options)
    driver.implicitly_wait(10)

    for experiment in c9_experiments:
        print("Scraping experiment: ", experiment["title"], "of class 9")
        create_directories(C9_PATH, experiment["title"])
        print("Getting theory.")
        save_content(
            driver,
            experiment["theory"],
            os.path.join(C9_PATH, slugify(experiment["title"]), "theory", "index.md"),
        )
        print("Getting procedure.")
        save_content(
            driver,
            experiment["procedure"],
            os.path.join(
                C9_PATH, slugify(experiment["title"]), "procedure", "index.md"
            ),
        )
        print("Getting simulator.")
        save_simulator(
            experiment["simulator"],
            Path(os.path.join(C9_PATH, slugify(experiment["title"]), "simulator")),
        )
        print("Getting viva voce.")
        save_viva(
            driver,
            experiment["viva voce"],
            os.path.join(
                C9_PATH, slugify(experiment["title"]), "viva-voce", "index.json"
            ),
        )

    for experiment in c10_experiments:
        print("Scraping experiment: ", experiment["title"], "of class 10")
        create_directories(C10_PATH, experiment["title"])
        save_content(
            driver,
            experiment["theory"],
            os.path.join(C10_PATH, slugify(experiment["title"]), "theory", "index.md"),
        )
        save_content(
            driver,
            experiment["procedure"],
            os.path.join(
                C10_PATH, slugify(experiment["title"]), "procedure", "index.md"
            ),
        )
        save_simulator(
            experiment["simulator"],
            Path(os.path.join(C10_PATH, slugify(experiment["title"]), "simulator")),
        )
        save_viva(
            driver,
            experiment["viva voce"],
            os.path.join(
                C10_PATH, slugify(experiment["title"]), "viva-voce", "index.json"
            ),
        )


if __name__ == "__main__":
    main()
