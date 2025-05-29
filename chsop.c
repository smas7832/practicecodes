#include<stdio.h>


//Switch For Arithemtic operations
int sum(char c, int n, int m){
    switch(c){
        case '+':return n+m;
        case '*':return n*m;
        case '/':return n/m;
        case '-':return n-m;
    }
}




int main(){

    int n1, n2;

    printf("Enter N1:\t");
    scanf("%d",&n1);
    printf("Enter N2:\t");
    scanf("%d",&n2);
    printf(" Sum is :%d\n Subtraction is:%d\n Product is:%d\n Division is:%d\n ",sum('+', n1, n2),sum('-', n1, n2),sum('*', n1, n2),sum('/', n1, n2));

}