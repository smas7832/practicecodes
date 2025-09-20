#include <stdio.h>
// To Calculate Age with current year being 2024
int calculateAge(int userInput) {
  int currentYear = 2024;
  int age = currentYear - userInput;
  int years = age / 100;
  int decades = age % 100;
  if (years < 18) {
    return printf("You are too young to become an adult\n");
  } else if (years > 18) {
    return printf(
        "It's common for people to reach their late 20s as an adult.\n");
  } else if (years >= 60) {
    return printf("Congratulations! You are now an Old Person.\n");
  }
  return 0;
}

int main() {
  int userInput;
  printf("Please enter your age: ");
  scanf("%d", &userInput);

  return 0;
}

