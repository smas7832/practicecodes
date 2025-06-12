#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
/*
        Ticket Management system with:
                1-Ticket Booking system:
                    -Able To Booking
                    -Ability Cancel ticket
                    -Ability To reschedule
                2-Ewallet system
                    -Ability to deposit, withdraw
        Flowchart: https://excalidraw.com/#json=J1-kzw-6jBQf_Iz5Z_ilw,RUl6XdgD927zZdv_u9VqVQ
 */

struct train
{
    int no;
    char name[20];
    int capacity;
    int seatavl;
};

/*------Ticket Booking system------*/
int bookTkt(struct train *tr); // To Be done
    void trainInit(struct train *tr);
int bookedTkt(); // TBD
int cancelTkt(); // TBD
int ticket();    // Half Done

/*------Ewallet system------*/
int wallet();

/*------Main------*/
int main()
{
    int choice;
    do
    {
        printf("\n______________\n");
        printf("1.Ticket Section\n2.Wallet\n3.Exit");
        printf("\nSelect Choice:");
        scanf("%d", &choice);
        switch (choice)
        {
        case 1:
            ticket();
            break;
        case 2:
            wallet();
            break;
        case 3:
            printf("\nExiting...\n");
            break;
        default:
            printf("Invalid choice");
            break;
        }
    } while (choice != 3);
    return 0;
}

/*------Ticket Booking system------*/
int ticket()
{
    struct train *tr;
    int trSize = 5;
    tr = (struct train *)malloc(trSize * sizeof(struct train));
    if (tr == NULL)
    {
        printf("Memory allocation failed");
    }
    int choice;
    do
    {
        printf("\n______________\n");
        printf("1.Book Ticket\n2.Booked Tickets\n3.Cancel Booking");
        printf("\nSelect Choice:");
        scanf("%d", &choice);
        switch (choice)
        {
        case 1:
            bookTkt(tr);
            break;
        case 2:
            bookedTkt();
            break;

        case 3:
            cancelTkt();
            break;

        default:
            printf("Invalid Choice.");
            break;
        }
    } while (choice != 4);
}

//Initialize Train Data
void trainInit(struct train *tr)
{
    for (int i = 0; i <= 5; i++)
    {
        (tr + i)->no = 1000 + i;
        gets((tr + i)->name);
        (tr + i)->capacity = 100;
        (tr + i)->seatavl = 5;
    }
    
}
int bookTkt(struct train *tr)
{
    trainInit(tr);
    printf("Trains Available are:\n");
    for (int i = 0; i < 10; i++)
    {
        printf("\nTrain No: %d", (tr+i)->no);
        printf("\nTrain Name: %s", (tr +i)->name);
        printf("\nTrain Available Seats: %d", (tr +i)->seatavl);
    }
}
int bookedTkt()
{
    printf("Enter the Train no. to book ticket\n");
}
int cancelTkt()
{
    printf("Enter the Train no. to book ticket\n");
}

/*------Ewallet system------*/
int wallet()
{
    int choice;
    do
    {
        printf("\n______________\n");
        printf("1.Book Ticket\n2.Booked Tickets\n3.Cancel Booking");
        printf("\nSelect Choice:");
        scanf("%d", &choice);
        switch (choice)
        {
        case 1:
            break;

        case 2:
            bookedTkt();
            break;
        case 3:
            cancelTkt();
            break;
        default:
            printf("Invalid Choice.");
            break;
        }
    } while (choice != 4);
}
