#include <stdio.h>
#include <stdlib.h>

#define MAX_NODES 100

typedef struct {
    int data;
    struct Node* left;
    struct Node* right;
} Node;

typedef struct {
    Node* items[MAX_NODES];
    int top;
    int top;
} Stack;

void push(Stack* stack, Node* node) {
    if (stack->top < MAX_NODES) {
        stack->items[stack->top++] = node;
    }
}

Node* pop(Stack* stack) {
    if (stack->top > 0) {
        return stack->items[--stack->top];
    }
    return NULL;
}

int isEmpty(Stack* stack) {
    return stack->top == 0;
}

Node* createNode(int data) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->data = data;
    node->left = NULL;
    node->right = NULL;
    return node;
}

void dfs(Node* root) {
    if (root == NULL) return;
    
    Stack stack = {.top = 0};
    push(&stack, root);
    
    while (!isEmpty(&stack)) {
        Node* node = pop(&stack);
        printf("%d ", node->data);
        
        if (node->right) push(&stack, node->right);
        if (node->left) push(&stack, node->left);
    }
}

int main() {
    Node* root = createNode(1);
    root->left = createNode(2);
    root->right = createNode(3);
    root->left->left = createNode(4);
    root->left->right = createNode(5);
    
    printf("DFS Traversal: ");
    dfs(root);
    printf("\n");
    
    return 0;
}