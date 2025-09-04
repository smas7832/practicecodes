#include <stdio.h>

int main() {
    int scores[3][4] = {
        {10, 20, 30, 40},
        {50, 60, 70, 80},
        {90, 100, 110, 120}
    };

    int scalar = 2;

    // Multiply the scores by the scalar
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 4; j++) {
            scores[i][j] *= scalar;
        }
    }

    // Print the results
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 4; j++) {
            printf("%d ", scores[i][j]);
        }
        printf("\n");
    }

    return 0;
}