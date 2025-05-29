#include <stdio.h>

int main() {
    int arr[] = {10, 45, 2, 67, 89, 34}; // Example array
    int n = sizeof(arr) / sizeof(arr[0]); // Number of elements in array

printf("%d\n",n);
printf("%d\n",sizeof(arr));
printf("%d\n",sizeof(arr[0]));
}