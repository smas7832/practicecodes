#include<stdio.h>


//calculate factorial of a given no.

int main(){
    int n, factorial;

    printf("Enter The No:\t");
    scanf("%d",&n);

    int arr[n];

    printf("%d! =", n);
    for (int i = 1; i <= n; i++) {
        factorial *= i;
        printf("%d", i);
        if (i < n) {
            printf(" * ");
        }
    }

    printf(" = %llu\n", factorial);

    return 0;
}
