#include <config.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>
#include <panel-applet.h>
#include <gnome.h>
#include <gdk/gdk.h>

#define LIFE_CYCLE 600
#define MAX_SIZE 80

int board[MAX_SIZE][MAX_SIZE];
guchar rgb_buffer[MAX_SIZE*MAX_SIZE*3];
GtkWidget *darea = NULL;
int size = 45;

double rsin = 0.1;
double gsin = 0.4;
double bsin = 1.0;

static int bouncex = 10;
static int bouncey = 10;
static int bouncexsp = 2;
static int bounceysp = 1;

static void
life_draw(void)
{
	int i,j;
	GdkGC *gc;
	int r,g,b;
	
	if(!darea ||
	   !GTK_WIDGET_REALIZED(darea) ||
	   !GTK_WIDGET_DRAWABLE(darea) ||
	   size<=0)
		return;
	
	r = 255*((sin(rsin)+1)/2);
	g = 255*((sin(gsin)+1)/2);
	b = 255*((sin(bsin)+1)/2);
	rsin+=((rand()>>6)%5 + 1)*0.01;
	gsin+=((rand()>>6)%5 + 1)*0.01;
	bsin+=((rand()>>6)%5 + 1)*0.01;
	
	bouncex+=bouncexsp;
	if(bouncex>size) {
		bouncex=size;
		bouncexsp=-((rand()>>6)%3+1);
	} else if(bouncex<0) {
		bouncex=0;
		bouncexsp=((rand()>>6)%3+1);
	}
	bouncey+=bounceysp;
	if(bouncey>size) {
		bouncey=size;
		bounceysp=-((rand()>>6)%3+1);
	} else if(bouncey<0) {
		bouncey=0;
		bounceysp=((rand()>>6)%3+1);
	}
	
	gc = gdk_gc_new(darea->window);

	for(j=0;j<size;j++) {
		guchar *p = rgb_buffer + j*MAX_SIZE*3;
		for(i=0;i<size;i++) {
			double distance =
				abs(sqrt((i-bouncex)*(i-bouncex)+
					 (j-bouncey)*(j-bouncey)))/5.0;
			double mult = 1.0;
			int val;
			if(distance < 0.1)
				distance = 0.1;
			mult += -log(distance)+2.4;
			if(mult<1.0) mult = 1.0;
			else if(mult>200.0) mult = 200.0;

			if(board[i][j]) {
				*(p++) = 255-r;
				val = (255-g)*mult;
				if(val>255) val = 255;
				*(p++) = val;
				*(p++) = (255-b)/mult;
			} else {
				val = r*mult;
				if(val>255) val = 255;
				*(p++) = val;
				*(p++) = g/mult;
				*(p++) = b;
			}
		}
	}
	gdk_draw_rgb_image(darea->window,gc,
			   0,0, size, size,
			   GDK_RGB_DITHER_NORMAL,
			   rgb_buffer, MAX_SIZE*3);
	
	gdk_gc_destroy(gc);
}
