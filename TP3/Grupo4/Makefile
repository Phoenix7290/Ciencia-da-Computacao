CC      = gcc
CFLAGS  = -Wall -Wextra -O2
TARGET  = roteador
SRCS    = main.c trie.c
OBJS    = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c trie.h
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

test:
	./roteador

.PHONY: all clean test