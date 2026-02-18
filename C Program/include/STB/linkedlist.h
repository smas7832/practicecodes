#ifndef LINKEDLIST_H
#define LINKEDLIST_H

#include <stdio.h>
#include <stdlib.h>

// Safely frees a pointer
#define SAFE_FREE(p) \
    do {             \
        free(p);     \
        p = NULL;    \
    } while (0)

typedef struct node {
    int data;
    struct node* nextNode;
} node;

//inset a new node to end of list
int insertNode(node** HEAD_ref, int data);

//deletes a linked list
//return 0:successfully deleted the list
int deleteList(node** HEAD_ref);

//Deletes a node associated with data
int deleteNode(node** HEAD_ref, int data);

//prints list in sequential order
void printlist(node* HEAD);

// returns an array pointer of given linked list
int* listtoarr(node* HEAD);

//returns number of elements in the list
int listlen(node* HEAD);

#endif

#ifdef LINKEDLIST_IMPLEMENTATION

int listlen(node* HEAD) {
    if (HEAD == NULL) return 0;

    int length = 1;
    node* temp = HEAD;
    while (temp->nextNode != NULL) {
        temp = temp->nextNode;
        length++;
    }
    return length;
}

int insertNode(node** HEAD_ref, int data) {
    // node **HEAD = HEAD_ref
    if ((*HEAD_ref) == NULL) {
        (*HEAD_ref) = (node*)malloc(sizeof(node));
        (*HEAD_ref)->data = data;
        (*HEAD_ref)->nextNode = NULL;
        return 0;
    }

    node* head_tracker = (*HEAD_ref);
    while (head_tracker->nextNode != NULL) {
        head_tracker = head_tracker->nextNode;
    }

    node* temp = (node*)malloc(sizeof(node));
    temp->data = data;
    temp->nextNode = NULL;
    head_tracker->nextNode = temp;
    return 0;
}

int deleteList(node** HEAD_ref) {
    if ((*HEAD_ref) == NULL) return 0;
    node* temp = (*HEAD_ref);
    while ((*HEAD_ref) != NULL) {
        temp = (*HEAD_ref);
        (*HEAD_ref) = (*HEAD_ref)->nextNode;
        free(temp);
    }
    return 0;
}

int deleteNode(node** HEAD_ref, int data) {
    if ((*HEAD_ref) == NULL || (*HEAD_ref)->data != data) return -1;

    node* temp;
    if ((*HEAD_ref)->data == data) {
        temp = (*HEAD_ref);
        (*HEAD_ref) = (*HEAD_ref)->nextNode;
        SAFE_FREE(temp);
        return 0;
    }
    node* saved_node;
    while (temp->data != data && temp->nextNode != NULL) {
        saved_node = temp;
        temp = temp->nextNode;
    }
    if (temp->data != data && temp->nextNode == NULL) return 0;
    if (temp->data == data) {
        saved_node->nextNode = temp->nextNode;
        SAFE_FREE(temp);
    }
    return 0;
}

void printlist(node* HEAD) {
    if (HEAD == NULL) {
        printf("\nEmpty List\n");
        return;
    }
    printf("\n\t\n");
    printf("\tLinked List Elements\n");
    printf("\n\tIndex\t-\tData\n");

    node* temp = HEAD;
    int i = 0, length = 0;
    while (temp != NULL) {
        printf("\t%d\t-\t%d\n", i, temp->data);
        temp = temp->nextNode;
        i++;
        length++;
    }
    printf("\t----EOL----\n");
    printf("Length of list: %d", length);
    printf("\n");
}

int* listtoarr(node* HEAD) {
    if (HEAD == NULL) return NULL;

    node* temp = HEAD;
    int* array = (int*)malloc(listlen(HEAD) * sizeof(int));
    if (array == NULL) return NULL;
    for (int i = 0; temp != NULL; temp = temp->nextNode, i++) {
        array[i] = temp->data;
    }
    return array;
}

#endif
