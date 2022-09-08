import pandas as pd
import numpy as np
import requests
import json
import csv
import os
import time
import urllib3
import warnings
import datetime

from PIL import Image
from bs4 import BeautifulSoup

warnings.filterwarnings("error", category=Image.DecompressionBombWarning)

NO_IMAGE_STR = "NO IMAGE"
PARSER_STR = 'html.parser'

DELETED_IMAGE_PATH = "scraper/deleted_image.jpg"

REDDIT_IMAGE_PREFIX = "https://i.redd.it/"

FULL_LINK_COL = "full_link"
IMAGE_LINK_COL = "image_link"
LOCAL_PATH_COL = "local_path"
CREATED_UTC_COL = "created_utc"
ID_COL = "id"
URL_COL = "url"
IMAGE_EXISTS_COL = "image_exists"
IMAGE_REGISTRY_COLS = [FULL_LINK_COL, IMAGE_LINK_COL,  ID_COL, LOCAL_PATH_COL, CREATED_UTC_COL]

PUSHSHIFT_SEARCH_URL = 'https://api.pushshift.io/reddit/search/submission/'
PUSHSHIFT_SIZE = 100
DESC_STR = "desc"
HEADERS = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

class ImageScrape():

    def __init__(self, subreddit, sample_size, image_directory, image_registry_path, before_override=None):
        self.subreddit = subreddit
        self.sample_size = sample_size
        self.post_data_list = []
        self.post_df = pd.DataFrame()
        self.image_directory = image_directory
        self.image_registry_path = image_registry_path

        if os.path.exists(self.image_registry_path):
            print(f"Image registry exists at {self.image_registry_path}.")
            self.image_registry = pd.read_csv(self.image_registry_path)
            self.before = min(self.image_registry[self.image_registry["full_link"].apply(lambda x: self.subreddit in x)][CREATED_UTC_COL])
            print(f"Earliest image currently in possession with created_utc = {self.before}")
        else:
            self.image_registry = pd.DataFrame(columns=IMAGE_REGISTRY_COLS)
            self.before = time.time()

        if before_override:
            self.before = before_override

        self.image_count = 0
        self.sleep_time = 5

        self.deleted_img_array = np.asarray(Image.open(DELETED_IMAGE_PATH))

    def run_scraper(self):
        start = time.time()
        self.update_image_registry()
        self.get_post_data()
        self.obtain_images()
        self.write_image_registry()
        end = time.time()
        duration = int(end - start)
        print(f"Run complete. {self.image_count} images obtained from the {self.subreddit} subreddit.\n")
        print(f"Run took {duration//60} minutes, {duration%60} seconds.")

    def get_post_data(self):
        print(f"Obtaining posts from r/{self.subreddit}.")
        end = self.before
        data_list = []

        while self.post_df.shape[0] < self.sample_size:
            print(f"Obtaining records before {end}")
            query = {"size": PUSHSHIFT_SIZE, "subreddit": self.subreddit, "sort": DESC_STR, "sort_type": CREATED_UTC_COL, "before": int(end)}
            r = requests.get(PUSHSHIFT_SEARCH_URL, params=query)
            print(f"Request status code: {r.status_code}")
            data = r.json()
            new_rows_df = pd.DataFrame(data['data'])
            try:
                new_rows_df = new_rows_df[new_rows_df['removed_by_category'].isna() & new_rows_df[URL_COL].apply(lambda x: x.startswith(REDDIT_IMAGE_PREFIX))]
            except KeyError:
                new_rows_df = new_rows_df[new_rows_df[URL_COL].apply(lambda x: x.startswith(REDDIT_IMAGE_PREFIX))]
            try:
                new_rows_df = new_rows_df[new_rows_df[URL_COL].apply(self.not_deleted)]
            except (Image.DecompressionBombWarning, Image.UnidentifiedImageError) as e:
                if isinstance(e,Image.DecompressionBombWarning):
                    print(f"Avoiding possible decompression bomb attack: {e}")
                elif isinstance(e, Image.UnidentifiedImageError):
                    print(f"Avoiding Unidentified Image Error: {e}")
                end = data['data'][-1][CREATED_UTC_COL]
                continue

            end = data['data'][-1][CREATED_UTC_COL]
            print("Inserting pushshift data into post_df")
            self.post_df = pd.concat([self.post_df, new_rows_df], ignore_index=True)
            print(f"Total number of records obtained: {self.post_df.shape[0]}")
            time.sleep(self.sleep_time)

        self.post_df["start_time"] = self.before

    def obtain_images(self):
        print(f"Obtaining images")
        for idx in self.post_df.index:
            url = self.post_df.loc[idx,FULL_LINK_COL]
            img_url = self.post_df.loc[idx,URL_COL]
            created_utc = self.post_df.loc[idx,CREATED_UTC_COL]
            entry_id = self.post_df.loc[idx,ID_COL]
            if entry_id not in self.image_registry[ID_COL]:
                print(f"Image URL: {img_url}")
                img_path = self.image_directory + img_url.strip(REDDIT_IMAGE_PREFIX)
                print(f"Image path: {img_path}")
                img_data = requests.get(img_url).content
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                self.image_count += 1
                registry_dict = {FULL_LINK_COL: [url], IMAGE_LINK_COL: [img_url], ID_COL: [entry_id], LOCAL_PATH_COL: [img_path], CREATED_UTC_COL: [created_utc]}
                new_row_df = pd.DataFrame(registry_dict)
                self.image_registry = pd.concat([self.image_registry, new_row_df], ignore_index=True)
            else:
                continue

    def write_image_registry(self):
        print(f"Writing image registry to {self.image_registry_path}")
        self.image_registry.reset_index(drop=True, inplace=True)
        self.image_registry.to_csv(self.image_registry_path)

    def not_deleted(self, img_url):
        if img_url[-3:] != "jpg":
            return False
        img_file = Image.open(requests.get(img_url, stream=True).raw)
        return np.asarray(img_file).all() != self.deleted_img_array.all()

    def update_image_registry(self):
        present_images = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if os.path.isfile(os.path.join(self.image_directory, f))]
        for image_file in self.image_registry[LOCAL_PATH_COL]:
            if image_file not in present_images:
                self.image_registry = self.image_registry[self.image_registry[LOCAL_PATH_COL] != image_file]



