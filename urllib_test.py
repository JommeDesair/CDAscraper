from urllib.request import urlopen
url = "https://ec.europa.eu/commission/presscorner/detail/en/ip_25_568"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf-8")
print(html)
