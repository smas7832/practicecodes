#include <stdio.h>
#include <stdlib.h>

struct element{
    int data;
    struct element *next;
};

void enqeue(struct element **head, int data){
    if(*head == NULL){
        *head = (struct element *) malloc(sizeof(struct element));
        (*head)->next= NULL;
        (*head)->data= data;
    }
    struct element *temp = (struct element *) malloc(sizeof(struct element));
    temp->next = *head;
    temp->data = data;
    *head = temp;
}

int main(){

    return 0;
}
