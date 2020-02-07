bin_PROGRAMS = wmlife

if SESSION
wmlife_SOURCES = wmlife.c \
	session.h session.c
else
wmlife_SOURCES = wmlife.c
endif	 

wmlife_LDADD = @LDFLAGS@

AM_LDFLAGS = -lXext -lX11 \
	-L/usr/X11R6/lib -L/usr/local/lib

INCLUDES = -I/usr/X11R6/include \
	-I/usr/local/include
