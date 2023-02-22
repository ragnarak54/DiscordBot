from PIL import Image
import datetime
import pytz
import items

images_dir = "images/"


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

slot_map = {
    "A": [
        "Gift for the Reaper",
        "Broken fishing rod",
        "Barrel of bait",
        "Anima crystal",
        "Small goebie burial charm",
        "Goebie burial charm",
        "Menaphite gift offering (small)",
        "Menaphite gift offering (medium)",
        "Shattered anima",
        "D&D token (daily)",
        "Sacred clay",
        "Livid plant",
        "Slayer VIP Coupon",
        "Silverhawk down",
        "Unstable air rune",
        "Advanced pulse core",
        "Tangled fishbowl",
        "Unfocused damage enhancer",
        "Horn of honour",
    ],
    "C": [
        "Taijitu",
        "Large goebie burial charm",
        "Menaphite gift offering (large)",
        "D&D token (weekly)",
        "D&D token (monthly)",
        "Dungeoneering Wildcard",
        "Message in a bottle",
        "Crystal triskelion",
        "Starved ancient effigy",
        "Deathtouched dart",
        "Dragonkin lamp",
        "Harmonic dust",
        "Unfocused reward enhancer",
    ],
}

slot_map["B"] = slot_map["A"]

slot_constants = {"A": (3, 19), "B": (8, 19), "C": (5, 13)}


def get_slot(slot: str, runedate: int) -> MerchItem:
    const, num_unique = slot_constants[slot]

    seed = (runedate << 32) + (runedate % const)
    multiplier = int("0x5DEECE66D", 16)

    mask = (2**48) - 1
    addend = 11

    seed = (seed ^ multiplier) & mask
    seed = (seed * multiplier) + addend
    seed = seed & mask

    slot_index = (seed >> 17) % num_unique

    item_name = slot_map[slot][slot_index]
    return MerchItem(f'{item_name}.png', item_name, *items.get_attrs(item_name))


def get_stock(days=0):
    # https://runescape.wiki/w/Travelling_Merchant%27s_Shop/Details

    stock = [MerchItem('Uncharted island map (Deep Sea Fishing).png', 'Uncharted island map', '800,000', 1,
                       "Allows travel to an [[uncharted island]] with the chance of 3-6 special resources at the cost "
                       "of no supplies<br />In addition, players may also rarely receive a [[Uncharted island map ("
                       "red)|red uncharted island map]].", "<:Uncharted_map:755960222949965825>")]
    now = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=days)
    runedate = (now - datetime.datetime(2002, 2, 27, 0, 0, 0, tzinfo=pytz.utc)).days

    stock.append(get_slot("A", runedate))
    stock.append(get_slot("B", runedate))
    stock.append(get_slot("C", runedate))
    return stock