import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv
from urllib.parse import urljoin


def get_department_urls(base_url):
    response = requests.get(urljoin(base_url, "thecollege/programsofstudy/"))
    soup = BeautifulSoup(response.text, "html.parser")
    department_urls = [
        urljoin(base_url, a["href"]) for a in soup.select("ul.nav.leveltwo a")
    ]
    print(f"Total departments = {len(department_urls)}")
    return department_urls


def get_course_info(department_url):
    response = requests.get(department_url)
    soup = BeautifulSoup(response.text, "html.parser")
    courses = []

    for block in soup.find_all("div", class_="courseblock main"):
        course_info = {
            "department": "",
            "course_number": "",
            "course_title": "",
            "instructor": "",
            "terms_offered": "",
            "description": "",
        }

        title_block = block.find("p", class_="courseblocktitle")
        if title_block:
            full_title = title_block.get_text(strip=True)
            parts = full_title.split()
            course_info["department"] = parts[0]
            course_info["course_number"] = parts[1]
            course_info["course_title"] = " ".join(parts[2:])

        desc_block = block.find("p", class_="courseblockdesc")
        if desc_block:
            course_info["description"] = desc_block.get_text(strip=True)

        extra_info = block.find_all("p")[1:]
        for info in extra_info:
            text = info.get_text()
            if "Instructor(s):" in text:
                instructor_name = text.split("Instructor(s):")[1].split(",")[0].strip()
                course_info["instructor"] = " ".join(instructor_name.split()[:2])
            if "Terms Offered:" in text:
                course_info["terms_offered"] = text.split("Terms Offered:")[1].strip()

        courses.append(course_info)

    return courses


def save_data_to_csv(data, filename):
    fieldnames = [
        "department",
        "course_number",
        "course_title",
        "instructor",
        "terms_offered",
        "description",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main():
    base_url = "http://collegecatalog.uchicago.edu/"
    department_urls = get_department_urls(base_url)
    all_course_data = []
    for url in department_urls:
        print(f"Getting data for {url}")
        course_data = get_course_info(url)
        all_course_data.extend(course_data)
        time.sleep(3)
    save_data_to_csv(all_course_data, "courses.csv")


if __name__ == "__main__":
    main()
