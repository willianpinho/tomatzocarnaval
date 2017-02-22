#!/usr/bin/python
# coding: utf-8

import os
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps
from flask.ext.thumbnails import Thumbnail
from pprint import pprint
import math


with open('blocos.json') as data_file:    
    blocos = json.load(data_file)

fonts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts/roboto_slab')
img = Image.open("fundo_carna_tomatzo.png")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(os.path.join(fonts_path, 'RobotoSlab-Regular.ttf'), 24)

user_img = Image.open("user_img.jpg")
size = 120,120
position =  (322,32)
user_img = user_img.resize(size,Image.ANTIALIAS)

croped_img = get_thumbnail(user_img, '100x100', crop='center', quality=99)


img.paste(user_img,position)

bloco_name = "Menino de Ceilandia - Ceilandia Ce."
draw.text((220, 325),blocos[0]["nome"],(0,0,0),font=font)
draw.text((220, 370),bloco_name.upper(),(0,0,0),font=font)
draw.text((220, 415),bloco_name.upper(),(0,0,0),font=font)
draw.text((220, 457),bloco_name.upper(),(0,0,0),font=font)
draw.text((220, 502),bloco_name.upper(),(0,0,0),font=font)



img.save('sample-out.png')	


