#include<stdio.h>

//Swap two numbers using pointers

int change(int* num1, int *num2){
    int t=*num1;
    *num1=*num2;
    *num2=t;
}

int main(){

    int n1=10, n2=20;
    int *num1=&n1, *num2=&n2;
    printf("num1: %d\t Num2: %d \n",*num1, *num2);
    change(num1, num2);
    printf("num1: %d\t Num2: %d \n",*num1, *num2);
}