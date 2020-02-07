#!/usr/bin/python3
"""
Experimental tool to create theme menu lists to be added to the theme menu in fvwm. It prints a log of stats as it runs.

- It takes as a parameter the file path to an image file, it supports PNG, should work with JPEG
- There are two algorithms involved, KMeans from sklearn.cluster and another one that relies on pixel frequencies
  and other color stats, it tries to weed out the background color, so the theme can use the more interesting colors.
- it creates or appends to file theme_database_source_algorithms
- once the tool runs, it will contain text that you can add to theme_database_source and rerun theme_database_regenerate.py
- the tool creates 3 files based on the image, and these do not get deleted automatically:
  1) _reduced.png, a file with the original image with reduced color space
  2) _colors.png, a file that shows the selected colors by the one algorithm
  2) _kcolors.png, a file that shows the selected colors by the kmeans algorithm
"""
import sys
from PIL import Image
from PIL import ImageOps
import png
import chroma
import cv2
from sklearn.cluster import KMeans
import re

class DominantColors:

  CLUSTERS = None
  IMAGE = None
  COLORS = None
  LABELS = None

  def __init__(self, image, clusters=3):
    self.CLUSTERS = clusters
    self.IMAGE = image
    
  def dominantColors(self):

    #read image
    img = cv2.imread(self.IMAGE)
    
    #convert to rgb from bgr
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
    #reshaping to a list of pixels
    img = img.reshape((img.shape[0] * img.shape[1], 3))
    
    #save image after operations
    self.IMAGE = img
    
    #using k-means to cluster pixels
    kmeans = KMeans(n_clusters = self.CLUSTERS)
    kmeans.fit(img)
    
    #the cluster centers are our dominant colors.
    self.COLORS = kmeans.cluster_centers_
    
    #save labels
    self.LABELS = kmeans.labels_
    
    #returning after converting to integer from float
    return self.COLORS.astype(int)

      
cwidth = 160
cheight = 100
imgpixels = [ '0,' * 20 + \
           '1,' * 20 + \
           '2,' * 20 + \
           '3,' * 20 + \
           '4,' * 20 + \
           '5,' * 20 + \
           '6,' * 20 + \
           '7,' * 20 ] * (cheight)

all_pixels = []
row_pixels = []
for i in imgpixels:
  p = i.split(',')
  for n in p:
    if n:
      row_pixels.append(int(n))
    else:
      all_pixels.append(row_pixels)
      row_pixels = []
img = map(lambda x: map(int, x), all_pixels)

def normalize(color):
  sat = color.hls[1]
  if sat < 0.17:
    color.hls = (color.hls[0], 0.17, color.hls[2])
  return color

def lightenrgb(r, g, b, factor=0.88):
  r = (int(r / factor))
  g = (int(g / factor))
  b = (int(b / factor))
  if r > 255:
    r = 255
  if g > 255:
    g = 255
  if b > 255:
    b = 255
  return (r, g, b)

def darkenrgb(r, g, b, factor=0.88):
  r = (int(r * factor))
  g = (int(g * factor))
  b = (int(b * factor))
  return (r, g, b)


def get_lum(r, g, b):
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255

def fix(color):
  return chroma.Color(color)
  r, g, b = color.rgb256
  lum = get_lum(r, g, b)
  i = 0
  if lum > 0.8: #light color, darken font
    while i < 50 and lum > 0.8:
      r, g, b = darkenrgb(r, g, b, 0.75)
      lum = get_lum(r, g, b)
      i += 1
  elif lum < 0.2: # dark color, lighten font
    while i < 50 and lum < 0.2:
      r, g, b = lightenrgb(r, g, b, 0.98)
      lum = get_lum(r, g, b)
      i += 1
  return chroma.Color('#{:02X}{:02X}{:02X}'.format(r, g, b)) 


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
  
def round_hls(color):
  #print('hls: ', color.hls)
  h, l, s, w = color.hls
  return '{}\t{}\t{}\t'.format(h, round(l, 2), round(s, 2))
  
image_file_name = sys.argv[1]
if image_file_name[0] == '.':
  image_file_name = image_file_name[2:]
  
if '_reduced' in image_file_name or '_colors' in image_file_name or '_kcolors' in image_file_name:
  sys.exit()
print('image_file_name: ', image_file_name)
file_parts = image_file_name.split('.')
new_image_file_name = file_parts[0] + '_reduced.png'
colors_image_file_name = file_parts[0] + '_colors.png'
kcolors_image_file_name = file_parts[0] + '_kcolors.png'
print('new_image_file_name: ', new_image_file_name)
image = Image.open(image_file_name)

basename = sys.argv[1].split('/')[-1].split('.')[0]

try:
  new_image = ImageOps.posterize(image, 3)
except:
  new_image = image
new_image = new_image.convert('P', palette=Image.ADAPTIVE, colors=16)

width, height = new_image.size
pixel_freqs = {}
for x in range(0, width):
  for y in range(0, height):
    pixel = new_image.getpixel((x,y))
    if pixel in pixel_freqs:
      pixel_freqs[(pixel)] = pixel_freqs[pixel] + 1
    else:
      pixel_freqs[pixel] = 1
pal = getPaletteInRgb(new_image)
colors = len(pixel_freqs)
new_image.save(new_image_file_name)


