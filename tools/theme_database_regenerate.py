#!/usr/bin/python3

"""
See theme_database_source for information.

"""
import sys
import os
import re
import json
import chroma

def lighten(color, factor=0.88):
  r, g, b = color.rgb256
  r = (int(r / factor))
  g = (int(g / factor))
  b = (int(b / factor))
  if r > 255:
    r = 255
  if g > 255:
    g = 255
  if b > 255:
    b = 255
  return chroma.Color('#{:02X}{:02X}{:02X}'.format(r, g, b)) 

def darken(color, factor=0.88):
  r, g, b = color.rgb256
  r = (int(r * factor))
  g = (int(g * factor))
  b = (int(b * factor))
  return chroma.Color('#{:02X}{:02X}{:02X}'.format(r, g, b)) 

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


def get_root_color(color):
  r, g, b = color.rgb256
  if r >= g and r >= g: 
    color = chroma.Color('#150000')
  elif g >= r and g >= r: 
    color = chroma.Color('#001500')
  else: 
    color = chroma.Color('#000020')
  return color
  
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

def get_font_color_white_or_black(color):
  r, g, b = color.rgb256
  # Counting the perceptive luminance - human eye favors green color... 
  luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  if luminance > 0.3:
    color = chroma.Color('#111111') #bright colors - black font
  else:
    color = chroma.Color('#dddddd') #dark colors - white font
  return color

def get_secfont_color_white_or_black(color):
  r, g, b = color.rgb256
  # Counting the perceptive luminance - human eye favors green color... 
  luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  if luminance > 0.3:
    color = chroma.Color('#555555') #bright colors - black font
  else:
    color = chroma.Color('#aaaaaa') #dark colors - white font
  return color

def complement(color):
    color = int(str(color)[1:], 16)
    # invert the three bytes
    # as good as substracting each of RGB component by 255(FF)
    comp_color = 0xFFFFFF ^ color
    # convert the color back to hex by prefixing a #
    comp_color = "#%06X" % comp_color
    color = chroma.Color(comp_color)
    return color
  
def get_term_bg_color(color):
  r, g, b = color.rgb256
  if r >= g and r >= g: 
    return "rgba:2000/0000/0000/dddd"
  elif g >= r and g >= r: 
    return "rgba:0000/2000/0000/dddd"
  else: 
    return "rgba:0000/0000/2000/dddd"

# PSTQ + R F G 
def get_color_type(color, index):
  color_type = ''
  color_type = re.findall(r'\(\w?\#', color)
  if len(color_type) > 0:
    color_type = color_type[0][1].upper()
  if color_type.isalpha():
    if color_type == 'P':
      color_type = 'Pri'
    elif color_type == 'S':
      color_type = 'Sec'
    elif color_type == 'T':
      color_type = 'Ter'
    elif color_type == 'Q':
      color_type = 'Quat'
    elif color_type == 'R':
      color_type = 'Root'
    elif color_type == 'F':
      color_type = 'PriFont'
    elif color_type == 'G':
      color_type = 'SecFont'
    elif color_type == 'B':
      color_type = 'Border'
    elif color_type == 'H':
      color_type = 'BorderHighlight'
    elif color_type == 'K':
      color_type = 'Background'
  else:
    if idx == 0:
      color_type = 'Pri'
    elif idx == 1:
      color_type = 'Sec'
    elif idx == 2:
      color_type = 'Ter'
    elif idx == 3:
      color_type = 'Quat'
    elif idx == 4:
      color_type = 'Root'
    elif idx == 5:
      color_type = 'PriFont'
    elif idx == 6:
      color_type = 'SecFont'
    elif idx == 7:
      color_type = 'Border'
    elif idx == 8:
      color_type = 'BorderHighlight'
    elif idx == 9:
      color_type = 'Background'

  return color_type
  
  
