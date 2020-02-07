/******************************************/
/* Wmlife - Game Of Life Dock             */
/******************************************/

/******************************************/
/* This program is free software; you can redistribute it and/or
/* modify it under the terms of the GNU General Public License
/* as published by the Free Software Foundation; either version 2
/* of the License, or (at your option) any later version.
/* 
/* This program is distributed in the hope that it will be useful,
/* but WITHOUT ANY WARRANTY; without even the implied warranty of
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
/* GNU General Public License for more details.
/* 
/* You should have received a copy of the GNU General Public License
/* along with this program; if not, write to the Free Software
/* Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
/******************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

#include <gdk/gdk.h>
#include <gdk/gdkx.h>

#include "session.h"

#include "master.xpm"
#include "icon.xpm"

/******************************************/
/* Defines                                */
/******************************************/

#define XMAX 56
#define YMAX 56
#define RGBSIZE (XMAX * YMAX * 3)

#define UPDATE		500000
#define REFRESH		20000

/******************************************/
/* Structures                             */
/******************************************/

typedef struct {
	Display *display;	/* X11 display */
	GdkWindow *win;		/* Main window */
	GdkWindow *iconwin;	/* Icon window */
	GdkGC *gc;		/* Drawing GC */
	GdkPixmap *pixmap;	/* Main pixmap */
	GdkBitmap *mask;	/* Dockapp mask */

	int x;			/* Window X position */
	int y;			/* Window Y position */
	int sticky;		/* Window sticky */

	unsigned char rgb[RGBSIZE];
} wmlife_data;

/******************************************/
/* Functions                              */
/******************************************/

void life_cycle();
void randomise_matrix();
void launch_puffer();
void draw_life(int);
GdkCursor *setup_cursor();
static void make_wmlife_dockapp();
void read_config(int, char **);
void do_help(void);

/******************************************/
/* Globals                                */
/******************************************/

static wmlife_data bm;

unsigned char matrix[XMAX][YMAX];
unsigned char evomatrix[XMAX][YMAX];

char *session_id = NULL;
char *command = NULL;

int cycle = UPDATE;

/******************************************/
/* Main                                   */
/******************************************/

int
main(int argc, char **argv)
{
	GdkEvent *event;
	GdkCursor *cursor;
	int redraw = 0;
	int pause = 0;
	int proximity = 0;
	int timer, x, y;

	/* Disable client-side windows due to mixed X and GDK calls */
	setenv("GDK_NATIVE_WINDOWS", "1", 0);

	/* Initialise random seed */
	srand(time(NULL));

	/* Initialize GDK */
	if (!gdk_init_check(&argc, &argv)) {
		fprintf(stderr, "GDK init failed. Check \"DISPLAY\" variable.\n");
		exit(-1);
	}

	/* Initialise invisible cursor */
	cursor = setup_cursor();

	/* Zero main data structures */
	memset(&bm, 0, sizeof (bm));

	/* Parse command line */
	read_config(argc, argv);
	timer = cycle;
#ifdef SESSION
	smc_connect(argc, argv, session_id);
#endif

	/* Create dockapp window. creates windows, allocates memory, etc */
	make_wmlife_dockapp();
	randomise_matrix();

	while (1) {
		while (gdk_events_pending()) {
			event = gdk_event_get();
			if (event) {
				switch (event->type) {
				case GDK_DESTROY:
				case GDK_DELETE:
					gdk_cursor_destroy(cursor);
					exit(0);
					break;
				case GDK_EXPOSE:
					redraw = 1;
					break;
				case GDK_BUTTON_PRESS:
					if (event->button.button == 1) {
						if (command)
							g_spawn_command_line_async(command, NULL);
						launch_puffer();
						redraw = 1;
						timer = 0;
					} else if (event->button.button == 2) {
						randomise_matrix();
						draw_life(0);
						redraw = 1;
						timer = 0;
					} else if (event->button.button == 3) {
						pause = !pause;
					}
					/* Disable life trails from cursor */
					if (proximity)
						proximity = 0;
					break;
				case GDK_ENTER_NOTIFY:
					proximity = 1;
					/* gdk_window_set_cursor(bm.win, cursor); */
					break;
				case GDK_LEAVE_NOTIFY:
					proximity = 0;
					/* gdk_window_set_cursor(bm.win, NULL); */
					break;
				default:
					break;
				}
				gdk_event_free(event);
			}
		}

		/* Life trails from cursor */
		if (proximity >= cycle) {
			gdk_window_get_pointer(bm.win, &x, &y, NULL);
			/* Following is specific to this 64x64 dock app    */
			/* 0-2,61-63 mask; 3,60 pixmap border, 4-59 matrix */
			if (x > 3 && x < 60 && y > 3 && y < 60) {
				matrix[x-4][y-4] = 1;
				draw_life(0);
				redraw = 1;
			}
		} else if (proximity)
			proximity += REFRESH;

		/* Run the game of life */
		if (timer >= cycle) {
			if (!pause) {
			        /* Fifteen minute reset */
				if (time(NULL) % 900)
					life_cycle();
				else
					randomise_matrix();
			}
			draw_life(1);
			redraw = 1;
			timer = 0;
		}

		/* Draw the rgb buffer to screen */
		if (redraw) {
			gdk_draw_rgb_image(bm.iconwin, bm.gc, 4, 4, XMAX, YMAX, GDK_RGB_DITHER_NONE, bm.rgb, XMAX * 3);
			gdk_draw_rgb_image(bm.win, bm.gc, 4, 4, XMAX, YMAX, GDK_RGB_DITHER_NONE, bm.rgb, XMAX * 3);
			redraw = 0;
		}

		usleep(REFRESH);
		timer += REFRESH;
	}

	return 0;
}

