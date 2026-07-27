from playwright.sync_api import sync_playwright

GOOGLE_IMAGES_URL = "https://images.google.com/"


def search_google_images(prompt: str) -> list[str]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
        )
        page = browser.new_page()
        page.goto(GOOGLE_IMAGES_URL, wait_until="domcontentloaded")
        search_box = page.locator('textarea[name="q"], input[name="q"]').first

        search_box.fill(prompt)
        search_box.press("Enter")

        page.wait_for_url("**/search?**")
        input(
            "Complete any Google verification, wait for the images to load, "
            "then press Enter"
        )
        images = page.locator("img")
        image_count = images.count()

        print(f"Found {image_count} image elements")

        image_urls: list[str] = []

        for index in range(image_count):
            image = images.nth(index)
            source = image.get_attribute("src")

            if not source:
                continue

            if not source.startswith("http"):
                continue

            if source in image_urls:
                continue

            image_urls.append(source)

            if len(image_urls) == 5:
                break

        browser.close()
        return image_urls