color_set_list = []
filepath = 'theme_database_source'
index = 0
with open('theme_database_index', 'w') as outfile:
  with open(filepath) as fp:
    line = fp.readline().strip()
    while line:
      groups = re.findall(r'\(\w?\#\w{8}\)', line)
      line = line.strip()
      print('######################### line ', line)
      if line and line[0] is '#':
        pass
      elif line and line[0] is '@':
        #New Menu
        name = line[1:]
        outfile.write('MENU {}\n'.format(name))
        menu_set = {}
        menu_set['index'] = int(-1)
        if 'Main' in name:
          menu_set['name'] = 'menu'
        else:
          menu_set['name'] = 'thememenu'
        menu_set['menu'] = name
        print('---------------------------------- MENU name ', name)
        color_set_list.append(menu_set)
      elif line and line[0] is not '!':
        print('#########################')
        set_name = re.sub(r'\s\(\w?\#\w{8}\)', '', line)
        color_set = {}
        color_set['name'] = set_name
        color_set['colors'] = len(groups)

        outfile.write(str(index))
        outfile.write(' ')
        outfile.write(set_name)
        outfile.write('\n')
        color_set['index'] = int(index)
        index = index + 1
        
        print('# ', set_name)
        add_second_color = False
        if len(groups) == 1:
          add_second_color = True
          color_set['colors'] = 2
        for idx, g in enumerate(groups):
          color_type = get_color_type(g, idx)
          g = re.sub(r'\(\#', '', g)
          g = re.sub(r'\(\w\#', '', g)
          g = re.sub(r'FF\)', '', g)
          
          colorog = chroma.Color(g)
          color = fix(colorog)
          print('color: ', str(color), ' color_type ', color_type)
          
          color_set[color_type] = {}
          color_set[color_type]['color'] = str(color)
          
          if color_type == 'Pri' or color_type == 'Sec' or color_type == 'Ter' or color_type == 'Quat':
            light = lighten(color)
            dark = darken(color)
            verydark = darken(dark)
            color_set[color_type]['colorog'] = str(colorog)
            color_set[color_type]['light'] = str(light)
            color_set[color_type]['dark'] = str(dark)
            color_set[color_type]['verydark'] = str(verydark)  
            compl = complement(color)
            font = get_font_color_white_or_black(color)
            secfont = get_secfont_color_white_or_black(color)
            color_set[color_type]['complement'] = str(compl)
            color_set[color_type]['font'] = str(font)
            color_set[color_type]['secfont'] = str(secfont)
          
          if color_type == 'Pri':
            root = get_root_color(compl)
            rootcompl = get_root_color(color)
            term_fade = 'rgb:{}/{}/{}'.format(verydark.rgb256[0], verydark.rgb256[1], verydark.rgb256[2])
            term_bg = get_term_bg_color(color)
            term_bg2 = get_term_bg_color(compl)
            color_set[color_type]['root'] = str(root)
            color_set[color_type]['rootcompl'] = str(rootcompl)
            color_set[color_type]['term_fade'] = term_fade
            color_set[color_type]['term_bg'] = term_bg
            color_set[color_type]['term_bg2'] = term_bg2
        if add_second_color == True:
          color_set['Sec'] = color_set['Pri'].copy() 
          del(color_set['Sec']['root'])
          del(color_set['Sec']['rootcompl'])
          del(color_set['Sec']['term_fade'])
          del(color_set['Sec']['term_bg'])
          del(color_set['Sec']['term_bg2'])
          color_set['Sec']['color'] = str(darken(chroma.Color(color_set['Pri']['color']))) 
          color_set['Sec']['font'] = str(darken(chroma.Color(color_set['Pri']['font']))) 
          color_set['Sec']['complement'] = str(darken(chroma.Color(color_set['Pri']['complement']))) 
          color_set['Sec']['light'] = str(darken(chroma.Color(color_set['Pri']['light']))) 
          color_set['Sec']['dark'] = str(darken(chroma.Color(color_set['Pri']['dark']))) 
          color_set['Sec']['verydark'] = str(darken(chroma.Color(color_set['Pri']['verydark']))) 
          add_second_color = False
        color_set_list.append(color_set)
      line = fp.readline().strip()
   
with open(os.path.expanduser('~/.fvwm/scripts/data/colors.json'), 'w') as outfile:
  json.dump(color_set_list, outfile)

