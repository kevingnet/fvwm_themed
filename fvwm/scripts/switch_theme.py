#!/usr/bin/python3

"""
Switches to another theme from fvwm, after themeing has been configured. It's a work in progress and other configuration
would be necessary.
Here is how it works, what it does:
1) .fvwm/scripts/data/colors.json is read. It contains color sets for the seleted theme to switch to.
2) The name of the theme is resolved from an index, or it was already passed in to this tool
3) Some colors do not seem to get along with each other well, so it attemps feebly to change them as it sees fit.
4) A set of template files for gtk and kde are used so that we can change their colors as well. New ones will be written to 
   a location in ~/.themes/pytheme (pytheme, is a directory included in the package which must be copied there) and there are other
   locations that this tool will overwrite: /usr/share/color-schemes/Oxygen.colors AND ~/.local/share/color-schemes/pytheme.colors
   so make sure you backup. Notice that the Oxygen theme was selected. You may be able to change it to one of your liking, and then 
   you would have to modify this tool to match. 
5) A file with color set information for the theme that fvwm will use will be created/updated in .fvwm/scripts/fvwm_theme.config
6) It creates a couple of PNG files that are used to show some effects in the windows title in fvwm
7) In order for the automatic switch of your kde and gnome environments, you must have /usr/bin/lookandfeeltool, so that the switch
   happens automatically there as well and not just in fvwm.

NOTE: It's a work in progress and the code needs a lot of cleanup and design work, it's something that sort of grew out of need/want.
Notice that you would also have to install some python libraries and an explanation on how is beyond scope, so unfortunately you might
have to know some python or at least how to install stuff. You can also look up how to do that. 

"""

from os import path
import re
import sys
import json
import png
import string 
from shutil import copyfile
import subprocess
import chroma

SkipImageCreation = False

# resolve image creation flag
if len(sys.argv) >= 3:
  skip = sys.argv[2]
  if skip == '-SkipImageCreation':
    print('SkipImageCreation')
    SkipImageCreation = True
SkipImageCreation = False

# read color database
color_sets = []
with open(path.expanduser('~/.fvwm/scripts/data/colors.json')) as json_file:
  color_sets = json.load(json_file)
 
# resolve theme index or name to switch to
index = -1
try:
  index = int(sys.argv[1])
  for cs in color_sets:
    if cs['index'] == index:
      name = cs['name']
      color_set = cs
      break
except:
  name = sys.argv[1]
  try:
    color_set = color_sets[name]
  except:
    for cs in color_sets:
      if name in cs:
        name = cs
        color_set = color_sets[name]
        break

def get_rgb(color):
  ccolor = chroma.Color(color)
  r, g, b = ccolor.rgb256
  return [r, g, b]

def get_rgb_decimal(hex_color):
  rgb = get_rgb(hex_color)
  return '{},{},{}'.format(rgb[0], rgb[1], rgb[2])

def lighten(color, factor=0.98):
  ccolor = chroma.Color(color)
  r, g, b = ccolor.rgb256
  r = (int(r / factor))
  g = (int(g / factor))
  b = (int(b / factor))
  if r > 255:
    r = 255
  if g > 255:
    g = 255
  if b > 255:
    b = 255
  return '#{:02X}{:02X}{:02X}'.format(r, g, b)

def darken(color, factor=0.98):
  ccolor = chroma.Color(color)
  r, g, b = ccolor.rgb256
  r = (int(r * factor))
  g = (int(g * factor))
  b = (int(b * factor))
  return '#{:02X}{:02X}{:02X}'.format(r, g, b)

def normalize(color):
  bghlSat = color.hls[1]
  if bghlSat < 0.25:
    color.hls = (color.hls[0], 0.25, color.hls[2])
    bghlSat = color.hls[1]
  bghlLum = color.hls[2]
  if bghlLum > 0.8:
    color.hls = (color.hls[0], color.hls[1], 0.8)
    bghlLum = color.hls[2]
  if bghlLum < 0.25:
    color.hls = (color.hls[0], color.hls[1], 0.25)
    bghlLum = color.hls[2]
  return color

