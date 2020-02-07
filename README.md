# fvwm_themed
Fvwm2 configuration files, tools, images, theme support, create new themes from image files.

Steps to use this fvwm config file with themes and included tools.

1) Look at install_history.txt and decide what to install.
2) Backup your ~/.fvwm dir, copy this .fvwm dir to your home directory
3) Copy the pytheme directory to ~/.themes/
4) Change permissions for /usr/share/color-schemes/Oxygen.colors, so that you can edit the file
5) Copy the files from bin to a location in the path ~/bin ir /usr/local/bin, or build your own
   from the sources included
6) cd ~/.fvwm/scripts/ and Run ./create_textures_menu.py, this creates a menu to change backgrounds from your image files in .fvwm/textures dir
7) Start or restart fvwm

The themes are accessible and some samples are provided (check for image copyright) 
- Main menu, right mouse click has a subset of the themes
- Theme menu, middle mouse click has a full set

You can also run the install.sh script,
First edit the script and uncomment the commented commands for sudo if you need:
1) thumnails for minimized windows
2) hsetroot with colorization support, which is broken in the original

If you're not comfortable with using other people's binaries, you may build them 
yourself, however for the thumb one, there's a glitch which I haven't worked on
and the thumbOG is the one used by the config because it doesn't have the issue,
I don't have the source code for that though.

The command sudo chown /usr/share/color-schemes/Oxygen.colors is necessary if you want kde
to update the theme automatically, highly recommended.
