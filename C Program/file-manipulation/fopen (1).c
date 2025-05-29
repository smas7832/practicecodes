#include <stdio.h>
#include <stdlib.h> // For exit()

int main() {
    FILE *file_pointer;
    char buffer[256]; // Buffer to hold each line

    // Open the file for reading ("r" mode)
    file_pointer = fopen("my_file.txt", "r");

    // Check if the file was opened successfully
    if (file_pointer == NULL) {
        perror("Error opening file"); // Print a system error message
        return 1; // Indicate an error
    }

    // Read the file line by line
    while (fgets(buffer, sizeof(buffer), file_pointer) != NULL) {
        printf("%s", buffer); // Print each line read
    }

    // Check for read errors or EOF after the loop
    if (ferror(file_pointer)) {
        perror("Error reading file");
    }

    // Close the file
    fclose(file_pointer);

    return 0; // Indicate success
}