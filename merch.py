from PIL import Image
import datetime
import pytz
import items

images_dir = "images/"

a_b_items = ['Barrel of bait', 'Tangled fishbowl', 'Broken fishing rod', 'Message in a bottle (Deep Sea Fishing)',
             'Small goebie burial charm', 'Goebie burial charm', 'Large goebie burial charm',
             'Menaphite gift offering (small)', 'Menaphite gift offering (medium)', 'Menaphite gift offering (large)',
             'D&D token (daily)', 'D&D token (weekly)', 'D&D token (monthly)',
             'Unstable air rune', 'Anima crystal', 'Taijitu', 'Gift for the Reaper', 'Slayer VIP Coupon',
             'Shattered anima', 'Livid plant (Deep Sea Fishing)', 'Sacred clay (Deep Sea Fishing)',
             'Unfocused damage enhancer', 'Unfocused reward enhancer',
             'Silverhawk down', 'Advanced pulse core', 'Dungeoneering Wildcard',
             'Dragonkin lamp', 'Starved ancient effigy', 'Harmonic dust',
             'Crystal triskelion', 'Deathtouched dart']

a_rotation = [18, 22, 17, 2, 15, 8, 5, 9, 19, 5, 11, 18, 21, 25, 2, 14, 25, 17, 2, 3,
              8, 5, 9, 21, 5, 11, 21, 19, 25, 17, 14, 3, 17, 2, 3, 5, 5, 9, 21, 19,
              11, 18, 19, 24, 2, 14, 3, 1, 2, 3, 5, 1, 9, 21, 8, 20, 21, 19, 24, 14,
              14, 3, 1, 17, 3, 5, 17, 6, 21, 19, 20, 14, 19, 24, 14, 18, 3, 1, 17, 6,
              5, 1, 6, 19, 8, 20, 14, 21, 24, 14, 18, 22, 1, 17, 15, 8, 17, 6, 19, 5,
              20, 14, 21, 25, 14, 18, 25, 17, 17, 6, 8, 5, 6, 19, 5, 11, 14, 21, 25, 17]

b_rotation = [18, 22, 17, 8, 14, 3, 6, 19, 21, 24, 2, 5, 18, 22, 3, 8, 8, 20, 14, 17,
              21, 25, 22, 5, 5, 11, 21, 2, 19, 24, 25, 1, 1, 9, 19, 14, 8, 11, 24, 17,
              17, 6, 8, 18, 1, 9, 20, 14, 2, 3, 5, 21, 17, 6, 9, 18, 18, 22, 1, 8,
              2, 15, 6, 21, 21, 25, 2, 5, 14, 3, 15, 19, 19, 24, 14, 1, 18, 25, 3, 8,
              8, 20, 18, 17, 19, 24, 22, 1, 5, 9, 21, 2, 8, 20, 24, 17, 17, 6, 19, 18,
              5, 11, 20, 2, 2, 15, 5, 21, 1, 9, 11, 14, 14, 3, 1, 19, 17, 15, 9, 18]

rotation_order = [1, 1, 2, 1, 3, 4, 3, 1, 5, 6, 6, 6, 5, 7, 8, 5, 7, 9, 1, 2,
                  4, 4, 1, 4, 6, 10, 4, 11, 7, 2, 5, 5, 9, 12, 2, 9, 4, 12, 4, 12]
initial_ids = [1, 8, 3, 7, 4, 11, 10, 13, 12, 2, 9, 5, 6]
c_items = ['Dragonkin lamp', 'D&D token (weekly)', 'Deathtouched dart',
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

    def __repr__(self):
        return self.name

    def get_icon(self):
        return Image.open(images_dir + self.image_key, 'r')


def get_stock(days=0):
    # https://runescape.wiki/w/Travelling_Merchant%27s_Shop/Details

    stock = []
    now = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=days)

    a_b_rotation = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days % 120 + 1
    slot_a = a_b_items[a_rotation[a_b_rotation-1]-1]
    print(slot_a)
    stock.append(MerchItem(f'{slot_a}.png', slot_a, *items.get_attrs(slot_a)))

    slot_b = a_b_items[b_rotation[a_b_rotation-1]-1]
    stock.append(MerchItem(f'{slot_b}.png', slot_b, *items.get_attrs(slot_b)))

    # number of 40 day periods since the start
    rotation_40 = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days // 40
    # number of days elapsed in this 40 day period
    rotation_daily = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days % 40 + 1
    current_item_id = rotation_order[rotation_daily - 1]
    mapped_id = initial_ids[current_item_id - 1]
    output_item_id = ((mapped_id + rotation_40) % len(c_items))
    slot_c = c_items[output_item_id - 1]
    stock.append(MerchItem(f'{slot_c}.png', slot_c, *items.get_attrs(slot_c)))
    return stock



