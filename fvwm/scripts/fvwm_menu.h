# the following file contains the functions:
# ftGetSectionIcon, ftFindIconByList, ftIsWmIcons, ftGetSectionIconForApp 
# used below
!include fvwm_menu_data.h

function ftFindSystemMiniIcon($n) = ""

# return the best possible section ($f) icon by using the following
# preference order:
#  1. the wm-icons associated to a standard menu system section ($s)
#  2. the menu system icon ($i) if it is a wm-icons
#  3. the "system" mini icon (ftFindSystemMiniIcon should be edited)
#  4. the wm-icons associated to a standard section if the section is a
#     subsection of a standard one
#  5. $f folder.xpm
# That you may want is to change this order
function ftFindBestSectionIcon($s,$i,$f)= \
  ifeqelse(ftGetSectionIcon($s),"",\
  ifeqelse($i,"",\
  ifeqelse(ftFindSystemMiniIcon($i),"",\
  ifeqelse(ftGetSectionIcon(parent($s)),"",\
  ifeqelse(ftGetSectionIcon(parent(parent($s))),"",\
	   $f "folder.xpm",\ 
	   $f ftGetSectionIcon(parent(parent($s)))),\
	   $f ftGetSectionIcon(parent($s))),\
	   ftFindSystemMiniIcon($i)),\
           $i),\
	   $f ftGetSectionIcon($s))

# return the best possible application ($f) icon by using the following
# preference order:
#  1. the menu system icon ($i) if it is a wm-icons
#  2. A wm-icons associated to the package ($p), or command ($c) or title ($t)
#     via the ftFindIconByList function
#  3. As above but try to found a kde2 or gnome icons produced by 
#     fvwm-themes-images
#  4. the "system" mini icon (ftFindSystemMiniIcon should be edited)
#  5. the wm-icons associated to a standard section if the app is in
#     such a section (or a subsection of such a section)
#  6. $f item.xpm
# That you may want is to change this order
function ftFindBestIcon($i,$p,$s,$c,$t,$f)= \
	ifeqelse($i, "",\
	ifeqelse(ftFindIconByList($p,$c,$t,$f), "",\
	$f "menu/item.xpm",\
	$f cond_surr(ftFindIconByList($p,$c,$t,$f),"menu/","")),\
	$f $i)
	

