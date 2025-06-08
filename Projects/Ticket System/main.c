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
#include <stdio.h>

int ticket(){
    int choice;
    do{
        printf("\n-------------\n");
        printf("1.Book Ticket\n2.Booked Tickets\n3.Cancel Booking");
        printf("Select Choice:");
        scanf("%d", &choice);
        switch(choice){
            case 1:bookTkt();
            case 2:bookedTkt();
            case 3:cancelTkt();
            default: printf("Invalid Choice."); 
        }
    }while(choice != 4);
}

int main(){
    int choice;
    do{
        printf("\n-------------\n");
        printf("1.Ticket Section\n2.Wallet\n3.Exit");
        printf("Select Choice:");
        scanf("%d", &choice);
        switch(choice){
            case 1: ticket();
            case 2: wallet();
            case 3: printf("\nExiting...\n");
            default: printf("Invalid choice");
        }
    }while (choice != 3);
}