#include <stdio.h>
#include <stdbool.h>

int main() {
    bool ans = false;
    int T;

    printf("Answer in True or False (0 for false & 1 for true) \n");
    printf("2 is an odd number.\n");
    scanf("%d", &T);

    // To Convert the integer input to a bool value
    if (T != 0 && T != 1) {
        printf("Invalid input! Please enter 0 or 1.\n");
        return 1;  // for invalid input
    }

    if (ans == T) {
        printf("Dumbo\n");
    } else {
        printf("Smart\n");
    }

    return 0;
}
