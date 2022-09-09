import time

from scraper.image_scraper import ImageScrape

# config
SUBREDDIT = 'RATS'
SAMPLE_SIZE = 50
IMAGE_DIRECTORY = "data/rats/images/"
IMAGE_REGISTRY_PATH = "data/rats/image_registry/image_registry.csv"

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