def write_title_images(pri_color, sec_color):
  #print('write_title_images')
  imgbg = [[0, 1], 
          [1, 0]]

  imgt = [[0, 1, 2],
          [1, 2, 1], 
          [2, 0, 1]]

  palette_t=[pri_color, sec_color]
  palette_t2=[pri_color, sec_color, sec_color]

  title_image_path = path.expanduser('~/.fvwm/themes')
  with open('{}/t.png'.format(title_image_path), 'wb') as fi:
    w = png.Writer(2, 2, palette=palette_t, bitdepth=1)
    w.write(fi, imgbg)
  with open('{}/t2.png'.format(title_image_path), 'wb') as fi:
    w = png.Writer(3, 3, palette=palette_t2, bitdepth=8)
    w.write(fi, imgt)

def write_value(f, label, value):
  f.write(label)
  f.write(str(value))
  f.write('\n')
  
def write_color(f, label, key, color):
  f.write(label)
  f.write(str(color_set[color][key]))
  f.write('\n')
  
def write_color_header(f, color):
  write_color(f, '#{} color '.format(color), 'color', color)
  write_color(f, '#{} complement '.format(color), 'complement', color)
  write_color(f, '#{} font '.format(color), 'font', color)
  write_color(f, '#{} light '.format(color), 'light', color)
  write_color(f, '#{} dark '.format(color), 'dark', color)
  write_color(f, '#{} verydark '.format(color), 'verydark', color)
  f.write('\n')

def write_color_values(order, theme_colors, f):
  #print('write_color_values for: ', order)
  if order in ['Pri', 'Sec']:
    write_color_header(f, order)
  write_value(f, 'SetEnv {}Font '.format(order), theme_colors.get('{}Font'.format(order)))
  write_value(f, 'SetEnv {}VDark '.format(order), theme_colors.get('{}VDark'.format(order)))
  write_value(f, 'SetEnv {}Dark '.format(order), theme_colors.get('{}Dark'.format(order)))
  write_value(f, 'SetEnv {}Light '.format(order), theme_colors.get('{}Light'.format(order)))
  write_value(f, 'SetEnv {}Color '.format(order), theme_colors.get('{}Color'.format(order)))
  write_value(f, 'SetEnv {}Compl '.format(order), theme_colors.get('{}Compl'.format(order)))
  f.write('\n')

