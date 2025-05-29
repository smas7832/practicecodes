#include<stdio.h>

//Print array elements using pointer arithmetic

int main(){

    int arr[10];
    int *ptr=&arr[1],*ptr2=&arr[10];
    int n=0;
    printf("Enter Values:\t");
    for (int *i=ptr;i<ptr2;i++){
        n++;
        scanf("%d",&arr[n]);
    }
    for (int i=arr[1];i<arr[10];i++){
        printf("%d",arr[i]);
    }
}