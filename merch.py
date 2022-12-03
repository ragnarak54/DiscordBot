from PIL import Image
import datetime
import pytz
import items

images_dir = "images/"

a_b_items = ['Barrel of bait', 'Tangled fishbowl', 'Broken fishing rod', 'Message in a bottle',
             'Small goebie burial charm', 'Goebie burial charm', 'Large goebie burial charm',
             'Menaphite gift offering (small)', 'Menaphite gift offering (medium)', 'Menaphite gift offering (large)',
             'D&D token (daily)', 'D&D token (weekly)', 'D&D token (monthly)',
             'Unstable air rune', 'Anima crystal', 'Taijitu', 'Gift for the Reaper', 'Slayer VIP Coupon',
             'Shattered anima', 'Livid plant', 'Sacred clay',
             'Unfocused damage enhancer', 'Unfocused reward enhancer',
             'Silverhawk down', 'Advanced pulse core', 'Dungeoneering Wildcard',
             'Dragonkin lamp', 'Starved ancient effigy', 'Harmonic dust',
             'Crystal triskelion', 'Deathtouched dart', 'Horn of honour']

a_rotation = [1, 15, 1, 6, 4, 8, 14, 9, 12, 17, 9, 13, 2, 16, 2, 7, 1, 5, 11, 6,
              9, 14, 10, 14, 18, 13, 18, 4, 17, 2, 8, 3, 6, 11, 7, 11, 19, 14, 15, 1,
              14, 18, 5, 19, 7, 12, 8, 12, 16, 11, 12, 17, 15, 19, 6, 1, 4, 9, 5, 9,
              13, 8, 13, 18, 12, 16, 3, 17, 1, 6, 2, 6, 10, 5, 10, 15, 13, 17, 19, 14,
              17, 3, 18, 3, 11, 6, 11, 16, 10, 14, 16, 11, 18, 4, 19, 4, 8, 3, 8, 13,
              7, 11, 17, 12, 15, 1, 16, 1, 5, 19, 5, 10, 4, 8, 14, 9, 16, 2, 13, 17]

b_rotation = [1, 15, 1, 1, 14, 9, 19, 14, 3, 17, 18, 18, 12, 7, 17, 12, 1, 15, 1, 1,
              10, 5, 15, 10, 18, 13, 18, 18, 8, 3, 13, 8, 16, 11, 16, 16, 10, 5, 11, 6,
              14, 9, 14, 14, 8, 3, 13, 8, 16, 11, 12, 12, 6, 1, 11, 6, 14, 9, 14, 14,
              4, 18, 9, 4, 12, 7, 12, 12, 2, 16, 7, 2, 10, 5, 10, 10, 4, 18, 5, 19,
              8, 3, 8, 8, 2, 16, 7, 2, 10, 5, 6, 6, 19, 14, 5, 19, 8, 3, 8, 8,
              17, 12, 3, 17, 6, 1, 6, 6, 15, 10, 1, 15, 4, 18, 4, 4, 17, 12, 18, 13]

ab_initial = [32, 15, 9, 20, 25, 17, 5, 19, 18, 2, 3, 6, 11, 24, 22, 1, 8, 21, 14]

rotation_order = [1, 1, 2, 1, 3, 4, 9, 1, 8, 6, 6, 6, 5, 7, 8, 5, 7, 9, 7, 2,
                  4, 4, 1, 4, 6, 10, 4, 11, 7, 2, 5, 5, 9, 12, 2, 9, 3, 12, 4, 12]
initial_ids = [1, 8, 3, 7, 4, 11, 10, 13, 12, 2, 9, 5, 6]
c_items = ['Dragonkin lamp', 'D&D token (weekly)', 'Deathtouched dart',
           'Menaphite gift offering (large)', 'Starved ancient effigy', 'Large goebie burial charm',
           'Crystal triskelion', 'Taijitu', 'Message in a bottle',
           'Unfocused reward enhancer', 'Dungeoneering Wildcard', 'Harmonic dust',
           'D&D token (monthly)']


class MerchItem:
    def __init__(self, image_key, name, cost, quantity, use, emoji):
        self.image_key = image_key
        self.name = name
        self.cost = cost
        self.quantity = quantity
        self.use = use
        self.emoji = emoji

    def __repr__(self):
        return self.name

    def get_icon(self):
        return Image.open(images_dir + self.image_key, 'r')


def get_stock(days=0):
    # https://runescape.wiki/w/Travelling_Merchant%27s_Shop/Details

    stock = [MerchItem('Uncharted island map (Deep Sea Fishing).png', 'Uncharted island map', '800,000', 1,
                       "Allows travel to an [[uncharted island]] with the chance of 3-6 special resources at the cost "
                       "of no supplies<br />In addition, players may also rarely receive a [[Uncharted island map ("
                       "red)|red uncharted island map]].", "<:Uncharted_map:755960222949965825>")]
    now = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=days)

    # number of days elapsed in this 120 day period
    a_b_rotation = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days % 120 + 1
    # number of 120 day rotations since the start minus 6 for some reason lol
    rotation_120 = (now - datetime.datetime(2018, 3, 11, 0, 0, 0, tzinfo=pytz.utc)).days // 120 - 6

    def add_slotAB(rotation):
        current_item_id = rotation[a_b_rotation - 1]
        output_item_id = ab_initial[(current_item_id + rotation_120) % len(ab_initial)]
        item_name = a_b_items[output_item_id - 1]
        stock.append(MerchItem(f'{item_name}.png', item_name, *items.get_attrs(item_name)))

    add_slotAB(a_rotation)
    add_slotAB(b_rotation)

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
