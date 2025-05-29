#include<stdio.h>
#include <math.h>


int main(){

    //To find i/p is Even Or Odd

    int x;
    printf ("Enter The Number : ");
    scanf ("%d \n", &x);
    printf("%d \n", x % 2 == 0 );
    return 0;
}