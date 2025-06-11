import csv
from dataclasses import dataclass
from time import sleep
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_quotes_from_page(url: str) -> List[Quote]:
    """Парсить цитати з однієї сторінки"""
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    quotes = []

    for quote_div in soup.find_all("div", class_="quote"):
        # Отримуємо текст цитати
        text_elem = quote_div.find("span", class_="text")
        text = text_elem.get_text().strip() if text_elem else ""

        # Отримуємо автора
        author_elem = quote_div.find("small", class_="author")
        author = author_elem.get_text().strip() if author_elem else ""

        # Отримуємо теги
        tag_elements = quote_div.find_all("a", class_="tag")
        tags = [tag.get_text().strip() for tag in tag_elements]

        quotes.append(Quote(text=text, author=author, tags=tags))

    return quotes


def get_next_page_url(soup: BeautifulSoup, base_url: str) -> str | None:
    """Отримує URL наступної сторінки, якщо вона існує"""
    next_btn = soup.find("li", class_="next")
    if next_btn:
        next_link = next_btn.find("a")
        if next_link and next_link.get("href"):
            return base_url + next_link.get("href")
    return None


def scrape_all_quotes() -> List[Quote]:
    """Парсить всі цитати з усіх сторінок"""
    base_url = "https://quotes.toscrape.com"
    current_url = base_url
    all_quotes = []

    while current_url:
        print(f"Парсинг сторінки: {current_url}")

        # Отримуємо цитати з поточної сторінки
        quotes = scrape_quotes_from_page(current_url)
        all_quotes.extend(quotes)

        # Перевіряємо чи є наступна сторінка
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        current_url = get_next_page_url(soup, base_url)

        # Робимо паузу щоб не перевантажувати сервер
        sleep(0.5)

    return all_quotes


def main(output_csv_path: str) -> None:
    """Основна функція що парсить усі цитати та зберігає їх у CSV файл"""
    quotes = scrape_all_quotes()

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Записуємо заголовки
        writer.writerow(["text", "author", "tags"])

        # Записуємо цитати
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
