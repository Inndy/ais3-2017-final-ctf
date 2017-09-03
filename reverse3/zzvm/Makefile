CC = gcc
CFLAGS = -O0 -std=c99

all: oovm

oovm: main.o zzvm.o
	$(CC) zzvm.o main.o -o $@
	strip $@

test: test.o zzvm.o
	$(CC) zzvm.o test.o -o $@

%.o: %.c
	$(CC) $< -c $(CFLAGS)

clean:
	rm *.o zzvm test || true
