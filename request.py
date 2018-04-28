import requests # pip install requests
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_stock = False
        self.stock_table = False
    def handle_starttag(self, tag, attrs):
        if self.found_stock and tag == "table":
            self.stock_table = True
    def handle_endtag(self, tag):
        if self.stock_table and tag == "table":
            print("end")
            self.found_stock = False
            self.stock_table = False
    def handle_data(self, data):
        if data == "Current stock":
            print("found section")
            self.found_stock = True
        if self.stock_table:
            print(data)

parser = MyHTMLParser()
r = requests.get('http://runescape.wikia.com/wiki/Travelling_Merchant%27s_Shop')
parser.feed(r.text)
