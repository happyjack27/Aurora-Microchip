CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -O2 -std=c11
TARGET   = aurora_asm

.PHONY: all clean test

all: $(TARGET)

$(TARGET): assembler.c
	$(CC) $(CFLAGS) -o $@ $<

test: $(TARGET)
	@echo "--- running self-test ---"
	@./$(TARGET) -f vhex -o /tmp/aurora_test.vhex test/hello.asm && \
	  echo "PASS: hello.asm assembled" || echo "FAIL"

clean:
	rm -f $(TARGET) *.o
