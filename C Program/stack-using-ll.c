#include <stdio.h>
#define LINKEDLIST_IMPLEMENTATION
#include "include/STB/linkedlist.h"
#define MAX_LEN 10  // maximum length of stack

node* HEAD = NULL;

/*--Properties Of Stack--
 * follows Last In, First Out (LIFO) principle.
 * Core Operations:
 *      Push: Adds an element to the top.
 *      Pop: Removes the top element (causes underflow if empty).
 *      Peek/Top: Returns the top element without removing it.
 *      isEmpty: Checks if the stack is empty.
 *      Size: Returns the number of elements.
 */

// push elemet to stack
int push(int data) {
    if (listlen(HEAD) == MAX_LEN) return -1;
    if (insertNode(&HEAD, data) == 0) return 0;
    return -1;
}

int pop() {
    // if(listlen(HEAD) == 0) return -1;
    if (deleteNode(&HEAD, HEAD->data) == 0) return 0;
    return -1;
}

int peek() { return HEAD->data; }

int isEmpty() { return listlen(HEAD) == 0; }
int Size() { return listlen(HEAD); }

int main() {
    for (int i = 0; i < 11; i++) {
        int flag = push(i + 1);
        if (flag == -1) {
            printf("ERROR: %d", flag);
            break;
        }
        printf("Index %d : %d\n", i, flag);
    }
    printf("\n\nSize : %d", Size());
    printf("\npop : %d", pop());
    printf("\nPeek : %d", peek());
    printf("\nIsempty : %d", isEmpty());
    printf("\nSize : %d", Size());
    printlist(HEAD);
}