class ThemeColors(object):
  BACKGROUNDALT = '242,240,212'
  BACKGROUND = '252,250,222'
  LTGRAY = '222,222,222'
  DKGRAY = '77,77,77'
  GRAY = '111,111,111'
  LTBLUE = '155,199,222'
  DKBLUE = '11,22,111'
  BLUE = '44,178,222'
  BLACK = '0,0,0'
  WHITE = '233,233,233'
  PINK = '222,111,222'
  GREEN = '22,144,22'
  PURPLE = '88,11,88'
  YELLOW = '255,222,0'
  RED = '111,11,11'
  ORANGE = '255,119,0'  
  GTKBACKGROUNDALT = '#e0e0d0'
  GTKBACKGROUND = '#eeeedd'

  def __init__(self, color_set):
    #print('ThemeColors')
    color1 = color_set['Pri']
    color2 = color_set['Sec']
    
    self.color = {}
    
    if 'PriFont' in color_set:
      self.color['FontColor'] = color_set['PriFont']['color']
    else:
      self.color['FontColor'] = color1['color']

    if 'Background' in color_set:
      self.color['BackgroundColor'] = color_set['Background']['color']
      self.color['BackgroundAltColor'] = darken(self.color['BackgroundColor'])
      ThemeColors.GTKBACKGROUND = self.color['BackgroundColor']
      ThemeColors.GTKBACKGROUNDALT = self.color['BackgroundAltColor']
      self.color['BackgroundColor'] = get_rgb_decimal(self.color['BackgroundColor'])
      self.color['BackgroundAltColor'] = get_rgb_decimal(self.color['BackgroundAltColor'])
    else:
      self.color['BackgroundColor'] = ThemeColors.BACKGROUND
      self.color['BackgroundAltColor'] = ThemeColors.BACKGROUNDALT
    
    self.color['PriColor'] = color1['color']
    self.color['PriFont'] = color1['font']
    self.color['PriCompl'] = color1['complement']
    self.color['PriLight'] = color1['light']
    self.color['PriDark'] = color1['dark']
    self.color['PriVDark'] = color1['verydark']
    self.color['SecColor'] = color2['color']
    self.color['SecFont'] = color2['font']
    self.color['SecCompl'] = color2['complement']
    self.color['SecLight'] = color2['light']
    self.color['SecDark'] = color2['dark']
    self.color['SecVDark'] = color2['verydark']
    if 'Ter' in color_set:
      color3 = color_set['Ter']
      self.color['TerColor'] = color3['color']
      self.color['TerFont'] = color3['font']
      self.color['TerCompl'] = color3['complement']
      self.color['TerLight'] = color3['light']
      self.color['TerDark'] = color3['dark']
      self.color['TerVDark'] = color3['verydark']
    else:
      self.color['TerColor'] = darken(self.color['SecColor'])
      self.color['TerFont'] = darken(self.color['SecFont'])
      self.color['TerCompl'] = darken(self.color['SecCompl'])
      self.color['TerLight'] = darken(self.color['SecLight'])
      self.color['TerDark'] = darken(self.color['SecDark'])
      self.color['TerVDark'] = darken(self.color['SecVDark'])
    if 'Quat' in color_set:
      color4 = color_set['Quat']
      self.color['QuatColor'] = color4['color']
      self.color['QuatFont'] = color4['font']
      self.color['QuatCompl'] = color4['complement']
      self.color['QuatLight'] = color4['light']
      self.color['QuatDark'] = color4['dark']
      self.color['QuatVDark'] = color4['verydark']
    else:
      self.color['QuatColor'] = lighten(self.color['SecColor'])
      self.color['QuatFont'] = lighten(self.color['SecFont'])
      self.color['QuatCompl'] = lighten(self.color['SecCompl'])
      self.color['QuatLight'] = lighten(self.color['SecLight'])
      self.color['QuatDark'] = lighten(self.color['SecDark'])
      self.color['QuatVDark'] = lighten(self.color['SecVDark'])

    self.color['FontColorDec'] = get_rgb_decimal(self.color['FontColor'])
    self.color['PriColorDec'] = get_rgb_decimal(self.color['PriColor'])
    self.color['PriFontDec'] = get_rgb_decimal(self.color['PriFont'])
    self.color['PriComplDec'] = get_rgb_decimal(self.color['PriCompl'])
    self.color['PriLightDec'] = get_rgb_decimal(self.color['PriLight'])
    self.color['PriDarkDec'] = get_rgb_decimal(self.color['PriDark'])
    self.color['PriVDarkDec'] = get_rgb_decimal(self.color['PriVDark'])
    self.color['SecColorDec'] = get_rgb_decimal(self.color['SecColor'])
    self.color['SecFontDec'] = get_rgb_decimal(self.color['SecFont'])
    self.color['SecComplDec'] = get_rgb_decimal(self.color['SecCompl'])
    self.color['SecLightDec'] = get_rgb_decimal(self.color['SecLight'])
    self.color['SecDarkDec'] = get_rgb_decimal(self.color['SecDark'])
    self.color['SecVDarkDec'] = get_rgb_decimal(self.color['SecVDark'])
    self.color['TerColorDec'] = get_rgb_decimal(self.color['TerColor'])
    self.color['TerFontDec'] = get_rgb_decimal(self.color['TerFont'])
    self.color['TerComplDec'] = get_rgb_decimal(self.color['TerCompl'])
    self.color['TerLightDec'] = get_rgb_decimal(self.color['TerLight'])
    self.color['TerDarkDec'] = get_rgb_decimal(self.color['TerDark'])
    self.color['TerVDarkDec'] = get_rgb_decimal(self.color['TerVDark'])
  
  def get(self, name):
    if name not in self.color:
      return ''
    return self.color[name]
  
