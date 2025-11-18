#include "quicksort.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void binaryS(int array[], int target, int size) {
  int low = 0;
  int high = size - 1;
  int mid;

  while (!(low >= high)) {
    mid = (low + high) / 2;
    if (array[mid] == target) {
      printf("\nthe target is at index: %d", mid);
      return;
    } else if (array[mid] < target) {
      low = mid + 1;
    } else if (array[mid] > target) {
      high = mid - 1;
    }
  }
  puts("\n\nTarget not found");
}

int main(int argv, char *argc[]) {
  srand(time(NULL));
  if (argv < 4)
    puts("Invalid arguments.\n\nFormat: ./*.exe sizeofArray targetNum "
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
