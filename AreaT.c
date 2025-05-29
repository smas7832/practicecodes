#include<stdio.h>
#include<math.h>
//to find Area of Triangle

int main(){
float height,base,area;
printf ("Enter Height Of Triangle =");
scanf ("%f", &height);
printf ("Enter Base Of Triangle =");
scanf ("%f", &base);
area = (0.5)*height*base;
printf ("Area is = %f \n", area);
return 0;
}