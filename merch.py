from PIL import Image

images_dir = "images/"

class MerchItem:    
    def __init__(self, image_key, name, cost, quantity, use):
        self.image_key = image_key
        self.name = name
        self.cost = cost
        self.quantity = quantity
        self.use = use
    def get_icon(self):
        return Image.open(images_dir + self.image_key, 'r')
