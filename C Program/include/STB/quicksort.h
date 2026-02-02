// quicksort.h
#ifndef QUICKSORT_H
#define QUICKSORT_H

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
// Function Declarations (Prototypes)


void swap(int *a, int *b);
void quicksort(int *array, int size);
void printArray(int array[], int size);
int randInt(int min, int max);

#endif

#ifdef QUICKSORT_IMPLEMENTATION

int randInt(int min, int max) {
  if (min > max) {
    printf("Minimum range can't be larger than maximum!!");
    return 0;
  }
  int rd_num = rand() % (max - min + 1) + min;
  return rd_num;
}
void swap(int *a, int *b) {
  int temp = *a;
  *a = *b;
  *b = temp;
}

void quicksort(int *array, int size) {
  if (size < 2) {
    return;
  }
  int pivot_idx = size - 1;
  int pivot_val = array[size - 1];
  int i = -1;

  for (int j = 0; j < size - 1; j++) {
    if (array[j] < pivot_val) {
      i++;
      swap(&(array[i]), &(array[j]));
    }
  }

  int pivot_pos = i + 1;
  swap(&array[pivot_pos], &array[pivot_idx]);
  quicksort(array, pivot_pos);
  quicksort(array + pivot_pos + 1, size - pivot_pos - 1);
}

void printArray(int array[], int size) {
  for (int i = 0; i < size; i++) {
    printf("\nElement %d: %d", i, array[i]);
  }
  return;
}

#endif // QUICKSORT_IMPLEMENTATION
