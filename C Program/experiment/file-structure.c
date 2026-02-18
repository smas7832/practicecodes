#include <stdio.h>
#include <time.h>

enum status { DONE = 1, PENDING = -1, NILL = 0 };
struct task {
    time_t save_time;
    time_t last_edit;
    char* description;
    enum status status;
};
int main() {
    FILE* fp = fopen("example.txt", "a+");
    if (fp == NULL) {
        printf("file creation/reading failed.");
    }
    printf("\nEnter details for structure: \n");
    printf("Description of task: ");
    // gets();
    struct task temp;
    temp.status = NILL;
    temp.last_edit = 0;
    temp.save_time = 0;
    struct task task1;
    fscanf(fp, "%ld,%ld,%m[^,],%d\n", &task1.save_time, &task1.last_edit, &task1.description, &task1.status);
}
