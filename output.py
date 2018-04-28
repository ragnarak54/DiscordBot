# https://code-maven.com/create-images-with-python-pil-pillow
# https://stackoverflow.com/questions/2563822/how-do-you-composite-an-image-onto-another-image-with-pil-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
from PIL import Image, ImageDraw, ImageFont

x_img = 20
x_cost = 300
y_space = 25
fnt = ImageFont.truetype('./fonts/roboto/Roboto-Regular.ttf', 24)

def image(items):
    """creates an image named res_img.png that displays items with icons and costs
    items = a list of tuples (image_name, item_name, item_cost)"""
    
    imgs = [ Image.open(item[0], 'r') for item in items ]
    max_img_width = 0
    max_img_height = 0
    for img in imgs:
        img_w, img_h = img.size
        max_img_width = max(max_img_width, img_w)
        max_img_height = max(max_img_height, img_h)
    
    img_height = len(items) * (y_space + max_img_height) + y_space
    img = Image.new('RGB', (500, img_height), color = 'white')
    d = ImageDraw.Draw(img)
    y = y_space
    for i in range(0,len(items)):
        img.paste(imgs[i], (x_img, y))
        d.text((2 * x_img + max_img_width, y), items[i][1], font=fnt, fill=(0,0,0))
        d.text((x_cost, y), str(items[i][2]), font=fnt, fill=(0,0,0))
        y += y_space + max_img_height
    img.save('res_img.png')

### below this is for testing purposes

test_colors = ['red', 'green', 'blue']
test_sizes = [ (32, 25), (30, 32) ]
    
def test(items):
    for i in range(0, len(items)):
        img = Image.new('RGB', test_sizes[i % 2], color = test_colors[i % 3])
        img.save(items[i][0])
    image(items)

# test([ ('img' + str(x) + '.png', 'Item ' + str(x), 2 * x) for x in range(0, 12) ])
