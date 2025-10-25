#include <stdio.h>
#include <stdlib.h>

struct element{
  int data;
  struct element *nextElement;
};
struct element* push(int data /*struct element *previous*/){
    struct element *newElement = (struct element *) malloc(sizeof (struct element));
    newElement->data = data;
    newElement->nextElement = NULL;
    return newElement;
}

// int push(int data, struct element *top){
//
//
// }

int main(){
  struct element *top;
  top-> data = 10;
  top->nextElement = push(17);
  printf("stack1: %d, \n stack2: %d", top->data, top->nextElement->data);
  return 0;
}
