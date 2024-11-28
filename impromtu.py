import json
from add_data import add_data

with open('lessondata.json', 'r') as file:
    c = json.load(file)

add_data(c)
print("done")
