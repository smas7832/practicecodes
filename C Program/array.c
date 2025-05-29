#include <stdio.h>
/*
Array Operations:
	Find the largest/smallest element in an array of integers.
	Calculate the average of the numbers in an array.
*/

int main()
{
	int n, choice;

	printf("Enter Length Of array: ");
	scanf("%d", &n);
	int arr[n];
	for (int i = 0; i < n; i++)
	{
		printf("\nEnter Element %d: ", arr[i] + 1);
	}

	printf("\n\t1.Find Largest no.\n\t2.Find smallest no.\n\t3.Calculate Average\n");
	printf("\nSelection operation: ");
	scanf("%d", &choice);

	if (choice == 1)
	{
		int lnum = 0;

		for (int i = 0; i < n; i++)
		{
			if (lnum < arr[i])
			{
				lnum = arr[i];
			}
		}
	}
	else if (choice == 2)
	{
		int snum;
		for (int i = 0; i < n; i++)
		{
			if (snum > arr[i])
			{
				snum = arr[i];
			}
		}
	}
}