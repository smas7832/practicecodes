#include<stdio.h>
#include<stdbool.h>

int main() {

    const bool ans=0;
    double T;
    int Q=2;

    printf("Answer In True Or False (0 for false & 1 For true) \n");
    printf("2 Is Odd No.\n");
    scanf("%d", &T);

    if (ans==T){
        printf("Dumbo");
    } else {
        printf("Smart");
    }
    fprintf("out.txt, Alone %d", Q);
}
