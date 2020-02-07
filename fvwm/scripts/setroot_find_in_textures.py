#!/usr/bin/python3
"""
Find image files in textures directory that are not in .thumb
Set desktop root to wallpaper mode if the file is found in wallpaper dir, otherwise tile it
Lower brightness

NOTE: hsetroot is broken, I've added a fixed version along with the source code. Use that one,
copy it to a directory in your path that will make it be found first.
"""

import sys
import os
from pathlib import Path
import subprocess

matches = []
file_to_find = sys.argv[1]
file_to_find = file_to_find + '.'
print(file_to_find)
for filename in Path(os.path.expanduser('~/.fvwm/textures')).rglob('*'):
  fname = str(filename)
  if ".thumb" in fname:
    continue
  if file_to_find in fname:
    matches.append(fname)
  
found_file = None
for f in matches:
  found_file = f
  break
   
if found_file:
  if "wallpaper" in found_file: 
    subprocess.run(["hsetroot", "-cover", found_file])
  else:
    subprocess.run(["hsetroot", "-tile", found_file, "-brightness", "-.2"])
    
