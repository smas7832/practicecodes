#include<stdio.h>
int main(){

    int prices[4]={100,200,300,400};
    int n=0;

    for(int i=0; i<4; i++){
        n+=prices[i];
    }
    printf("Sum:- %d",n);
    }