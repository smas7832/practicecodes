#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "include/STB/quicksort.h"

int binaryS(int array[], int size, int target) {
    int low = 0;
    int high = size - 1;
    int mid;

    while (!(low >= high)) {
        mid = (low + high) / 2;
        if (array[mid] == target) {
            return mid;
        } else if (array[mid] < target) {
            low = mid + 1;
        } else if (array[mid] > target) {
            high = mid - 1;
        }
    }
    return 0;
}

int main(int argv, char* argc[]) {
    srand(time(NULL));
    if (argv < 4)
        puts(
            "Invalid arguments.\n\nFormat: ./*.exe sizeofArray targetNum "
            "minimumRange\n");
    int minimum = atoi(argc[3]);
    int target = atoi(argc[2]);
    int size = atoi(argc[1]);
    int array[size];
    for (int i = 0; i < size; i++) {
        array[i] = randInt(minimum, 45);
    }
    puts("OG Array:");
    printArray(array, size);
    quicksort(array, size);
    puts("\nSorted array:");
    printArray(array, size);
    binaryS(array, target, size);
    return 0;
}