/******************************************/
/* Game of life                           */
/******************************************/

void
life_cycle()
{
	int x, y, l, r, t, b;
	int n;

	memset(evomatrix, 0, sizeof(evomatrix));

	for(x = 0; x < XMAX; x++) {
		l = (x - 1) % XMAX;
		r = (x + 1) % XMAX;
		for(y = 0; y < YMAX; y++) {
			t = (y - 1) % YMAX;
			b = (y + 1) % YMAX;

			n = (matrix[l][t] + matrix[x][t] + matrix[r][t] +
			     matrix[l][y]                + matrix[r][y] +
			     matrix[l][b] + matrix[x][b] + matrix[r][b]);

			if (n == 3 || (matrix[x][y]) && n == 2)
				evomatrix[x][y] = 1;
		}
	}

	memcpy(matrix, evomatrix, sizeof(matrix));
}

/******************************************/
/* Randomise matrix                       */
/******************************************/

void
randomise_matrix()
{
	int x, y;

	memset(matrix, 0, sizeof(matrix));

	for(x = 0; x < XMAX; x++)
		for(y = 0; y < YMAX; y++)
			matrix[x][y] = rand() % 2;

	draw_life(0);
}

/******************************************/
/* Launch puffer train                    */
/******************************************/

void
launch_puffer()
{
	static int n;

	memset(matrix, 0, sizeof(matrix));

	/* PATTERN: R-pentomino */
	matrix[28][27] = 1;
	matrix[29][27] = 1;
	matrix[27][28] = 1;
	matrix[28][28] = 1;
	matrix[28][29] = 1;

	draw_life(0);
}

/******************************************/
/* Draw matrix                            */
/******************************************/

