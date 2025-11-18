/*i. Write a ‘C’ program to accept three dimensions length (l), breadth(b)
 * and height(h) of a cuboid and print surface area  (surface area=2(lb+lh+bh)
 */
#include <stdio.h>

int main() {
  int l, b, h, area;

  printf("Enter length \n");
  scanf("%d", &l);
  printf("enter Breadth \n");
  scanf("%d", &b);
  printf("enter Height \n");
  scanf("%d", &h);

  area = 2 * (l * h + l * b + b * h);
  printf("Area Of Cuboid Is: %d", area);
}
