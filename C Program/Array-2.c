#include <stdio.h>
//to use array for desired no of elements
int main()
{
    int i, n, A[100];
    printf("\n How many elements you want to store =");
    scanf("%d",&n);
    for(i=0;i<n;i++)
    {
        printf("\n Enter no %d=",i);
        scanf("%d",&A[i]);
    }
    
    printf("\n Numbers are as follows=");
    for(i=0;i<n;i++)
    {
        printf("\n %d", A[i]);
    }
    return 0;
}
