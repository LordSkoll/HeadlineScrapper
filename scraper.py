
import requests
from bs4 import BeautifulSoup
import yaml
import time
import random
from datetime import datetime
from deep_translator import GoogleTranslator


# ==============================
# CONFIGURATION
# ==============================

MAX_HEADLINES = 5

OUTPUT_FILE = "headlines.txt"

TRANSLATE_HEADLINES = False  # True = translate, False = original text

TARGET_LANGUAGE = "pl"

TRANSLATION_DELAY = 2       # Seconds between translation requests
TRANSLATION_RETRIES = 4     # Maximum number of attempts


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HeadlineBot/1.0)"
}


# ==============================
# TRANSLATION
# ==============================

def translate_text(text, target_lang="pl", retries=4):

    for attempt in range(retries):

        try:
            return GoogleTranslator(
                source="auto",
                target=target_lang
            ).translate(text)

        except Exception as e:

            print(
                f"Translation failed "
                f"(attempt {attempt + 1}/{retries}): {e}"
            )

            if attempt < retries - 1:

                wait_time = 2 ** (attempt + 1) + random.uniform(0, 1)

                print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)

    return "[TRANSLATION ERROR: MAX RETRIES EXCEEDED]"


# ==============================
# SCRAPING
# ==============================

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


# ==============================
# TEXT CLEANING
# ==============================

def remove_symbol(text, symbol):

    if not symbol:
        return text

    return text.replace(symbol, "")


def replace_symbol(text, old_symbol, new_symbol):

    if not old_symbol:
        return text

    return text.replace(old_symbol, new_symbol)


def clean_text(text):

    replacements = {
        "ą": "a",
        "ć": "c",
        "ż": "z",
        "ź": "z",
        "ł": "l",
        "ó": "o",
        "ę": "e",
        "ś": "s",
        "ń": "n",
        "‘": '"',
        "’": '"',
        "„": '"',
        "”": '"',
        "–": "-"
    }

    for old, new in replacements.items():
        text = replace_symbol(text, old, new)

    return text


# ==============================
# MAIN
# ==============================

def main():

    with open("sites.yaml", encoding="utf-8") as f:
        sites = yaml.safe_load(f)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        out.write(
            f"Updated: {datetime.utcnow().isoformat()} UTC\n\n"
        )

        for site in sites["sites"]:

            name, headlines = scrape_site(site)

            for h in headlines:

                if TRANSLATE_HEADLINES:

                    time.sleep(TRANSLATION_DELAY)

                    translated = translate_text(
                        h,
                        target_lang=TARGET_LANGUAGE,
                        retries=TRANSLATION_RETRIES
                    )

                    # Clean translated text
                    translated = clean_text(translated)

                    out.write(f"{translated}\n")

                else:

                    # Save original headline without translation
                    out.write(f"{h}\n")

            out.write("\n")

    print(f"Headlines saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
