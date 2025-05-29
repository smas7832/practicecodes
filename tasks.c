#include <stdio.h>
#include <string.h>
/*
.Store tasks in an array of structs (each task has a description and status).
"Implement a menu-driven interface (e.g., 1 to add, 2 to delete, 3 to view, etc.).
Save tasks to a file and load them on startup.
*/

typedef enum
{
    TODO,
    DONE,
    NILL
} TaskStatus;

typedef struct
{
    char desc[50];
    TaskStatus status;
} Task;

int view_task(Task *task)
{
    printf("Task: %s\n", task->desc);
    printf("Status: %d\n", task->status);
    return 0;
}

int add_task(Task *task)
{
    printf("Enter description of the task:");
    scanf("%s", &task->desc);
    return 0;
}

int delete_task(Task *task)
{
    printf("Enter ID of the task to be deleted:");
    scanf("%d", &task->status);
    return 0;
}

int main()
{
    int choice;
    int i = 0;
    Task tasks[10];
    for (i = 0; i < 10; i++)
    {
        tasks[i].status = NILL;
    }

    do
    {
        printf("\n\n");
        printf("Menu:\n");
        printf("1. Add task\n");
        printf("2. Delete task\n");
        printf("3. View task\n");
        printf("4. Exit\n");
        scanf("%d", &choice);
        switch (choice)
        {
        case 1:
            add_task(&tasks[i]);
            i++;
            break;
        case 2:
            delete_task(&tasks[i]);
            i--;
            break;
        case 3:
            view_task(&tasks[i]);
        }
    } while (choice != 4);
    return 0;
}