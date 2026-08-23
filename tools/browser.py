from playwright.sync_api import Page, sync_playwright
from urllib.parse import urlencode

from config import CANDIDATE_COUNT

GOOGLE_IMAGES_URL = "https://images.google.com/"

def _collect_image_urls(page: Page) -> list[str]:
    images = page.locator("img")
    image_count = images.count()
    image_urls: list[str] = []

    for index in range(image_count):
        source = images.nth(index).get_attribute("src")

        if not source:
            continue

        if not source.startswith("http"):
            continue

        if source in image_urls:
            continue

        image_urls.append(source)

        if len(image_urls) == CANDIDATE_COUNT:
            break

    return image_urls

def search_google_images_batch(
    prompts: list[str],
) -> list[list[str]]:
    if not prompts:
        return []

    results: list[list[str]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
        )

        page = browser.new_page()

        for index, prompt in enumerate(prompts):
            query_string = urlencode(
                {
                    "tbm": "isch",
                    "q": prompt,
                }
            )

            page.goto(
                f"https://www.google.com/search?{query_string}",
                wait_until="domcontentloaded",
            )

            if index == 0:
                input(
                    "Complete any Google verification, "
                    "wait for the images to load, "
                    "then press Enter once: "
                )
            else:
                page.wait_for_timeout(1500)

            image_urls = _collect_image_urls(page)
            results.append(image_urls)

            print(
                f"Collected {len(image_urls)} candidates "
                f"for search {index + 1}/{len(prompts)}"
            )

        browser.close()

    return results