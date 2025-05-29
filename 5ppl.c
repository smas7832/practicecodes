#include<stdio.h>

//Enter address (House no, block,city, state) of 5 people

struct address{
    int hsn;
    int blk;
    char city[20];
    char state[50];
};

int main(){
    struct address a[5];
    for (int i=0; i=4; i++){

        printf("\t\t---Enter Data For Person : %d---",i+1);
        printf("\n\t House Number:\t");
        scanf("%d",&a[i].hsn); 
        printf("\n\t Block Number:\t");
        scanf("%d",&a[i].blk);
        printf("\n\t City:\t");
        scanf("%s",&a[i].city);
        printf("\n\t State:\t");
        scanf("%s",&a[i].state);
        printf("\n\n");
    }

    //Printer
    for (int i=0; i=4; i++){
        printf("\t\t---Data Given For Person : %d---",i+1);
        printf("\n House Number:\t %d",a[i].hsn); 
        printf("\n Block Number:\t %d",a[i].blk);
        printf("\n Enter City:\t %s",a[i].city);
        printf("\n Enter State:\t %s",a[i].state);
        printf("\n\n");
    }


}