#ifndef LINKEDLIST_H
#define LINKEDLIST_H
#include <stdint.h>
#include <stdio.h>
// Trying to create a dynamic linked list with ability to define custom data
// type by the user
#ifndef STRUCT_DATA_TYPE
#define STRUCT_DATA_TYPE int
#endif
#define SAFE_FREE(p) \
    free(p);         \
    p = NULL

struct node {
    STRUCT_DATA_TYPE data;
    struct node* next;
};

int insertElement(struct node** HEAD_ref, STRUCT_DATA_TYPE data);
void printlist(struct node* HEAD);
int freeStruct(struct node** HEAD_ref);

#endif

#ifdef LINKEDLIST_IMPLEMENTATION
int insertElement(struct node** HEAD_ref, STRUCT_DATA_TYPE data) {
    if ((*HEAD_ref) == NULL) {
        (*HEAD_ref) = (struct node*)malloc(sizeof(struct node));
        if ((*HEAD_ref) == NULL) return -1;
        (*HEAD_ref)->data = data;
        (*HEAD_ref)->next = NULL;
        return 0;
    }
    struct node* temp = (*HEAD_ref);
    while (temp->next != NULL) {
        temp = temp->next;
    }
    struct node* temp2 = (struct node*)malloc(sizeof(struct node));
    if (temp2 == NULL) return -1;
    temp2->next = NULL;
    temp2->data = data;
    temp->next = temp2;
    return 0;
}

void printlist(struct node* HEAD) {
    if (HEAD == NULL) {
        printf("Empty list");
        return;
    } else {
        printf("\n");
        struct node* temp = HEAD;
        while (temp != NULL) {
            printf("\n%d\t\t%p", temp->data, temp);
            temp = temp->next;
        }
    }
    return;
}

int freeStruct(struct node** HEAD_ref) {
    if ((*HEAD_ref) == NULL) return 0;
    struct node* temp;
    while ((*HEAD_ref) != NULL) {
        temp = (*HEAD_ref)->next;
        SAFE_FREE((*HEAD_ref));
        *HEAD_ref = temp;
    }
    if ((*HEAD_ref) != NULL) return -1;
    return 0;
}

#endif
