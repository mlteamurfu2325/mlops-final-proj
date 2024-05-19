import argparse
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


# Constants
DEFAULT_BASE_URL = "https://www.ticketland.ru"
DEFAULT_SEARCH_URL = f"{DEFAULT_BASE_URL}/search/performance/?page="
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
}
DEFAULT_NUM_PAGES = 50
DEFAULT_NUM_REVIEW_PAGES = 100
DEFAULT_SLEEP_TIME = 1
DEFAULT_SAVE_DIR = f"{str(Path(__file__).parent.parent.parent)}/data/raw"


def fetch_page(url, headers=DEFAULT_HEADERS):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def parse_event_page(html):
    soup = BeautifulSoup(html, "html.parser")
    event_divs = soup.find_all("div", class_="card-search__img")
    return event_divs


def extract_event_data(div, base_url=DEFAULT_BASE_URL, headers=DEFAULT_HEADERS):
    a_tag = div.find("a", attrs={"data-seo-link": True})
    if not a_tag:
        return None

    event_url = base_url + a_tag["href"]
    detail_html = fetch_page(event_url, headers)
    if not detail_html:
        return None

    detail_soup = BeautifulSoup(detail_html, "html.parser")
    event_title = detail_soup.find("title").text if detail_soup.find("title") else ""
    match = re.search(r'data-url-ajax="/show/ReviewsTab\?id=(\d+)"', detail_html)
    event_id = match.group(1) if match else None

    if not event_id:
        return None

    reviews_url = f"{base_url}/show/GetReviews/?id={event_id}"
    return {"event_id": event_id, "event_title": event_title, "event_url": event_url, "reviews_url": reviews_url}


def scrape_events(num_pages=DEFAULT_NUM_PAGES, sleep_time=DEFAULT_SLEEP_TIME):
    events = []
    for page in range(1, num_pages + 1):
        url = f"{DEFAULT_SEARCH_URL}{page}"
        html = fetch_page(url)
        if not html:
            continue

        event_divs = parse_event_page(html)
        if not event_divs:
            print(f"No event divs found on page {page}")

        for div in event_divs:
            event_data = extract_event_data(div)
            if event_data:
                events.append(event_data)
        time.sleep(sleep_time)
        print(f"Page {page} done. Total events: {len(events)}")
    return events


def scrape_reviews(events, num_review_pages=DEFAULT_NUM_REVIEW_PAGES, sleep_time=DEFAULT_SLEEP_TIME):
    reviews = []
    for index, event in enumerate(events):
        for page in range(1, num_review_pages + 1):
            url = f"{event['reviews_url']}&page={page}"
            html = fetch_page(url)
            if not html or len(html) < 1024:
                break

            soup = BeautifulSoup(html, "html.parser")
            review_divs = soup.find_all("div", class_="review p-3 mb-3")
            for review in review_divs:
                review_rating = review.find("div", class_="review__rate").text.strip()
                review_text = review.find("p", class_="mb-2").text.strip() if review.find("p", class_="mb-2") else ""
                reviews.append({
                    "event_id": event["event_id"],
                    "review_rating": review_rating,
                    "review_text": review_text,
                })

            time.sleep(sleep_time)
        print(f"Event {event['event_id']} done. Total reviews: {len(reviews)}")
    return reviews


def save_to_csv(data, filename, columns, save_dir=DEFAULT_SAVE_DIR):
    df = pd.DataFrame(data)
    if df.empty:
        print("No data collected. DataFrame is empty.")
    else:
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        df.to_csv(file_path, index=False, header=True, sep=";", columns=columns)
        print(f"Data saved to {file_path}")


def main(num_pages, num_review_pages, sleep_time, save_dir, save_events, save_reviews):
    events = scrape_events(num_pages, sleep_time)
    if save_events:
        save_to_csv(events, "events.csv", ["event_id", "event_title", "event_url", "reviews_url"], save_dir)

    reviews = scrape_reviews(events, num_review_pages, sleep_time)
    if save_reviews:
        save_to_csv(reviews, "reviews.csv", ["event_id", "review_rating", "review_text"], save_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape event and review data from Ticketland.")
    parser.add_argument("--num_pages", type=int, default=DEFAULT_NUM_PAGES, help="Number of pages to scrape for events")
    parser.add_argument(
        "--num_review_pages", type=int, default=DEFAULT_NUM_REVIEW_PAGES, help="Number of pages to scrape for reviews"
    )
    parser.add_argument(
        "--sleep_time", type=int, default=DEFAULT_SLEEP_TIME, help="Time to sleep between requests (in seconds)"
    )
    parser.add_argument("--save_dir", type=str, default=DEFAULT_SAVE_DIR, help="Directory to save the CSV files")
    parser.add_argument("--save_events", action="store_true", help="Save events.csv")
    parser.add_argument("--save_reviews", action="store_true", help="Save reviews.csv")

    args = parser.parse_args()
    main(args.num_pages, args.num_review_pages, args.sleep_time, args.save_dir, args.save_events, args.save_reviews)
