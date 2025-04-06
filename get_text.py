from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "https://ec.europa.eu/commission/presscorner/detail/en/ip_25_568"
html = urlopen(url).read()
soup = BeautifulSoup(html, features="html.parser")

# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out

# get text
text = soup.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text)

articles = soup.find_all('article')

for article in articles:
    print(article.get_text(separator="\n", strip=True))
