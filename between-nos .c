/*ii. Write a ‘C’ program to display all numbers between two given 
numbers.*/

#include <stdio.h>

int main(){
    int start, end;

    printf ("start and end nos");
    scanf ("%d, %d",&start, &end);

    if(start>end){
        printf("invalid");
        return 1;
    }
    printf("nos between are:");
    for(int i=start+1; start <end ; i++){
        printf("%d", i);
    }
    return 0;
}