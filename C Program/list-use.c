#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define LINKEDLIST_IMPLEMENTATION
#include "include/STB/linkedlist.h"

void randomSeed() { srand(time(NULL)); }

int randomInt(int min, int max) {
  int rd_num = rand() % (max - min + 1) + min;
  return rd_num;
}

int main(int argc, char *argv[]) {
  if (argc == 1) {
    printf("Please give number of nodes.");
    return 0;
  }
  randomSeed();

  int input = atoi(argv[1]);
  node *HEAD = NULL;
  printlist(HEAD);


  for (int i = 0; i < input; i++) {
    insertNode(&HEAD, randomInt(input, input * 5));
  }
  int *array = (int *)malloc(listlen(HEAD) * sizeof(int));
  array = listtoarr(HEAD);
  int length = listlen(HEAD);

  for (int i = 0; i < length; i++) {
    printf("\n%d", array[i]);
  }
  printlist(HEAD);
  deleteList(&HEAD);
  return 0;
}
