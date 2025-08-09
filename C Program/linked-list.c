#include<stdio.h>
#include<stdlib.h>
// Singly Linked list
void* HEAD;

typedef struct{
	int data;
	void* next;
}nodes;

//fn for creating node

void *createNode(int value, nodes *node){
	nodes *newNode;
	node->next = &newNode;
	newNode->data = value;
	newNode->next = NULL;
	return &newNode;
}

int main(){
	nodes *node[5];

	for (int i = 0; i<5; i++)
	{
		node[i] = malloc(sizeof(nodes));
		printf("\n node %d : %p", i, node[i]);
	}

	HEAD = &node[0];
	printf("\n HEAD : %p", HEAD);
	printf("\n NODE1 : %p", node[0]);
	// node[1]->next = createNode(1);
	for(int i = 1; i<5;i++){
		node[i] = createNode(i, node[i-1]);
		printf("\n node1 : %p", node[i]);
		printf("\n HEAD : %p", node);
}
	for(int i = 0; i<5; i++){
		free(node[i]);
	}
}
