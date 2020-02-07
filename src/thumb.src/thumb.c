#include <X11/Xlib.h>
#include <Imlib2.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    Display *display;
    XWindowAttributes windowattr;
    Imlib_Image image;
    Imlib_Image icon;
    int windowid, thumbwidth, thumbheight;
    char *imageformat, *imagepath;
    char *iconformat, *iconpath;
    int w, h;

    if(argc != 5) {
        puts("Usage: thumb WindowId ThumbWidth ThumbFile IconFile");
        return 1;
    }
    sscanf(argv[1], "%x", &windowid);
    sscanf(argv[2], "%d", &thumbwidth);
    imagepath = argv[3];
    imageformat = strrchr(argv[3], '.');
    iconpath = argv[4];
    iconformat = strrchr(argv[4], '.');

    if((display = XOpenDisplay(NULL)) == NULL )
        return 1;
    XGetWindowAttributes(display, windowid, &windowattr);
    thumbheight = (int)((float)windowattr.height / ((float)windowattr.width/(float)thumbwidth));

    imlib_context_set_anti_alias(1);
    imlib_context_set_display(display);
    imlib_context_set_visual(DefaultVisual(display, DefaultScreen(display)));
    imlib_context_set_colormap(DefaultColormap(display, DefaultScreen(display)));
    imlib_context_set_drawable(windowid);

    if( 4*thumbwidth >= windowattr.width ||
        4*thumbheight >= windowattr.height ) {
        image = imlib_create_image_from_drawable((Pixmap)0, 0, 0, windowattr.width, windowattr.height, 1);
        imlib_context_set_image(image);
        image = imlib_create_cropped_scaled_image(0, 0, windowattr.width, windowattr.height, thumbwidth, thumbheight);
    } else {
        image = imlib_create_scaled_image_from_drawable((Pixmap)0, 0, 0, windowattr.width, windowattr.height, 4*thumbwidth, 4*thumbheight, 1, 1);
        imlib_context_set_image(image);
        image = imlib_create_cropped_scaled_image(0, 0, 4*thumbwidth, 4*thumbheight, thumbwidth, thumbheight);
    }
    icon = imlib_load_image(argv[4]);
    imlib_context_set_image(icon);
    w = imlib_image_get_width();
    h = imlib_image_get_height();
    imlib_context_set_image(image);
    imlib_blend_image_onto_image(icon, 0, 0, 0, w, h, 0, 0, w, h);
    imlib_image_set_format(imageformat + 1);
    imlib_save_image(argv[3]);

    fprintf(stdout, "WindowStyle IconOverride, Icon %s\n", argv[3]);
    return 0;
}

