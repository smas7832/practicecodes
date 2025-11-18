#include <stdarg.h>
#include <stdio.h>

double average(int num_args, ...) {
  va_list ap; // Declare a va_list variable
  double total = 0.0;
  int i;

  // Initialize the va_list with the last fixed argument (num_args)
  va_start(ap, num_args);

  // Loop through the arguments and add them to the total
  for (i = 0; i < num_args; i++) {
    total += va_arg(ap, int); // Retrieve the next argument as an integer
  }

  // Clean up the va_list
  va_end(ap);

  return total / num_args;
}

int main(int argc, char *argv[]) {
  // Example usage of the average function
  int i = 0;
  if (i <= argc) {
  }
  printf("Average of 2, 4, 6: %f\n", average(3, 2, 4, 6));
  printf("Average of 10, 20: %f\n", average(2, 10, 20));
  return 0;
}