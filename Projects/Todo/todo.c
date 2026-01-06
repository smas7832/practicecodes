#include <stdio.h>
#include <stdlib.h>
/*
 Features:
        . Store tasks in an array of structs (each task has a description and
 status). . Implement a menu-driven interface (e.g., 1 to add, 2 to delete, 3
 toview, etc.). . Save tasks to a file and load them on startup.
*/
typedef enum status { DONE, PENDING, NSET } status;

typedef struct {
  int Tasknum;
  char task[50];
  status status;
} task;

int main() {
  FILE *taskf;
  taskf = fopen("task", "r+");

  task *tasks;
  tasks = malloc(5 * sizeof(task));
  for (int i = 0; i < 5; i++) {
    (tasks + i)->Tasknum = i;
    (tasks + i)->status = NSET;
  }
}
