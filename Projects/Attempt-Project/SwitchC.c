#include <stdio.h>

int main() {
    int day;

    printf("Enter Day Of The Week ;) \n");
    scanf("%d", &day);

    switch (day) {
        case 1:
            printf("It's Monday\n");
            break;
        case 2:
            printf("It's Tuesday\n");
            break;
        case 3:
            printf("It's Wednesday\n");
            break;
        case 4:
            printf("It's Thursday\n");
            break;
        case 5:
            printf("It's Friday\n");
            break;
        case 6 :
            printf("It's Saturday\n");
            break;
        case 7:
            printf("It's Sunday\n");
            break;
        default:
            printf("Please Enter A Valid day :)\n");
    }

    return 0;
}
