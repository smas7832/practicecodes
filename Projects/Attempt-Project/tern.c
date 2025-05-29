#include<stdio.h>


int main(){
    int M,N;

    printf("Enter First Value: \n");
    scanf("%d", &M);
    printf("Enter Second Value: \n");
    scanf("%d",&N);

    (M>N) ? printf("%d Is Greater Than %d",M ,N )
    : printf("%d Is Greater Than %d", N ,M);
    return 0;
}