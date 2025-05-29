#include <stdio.h>
#include <stdlib.h>

// Structure to represent an array
typedef struct {
    int *data;
    int size;
} Array;

// Function to input array elements
void input_array(Array *arr) {
    printf("Enter %d elements: ", arr->size);
    for (int i = 0; i < arr->size; i++) {
        scanf("%d", &arr->data[i]);
    }
}

// Function to print array elements
void print_array(Array arr) {
    for (int i = 0; i < arr.size; i++) {
        printf("%d ", arr.data[i]);
    }
    printf("\n");
}

// Function to perform addition of two arrays
Array add_arrays(Array arr1, Array arr2) {
    Array result;
    result.size = arr1.size;
    result.data = (int *)malloc(result.size * sizeof(int));
    for (int i = 0; i < result.size; i++) {
        result.data[i] = arr1.data[i] + arr2.data[i];
    }
    return result;
}

// Function to perform subtraction of two arrays
Array subtract_arrays(Array arr1, Array arr2) {
    Array result;
    result.size = arr1.size;
    result.data = (int *)malloc(result.size * sizeof(int));
    for (int i = 0; i < result.size; i++) {
        result.data[i] = arr1.data[i] - arr2.data[i];
    }
    return result;
}

// Function to perform operations on 'n' number of arrays
void perform_operations(int n) {
    Array *arrays = (Array *)malloc(n * sizeof(Array));

    for (int i = 0; i < n; i++) {
        printf("Enter size of array %d: ", i + 1);
        scanf("%d", &arrays[i].size);
        arrays[i].data = (int *)malloc(arrays[i].size * sizeof(int));
        input_array(&arrays[i]);
    }

    int choice;
    printf("Choose an operation:\n1. Add arrays\n2. Subtract arrays\n");
    scanf("%d", &choice);

    if (choice == 1) {
        Array result = arrays[0];
        for (int i = 1; i < n; i++) {
            result = add_arrays(result, arrays[i]);
        }
        printf("Result of adding all arrays: ");
        print_array(result);
    } else if (choice == 2) {
        Array result = arrays[0];
        for (int i = 1; i < n; i++) {
            result = subtract_arrays(result, arrays[i]);
        }
        printf("Result of subtracting all arrays: ");
        print_array(result);
    }

    // Free memory
    for (int i = 0; i < n; i++) {
        free(arrays[i].data);
    }
    free(arrays);
}

int main() {
    int n;
    printf("Enter the number of arrays: ");
    scanf("%d", &n);
    perform_operations(n);
    return 0;
}