#include <stdio.h>

int main() {
  char ch;

  // Accept a character
  printf("Enter a character: ");
  scanf("%c", &ch);

  // Check if it is an alphabet
  if ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z')) {
    printf("'%c' is an alphabet.\n", ch);

    // Check if it is uppercase or lowercase
    if (ch >= 'A' && ch <= 'Z') {
      printf("It is an uppercase letter.\n");
    } else {
      printf("It is a lowercase letter.\n");
    }
  }
  // Check if it is a digit
  else if (ch >= '0' && ch <= '9') {
    printf("'%c' is a digit.\n", ch);
  }
  // If it is not an alphabet or digit, it is a special symbol
  else {
    printf("'%c' is a special symbol.\n", ch);
  }

  return 0;
}
