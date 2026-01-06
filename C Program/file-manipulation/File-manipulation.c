#include<stdio.h>
#include <errno.h>

int main(){
    char *path;
    printf("Enter Filename: ");
    fgets(path, 50, stdin);
    FILE* text = fopen(path, "w+");
    printf("errorcode: %d", errno);
    perror("\nError:");

    if (text == NULL){
        perror("\nError:");
      }else{
        printf("\nSuccess\n");
      }
    for (int i=1; i< 10; i++){
        fprintf(text, " Line NO. Is %d\n", i);
    }
    fclose(text);

    text =fopen("sample.txt", "a");
    for (int i=1; i< 10; i++){
        fprintf(text, " Newline no. is %d \n", i);
    }
    char file [100];
    fgets(file, sizeof(file), text);
    printf("Data in file is: \n %s", file);

}
