#include <stdio.h>
#include <strings.h>

int main (){
    char path[50];
    fgets(path, 50, stdin);

    FILE* fptr;
    fptr= fopen(path, "r" );

    if (fptr == NULL){
        printf("Failed To Load Data \n");
    } else {
        printf("File Read Successfully");
    }
    fprintf(fptr, "path");


}

