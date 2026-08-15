from config import IMAGE_DIR
from tools.browser import search_google_images
from tools.downloader import download_images, save_selected_image
from tools.selector import select_best_image


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

    candidate_paths = download_images(
        image_urls,
        IMAGE_DIR,
    )

    for candidate_path in candidate_paths:
        print(f"Downloaded: {candidate_path}")

    selected_path = select_best_image(prompt, candidate_paths)

    print(f"Openai ai selected: {selected_path}")

    final_path = save_selected_image(
        selected_path,
        IMAGE_DIR,
    )

    print(f"final image saved: {final_path}")



if __name__ == "__main__":
    main()
