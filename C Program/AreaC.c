
#include <stdio.h>
#include <math.h>


#define PI 3.14159 // Define constant for pi
int main() {
float radius, area; 

    // Prompt user for input
    printf("Enter the radius of the circle: ");
    scanf("%f", &radius);

    // Calculate area using the formula: pi * r^2
    area = PI * radius * radius;
    printf("The area of the circle is: %.2f\n", area);
return 0;
}
