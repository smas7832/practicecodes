#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

struct node {
  int data;
  struct node *l_node;
  struct node *r_node;
};

struct node *root;

#define globalv(x) root = *x

int main() {
  struct node **local_root = &root;
  globalv(local_root);
  printf("\n%p : %d : ", root, errno);

  perror("");

  (*local_root)->data = 10;
  (*local_root)->l_node = (struct node *)malloc(sizeof(struct node));
  perror("");
  (*local_root)->r_node = (struct node *)malloc(sizeof(struct node));
  perror("");
  printf("\n%p", (*local_root)->l_node);
  printf("\n%p", (*local_root)->r_node);
  printf("\n%d", (*local_root)->data);
}