class ThemeKDE(object):

  def __init__(self):
    self.kde_colors = ''
    self.kde_colors_pytheme = ''
    with open(path.expanduser('~/.fvwm/scripts/data/pytheme.colors')) as f:
      self.kde_colors = f.read()
    #print('ThemeKDE kde_colors: ', self.kde_colors)

  def write(self):
    #print('ThemeKDE write()')
    # write kde theme
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    valid_file_name = ''.join(c for c in name if c in valid_chars)
    out_file_name = path.expanduser("~/.local/share/color-schemes/{}.colors".format(valid_file_name))
    #print('ThemeKDE color-schemes out_file_name: ', out_file_name)
    with open(out_file_name, 'w') as outfile:
      outfile.write(self.kde_colors)
    out_file_name = path.expanduser("~/.local/share/color-schemes/pytheme.colors")
    #print('ThemeKDE pytheme.colors out_file_name: ', out_file_name)
    with open(out_file_name, 'w') as outfile:
      outfile.write(self.kde_colors_pytheme)
    copyfile(out_file_name, '/usr/share/color-schemes/Oxygen.colors')

  def replace(self, theme_colors, name):
    #print('ThemeKDE replace()')
    self.kde_colors = self.kde_colors.replace('LTGRAY', ThemeColors.LTGRAY)  
    self.kde_colors = self.kde_colors.replace('DKGRAY', ThemeColors.DKGRAY)  
    self.kde_colors = self.kde_colors.replace('GRAY', ThemeColors.GRAY)  
    self.kde_colors = self.kde_colors.replace('LTBLUE', ThemeColors.LTBLUE)  
    self.kde_colors = self.kde_colors.replace('DKBLUE', ThemeColors.DKBLUE)  
    self.kde_colors = self.kde_colors.replace('BLUE', ThemeColors.BLUE)  
    self.kde_colors = self.kde_colors.replace('BLACK', ThemeColors.BLACK)  
    self.kde_colors = self.kde_colors.replace('WHITE', ThemeColors.WHITE)  
    self.kde_colors = self.kde_colors.replace('PINK', ThemeColors.PINK)  
    self.kde_colors = self.kde_colors.replace('GREEN', ThemeColors.GREEN)  
    self.kde_colors = self.kde_colors.replace('PURPLE', ThemeColors.PURPLE)  
    self.kde_colors = self.kde_colors.replace('YELLOW', ThemeColors.YELLOW)  
    self.kde_colors = self.kde_colors.replace('RED', ThemeColors.RED)  

    self.kde_colors = re.sub('BACKGROUND', theme_colors.get('BackgroundColor'), self.kde_colors)
    self.kde_colors = re.sub('BACKGROUNDALT', theme_colors.get('BackgroundAltColor'), self.kde_colors)
    
    self.kde_colors = re.sub('FontColor', theme_colors.get('FontColorDec'), self.kde_colors)
    self.kde_colors = re.sub('ViewBGAlt', ThemeColors.BACKGROUNDALT, self.kde_colors)
    self.kde_colors = re.sub('ViewBG', ThemeColors.BACKGROUND, self.kde_colors)
    self.kde_colors = re.sub('ViewFGAct', ThemeColors.ORANGE, self.kde_colors)
    self.kde_colors = re.sub('ViewFGInact', ThemeColors.LTGRAY, self.kde_colors)
    self.kde_colors = re.sub('ViewFG', theme_colors.get('PriFontDec'), self.kde_colors)
    self.kde_colors = re.sub('ViewDecFocus', theme_colors.get('TerColorDec'), self.kde_colors)
    self.kde_colors = re.sub('ViewDecHover', theme_colors.get('TerLightDec'), self.kde_colors)
    
    self.kde_colors = re.sub('BtnBGAlt', theme_colors.get('SecLightDec'), self.kde_colors)
    self.kde_colors = re.sub('BtnBG', theme_colors.get('SecColorDec'), self.kde_colors)
    self.kde_colors = re.sub('BtnFGAct', theme_colors.get('SecDarkDec'), self.kde_colors)
    self.kde_colors = re.sub('BtnFGInact', theme_colors.get('SecLightDec'), self.kde_colors)
    self.kde_colors = re.sub('BtnFG', theme_colors.get('SecFontDec'), self.kde_colors)
    self.kde_colors = re.sub('BtnDecFocus', theme_colors.get('TerColorDec'), self.kde_colors)
    self.kde_colors = re.sub('BtnDecHover', theme_colors.get('TerLightDec'), self.kde_colors)
    
    self.kde_colors = re.sub('WinBGAlt', theme_colors.get('PriLightDec'), self.kde_colors)
    self.kde_colors = re.sub('WinBG', theme_colors.get('PriColorDec'), self.kde_colors)
    self.kde_colors = re.sub('WinFGAct', theme_colors.get('PriDarkDec'), self.kde_colors)
    self.kde_colors = re.sub('WinFGInact', theme_colors.get('PriVDarkDec'), self.kde_colors)
    self.kde_colors = re.sub('WinFG', theme_colors.get('PriFontDec'), self.kde_colors)
    self.kde_colors = re.sub('WinDecFocus', theme_colors.get('TerColorDec'), self.kde_colors)
    self.kde_colors = re.sub('WinDecHover', theme_colors.get('TerLightDec'), self.kde_colors)
    
    self.kde_colors = re.sub('SelBGAlt', theme_colors.get('PriLightDec'), self.kde_colors)
    self.kde_colors = re.sub('SelBG', theme_colors.get('PriDarkDec'), self.kde_colors)
    self.kde_colors = re.sub('SelFGAct', theme_colors.get('ThemeColors.ORANGE'), self.kde_colors)
    self.kde_colors = re.sub('SelFGInact', theme_colors.get('PriFontDec'), self.kde_colors)
    self.kde_colors = re.sub('SelFG', theme_colors.get('SecFontDec'), self.kde_colors)
    self.kde_colors = re.sub('SelDecFocus', theme_colors.get('TerColorDec'), self.kde_colors)
    self.kde_colors = re.sub('SelDecHover', theme_colors.get('TerLightDec'), self.kde_colors)
    
    self.kde_colors = re.sub('ToolBGAlt', theme_colors.get('TerLightDec'), self.kde_colors)
    self.kde_colors = re.sub('ToolBG', theme_colors.get('TerColorDec'), self.kde_colors)
    self.kde_colors = re.sub('ToolFGAct', theme_colors.get('TerDarkDec'), self.kde_colors)
    self.kde_colors = re.sub('ToolFGInact', theme_colors.get('TerVDarkDec'), self.kde_colors)
    self.kde_colors = re.sub('ToolFG', theme_colors.get('TerFontDec'), self.kde_colors)
    self.kde_colors = re.sub('ToolDecFocus', theme_colors.get('PriColorDec'), self.kde_colors)
    self.kde_colors = re.sub('ToolDecHover', theme_colors.get('TerLightDec'), self.kde_colors)
    
    self.kde_colors_pytheme = self.kde_colors.replace('THEMENAME', 'pytheme')  
    self.kde_colors = self.kde_colors.replace('THEMENAME', name)  


