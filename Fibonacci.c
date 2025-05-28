#include<stdio.h>
//Fibonacci series

int fib(int n){
  if(n==1 || n==0){
      return 1;
    }
  else{
      return fib(n-2) + fib(n-1);
    }
  }

int main(){
  printf("Enter Value Of X: \t");
  int x;
  scanf("%d",&x);
  int result = fib(x);
  printf("Result is: %d\n", result);
  
return 0;
}
