#ifndef LINKEDLIST_H
#define LINKEDLIST_H

#include <stdio.h>
#include <stdlib.h>

//Safely frees a pointer
#define SAFE_FREE(p) \
    do {             \
        free(p);     \
        p = NULL;    \
    } while (0)

typedef struct node {
    int data;
    struct node* nextNode;
} node;

/// @brief inset a node to end of list
/// @param HEAD_ref pointer->pointer->HEAD_NODE
/// @param data 
int insertNode(node **HEAD_ref, int data);

/// @brief deletes a linked list
/// @param HEAD_ref pointer->pointer->HEAD_NODE
/// @return 
int deleteList(node** HEAD_ref);

/// @brief Deletes a node associated with \@param data
/// @param HEAD_ref 
/// @param data 
/// @return 
int deleteNode(node** HEAD_ref, int data);

/// @brief 
/// @param HEAD 
void printlist(node* HEAD);

/// @brief 
/// @param HEAD 
/// @return 
int* listtoarr(node* HEAD);

/// @brief 
/// @param HEAD 
/// @return 
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
    if ((*HEAD_ref) == NULL) return -1;
    node* temp;

    temp = (*HEAD_ref);
    if ((*HEAD_ref)->data == data) {
        (*HEAD_ref) = (*HEAD_ref)->nextNode;
        SAFE_FREE(temp);
        temp = NULL;
        return 1;
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
    return 1;
}

void printlist(node* HEAD) {
    if (HEAD == NULL) {
        printf("\nEmpty List\n");
        return;
    }
    printf("\n\t╔════════════════════════════╗\n");
    printf("\t║   Linked List Elements     ║\n");
    printf("\t╚════════════════════════════╝\n");
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