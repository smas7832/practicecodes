#include<stdio.h>
#include<stdlib.h>

struct node{
  int data;
  struct node *next;
};

void insertNode(int data, struct node **HEAD){
  struct node *newNode =(struct node *)malloc(sizeof(struct node));
  newNode-> data = data;
  newNode-> next = NULL;
  if (*HEAD == NULL){
    *HEAD = newNode;
    return;
  }

  struct node *temp = *HEAD;
  while (temp->next != NULL){
    temp = temp->next;
  }
  temp->next = newNode;
}

void printList(struct node *HEAD){
  int i = 0;
  struct node *temp = HEAD;
  printf("Node\t\tData\t\tAdress\n");

  while(temp->next !=NULL){
    printf("%d\t\t%d\t\t%p\n",i,temp->data,temp);
    temp = temp->next;
    i +=1;
  }
  printf("NULL\n");
}

 int main(int argc, char *argv[]){
   struct node *HEAD = NULL;
   int n = atoi(argv[1]);
   for(int i = 0; i<=n; i++){
     insertNode(i+i*i, &HEAD);
   }
  printList(HEAD);

}
