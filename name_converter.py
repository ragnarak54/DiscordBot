from os import listdir, rename
import slpp as lua

def convert_names():
    for file in listdir("./images"):
        rename("./images/" + file, "./images/" + file.replace("_", " ").replace("%28", "(").replace("%29", ")").replace("%26", "&"))


def convert_list():
    str = []
    with open("items.txt", 'r') as f:
        file = f.read()
        i = 0
        while i < len(file):
            if file[i] == '[' and file[i+1] != '[':
                i += 2
                dic = {}
                name = ""
                while file[i] != """'""":
                    name += file[i]
                    i += 1
                dic['name'] = name
                while file[i] != 't':
                    i += 1
                i += 4
                cost = ""
                while file[i+1] != ',':
                    cost += file[i]
                    i += 1
                dic['cost'] = cost
                while file[i] != 'y':
                    i += 1
                i += 4
                quantity = ""
                while file[i] != ',':
                    quantity += file[i]
                    i += 1
                dic["quantity"] = quantity
                while file[i] != """'""":
                    i += 1
                i += 1
                use = ""
                while file[i] != """'""":
                    use += file[i]
                    i += 1

                dic['use'] = use
                str.append(dic)
                print(dic, ",")
            i += 1


convert_list()



