import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime

MAX_HEADLINES = 5

OUTPUT_FILE = "headlines.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HeadlineBot/1.0)"
}

def scrape_site(site):
    url = site["url"]
    selector = site["selector"]
    name = site["name"]

    headlines = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        elements = soup.select(selector)

        for el in elements[:MAX_HEADLINES]:
            text = el.get_text(strip=True)
            if text:
                headlines.append(text)

    except Exception as e:
        headlines.append(f"[ERROR scraping {name}: {e}]")

    return name, headlines


def main():
    with open("sites.yaml") as f:
        sites = yaml.safe_load(f)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"Updated: {datetime.utcnow().isoformat()} UTC\n\n")

        for site in sites["sites"]:
            name, headlines = scrape_site(site)
            #out.write(f"=== {name} ===\n")#the headline
            for h in headlines:
                out.write(f"{h};\n") #Formatting of the file itself
            out.write("\n")


if __name__ == "__main__":
    main()
