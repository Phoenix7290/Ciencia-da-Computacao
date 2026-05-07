CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -fopenmp
LDFLAGS = -lm
TARGET  = quadtree_sim
SRCS    = main.c quadtree.c
OBJS    = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c quadtree.h
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

test:
	./quadtree_sim 8

.PHONY: all clean test