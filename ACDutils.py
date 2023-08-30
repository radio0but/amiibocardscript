import requests
from gi.repository import GdkPixbuf

def fetch_amiibo_data():
    response = requests.get('https://www.amiiboapi.com/api/amiibo/')
    return json.loads(response.text)['amiibo']

def load_image_data(url, size=None):
    response = requests.get(url)
    loader = GdkPixbuf.PixbufLoader()
    loader.write(response.content)
    loader.close()

    pixbuf = loader.get_pixbuf()
    if size:
        aspect_ratio = pixbuf.get_height() / pixbuf.get_width()
        new_height = size * aspect_ratio
        pixbuf = pixbuf.scale_simple(size, int(new_height), GdkPixbuf.InterpType.BILINEAR)

    return pixbuf
