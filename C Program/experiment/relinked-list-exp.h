#ifndef LINKEDLIST_H
#define LINKEDLIST_H
#include <stdint.h>
#include <stdio.h>

// dynamic linked list with ability to let user define custom data type

#ifdef DATA_PRINT_METHOD
#define DATA_PRINT_METHOD(member)               \
    struct node* temp = HEAD;                   \
    while (temp != NULL) {                      \
        printf("\n%d\t\t%p", temp->data, temp); \
        temp = temp->member;                    \
    }

#endif

#define SAFE_FREE(p) \
    free(p);         \
    p = NULL

struct node {
    void* data;
    struct node* next;
};

int insertElement(struct node** HEAD_ref, void* data);
void printlist(struct node* HEAD);
int freeStruct(struct node** HEAD_ref);

#endif

#ifdef LINKEDLIST_IMPLEMENTATION
int insertElement(struct node** HEAD_ref, void* data) {
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
        DATA_PRINT_METHOD
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
