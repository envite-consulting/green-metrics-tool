PROGRAM = metric-provider-binary
SOURCES = source.c chips.c
GLIBLIB = $(shell pkg-config --libs glib-2.0)
GLIBGLAGS = $(shell pkg-config --cflags glib-2.0)
CFLAGS = -O3 -Wall -Werror -Llib -lsensors $(GLIBLIB) $(GLIBGLAGS) -I../../lib/c

binary:
	gcc ../../lib/c/gmt-lib.o $(SOURCES) $(CFLAGS) -o $(PROGRAM)

lint:
	cpplint *.c *.h

debug:
	gcc ../../lib/c/gmt-lib.o $(SOURCES) $(CFLAGS) -g -o $(PROGRAM)
