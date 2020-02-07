#!/usr/bin/python3

"""
Create and print a random color to be used for a terminal such as xterm, rxvt, etc...
"""

import random


#0000/0000/2000/dddd

def rand_channel():
    return ''.join(random.choice('012345678') for j in range(2))
  
def rand_alfa():
    return ''.join(random.choice('DE') for j in range(2))

color = rand_channel() + "00/" + rand_channel() + "00/" + rand_channel() + "00/" + rand_alfa() + "00" 
print(color, end='')

