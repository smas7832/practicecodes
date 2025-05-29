#include<stdio.h>
//Array of n nos, element sum using pointer

int main(){
    int n,sum=0;
    printf("Enter Length of Array");
    scanf("%d",&n);
    int *arr[n];
    printf("\nEnter Elements Of Array:-");
    for(int i=0; i<=n; i++){
        printf("\nElement %d:",i );
        scanf("%d",arr[i]);
    }
    int *ptr = arr[n];
    int *in= arr[0];
    // for(int i=0; i<=n; i++){
    //     sum=sum + *

    // }
}

