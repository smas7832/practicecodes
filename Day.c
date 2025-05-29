#include<stdio.h>

//if-else Codition

int main(){
    int s;
    char c; // This is not a placeholder, it's the input character
    printf("Enter a day number (1-7): ");
    scanf("%d", &s); // This is the actual input for the user
    if(s == 1){ // If the user inputs a number greater than 6, this condition will be executed
        printf("Monday\n");
    }
}