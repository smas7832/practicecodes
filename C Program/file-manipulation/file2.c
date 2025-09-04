#include <stdio.h>
#include <stdlib.h>

int main(){
    FILE *fp; char filename[50];
    printf("Enter Filename: ");
    scanf("%s",&filename);
    printf("%s",filename);
    fp = fopen(filename, "w");
    if (fp == NULL){
        printf("Error Occured");
    }
    fprintf(fp, "Maan Jaan", stdin);

}
