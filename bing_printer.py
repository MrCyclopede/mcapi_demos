
import time
import math
import PIL

import numpy as np
import json

import mc_api as mc
from PIL import Image


from bing_image_downloader import downloader

import glob



HEIGHT = 120
WIDTH = 120

rcon = mc.connect("localhost", "test")

def get_closest_color(pixel,  block_palette):
    best_delta = 9999999
    last_stddev = 999999
    block_name = None
    for block in block_palette["averages"]:
        if "shulker" in block["image"]:
            continue
        if "side" in block["image"] or "bottom" in block["image"] or "top" in block["image"] or "front" in block["image"]:
            continue
        delta = math.sqrt(
            (pixel[0] - block["rgba"][0]) ** 2
            + (pixel[1] - block["rgba"][1]) ** 2
            + (pixel[2] - block["rgba"][2]) ** 2
        )
        # if delta < best_delta and block["stddev"] < last_stddev:
        if delta < best_delta:
            best_delta = delta
            last_stddev = block["stddev"]
            block_name = block["image"][:-4]
    return block_name
 
with open("colors.json") as f:
    block_palette = json.load(f)

def reset_zone():
    mc.post("say Reset start")
    for i in range(0, 4):
        mc.set_zone([(0, i, 0), (WIDTH, i, HEIGHT)], "grass_block")
    for i in range(4, 100):
        mc.set_zone([(0, i, 0), (WIDTH, i, HEIGHT)], "air")
    mc.post("say Reset Done")

def get_palette():
    n = 8
    palette = [[[0 for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for i in range(0, 8):
        for j in range(0, 8):
            for k in range(0, 8):

                block = get_closest_color((i * 32, j * 32, k * 32), block_palette)
                # block = block.replace("_bottom", "")
                # block = block.replace("_top", "")
                # block = block.replace("_side", "")
                # block = block.replace("_front", "")                
                palette[i][j][k] = block
    return palette


palette = get_palette()

def color_picker(pixel):

    r = int(pixel[0] / 32)
    g = int(pixel[1] / 32)
    b = int(pixel[2] / 32)
    return palette[r][g][b]

fruits=['apples','oranges','bananas','mangoes','grapes','strawberry']
for name in fruits:

    # name = input()
    downloader.download(name, limit=1,  output_dir='out', adult_filter_off=True, force_replace=False, timeout=60, verbose=True)

    extension = glob.glob(f"out/{name}/*")[0].split("/")[-1].split(".")[-1]
    print(extension)
    im = Image.open(f"out/{name}/Image_1.{extension}")
    image = im.transpose(PIL.Image.FLIP_LEFT_RIGHT)
    image = image.resize((WIDTH,HEIGHT))
    converted_image = image.convert('RGB')
        
    pixels = list(converted_image.getdata())
    width, height = converted_image.size
    pixels = [pixels[i * width : (i + 1) * width] for i in range(height)]


    block_list = []


    x = 0
    passed = 0
    for line in pixels:
        x += 1
        y = 0
        for pixel in line:
            passed += 1

            y += 1
            block = color_picker(pixel)
            # mc.post(f"tp funyrom {x} 50 {y}")
            ret = mc.set_block((x, 15, y), block)            
            
