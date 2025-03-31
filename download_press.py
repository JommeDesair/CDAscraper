import feedparser
import requests
import csv

# Base URL for the RSS feed (fetches results in English with "sustainable economy" keyword)
base_url = "https://ec.europa.eu/commission/presscorner/api/rss?search?language=en&documenttype=1&text=sustainable%20economy&policyarea=&pagesize=100&page="

# Output CSV file
csv_filename = "all_press_releases.csv"

# Open CSV file for writing
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["ip_id", "title"])  # CSV header

    total_entries = 0
    page = 1

    while True:
        # Construct the URL for the current page
        rss_url = f"{base_url}{page}"
        print(f"Fetching page {page}...")

        # Parse the RSS feed
        feed = feedparser.parse(rss_url)

        # If no entries are found, stop fetching
        if not feed.entries:
            print("No more press releases found. Stopping.")
            break

        # Write entries to CSV
        for entry in feed.entries:
            title = entry.title
            guid=entry.guid
            ip_id = guid.split('/')[-1]
            url="https://ec.europa.eu/commission/presscorner/api/files/document/print/en/{0}/{1}.pdf".format(ip_id, ip_id.upper())
            response = requests.get(url)
            with open(f'pdf_files/{ip_id}.pdf', 'wb') as f:
                f.write(response.content)
            writer.writerow([ip_id, title])

        total_entries += len(feed.entries)
        page += 1  # Go to the next page

print(f"✅ Downloaded {total_entries} press releases and saved them to {csv_filename}")
