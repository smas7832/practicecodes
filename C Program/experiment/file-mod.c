#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// 1. Define your structure
typedef enum { TODO, IN_PROGRESS, DONE } taskStatus;

struct task {
    time_t save_time;
    time_t last_edit;
    char* description;
    taskStatus status;
};

// 2. Define the macro BEFORE including the header
#define STRUCT_DATA_TYPE struct task
#define LINKEDLIST_IMPLEMENTATION
#include "relinked-list-exp.h"

int main() {
    FILE* file = fopen("tasks.txt", "r");
    if (file == NULL) {
        perror("File opening failed");
        return 1;
    }

    struct node* HEAD = NULL;
    STRUCT_DATA_TYPE temp;
    printlist(HEAD);

    // 3. The Loading Loop
    // Reads: save_time, last_edit, description (auto-malloc), status
    while (fscanf(file, "%ld,%ld,%m[^,],%d\n", &temp.save_time, &temp.last_edit,
                  &temp.description, &temp.status) == 4) {
        insertElement(&HEAD, temp);
    }

    fclose(file);

    // 4. Display and Cleanup
    struct node* current = HEAD;
    while (current != NULL) {
        printf("[%ld] Task: %s\n", current->data.save_time,
               current->data.description);

        // IMPORTANT: Since %m allocated memory, we must free it
        free(current->data.description);

        struct node* next = current->next;
        free(current);  // Free the node itself
        current = next;
    }

    return 0;
}
