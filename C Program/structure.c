#include <stdio.h>
#include <stdlib.h>

typedef struct master {
  int num_slaves;
  char name[50];
} mtr;

void function(int num) {
  mtr m[num];
  for (int i = 0; i < num; i++) {
    printf("Slave %d\n", i + 1);
    m[i].num_slaves = i + 1;
    printf("Enter your name:");
    scanf("%s", m[i].name);
    printf("Hello, %s!\n", m[i].name);
  }
}

int main(int argc, char *argv[]) {
  int num;

  if (argc < 2) {
    printf("Usage: %s <num of slaves>\n", argv[0]);
    return 1;
  }

  num = atoi(argv[1]); // Convert the command-line arg to an integer

  int choice = 1;
  while (choice) {
    function(num);
    printf("\nEnter 0 to exit or any other number to continue:");
    scanf("%d", &choice);
  }

  return 0;
}