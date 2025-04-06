import feedparser
import requests
import csv
import os
from datetime import datetime, timedelta
import calendar
import pytz

# Base URL for the RSS feed (fetches results in English with "sustainable economy" keyword)
#base_url = "https://ec.europa.eu/commission/presscorner/api/rss?search?language=en&documenttype=1&text=sustainable%20economy&datefrom=01012025&dateto=06042025&policyarea=&pagesize=100&page="

#title cleaning function
import re

def clean_filename(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)  # remove forbidden characters
    s = s.strip()
    s = s.replace(" ", "_")  # optional: replace spaces with underscores
    s = s.replace('€', 'Euro')  # Replace € with 'Euro'
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
     
    

   

# Starting period
start_date = datetime(2018, 1, 1)
end_date = datetime(2018, 12, 31)  # Your specified end date

# Function to format date
def format_date(dt):
    return dt.strftime("%d%m%Y")  # DDMMYYYY


# Output CSV file
csv_filename = "all_press_releases.csv"
save_folder = 'data/pdf_files'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Open CSV file for writing
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Published Date","title","ip_id","Link"])  # CSV header

    current_start = start_date
    while current_start <= end_date:
        # Set a tentative end date (end of the month)
        last_day_of_month = calendar.monthrange(current_start.year, current_start.month)[1]
        current_end = datetime(current_start.year, current_start.month, last_day_of_month)
        if current_end > end_date:
            current_end = end_date

        print(f"\n🔍 Checking from {current_start.date()} to {current_end.date()}")

          
        while True:
            # Build URL
            base_url = f"https://ec.europa.eu/commission/presscorner/api/rss?search?language=en&documenttype=1&text=sustainable%20economy&datefrom={format_date(current_start)}&dateto={format_date(current_end)}&policyarea=&pagesize=100"

            # Parse
            feed = feedparser.parse(base_url)
            entries = feed.entries

            print(f"🔹 Found {len(entries)} entries.")

            if len(entries) < 100:
                # All entries fit, save them in CSV
                for entry in entries:
                    title = entry.title
                    link = entry.link
                    guid = entry.guid
                    ip_id = guid.split('/')[-1]
                    published_raw = entry.published  # e.g., "Fri, 05 Jan 2018 10:00:00 GMT"
                    published_date = format_published_date(published_raw)

                    # Write CSV
                    writer.writerow([published_date, title, ip_id, link])

                    # Clean title for filename
                    clean_title = clean_filename(title)

                    # Create a nice filename
                    pdf_filename = f"{published_date}_{clean_title}_{ip_id}.pdf"
                    pdf_path = os.path.join(save_folder, pdf_filename)


                    # Download PDF
                    url = f"https://ec.europa.eu/commission/presscorner/api/files/document/print/en/{ip_id}/{ip_id.upper()}.pdf"
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Saved PDF for {ip_id}")
                    else:
                        print(f"❌ Failed to download PDF for {ip_id}")
                   
                break
            else:
                # Too many results: split the date range smaller
                print(f"⚡ Too many results. Splitting date range...")
                # Split period into two
                middle_date = current_start + (current_end - current_start) / 2
                middle_date = middle_date.replace(hour=0, minute=0, second=0, microsecond=0)

                current_end = middle_date  # Reduce end date for next try

        # Move to next period (day after last covered day)
        current_start = current_end + timedelta(days=1)

print("\n🎯 Finished downloading all press releases dynamically!")

