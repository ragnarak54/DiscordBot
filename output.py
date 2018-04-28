# https://code-maven.com/create-images-with-python-pil-pillow
# https://stackoverflow.com/questions/2563822/how-do-you-composite-an-image-onto-another-image-with-pil-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
from PIL import Image, ImageDraw, ImageFont

x_img = 20
x_item = 60
x_cost = 250
y_space = 20
fnt = ImageFont.truetype('./fonts/roboto/Roboto-Regular.ttf', y_space)

def image(items):
    """items = a list of tuples (image_name, item_name, item_cost)"""
    img_height = len(items) * y_space * 2 + y_space
    img = Image.new('RGB', (300,img_height), color = 'white')
    d = ImageDraw.Draw(img)
    y = y_space
    for item in items:
        item_img = Image.open(item[0], 'r')
        img.paste(item_img, (x_img, y))
        d.text((x_item, y), item[1], font=fnt, fill=(0,0,0))
        d.text((x_cost, y), str(item[2]), font=fnt, fill=(0,0,0))
        y += 40
    img.save('res_img.png')
    
image([('img1.png', 'Item 1', 2), ('img2.png', 'Item 2', 4)])
