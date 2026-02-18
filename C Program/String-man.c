#include <stdio.h>
#include <strings.h>

/* Basic String Manipulation Program
        1.Reverse the string
        2.Count Vowels
*/

int stlencount(char text[]) {
  int count = 0, i = 0;
  while (text[i] != '\0') {
    count++;
    i++;
  }
  return count;
}

int main() {

  char text[50];
  int choice;

  printf("Enter Your string:\t");
  gets(text);

  printf("\n\t1.Reverse String\n\t2.Count Vowels");
  printf("\nSelect action to perform:\t");
  scanf("%d", &choice);

  char temp[sizeof(text)];
  int j = 0;
  int len = stlencount(text);
  if (choice == 1) {

    for (int i = len - 1; i >= 0; i--) {

      temp[j] = text[i];
      j++;
    }
    temp[j] = '\0';
    printf("Reverse String: %s", temp);
  } else if (choice == 2) {
    int counter = 0;

    /* Count the vowels in the string */
    for (int i = 0; i < len; i++) {
      char c = text[i];
      if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
          c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
        counter++;
      }
    }
    printf("Number of vowels: %d", counter);
  }
}
