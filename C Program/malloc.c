#include<stdio.h>
#include<stdlib.h>
#include<strings.h>


//Pointer Dynamic Mamery Location
int main(){
    int n=3;

    char *ptr = malloc(n * sizeof(char));
   
    for(int i=0;i<=n;i++ ){
    puts("\nCharachter:");
    scanf("%c",&ptr[0]);
    puts("\nCharcter Is : ");
    printf("%c",ptr[0]);
    }
    int *ptr= calloc(n, sizeof(int));
    for(int i=0; i<=n;i++ ){
        printf("\nEnter Num %d: ", i);
        scanf("%d", &ptr[i]);
        printf("%d",ptr[i]);
    }

}