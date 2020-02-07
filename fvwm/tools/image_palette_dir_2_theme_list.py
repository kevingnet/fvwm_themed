#!/usr/bin/python

"""
put palette image files in .fvwm/images
palette images should have a palette with just a few colors, anywhere from 2 to 6, since at most 6 colors will be used
it creates or appends to file theme_database_source_palette
once the tool runs, it will contain text that you can add to theme_database_source and rerun theme_database_regenerate.py
"""

import re
from os import path
import sys
import json
import png
from PIL import Image, ImageOps
import numpy as np
from os import listdir
from os.path import isfile, join

def get_color(col):
  r, g, b = col
  return '#{:02x}{:02x}{:02x}FF'.format(r, g, b)

def chunk(seq, size, groupByList=True):
  """Returns list of lists/tuples broken up by size input"""
  func = tuple
  if groupByList:
      func = list
  return [func(seq[i:i + size]) for i in range(0, len(seq), size)]
  
def getPaletteInRgb(img):
  """
  Returns list of RGB tuples found in the image palette
  :type img: Image.Image
  :rtype: list[tuple]
  """
  assert img.mode == 'P', "image should be palette mode"
  pal = img.getpalette()
  colors = chunk(pal, 3, False)
  return colors
  
img_path = os.path.expanduser('~/.fvwm/images')

file_set = []
onlyfiles = [f for f in listdir(img_path) if isfile(join(img_path, f))]
sortedfiles = list(onlyfiles)
sortedfiles.sort()
for f in sortedfiles:
  filename, file_extension = path.splitext(f)
  file_set.append((filename, file_extension))

files_colors = []
out_file_name = "theme_database_source_palette"
with open(out_file_name, 'a') as outfile:
  for fn, fe in file_set:
    file_name = os.path.expanduser('~/.fvwm/images/{}{}'.format(fn, fe))
    img = Image.open(file_name)
    #p_img = img.convert("P")
    width, height = img.size
    pixel_freqs = {}
    for x in range(0, width):
      for y in range(0, height):
        pixel = img.getpixel((x,y))
        if pixel in pixel_freqs:
          pixel_freqs[(pixel)] = pixel_freqs[pixel] + 1
        else:
          pixel_freqs[pixel] = 1
    pal = getPaletteInRgb(img)
    colors = len(pixel_freqs)
    line = ''
    if colors == 2:
      line = '{} {} colors ({}) ({})'.format(fn, colors, get_color(pal[0]), get_color(pal[1]))
    elif colors == 3:
      line = '{} {} colors ({}) ({}) ({})'.format(fn, colors, get_color(pal[0]), get_color(pal[1]), get_color(pal[2]))
    elif colors == 4:
      line = '{} {} colors ({}) ({}) ({}) ({})'.format(fn, colors, get_color(pal[0]), get_color(pal[1]), get_color(pal[2]), get_color(pal[3]))
    elif colors == 5:
      line = '{} {} colors ({}) ({}) ({}) ({}) ({})'.format(fn, colors, get_color(pal[0]), get_color(pal[1]), get_color(pal[2]), get_color(pal[3]), get_color(pal[4]))
    elif colors == 6: 
      line = '{} {} colors ({}) ({}) ({}) ({}) ({}) ({})'.format(fn, colors, get_color(pal[0]), get_color(pal[1]), get_color(pal[2]), get_color(pal[3]), get_color(pal[4]), get_color(pal[5]))
    else: 
      line = '{} {} colors ({}) ({}) ({}) ({}) ({}) ({}) ({})'.format(fn, colors, get_color(pal[0]), get_color(pal[1]), get_color(pal[2]), get_color(pal[3]), get_color(pal[4]), get_color(pal[5]))
    print(line)
    outfile.write(line)
    outfile.write('\n')
