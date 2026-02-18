#include<stdio.h>
#include "stdlib.h"
#define LINKEDLIST_IMPLEMENTATION
#define STRUCT_DATA_TYPE char
#include "relinked-list-exp.h"

int main(int argc, char* argv[]) {
    struct node* HEAD = NULL;
    int n = atoi(argv[1]);
    printlist(HEAD);
    for(int i=0; i<10;i++){
        if(insertElement(&HEAD, n*i)==-1){
            printf("\nMemory Allocation Failed. @%d", i);
        }
    }
    printlist(HEAD);
    if(freeStruct(&HEAD) == -1){
        printf("\nMemory Deallocation failed.");
    }
}
