import requests
import pandas as pd
from pandas import json_normalize
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# ADZUNA API CREDENTIALS
# -----------------------------
APP_ID = "YOUR_APP_ID"
API_KEY = "YOUR_API_KEY"

# -----------------------------
# SEARCH SETTINGS
# -----------------------------
COUNTRY = "nl"              # nl = Netherlands, gb = UK, us = USA, de = Germany
LOCATION = ""              # Example: Netherlands, Amsterdam, Eindhoven, Remote
WHAT = ""                  # Empty = broad search / all jobs

MAX_PAGES = 30
RESULTS_PER_PAGE = 100
MAX_DAYS_OLD = 21

BASE_URL = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{{}}"


def fetch_jobs():
    all_jobs = []

    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page}...")

        params = {
            "app_id": APP_ID,
            "app_key": API_KEY,
            "what": WHAT,
            "where": LOCATION,
            "results_per_page": RESULTS_PER_PAGE,
            "max_days_old": MAX_DAYS_OLD,
            "content-type": "application/json"
        }

        response = requests.get(BASE_URL.format(page), params=params)

        if response.status_code != 200:
            print("API error:", response.status_code)
            print(response.text)
            break

        data = response.json()
        jobs = data.get("results", [])

        if not jobs:
            print("No more jobs found.")
            break

        all_jobs.extend(jobs)
        print(f"Collected {len(jobs)} jobs")

    return all_jobs


def clean_jobs(jobs):
    df = json_normalize(jobs)

    columns = [
        "id",
        "title",
        "company.display_name",
        "location.display_name",
        "created",
        "description",
        "redirect_url",
        "contract_type",
        "category.label"
    ]

    available_columns = [col for col in columns if col in df.columns]
    df = df[available_columns]

    df = df.rename(columns={
        "company.display_name": "company",
        "location.display_name": "location",
        "category.label": "category"
    })

    df["created"] = pd.to_datetime(df["created"], errors="coerce")

    df = df.drop_duplicates(subset=["id"])

    return df


def create_charts(df):
    if "category" in df.columns:
        category_counts = df["category"].value_counts().head(20)

        plt.figure(figsize=(10, 6))
        category_counts.plot(kind="bar")
        plt.title(f"Top Job Categories in {LOCATION}")
        plt.xlabel("Category")
        plt.ylabel("Number of Jobs")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("jobs_by_category.png")
        plt.show()

    if "location" in df.columns:
        location_counts = df["location"].value_counts().head(20)

        plt.figure(figsize=(10, 6))
        location_counts.plot(kind="bar")
        plt.title(f"Top Job Locations in {LOCATION}")
        plt.xlabel("Location")
        plt.ylabel("Number of Jobs")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("jobs_by_location.png")
        plt.show()

    if "company" in df.columns:
        company_counts = df["company"].value_counts().head(20)

        plt.figure(figsize=(10, 6))
        company_counts.plot(kind="bar")
        plt.title(f"Top Hiring Companies in {LOCATION}")
        plt.xlabel("Company")
        plt.ylabel("Number of Jobs")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("jobs_by_company.png")
        plt.show()


def save_csv(df):
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"adzuna_all_jobs_{COUNTRY}_{today}.csv"

    df.to_csv(filename, index=False, encoding="utf-8")

    print(f"\nCSV saved: {filename}")


def main():
    jobs = fetch_jobs()

    if not jobs:
        print("No jobs collected.")
        return

    df = clean_jobs(jobs)

    print("\nPreview:")
    print(df.head())

    print("\nSummary:")
    print("Total jobs:", len(df))

    if "company" in df.columns:
        print("Unique companies:", df["company"].nunique())

    if "location" in df.columns:
        print("Unique locations:", df["location"].nunique())

    if "category" in df.columns:
        print("\nTop categories:")
        print(df["category"].value_counts().head(10))

    save_csv(df)
    create_charts(df)


main()
