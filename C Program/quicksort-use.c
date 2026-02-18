#include <stdio.h>
#include <stdlib.h>
/*How does quicksort works??
 *      1. it decides a pivot in an array
 *      2. it moves elements smaller than pivot to it's left, and larger to it's
 * right
 *      3. pivots new left and right subarrays are recursively arranged again
 *      4. it stops when the subarray has only one element left
 *      5. put together all the subbarrays and create new sorted array.
 *note: the array is sorted by assigning every elemnt it's correct pos along
 * until pivot is at it's pos, once pivot is in its place, we would restart the
 * whole process.
 */
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
