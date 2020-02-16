import urllib.request
import os
import pandas as pd

folder = "dump"
file = "dump_2019_04_03.json"

full_path = os.path.join(folder, file)

data = pd.read_json(full_path)

all_color_photos = []
for row in data.color_photos:
    row_list = row
    for item in row_list:
        all_color_photos.append(item[0])


all_more_photos = []
for row in data.more_photos:
    row_list = row
    for item in row_list:
        all_more_photos.append(item)


output_folder = "../imgs/akusherstvo/"
os.makedirs(output_folder, exist_ok=True)
with open(output_folder + "list.txt", "w" ) as f:
    for line in all_color_photos:
        f.write(line + "\n")
    for line in all_more_photos:
        f.write(line + "\n")

#urllib.request.urlretrieve ("http://www.example.com/songs/mp3.mp3", "mp3.mp3")