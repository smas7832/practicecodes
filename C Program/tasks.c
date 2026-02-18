#include "include/STB/linkedlist.h"
#include <stdio.h>
#include <strings.h>
#include <time.h>
/*
.Store tasks in an array of structs (each task has a description and status).
"Implement a menu-driven interface (e.g., 1 to add, 2 to delete, 3 to view,
etc.). Save tasks to a file and load them on startup.
*/

typedef enum { TODO = 0, DONE = 1, NILL = -1} taskStatus;

struct task {
  time_t save_time;
  time_t last_edit;
  char *description;
  taskStatus status;
};

// TODO: create a file to structure and structure loader.

struct task *fileToTask(){

}
struct task *loadTaskFile(FILE *pointer) {
  if (pointer == NULL) return NULL;
  char *buffer;

}
