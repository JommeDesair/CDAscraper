import feedparser
import requests
import csv
import os
from datetime import datetime, timedelta
import calendar
import pytz
from dateutil import parser
import re

# Base URL for the RSS feed (fetches results in English with "sustainable economy" keywords)
#base_url = "https://ec.europa.eu/commission/presscorner/api/rss?search?language=en&documenttype=1&text=sustainable%20economy&datefrom=01012025&dateto=06042025&policyarea=&pagesize=100&page="



# -------- Configuration --------
start_date = datetime(1995, 1, 1) # Your specified start date, format YYYY, M, D
end_date = datetime(2025, 4, 19) # Your specified end date
keywords = [
    "sustainable economy", "sustainability economy", "sustainable economic",
    "sustainability economic", "sustainable economies", "sustainability economies"
]
 
# -------- Set-up --------------
csv_filename = "all_press_releases.csv"
save_folder = 'data/pdf_files'

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

seen_ids = set()  # To track duplicates

from collections import defaultdict
log_summary = defaultdict(lambda: defaultdict(int))  # month -> keyword -> count
log_failures = []  # list of failed downloads
unique_entries_per_month = defaultdict(set)  # month -> set of unique ip_ids

#title cleaning function
def clean_filename(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)  # remove forbidden characters
    s = s.strip()
    s = s.replace(" ", "_")  # optional: replace spaces with underscores
    s = s.replace('€', 'Euro')  # Replace € with 'Euro'
    s = s.replace("\n","_")
    s = s.replace("\r","_")
    return s[:100]  # Limit length to avoid Windows path issues

#date in title cleaning function
from dateutil import parser
def format_published_date(published_date):
    utc = pytz.utc   # Define the timezone
    cet = pytz.timezone('Europe/Brussels')  # Brussels time (CET/CEST)dt = parser.parse(published)
    # Parse published date
    published_date_utc = datetime(*entry.published_parsed[:6], tzinfo=utc)
    published_date_cet = published_date_utc.astimezone(cet)

    # Now format
    published_date = published_date_cet.strftime("%Y-%m-%d") 
    
    return published_date # you can change format if you want
     
 #format date function
def format_date(dt):
    return dt.strftime("%d%m%Y")  # DDMMYYYY   

#------- Start extraction --------------------

# Open CSV file for writing
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Published Date","Title","IP ID","Link"])  # CSV header

    current_start = start_date
    while current_start <= end_date:
        # Set a tentative end date (end of the month)
        last_day_of_month = calendar.monthrange(current_start.year, current_start.month)[1]
        current_end = datetime(current_start.year, current_start.month, last_day_of_month)
        if current_end > end_date:
            current_end = end_date

        date_label = current_start.strftime("%Y-%m")
        print(f"\n🔍 Checking from {current_start.date()} to {current_end.date()}")
        for keyword in keywords:
            print(f"   🧠 Searching for: {keyword}")
            encoded_keyword = keyword.replace(" ", "%20")
            base_url = f"https://ec.europa.eu/commission/presscorner/api/rss?search?language=en&documenttype=1&text={encoded_keyword}&datefrom={format_date(current_start)}&dateto={format_date(current_end)}&policyarea=&pagesize=100"
          
     
          # Parse
            feed = feedparser.parse(base_url)
            entries = feed.entries
            print(f"   🔹 Found {len(entries)} entries for {keyword}")

            log_summary[date_label][keyword] += len(entries)


            for entry in entries:
                ip_id = entry.guid.split('/')[-1]
                if ip_id in seen_ids:
                    continue  # Skip duplicates
                seen_ids.add(ip_id)
                unique_entries_per_month[date_label].add(ip_id)
                
                title = entry.title
                link = entry.link
                published_date = format_published_date(entry)
                clean_title = clean_filename(title)
                pdf_filename = f"{published_date}_{clean_title}_{ip_id}.pdf"
                pdf_path = os.path.join(save_folder, pdf_filename)


                # Save to CSV
                writer.writerow([published_date, title, ip_id, link])

                # Download PDF
                # Count for summary
                date_label = published_date[:7]  # Format: YYYY-MM
                log_summary[date_label][keyword] += 1
                pdf_url = f"https://ec.europa.eu/commission/presscorner/api/files/document/print/en/{ip_id}/{ip_id.upper()}.pdf"
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    with open(pdf_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ Saved PDF for {ip_id}")

                else:
                    print(f"❌ Failed to download PDF for {ip_id}")
                    log_failures.append([published_date, keyword, title, ip_id, pdf_url])
                   
        # Move to next period (day after last covered day)
        current_start = current_end + timedelta(days=1)

# -------- Write summary log --------
with open("press_log_summary.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Month", "Keyword", "Press Releases Found"])
    for month, keywords in sorted(log_summary.items()):
        unique_count = len(unique_entries_per_month[month])
        for keyword, count in keywords.items():
            writer.writerow([month, keyword, count, unique_count])

# -------- Write failure log --------
with open("press_log_failures.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Keyword", "Title", "IP ID", "Failed URL"])
    for failure in log_failures:
        writer.writerow(failure)

print("\n🎯 Finished downloading all press releases!")