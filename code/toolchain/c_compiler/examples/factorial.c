/* factorial.c — recursive factorial example for the Aurora C compiler */

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int result = factorial(10);
    return result;
}
