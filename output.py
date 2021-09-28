# https://code-maven.com/create-images-with-python-pil-pillow
# https://stackoverflow.com/questions/2563822/how-do-you-composite-an-image-onto-another-image-with-pil-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
import datetime
import discord
from PIL import Image, ImageDraw, ImageFont
import merch

today_img = "res_img.png"
tomorrow_img = "tomorrow_img.png"
custom_img = "custom_date_img.png"

img_bg = (54, 57, 62)
img_text = (255,255,255)

x_icon = 20
x_cost = 400
y_space = 25
title_fnt = ImageFont.truetype('./fonts/roboto/Roboto-Regular.ttf', 20)
fnt = ImageFont.truetype('./fonts/roboto/Roboto-Regular.ttf', 15)


def write_title(draw, coord, text):
    draw.text(coord, text, font=title_fnt, fill=img_text)


def write(draw, coord, text):
    draw.text(coord, text, font=fnt, fill=img_text)


def image(items, output_img="res_img.png"):
    """creates an image named res_img.png that displays items with icons and costs"""

    # pre-compute icon sizes to get the overall image formatted nicely
    icons = [ item.get_icon() for item in items ]
    max_icon_width = 0
    max_icon_height = 0
    for icon in icons:
        icon_w, icon_h = icon.size
        max_icon_width = max(max_icon_width, icon_w)
        max_icon_height = max(max_icon_height, icon_h)
    x_name = 2 * x_icon + max_icon_width
    
    img_height = (len(items) + 1) * (y_space + max_icon_height) + y_space
    img = Image.new('RGB', (500, img_height), color = img_bg)
    d = ImageDraw.Draw(img)
    y = y_space
    write_title(d, (x_icon, y), "Item")
    write_title(d, (x_cost, y), "Cost")
    for i in range(0,len(items)):
        y += y_space + max_icon_height
        img.paste(icons[i], (x_icon, y))
        write(d, (x_name, y), items[i].name)
        write(d, (x_cost, y), items[i].cost)
    img.save(output_img)


def generate_merch_embed(days=0, items=None, dsf=False, worlds=[]):
    items = merch.get_stock(days) if not items else items
    embed = discord.Embed()
    embed.title = f"Stock for {(datetime.datetime.now()+ datetime.timedelta(days=days)).strftime('%B %d %Y')}:"
    embed.description = ""
    for item in items:
        embed.description += f"\u200b \u200b \u200b \u200b \u200b \u200b" \
            f"{item.emoji} {item.quantity} **{item.name}** - {item.cost[:-4]}k\n\n"
    if days == 0:
        if worlds:
            embed.description += f"Latest worlds from [DSF discord](https://discord.gg/whirlpooldnd): {', '.join(worlds)}"
        embed.description += f"**Tomorrow:** {', '.join([x.name for x in merch.get_stock(1)][1:])}\n"
    if not dsf:
        embed.description += "[Command reference](https://github.com/ragnarak54/DiscordBot)"
    else:
        embed.colour = discord.Color.blue()
    embed.set_footer(text="made by Proclivity (ragnarak54#9413)")
    return embed


def generate_merch_image(days=0, items=None):
    if items:
        image(items)
    elif days == 0:
        image(merch.get_stock(days))
    elif days == 1:
        image(merch.get_stock(days), tomorrow_img)
    else:
        image(merch.get_stock(days), custom_img)

### below this is for testing purposes

test_colors = ['red', 'green', 'blue']
test_sizes = [ (32, 25), (30, 32) ]
    
# def test(items):
#     for i in range(0, len(items)):
#         img = Image.new('RGB', test_sizes[i % 2], color = test_colors[i % 3])
#         img.save(items[i].image_key)
#     image(items)

# test([ merch.MerchItem('img' + str(x) + '.png', 'Item ' + str(x), str(1000000 * x), str(1000000 * x)) for x in range(0, 12) ])
