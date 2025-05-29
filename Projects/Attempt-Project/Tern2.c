// C program to check whether a year is leap year or not
// using ternary operator

#include <stdio.h>

int main()
{
    int yr;
  printf("Enter The Year:");
scanf("%d", &yr);
    (yr%4==0) ? (yr%100!=0? printf("The year %d is a leap year",yr)
     : (yr%400==0 ? printf("The year %d is a leap year",yr)
         : printf("The year %d is not a leap year",yr)))
             : printf("The year %d is not a leap year",yr);
    return 0;
}

//This code is contributed by Susobhan AKhuli
