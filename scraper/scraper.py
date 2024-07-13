import csv
import os
from dataclasses import dataclass, fields
import re
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from config import TECHNOLOGIES, BASE_URL, PYTHON_URL, LOGIN_URL

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


@dataclass
class Vacancy:
    title: str
    company_name: str
    technologies: str


VACANCY_FIELDS = [field.name for field in fields(Vacancy)]


class JobScraper:
    def __init__(self, base_url, job_url, technologies, login_url, username, password):
        self.base_url = base_url
        self.job_url = job_url
        self.technologies = technologies
        self.login_url = login_url
        self.username = username
        self.password = password
        self.vacancies = []
        self.driver = None

    def __enter__(self):
        self._setup_driver()
        self._login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)

    def _login(self):
        self.driver.get(self.login_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        ).send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        time.sleep(3)

    def _get_job_list(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".list-jobs__item.job-list__item")
            )
        )
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        jobs = soup.select(".list-jobs__item.job-list__item")
        return jobs, soup

    def _get_detail_pages_urls(self, jobs):
        detail_page_urls = []
        for job in jobs:
            link = job.select_one("a.job-list-item__link")
            if link:
                detail_page_urls.append(self.base_url + link.get("href"))
        return detail_page_urls

    def _get_title(self, detail_page_soup):
        title_element = detail_page_soup.select_one("h1")
        title = (
            title_element.text.strip().split("\n")[0]
            if title_element
            else "No title found"
        )
        return title

    def _get_company_name(self, detail_page_soup):
        company_name_element = detail_page_soup.select_one(".job-details--title")
        company_name = (
            company_name_element.text.strip()
            if company_name_element
            else "No company name found"
        )
        return company_name

    def _get_technologies(self, detail_page_soup):
        job_description_element = detail_page_soup.select_one(
            ".mb-4.job-post-description"
        )
        job_description = (
            job_description_element.text if job_description_element else ""
        )
        job_description = re.sub(r"[^\w\s]", "", job_description)
        job_words = job_description.split()
        technologies = [word for word in job_words if word in self.technologies]
        technologies = ", ".join(set(technologies))
        return technologies

    def _get_job_details(self, detail_page_url):
        self.driver.get(detail_page_url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        title = self._get_title(soup)
        company_name = self._get_company_name(soup)
        technologies = self._get_technologies(soup)
        return Vacancy(
            title=title, company_name=company_name, technologies=technologies
        )

    def _get_next_page_url(self, soup):
        next_page_link = soup.select_one(
            "ul.pagination.pagination_with_numbers li.page-item.active + li.page-item:not(.disabled) a.page-link"
        )
        if next_page_link:
            next_page_url = next_page_link.get("href")
            if next_page_url:
                next_page_url = self.base_url + "/jobs/" + next_page_url
                return next_page_url
        return None

    def scrape_vacancies(self, url=None):
        if url is None:
            url = self.job_url

        jobs, soup = self._get_job_list(url)
        detail_page_urls = self._get_detail_pages_urls(jobs)

        for detail_page_url in detail_page_urls:
            vacancy = self._get_job_details(detail_page_url)
            self.vacancies.append(vacancy)

        next_page_url = self._get_next_page_url(soup)
        if next_page_url:
            self.scrape_vacancies(next_page_url)

    def save_to_csv(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        directory = "../scraped_data"
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(directory, f"{current_date}.csv")
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=VACANCY_FIELDS)
                writer.writeheader()
                for vacancy in self.vacancies:
                    writer.writerow(vacancy.__dict__)
        except IOError:
            print("I/O error")

    def close(self):
        if self.driver:
            self.driver.quit()


def main():
    with JobScraper(
        base_url=BASE_URL,
        job_url=PYTHON_URL,
        technologies=TECHNOLOGIES,
        login_url=LOGIN_URL,
        username=USERNAME,
        password=PASSWORD,
    ) as scraper:
        scraper.scrape_vacancies()
        scraper.save_to_csv()


if __name__ == "__main__":
    main()