pixfreq = []
freqs_pixel = {}
for i in range(0, 16):
  pixfreq.append(pixel_freqs[i])
  freqs_pixel[pixel_freqs[i]] = i
pixfreq.sort()
background_pixels = pixfreq.pop()
background_pixel_idx = freqs_pixel[background_pixels]
print('pixfreq: ', pixfreq)
print('freqs_pixel: ', freqs_pixel)
print('background_pixels: ', background_pixels)
print('background_pixel_idx: ', background_pixel_idx)

print('colors: ', colors)
pixel_count = width * height
non_background_pixels = pixel_count - background_pixels
print('pixel count: ', pixel_count)
print('non_background_pixels: ', non_background_pixels)
chromas = []
color_queue = []
for i in range(0, colors):
  if background_pixel_idx == i:
    continue
  pixel = fix(chroma.Color(get_color(pal[i])))
  if pixel.hls[1] < 0.15:
    color_queue.append((pixel_freqs[i], pixel, i))
    continue
  if pixel.hls[2] < 0.25:
    color_queue.append((pixel_freqs[i], pixel, i))
    continue
  chromas.append((pixel_freqs[i], pixel, i))
  

"""
SELECT COLORS:
- remove background, the highest frequency
- remove those with low frequency, calculate average freq
"""

bgpixel = chroma.Color(get_color(pal[background_pixel_idx]))
print('sat: ',  round(bgpixel.hls[2], 2), ' lum: ',  round(bgpixel.hls[1], 2), ' hue: ',  bgpixel.hls[0], '\tpixel: ', bgpixel.rgb256[0], ',', bgpixel.rgb256[1], ',', bgpixel.rgb256[2])

background_pixel = bgpixel

palette = []
chromas.sort()
chromas2 = []
for f, pix, i in reversed(chromas):
  chromas2.append((f, pix, i))

prev_hue = 0
for f, p, i in chromas2:
  hue = p.hls[0]
  if abs(prev_hue - hue) < 10:
    prev_hue = hue
    color_queue.insert(0, (f, p, i))
    continue
  (r, g, b, s) = p.rgb256
  palette.append([r, g, b])
  prev_hue = hue

while len(palette) < 9:
  f, p, i = color_queue.pop(0)
  chromas2.append((f, p, i))
  (r, g, b, s) = p.rgb256
  palette.append([r, g, b])
print(palette)

for f, p, i in chromas2:
  (h, l, s, t) = p.hls
  (r, g, b, t) = p.rgb256
  print('i: ',  i, '\tf: ',  f, '\tsat: ',  round(s, 2), ' lum: ',  round(l, 2), ' hue: ',  round(h, 2), '\tpixel: ', r, ',', g, ',', b)
                    
print(background_pixel.rgb256)

(bgr, bgg, bgb, t) = background_pixel.rgb256
def is_similar(r, g, b, threshold=3):
  if abs(bgr - r) > threshold:
    return False
  if abs(bgg - g) > threshold:
    return False
  if abs(bgb - b) > threshold:
    return False
  print('FOUND SIMILAR BACKGROUND')
  return True

clusters = 11
dc = DominantColors(new_image_file_name, clusters) 
colors = dc.dominantColors()
kpalette = []

i = 0
for (r, g, b) in colors:
  if is_similar(r, g, b):
    continue
  if i == 8:
    break
  pixel = fix(chroma.Color(get_color([r, g, b])))
  (r, g, b, t) = pixel.rgb256
  kpalette.append([r, g, b])
  i = i + 0
  
with open(kcolors_image_file_name, 'wb') as fi:
  w = png.Writer(cwidth, cheight, palette=kpalette, bitdepth=8)
  w.write(fi, all_pixels)

with open(colors_image_file_name, 'wb') as fi:
  w = png.Writer(cwidth, cheight, palette=palette, bitdepth=8)
  w.write(fi, all_pixels)
    
def get_color(col):
  r, g, b = col
  return '#{:02x}{:02x}{:02x}FF'.format(r, g, b)

out_file_name = "theme_database_source_algorithms"
with open(out_file_name, 'a') as outfile:
    line0 = '{} -nop'.format(basename)
    line1 = '{} ({}) ({}) ({}) ({}) -skip'.format(basename, get_color(palette[0]), get_color(palette[1]), get_color(palette[2]), get_color(palette[3]))
    line2 = '{} ({}) ({}) ({}) ({}) -skip'.format(basename, get_color(palette[4]), get_color(palette[5]), get_color(palette[6]), get_color(palette[7]))
    line3 = '{} ({}) ({}) ({}) ({}) -skip'.format(basename, get_color(kpalette[0]), get_color(kpalette[1]), get_color(kpalette[2]), get_color(palette[3]))
    line4 = '{} ({}) ({}) ({}) ({}) -skip'.format(basename, get_color(kpalette[4]), get_color(kpalette[5]), get_color(kpalette[6]), get_color(kpalette[7]))
    print(line0)
    outfile.write(line0)
    outfile.write('\n')
    outfile.write(line1)
    outfile.write('\n')
    outfile.write(line2)
    outfile.write('\n')
    outfile.write(line3)
    outfile.write('\n')
    outfile.write(line4)
    outfile.write('\n')
