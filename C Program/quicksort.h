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
