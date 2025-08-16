#include<stdio.h>
#include<stdlib.h>
// Singly Linked list

typedef struct{
	int data;
	void* next;
}nodes;
nodes* HEAD;

//fn for creating node
void *createNode(int value, nodes *node){
	nodes *newNode;
	node->next = &newNode;
	newNode->data = value;
	newNode->next = NULL;
	return newNode;
}

//fn to delete node
void deleteNode(nodes * node, nodes *pvsNode){
	 pvsNode->next = node->next;
	 free(node);
}

//fn to print list
int printlist(nodes *HEAD){
	nodes *p = HEAD;
	while(p != NULL) {
		printf(" %d ",p->data);
		p = p->next;
		if(p->next == NULL)
			{return 1;}
	}
	return 0;
}

int main(){
	nodes *node[5];
	for(int i =0; i<5;i++){
		node[i] = malloc(5* sizeof(nodes));
	}

	HEAD->next = &node;
	int choice = 1;
	while (choice != 0){
		printf("\n1.Print Nodes In the list\n2.delete a node\n3.insert a node\n");
		printf("\n^___________________________\n");
		printf("Select operation to peform:");
		scanf("%d",&choice);
		switch(choice){
			case 1:
				printlist(HEAD);
			case 2:
				deleteNode(node[4], node[3]);
				printf("\noperation successful");
			case 3:
				printf("Enter Node Value and position\n");
				int value; scanf("%d", &value);
				// insertNode(node)
			case 4:
				return 0;
			default: printf("\nInvalid operation\n");
		}
	}
	// node[1]->next = createNode(1);
	// for(int i = 1; i<5;i++){
	// 	printf("\n node1 : %p", node[i]);
	// 	printf("\n HEAD : %p", node);
}
