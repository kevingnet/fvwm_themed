CC := gcc
CFLAGS :=   -Wall -O3 -fomit-frame-pointer \
        `imlib2-config --cflags`
CPPFLAGS :=
CXXFLAGS := $(CFLAGS)
TARGET_ARCH :=  
#TARGET_ARCH :=  -march=athlon-xp -mcpu=athlon-xp
LDFLAGS :=  -Wl,-O1 -lX11 \
        `imlib2-config --libs`
PRODUCTS := thumb

.PHONY: clean

all:    $(PRODUCTS)

clean:
	find *.o -exec rm {} \; && echo || echo

mrproper: clean
	for product in $(PRODUCTS); \
	do [ -f $$product ] && rm $$product; \
	done && echo || echo

rebuild: mrproper all

thumb: thumb.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@
	strip $@

