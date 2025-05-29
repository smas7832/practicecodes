#include<stdio.h>
#include<math.h>
//to find Area of Rectangle

int main(){
float Length,width,area;
printf ("Enter Length Of Square =");
scanf ("%f", &Length);
printf ("Enter width Of Square =");
scanf ("%f", &width);
area = Length*width;
printf ("Area is = %f \n", area);
return 0;
}