#!/usr/bin/python3

from os import path

home_dir = path.expanduser('~/.fvwm/textures/')
with open('textures_menu', 'w') as outfile:
  outfile.write('+ "Textures" Popup "{}"'.format(home_dir))
