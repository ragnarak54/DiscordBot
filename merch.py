from PIL import Image
import datetime
import pytz

images_dir = "images/"

rotation_order = [1, 1, 2, 1, 3, 4, 3, 1, 5, 6, 6, 6, 5, 7, 8, 5, 7, 9, 1, 2,
                  4, 4, 1, 4, 6, 10, 4, 11, 7, 2, 5, 5, 9, 12, 2, 9, 4, 12, 4, 12]
initial_ids = [1, 8, 3, 7, 4, 11, 10, 13, 12, 2, 9, 5, 6]
items = ['Dragonkin lamp', 'D&D token (weekly)', 'Deathtouched dart',
         'Menaphite gift offering (large)', 'Starved ancient effigy', 'Large goebie burial charm',
         'Crystal triskelion', 'Taijitu', 'Message in a bottle (Deep Sea Fishing)',
         'Unfocused reward enhancer', 'Dungeoneering Wildcard', 'Harmonic dust',
         'D&D token (monthly)']


class MerchItem:
    def __init__(self, image_key, name, cost, quantity, use):
        self.image_key = image_key
        self.name = name
        self.cost = cost
        self.quantity = quantity
        self.use = use

    def get_icon(self):
        return Image.open(images_dir + self.image_key, 'r')


def get_item():
    now = datetime.datetime.now(pytz.utc)
    # number of 40 day periods since the start
    rotation_40 = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days // 40
    print(rotation_40)
    # number of days elapsed in this 40 day period
    rotation_daily = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days % 40 + 1
    print(rotation_daily)
    current_item_id = rotation_order[rotation_daily]
    mapped_id = initial_ids[current_item_id]
    output_item_id = ((mapped_id + rotation_40) % len(items)) + 1
    return items[output_item_id]


print(get_item())
