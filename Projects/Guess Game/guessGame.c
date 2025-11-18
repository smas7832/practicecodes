#include <stdio.h>
#include <stdlib.h>

/*To-Dos:
	. Create a hint system - DONE
	. Implement logic for dynamic Hints - PENDING
	. Create game logic - DONE
----------------------------------------
The computer picks a random number between Min and max range. The user has to guess it. The computer provides hints like "Too high!" or "Too low!".
*/

int rando(int min, int max) {
	int rd_num = rand() % (max - min + 1) + min;
	return rd_num;
}

int hint(int min, int max, int guess, int guessNo, int num) {

	if(guess < min || guess > max) {
		printf("out of range.");
	}else if (guess == num) {
		printf("\nRight!!");
		guessNo++;
	}else if (guessNo >= 4 && guess > num) {
		printf("\nYou're getting warmer! The number is between %d and %d.", min, guess);
		guessNo++;
	}else if(guess > num) {
		printf("\nGuessed high.");
		guessNo++;
	} else if(guess < num) {
		printf ("You're low.");
		guessNo++;
	}
	return guessNo;
}

void game() {
	int min,
	max,
	num,
	guess,
	guessNo = 0; //Guess count
	printf ("\n___Enter range___");
	printf("\nMin-Max: ");
	scanf("%d-%d", &min, &max);
	num = rando(min, max);

	do {
		printf("\nEnter Guess: ");
		scanf ("%d", &guess);
		guessNo = hint(min, max, guess, guessNo, num);
	}while(guess != num);
}

int main() {
	int choice;
	printf("---Game has started!!---");
	do {
		printf("\n\n\t0.Exit\n\t1.Start a new game\nSelect option:");
		scanf("%d", &choice);
		while(choice != 0 && choice != 1) {
			printf("Enter Valid selection: ");
			scanf("%d", &choice);
		}
		switch(choice) {
			case 0: printf("Exiting....");
			return 0;
			break;
			case 1: game();
			break;
		}
	}while(choice != 0);
	return 0;
}
