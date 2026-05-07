CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -fopenmp
LDFLAGS = -lm
TARGETS = k_way_merge benchmark

all: $(TARGETS)

k_way_merge: k_way_merge_parallel.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

benchmark: benchmark.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGETS)

# Execuções rápidas para teste
test:
	./k_way_merge 1000000 16 8

bench:
	./benchmark

.PHONY: all clean test bench