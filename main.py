from browser import search_google_images


def main() -> None:

    prompt = input("enter image search: ").strip()

    if not prompt:
        print("error, can't be empty")
        return
    print(f"searching google images for: {prompt}")

    image_urls = search_google_images(prompt)

    print(f"Collected {len(image_urls)} candidate URLs")

    for index, url in enumerate(image_urls, start=1):
        print(index, url)


if __name__ == "__main__":
    main()
