#!/usr/bin/python

"""
From the json theme database, create menu files which are already included in fvwm config.

Also, create png icons in textures directory, to show in the menu along with the description.
"""
import re
import json
import png
import chroma
import sys
import os
from PIL import Image

image_files = []
for root, dirs, files in os.walk(os.path.expanduser("~/.fvwm/textures")):
  for file_name in files:
    fpath = os.path.join(root, file_name)
    if ".thumb" not in fpath:
      name_parts = file_name.split('.')
      file_name = name_parts[0]
      image_files.append((file_name, fpath))
             
color_sets = {}
with open(os.path.expanduser('~/.fvwm/scripts/data/colors.json')) as json_file:
  color_sets = json.load(json_file)
  
def get_rgb(color):
  ccolor = chroma.Color(color)
  r, g, b = ccolor.rgb256
  return [r, g, b]

width = 40
height = 20
color21len = int((width / 2))
color22len = int((width / 2) - 2)
color31len = 16
color32len = 13
color33len = 9
color41len = 13
color42len = 10
color43len = 8
color44len = 7

pixels0 = ['0' * width]

pixels2 = ['0' + '1' * color21len + '2' * color22len + '0'] * (height - 2)
pixels3 = ['0' + '1' * color31len + '2' * color32len + '3' * color33len + '0'] * (height - 2)
pixels4 = ['0' + '1' * color41len + '2' * color42len + '3' * color43len + '4' * color44len + '0'] * (height - 2)

pixels2 = pixels0 + pixels2 + pixels0
pixels3 = pixels0 + pixels3 + pixels0
pixels4 = pixels0 + pixels4 + pixels0

img2 = map(lambda x: map(int, x), pixels2)
img3 = map(lambda x: map(int, x), pixels3)
img4 = map(lambda x: map(int, x), pixels4)


themes_dir = os.path.expanduser('~/.fvwm/themes')
menu_name = 'menu'.encode('ascii', 'ignore')
theme_name = 'thememenu'.encode('ascii', 'ignore')
main_menu = []
theme_menu = []
with open(os.path.expanduser('~/.fvwm/scripts/ColorsMenu'), 'w') as outfile:  
  menu_list = []
  for cs in color_sets:
    name = cs['name'].encode('ascii', 'ignore')
    idx = cs['index']
    
    if name == menu_name or name == theme_name:
      menu_title = cs['menu']
      menu_list.append((0, idx, 'DestroyMenu FvwmThemesMenu{}'.format(menu_title)))
      menu_list.append((0, idx, 'AddToMenu FvwmThemesMenu{} "{}"  Title'.format(menu_title, menu_title)))
      menu_type = cs['name']
      if menu_type == 'menu':
        menu_title = re.sub(r'Main', '', menu_title)
        main_menu.append(menu_title)
      else:
        theme_menu.append(menu_title)
      print('menu_title ', menu_title)
    else:
      num_colors = cs['colors']
        
      # if image exists, convert into png icon and copy, otherwise create an image based on colors 
      name_parts = name.split()
      file_name = name_parts[0]
      name = ''
      for n in name_parts:
        if n[0] != '-':
          name = name + n
      op = name_parts[-1]
      file_path = None
      if op != '-skip':
        for fname, fpath in image_files:
          if name == fname:
            file_path = fpath
            break
          
      if file_path:
        img = Image.open(file_path)
        img.thumbnail((48, 48), Image.ANTIALIAS)
        img.save('{}/{}.png'.format(themes_dir, idx), "PNG") 
      else:
        img = None
        if 'Quat' in cs:
          palette=[[0, 0, 0], get_rgb(cs['Pri']['color']), get_rgb(cs['Sec']['color']), get_rgb(cs['Ter']['color']), get_rgb(cs['Quat']['color'])]
          img = img4
        elif 'Ter' in cs:
          palette=[[0, 0, 0], get_rgb(cs['Pri']['color']) , get_rgb(cs['Sec']['color']), get_rgb(cs['Ter']['color'])]
          img = img3
        elif 'Pri' in cs and 'Sec' in cs:
          palette=[[0, 0, 0], get_rgb(cs['Pri']['color']), get_rgb(cs['Sec']['color'])]
          img = img2
        
        if img: 
          with open('{}/{}.png'.format(themes_dir, idx), 'wb') as fi:
            w = png.Writer(width, height, palette=palette, bitdepth=8)
            w.write(fi, img)
      
      sort_idx = num_colors
      if op == '-nop':
        menu_entry = '+ "%themes/{}.png%" Nop " "'.format(idx)
      else:
        menu_entry = '+ "{}%themes/{}.png%" PipeRead "$[switch_theme] {}; sleep 0.2; FvwmCommand Restart fvwm2"'.format(name, idx, idx)
      menu_list.append((sort_idx, idx, menu_entry))
      

  for cols, idx, m in menu_list:
    outfile.write(m)
    outfile.write('\n')

with open(os.path.expanduser('~/.fvwm/scripts/ColorsMenuList'), 'w') as outfile:  
  for menu in main_menu:
    entry = '+ "Theme {}%menu/themes.xpm%" Popup FvwmThemesMenuMain{}'.format(menu, menu)
    outfile.write(entry)
    outfile.write('\n')
  outfile.write('+ "" Nop')
  outfile.write('\n')
  
with open(os.path.expanduser('~/.fvwm/scripts/ColorsThemeList'), 'w') as outfile:  
  for menu in theme_menu:
    entry = '+ "Theme {}%menu/themes.xpm%" Popup FvwmThemesMenu{}'.format(menu, menu)
    outfile.write(entry)
    outfile.write('\n')
  outfile.write('+ "" Nop')
  outfile.write('\n')
