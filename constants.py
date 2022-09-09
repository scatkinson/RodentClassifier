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