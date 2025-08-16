#include<stdio.h>

struct node{
  int data;
  struct node *next;
};

struct node HEAD;

 int main(){
   struct node node1;
   HEAD = &node1;
   node1.data = 10;
   printf("Node1:\n\tAdress: %p\n\tData: %d", HEAD, node1.data);
}
