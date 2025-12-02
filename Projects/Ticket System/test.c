#include <stdio.h>

// For test codes

void json_write(char string[], char filename[]) {
  FILE *fp = fopen(filename, "a   +");
  if (fp == NULL) {
    perror("Error occured:");
  }
  fprintf(fp, string, stdin);
}

int main() {
  char master[] = "data.json";

  for (int i; i < 100; i++) {
    json_write("\nLovly day", master);
  }
}