void
draw_life(int update)
{
	int x, y;
	int r, g, b, val;
	unsigned char *p;
	double distance, mult;
	
	static double rsin = 0.1; /* + ((rand() >> 6) % 255) / 100.0; */
	static double gsin = 0.4; /* + ((rand() >> 6) % 255) / 100.0; */
	static double bsin = 1.0; /* + ((rand() >> 6) % 255) / 100.0; */
	
	static int bouncex = 10;
	static int bouncey = 10;
	static int bouncexsp = 2;
	static int bounceysp = 1;


	r = 255 * ((sin(rsin) + 1) / 2);
	g = 255 * ((sin(gsin) + 1) / 2);
	b = 255 * ((sin(bsin) + 1) / 2);

	if (update) {
		rsin += ((rand() >> 6) % 5 + 1) * 0.01;
		gsin += ((rand() >> 6) % 5 + 1) * 0.01;
		bsin += ((rand() >> 6) % 5 + 1) * 0.01;

		bouncex += bouncexsp;
		if (bouncex > XMAX) {
			bouncex = XMAX;
			bouncexsp =- ((rand() >> 6) % 3 + 1);
		} else if (bouncex < 0) {
			bouncex = 0;
			bouncexsp = ((rand() >> 6) % 3 + 1);
		}
		bouncey += bounceysp;
		if (bouncey > YMAX) {
			bouncey = YMAX;
			bounceysp = -((rand() >> 6) % 3 + 1);
		} else if (bouncey < 0) {
			bouncey = 0;
			bounceysp = ((rand() >> 6) % 3 + 1);
		}
	}

	for (y = 0; y < YMAX; y++) {
		p = bm.rgb + y * YMAX * 3;
		for (x = 0; x < XMAX; x++) {
			distance = abs(sqrt((x - bouncex) * (x - bouncex) +
					 (y - bouncey) * (y - bouncey))) / 5.0;
			if (distance < 0.1)
				distance = 0.1;

			mult = 3.4 - log(distance);
			if (mult < 1.0)
				mult = 1.0;
			else if (mult > 200.0)
				mult = 200.0;

			if (matrix[x][y]) {
				*(p++) = 255 - r;
				val = (255 - g) * mult;
				if(val > 255)
					val = 255;
				*(p++) = val;
				*(p++) = (255 - b) / mult;
			} else {
				val = r * mult;
				if(val > 255)
					val = 255;
				*(p++) = val;
				*(p++) = g / mult;
				*(p++) = b;
			}
		}
	}
}

/******************************************/
/* Setup invisible cursor                 */
/******************************************/

GdkCursor *
setup_cursor()
{
	GdkPixmap *source, *mask;
	GdkColor col = { 0, 0, 0, 0 };
	GdkCursor *cursor;
	unsigned char hide[] = { 0x00 };

	/* No obviously invisible cursor available though */
	/* X/GDK, so using a custom 1x1 bitmap instead    */

	source = gdk_bitmap_create_from_data(NULL, hide, 1, 1);
	mask = gdk_bitmap_create_from_data(NULL, hide, 1, 1);

	cursor = gdk_cursor_new_from_pixmap(source, mask, &col, &col, 0, 0);

	gdk_pixmap_unref(source);
	gdk_pixmap_unref(mask);

	return cursor;
}

/******************************************/
/* Create dock app window                 */
/******************************************/

