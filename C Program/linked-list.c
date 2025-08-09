#include<stdio.h>
#include<stdlib.h>
// Singly Linked list 
void* HEAD;

typedef struct{
	int data;
	void* next;
}nodes;

//fn for creating node

void *createNode(int value){
	nodes *newNode;
	newNode->data = value;
	newNode->next = NULL;
	return &newNode;
}

int main(){
	nodes *node= (nodes*)calloc(5, sizeof(nodes));;
	//node[5] 
	HEAD = &node[1];
	node[1]->next = createNode(1);
	for(int i = 2; i<5;i++){
		node[i-1]->next = createNode(i);
	}
	printf("\n HEAD : %p", HEAD);
	//printf("\n node1 : %p", node);
}
