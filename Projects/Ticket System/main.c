#include <stdio.h>

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
int bookedTkt();               // TBD
int cancelTkt();               // TBD
int ticket();                  // Half Done

/*------Ewallet system------*/
int wallet();

/*------Main------*/
int main()
{
    int choice;
    do
    {
        printf("\n-------------\n");
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
    struct train tr[10];
    int choice;
    do
    {
        printf("\n-------------\n");
        printf("1.Book Ticket\n2.Booked Tickets\n3.Cancel Booking");
        printf("\nSelect Choice:");
        scanf("%d", &choice);
        switch (choice)
        {
        case 1:
            bookTkt(&tr);
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

int bookTkt(struct train *tr)
{
    printf("Trains Available are:\n");
    for (int i = 0; i<10; i++){
        printf("Train No: %d", tr->no);
        printf("Train Name: %s", tr->name);
        printf("Train Available Seats: %d", tr->seatavl);
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
        printf("\n-------------\n");
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
