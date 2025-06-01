#include <stdio.h>

int main()
{
	// Temp Converter

	float c, f, result;
	int choice;

	printf("What Operation would you like to do");
	while (choice != 3)
	{
		printf("\nConvert: \n\t1.Fahrenheit to Celsius \n\t2.Celsius to Fahrenheit\n\t3.Exit\nOption:");
		scanf("%d", &choice);

		if (choice == 1)
		{
			printf("Enter the temperature in Fahrenheit: ");
			scanf("%f", &f);
			result = (f - 32) * 5.0 / 9.0;
			printf("Result = %.2f Celsius", result);
		}
		else if (choice == 2)
		{
			printf("Enter the temperature in Celsius: ");
			scanf("%f", &c);
			result = c * (9 / 5) + 32;
			printf("Result = %2.lf Fahrenheit", result);
		}else if (choice != 3 && choice != 1 && choice != 2)
		{
			printf("Invalid option");
		}
	}
}