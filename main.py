from browser import search_google_images
from config import IMAGE_DIR
from downloader import download_image

def main() -> None:

    prompt = input("enter image search: ").strip()

    if not prompt:
        print("error, can't be empty")
        return
    print(f"searching google images for: {prompt}")

    image_urls = search_google_images(prompt)

    if not image_urls:
        print("No candidate images found.")
        return

    first_candidate = IMAGE_DIR / "candidate1.jpg"

    download_image(
        image_urls[0],
        first_candidate,
    )

    print(f"Downloaded: {first_candidate}")



if __name__ == "__main__":
    main()
