/* bitops.c — demonstrates bitwise and shift operations */

int popcount(int x) {
    int count = 0;
    while (x != 0) {
        count = count + (x & 1);
        x = x >> 1;
    }
    return count;
}

int clz(int x) {
    int n = 0;
    int mask = 1 << 31;
    while (n < 32 && (x & mask) == 0) {
        n = n + 1;
        mask = mask >> 1;
    }
    return n;
}

int main() {
    int a = popcount(0xFF);
    int b = clz(0x00010000);
    return a + b;
}
