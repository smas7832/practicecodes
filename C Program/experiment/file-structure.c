#include <stdio.h>

void chkfile(FILE *fp){
  if(fp == NULL){
    printf("file is missing.");

  } else {
    printf("file is present.");
  }
}

int main (){
  FILE *fp = fopen("example.txt", "w+");
  if(fp == NULL){
    printf("file creation/reading failed.");
    return 1;
  }
  while (1){
    chkfile(fp);
    printf("delete file and press enter");
    getchar();
  }
}
