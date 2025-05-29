#include <stdio.h>
#include <stdlib.h>



int main(){
    char path[50];
    printf("Enter Path to the file: ");
    scanf("%s", &path);
    FILE *fp = fopen(path, "w");
    if(fp == NULL){
        perror("Error opening file");
        exit(1);
    }
    fprintf(fp, path, stdin);
    char line = fgetc(fp);
    printf("%c\n", line);


    


}