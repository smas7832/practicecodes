#include <stdio.h>

int gcd(int a, int b) {
    if (b == 0)
        return a;
    else
        return gcd(b, a % b);
}

int lcm(int a, int b) {
    return (a / gcd(a, b)) * b;
}

int main() {
    int i, n, temp = 1;

    printf("Enter the number of input numbers: ");
    scanf("%d", &n);

    for(i=0; i<n; i++) {
        printf("Enter number %d: ", i+1);
        scanf("%d", &temp);

        if(i == 0)
            continue;
        temp = lcm(temp, i);
    }

    printf("\nThe Least Common Multiple among the input numbers is: %d\n", temp);

    return 0;
}
