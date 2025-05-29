#include<stdio.h>


int main(){
    char path[50];
    printf("Enter Filename: ");
    fgets(path, sizeof(path), stdin);

    FILE* text = fopen(path, "w");

    if (text == NULL)
        printf(" Failed To read Or Create the file.");
    else
        printf("Success\n");

    for (int i=1; i< 10; i++){
        fprintf(text, " Line NO. Is %d\n", i);
    }
    fclose(text);

    text =fopen("sample.txt", "a");
    for (int i=1; i< 10; i++){
        fprintf(text, " Newline no. is %d \n", i);
    }
    char file [100];
    // fgets(file, sizeof(file), stdin);
    printf("Data in file is: \n %s", text);

}