class ThemeGTK(object):

  def __init__(self):
    self.gtk_colors = ''
    self.gtk_widgets_assets_colors = ''
    self.gtk_widgets_colors = ''
    with open(path.expanduser('~/.fvwm/scripts/data/gtk-main.css')) as f:
      self.gtk_colors = f.read()
    with open(path.expanduser('~/.fvwm/scripts/data/gtk-widgets-assets.css')) as f:
      gtk_widgets_assets_colors = f.read()
    with open(path.expanduser('~/.fvwm/scripts/data/gtk-widgets.css')) as f:
      self.gtk_widgets_colors = f.read()
    #print('ThemeGTK gtk_colors: ', self.gtk_colors)
  
  def write(self):
    #print('ThemeGTK write()')
    # write gtk theme
    out_file_name = path.expanduser("~/.themes/pytheme/gtk-3.0/gtk-main.css")
    #print('ThemeGTK gtk_colors out_file_name: ', out_file_name)
    with open(out_file_name, 'w') as outfile:
      outfile.write(self.gtk_colors)
    out_file_name = path.expanduser("~/.themes/pytheme/gtk-3.0/gtk-widgets-assets.css")
    #print('ThemeGTK widgets_assets out_file_name: ', out_file_name)
    with open(out_file_name, 'w') as outfile:
      outfile.write(self.gtk_widgets_assets_colors)
    out_file_name = path.expanduser("~/.themes/pytheme/gtk-3.0/gtk-widgets.css")
    #print('ThemeGTK widgets out_file_name: ', out_file_name)
    with open(out_file_name, 'w') as outfile:
      outfile.write(self.gtk_widgets_colors)
    #print('ThemeGTK out_file_name: ', out_file_name)
  
  def replace(self, colors):
    #print('ThemeGTK replace()')
    self.gtk_widgets_assets_colors = self.gtk_widgets_assets_colors.replace('PriDark', theme_colors.get('PriDarkDec'))  
    self.gtk_widgets_assets_colors = self.gtk_widgets_assets_colors.replace('WHITE', ThemeColors.WHITE)  

    self.gtk_widgets_colors = self.gtk_widgets_colors.replace('PriColor', theme_colors.get('PriColorDec'))  
    self.gtk_widgets_colors = self.gtk_widgets_colors.replace('SecColor', theme_colors.get('SecColorDec'))  
    self.gtk_widgets_colors = self.gtk_widgets_colors.replace('PriLight', theme_colors.get('PriLightDec'))  
    self.gtk_widgets_colors = self.gtk_widgets_colors.replace('WHI_TE', ThemeColors.WHITE)  
    self.gtk_widgets_colors = self.gtk_widgets_colors.replace('WHITE', ThemeColors.WHITE)  
    self.gtk_widgets_colors = self.gtk_widgets_colors.replace('BLACK', ThemeColors.BLACK)  

    GTKBLACK = '#111111'
    self.gtk_colors = re.sub('FontColor', theme_colors.get('FontColor'), self.gtk_colors)
    self.gtk_colors = re.sub('BACKGROUNDALT', theme_colors.get('PriLight'), self.gtk_colors)
    self.gtk_colors = re.sub('BACKGROUND', theme_colors.get('PriColor'), self.gtk_colors)
    self.gtk_colors = re.sub('THEME_BASE', ThemeColors.GTKBACKGROUND, self.gtk_colors)
    self.gtk_colors = re.sub('THEME_SEC', theme_colors.get('PriVDark'), self.gtk_colors)
    self.gtk_colors = re.sub('THEME_FG', GTKBLACK, self.gtk_colors)
    self.gtk_colors = re.sub('BUTTON_TEXT', theme_colors.get('SecFont'), self.gtk_colors)
    self.gtk_colors = re.sub('BUTTON', theme_colors.get('SecColor'), self.gtk_colors)
    self.gtk_colors = re.sub('THROUGH', theme_colors.get('SecDark'), self.gtk_colors)
    self.gtk_colors = re.sub('SELECTED_BG', theme_colors.get('SecColor'), self.gtk_colors)
    self.gtk_colors = re.sub('SELECTED_FG', theme_colors.get('SecFont'), self.gtk_colors)
    self.gtk_colors = re.sub('LIGHT_BORDER', theme_colors.get('TerLight'), self.gtk_colors)
    self.gtk_colors = re.sub('DARK_BORDER', theme_colors.get('TerDark'), self.gtk_colors)
    self.gtk_colors = re.sub('BORDER', theme_colors.get('TerColor'), self.gtk_colors)
    self.gtk_colors = re.sub('LIGHT', theme_colors.get('PriLight'), self.gtk_colors)
    self.gtk_colors = re.sub('MEDIUM', theme_colors.get('PriColor'), self.gtk_colors)
    self.gtk_colors = re.sub('DARKER', theme_colors.get('PriVDark'), self.gtk_colors)
    self.gtk_colors = re.sub('DARK', theme_colors.get('PriDark'), self.gtk_colors)


