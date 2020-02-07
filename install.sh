#!/bin/bash

# BACK UP AND COPY .fvwm directory with configs, images, tools, etc...
rm -fr ~/.fvwm.bak.og
cp -r ~/.fvwm.bak ~/.fvwm.bak.og
cp -r .fvwm ~/

# copy pythemes dir, this is used to update colors for gtk
cp -r pythemes ~/.themes/

# this is so kde colors can change automatically, the tool creates
# color files anyway and you can later select them manually, but, 
# make your life a little easier and run this command.
#sudo chown /usr/share/color-schemes/Oxygen.colors

# copy binaries to a location in the path
#sudo cp bin/thumb* bin/hsetroot /usr/bin

# create textures menu
cd ~/.fvwm/scripts/
./create_textures_menu.py



