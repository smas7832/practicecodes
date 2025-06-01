
#include <stdio.h>

void addition(int n1, int n2);
void subtraction(int n1, int n2);
void multiplication(int n1, int n2);
void division(int n1, int n2);

int main()
{
    int choice;
    int n1, n2;

    while (choice != 5)
    {

        printf("\n\t 1.Addition\n\t 2.Subtraction\n\t 3.Multiplication\n\t 4.Division\n\t 5.Exit\n");
        printf("Select operation you want to perform:");
        scanf("%d", &choice);

        printf("Enter 1st No:");
        scanf("%d", &n1);
        printf("Enter 2nd No:");
        scanf("%d", &n2);

        switch (choice)
        {
        case 1:
            addition(n1, n2);
            break;
        case 2:
            subtraction(n1, n2);
            break;
        case 3:
            multiplication(n1, n2);
            break;
        case 4:
            division(n1, n2);
            break;
        case 5:
            break;
        default:
            printf("\nInvalid choice");
            break;
        }
    }
}

void addition(int n1, int n2)
{
    printf("%d", n1 + n2);
}

void subtraction(int n1, int n2)
{
    printf("%d", n1 - n2);
}

void multiplication(int n1, int n2)
{
    printf("%d", n1 * n2);
}

void division(int n1, int n2)
{
    printf("%d", n1 / n2);
}
