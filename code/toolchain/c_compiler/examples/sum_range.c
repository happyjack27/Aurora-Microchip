/* sum_array.c — sum of an array using a for loop */

int g_total = 0;

int sum_range(int lo, int hi) {
    int acc = 0;
    for (int i = lo; i <= hi; i++) {
        acc = acc + i;
    }
    return acc;
}

int main() {
    g_total = sum_range(1, 100);
    return g_total;
}
