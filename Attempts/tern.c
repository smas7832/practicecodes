
#include<stdio.h>

/**
 * This program compares two integers entered by the user and prints 
 * the larger of the two.
 * 
 * @return 0 upon successful execution
 */
int main() {
    int M, N;

    printf("Enter First Value: \n");
    scanf("%d", &M);
    printf("Enter Second Value: \n");
    scanf("%d",&N);

    (M>N) ? printf("%d Is Greater Than %d",M ,N )
    : printf("%d Is Greater Than %d", N ,M);
    return 0;
}