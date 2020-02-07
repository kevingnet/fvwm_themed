#!/usr/bin/python3

import sys
import os
import subprocess

file_name = sys.argv[1]
tint_color = '{}'.format(sys.argv[2])

if 'wallpaper' in file_name:
  subprocess.run(["/usr/ubin/hsetroot", "-cover", file_name])
else:
  subprocess.run(["/usr/ubin/hsetroot", "-tile", file_name, "-tint2", tint_color])