static void
make_wmlife_dockapp(void)
{
#define MASK GDK_BUTTON_PRESS_MASK | GDK_ENTER_NOTIFY_MASK | GDK_LEAVE_NOTIFY_MASK | GDK_POINTER_MOTION_HINT_MASK | GDK_EXPOSURE_MASK

	GdkWindowAttr attr;
	GdkWindowAttr attri;
	Window win;
	Window iconwin;

	GdkPixmap *icon;

	XSizeHints sizehints;
	XWMHints wmhints;

	memset(&attr, 0, sizeof (GdkWindowAttr));

	attr.width = 64;
	attr.height = 64;
	attr.title = "wmlife";
	attr.event_mask = MASK;
	attr.wclass = GDK_INPUT_OUTPUT;
	attr.visual = gdk_visual_get_system();
	attr.colormap = gdk_colormap_get_system();
	attr.wmclass_name = "wmlife";
	attr.wmclass_class = "wmlife";
	attr.window_type = GDK_WINDOW_TOPLEVEL;

	/* Make a copy for the iconwin - parameters are the same */
	memcpy(&attri, &attr, sizeof (GdkWindowAttr));
	attri.window_type = GDK_WINDOW_CHILD;

	sizehints.flags = USSize;
	sizehints.width = 64;
	sizehints.height = 64;

	bm.win = gdk_window_new(NULL, &attr, GDK_WA_TITLE | GDK_WA_WMCLASS | GDK_WA_VISUAL | GDK_WA_COLORMAP);
	if (!bm.win) {
		fprintf(stderr, "FATAL: Cannot make toplevel window\n");
		exit(1);
	}

	bm.iconwin = gdk_window_new(bm.win, &attri, GDK_WA_TITLE | GDK_WA_WMCLASS);
	if (!bm.iconwin) {
		fprintf(stderr, "FATAL: Cannot make icon window\n");
		exit(1);
	}

	win = GDK_WINDOW_XWINDOW(bm.win);
	iconwin = GDK_WINDOW_XWINDOW(bm.iconwin);
	XSetWMNormalHints(GDK_WINDOW_XDISPLAY(bm.win), win, &sizehints);

	wmhints.initial_state = WithdrawnState;
	wmhints.icon_window = iconwin;
	wmhints.icon_x = 0;
	wmhints.icon_y = 0;
	wmhints.window_group = win;
	wmhints.flags = StateHint | IconWindowHint | IconPositionHint | WindowGroupHint;

	bm.gc = gdk_gc_new(bm.win);

	bm.pixmap = gdk_pixmap_create_from_xpm_d(bm.win, &(bm.mask), NULL, master_xpm);
	gdk_window_shape_combine_mask(bm.win, bm.mask, 0, 0);
	gdk_window_shape_combine_mask(bm.iconwin, bm.mask, 0, 0);

	gdk_window_set_back_pixmap(bm.win, bm.pixmap, False);
	gdk_window_set_back_pixmap(bm.iconwin, bm.pixmap, False);

#if 0
        gdk_window_set_type_hint(bm.win, GDK_WINDOW_TYPE_HINT_DOCK);
#else
        gdk_window_set_decorations(bm.win, 0);
        gdk_window_set_skip_taskbar_hint(bm.win, 1);
#endif

	icon = gdk_pixmap_create_from_xpm_d(bm.win, NULL, NULL, icon_xpm);
	gdk_window_set_icon(bm.win, bm.iconwin, icon, NULL);

	gdk_window_show(bm.win);

	/* Moved after gdk_window_show due to change in GTK 2.4 */
	XSetWMHints(GDK_WINDOW_XDISPLAY(bm.win), win, &wmhints);

	if (bm.x > 0 || bm.y > 0)
		gdk_window_move(bm.win, bm.x, bm.y);
	if (bm.sticky)
		gdk_window_stick(bm.win);
#undef MASK
}

/******************************************/
/* Read config file                       */
/******************************************/

void
read_config(int argc, char **argv)
{
	int i, j;

	/* Parse command options */
	while ((i = getopt(argc, argv, "c:g:hl:S:y")) != -1) {
		switch (i) {
		case 'S':
			if (optarg)
				session_id = strdup(optarg);
			break;
		case 'g':
			if (optarg) {
				j = XParseGeometry(optarg, &bm.x, &bm.y, &j, &j);

				if (j & XNegative)
					bm.x = gdk_screen_width() - 64 + bm.x;
				if (j & YNegative)
					bm.y = gdk_screen_height() - 64 + bm.y;
			}
			break;
		case 'y':
			bm.sticky = 1;
			break;
		case 'c':
			if (optarg)
				command = strdup(optarg);
			break;
		case 'l':
			if (optarg)
				cycle = atoi(optarg) * 1000;
			break;
		case 'h':
		default:
			do_help();
			exit(1);
		}
	}
}

/******************************************/
/* Help                                   */
/******************************************/

void
do_help(void)
{
	int i;

	fprintf(stderr, "\nWmlife - Game Of Life Dock V %s\n\n", VERSION);
	fprintf(stderr, "Usage: wmlife [ options... ]\n\n");
	fprintf(stderr, "\t-g [{+-}X{+-}Y]\t\tinital window position\n");
	fprintf(stderr, "\t-y\t\t\tset window sticky\n");
	fprintf(stderr, "\t-l [...]\t\tlife cycle in milliseconds (default:%d)\n", cycle / 1000);
	fprintf(stderr, "\t-c [...]\t\tcommand\n");
	fprintf(stderr, "\t-h\t\t\tprints this help\n");
}
