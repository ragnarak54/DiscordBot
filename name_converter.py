from os import listdir, rename

def convert_names():
    for file in listdir("./images"):
        rename("./images/" + file, "./images/" + file.replace("_", " ").replace("%28", "(").replace("%29", ")").replace("%26", "&"))

convert_names()
