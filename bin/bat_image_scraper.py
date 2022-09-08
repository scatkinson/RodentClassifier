import time

from scraper.image_scraper import ImageScrape

# config
SUBREDDIT = 'batty'
SAMPLE_SIZE = 20
IMAGE_DIRECTORY = "data/bats/images/"
IMAGE_REGISTRY_PATH = "data/bats/image_registry/image_registry.csv"

def main():
    scraper = ImageScrape(
        subreddit=SUBREDDIT,
        sample_size=SAMPLE_SIZE,
        image_directory=IMAGE_DIRECTORY,
        image_registry_path=IMAGE_REGISTRY_PATH
    )
    scraper.run_scraper()

if __name__ == "__main__":
    main()