theme_colors = ThemeColors(color_set)
  
# main loop
colors = color_set['colors']
out_file_name = path.expanduser("~/.fvwm/scripts/fvwm_theme.config")
with open(out_file_name, 'w') as fd:
  # write header
  fd.write('# THEME: ')
  fd.write(str(colors))
  fd.write(' colors - ')
  fd.write(name)
  fd.write('\n')
  fd.write('\n')
  
  write_value(fd, 'SetEnv ThemeIdx ', index)
  fd.write('\n')
  name = name.strip()

  name_parts = name.split()
  name = ''
  for n in name_parts:
    if n[0] != '-':
      name = name + n

  # write theme name
  theme_name = '"{}"'.format(name)
  #print('Theme name: ', theme_name)
  write_value(fd, 'SetEnv ThemeName ', theme_name)
  fd.write('\n')
  write_value(fd, 'SetEnv ThemeColors ', str(colors))
  fd.write('\n')

  # write button background highlight
  ButtonBGHL = chroma.Color(theme_colors.get('PriColor'))
  if 'BorderHighlight' in color_set:
    ButtonBGHL = chroma.Color(color_set['BorderHighlight']['color'])
  ButtonBGHL = normalize(ButtonBGHL)
  write_value(fd, '#ButtonBGHL.hls ', str(ButtonBGHL.hls))
  write_value(fd, 'SetEnv ButtonBGHL ', str(ButtonBGHL))
  fd.write('\n')
  
  # write button background
  ButtonBG = chroma.Color(theme_colors.get('SecColor'))
  if 'Border' in color_set:
    ButtonBG = chroma.Color(color_set['Border']['color'])
  ButtonBG = normalize(ButtonBG)
  write_value(fd, '#ButtonBG.hls ', str(ButtonBG.hls))
  write_value(fd, 'SetEnv ButtonBG ', str(ButtonBG))
  fd.write('\n')
  
  # write all 4 colors info
  write_color_values('Pri', theme_colors, fd)
  write_color_values('Sec', theme_colors, fd)
  write_color_values('Ter', theme_colors, fd)
  write_color_values('Quat', theme_colors, fd)
    
  if 'Root' in color_set:
    write_color(fd, 'SetEnv RootColor ', 'color', 'Root')
  else:
    write_color(fd, 'SetEnv RootColor ', 'root', 'Pri')

  if 'PriFont' in color_set:
    write_color(fd, 'SetEnv PriFont ', 'color', 'PriFont')
  else:
    write_color(fd, 'SetEnv PriFont ', 'font', 'Pri')

  if 'SecFont' in color_set:
    write_color(fd, 'SetEnv SecFont ', 'color', 'PriFont')
  else:
    write_color(fd, 'SetEnv SecFont ', 'secfont', 'Pri')

  fd.write('\n')
  write_color(fd, 'SetEnv RootCompl ', 'rootcompl', 'Pri')
  color1 = color_set['Pri']
  write_value(fd, 'SetEnv TermFade ', color1['term_fade'])
  write_value(fd, 'SetEnv TermBG ', color1['term_bg'])
  write_value(fd, 'SetEnv TermBGInit ', color1['term_bg2'])
  fd.write('\n')
  
  if not SkipImageCreation:
    write_title_images(get_rgb(theme_colors.get('PriColor')), get_rgb(theme_colors.get('SecColor')))
      
# read templated themes, replace colors and write to ~ user locations (overwrite)
theme_kde = ThemeKDE()
theme_gtk = ThemeGTK()
theme_kde.replace(theme_colors, name)
theme_gtk.replace(theme_colors)
theme_kde.write()
theme_gtk.write()

# refresh kde apps, gtk happens automatically
res = subprocess.run(["/usr/bin/lookandfeeltool", "-a",'org.kde.oxygen'])
#print('lookandfeeltool result: ', res)

