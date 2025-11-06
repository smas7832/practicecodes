#include <stdio.h>
#include <stdlib.h>

struct element {
  int data;
  struct element *Below;
};

void push(struct element **top, int data) {
  struct element *newElement = (struct element *)malloc(sizeof(struct element));

  if (newElement == NULL) {
    printf("Memory allocation failed! Cannot push data.\n");
    return;
  }
  newElement->data = data;
  newElement->Below = *top;
  *top = newElement;
}

void pop(struct element **top) {
  if ((*top) == NULL) {
    printf("\nStack is Empty - Cannot pop.");
    return;
  }

  struct element *temp = *top;
  *top = temp->Below;
  free(temp);
  printf("\nSuccessfully popped TOP element.");
}

void printStack(struct element *top) {
  if (top == NULL) {
    printf("Stack is Empty\n");
    return;
  }

  struct element *temp = top;
  do {
    printf("Data : %d\n", temp->data);
    temp = temp->Below;
  } while (temp != NULL);
}

void freeStack(struct element **top) {
  struct element *current = *top;
  struct element *next;

  while (current != NULL) {
    next = current->Below;
    free(current);
    current = next;
  }
  *top = NULL;
}

int main(int argc, char *argv[]) {

  if (argc < 2) {
    printf("Usage: %s <integer_value>\n", argv[0]);
    return 1;
  }

  int input = atoi(argv[1]);
  int iterration = atoi(argv[2]);
  struct element *top = NULL;

  printf("\n--- Start Stack Operations ---");

  for (int i = 0; i < iterration; i++) {
    push(&top, input * i + 1);
  }
  printStack(top);
  pop(&top);
  printStack(top);
  freeStack(&top);
  return 0;
}
