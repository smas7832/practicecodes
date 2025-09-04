#include<stdio.h>
#include<stdlib.h>
#include<time.h>

struct node{
  int data;
  struct node *next;
};

void randomSeed(){
  srand(time(NULL));
}

int randomInt(int min, int max) {
	int rd_num = rand() % (max - min + 1) + min;
	return rd_num;
}
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

void freeList(struct node *HEAD){
  struct node *current = HEAD;
  struct node *nextNode;
  while(current != NULL){
    nextNode = current->next;
    free(current);
    current = nextNode;
  }
}

void deleteNode(struct node **HEAD, struct node *delete){
    if (*HEAD == NULL && delete == NULL){
      printf("Error: Empty list or invalid node");
      return;
    }

    if (*HEAD == delete){
      *HEAD=delete->next;
      free(delete);
      printf("Head Node deleted\n");
      return;
    }


    struct node *pvsNode = *HEAD;
    while(pvsNode->next != NULL && pvsNode->next != delete){
      pvsNode = pvsNode->next;
    }
    pvsNode->next = delete->next;
    free(delete);
}

int searchNode(struct node *HEAD, int target){
  struct node *current=HEAD;
  int count = 0;
  while(current !=NULL){
    if(current->data == target){
      return count;
    }
    current = current->next;
    count++;
  }
  return -1;
}

void printList(struct node *HEAD){
  if(HEAD==NULL){
    printf("\nEmpty list");
    return;
  }
  int i = 0;
  struct node *temp = HEAD;
  printf("Node\tData\tAdress\t\t\tnextNode\n");

  while(temp !=NULL){
    printf("%d\t%d\t%p\t\t%p\n",i,temp->data,temp,temp->next);
    temp = temp->next;
    i +=1;
  }
  printf("\n\t-----------------END-----------------\n");
}

 int main(int argc, char *argv[]){
   struct node *HEAD = NULL;
   int n = atoi(argv[1]);
   int target = atoi(argv[2]);
   randomSeed();
   for(int i = 0; i<n; i++){
     insertNode(randomInt(i,i*10), &HEAD);
   }
  printList(HEAD);
  int result = searchNode(HEAD, target);
  if (result == -1){
    printf("\nCouldn't find the node");
  }else{
    printf("\nnode is at index: %d ", result);
  }
  freeList(HEAD);
  return 0;
}
