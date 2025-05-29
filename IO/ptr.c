#include<stdio.h>
#include<string.h>


int main(){
    FILE *ptr;
    char ch[100];
    printf("Enter file Location:\t");
    scanf("%s",&ch);
    ptr=fopen(ch, "r");
    fprintf(ptr,"\n%s",ch);
}