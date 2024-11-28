import json
from add_data import add_data

with open('lessondata.json', 'r') as file:
    data = json.load(file)

add_data(data)
print("done")
