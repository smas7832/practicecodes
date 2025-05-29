from sympy import *


A=Matrix([[1,2,3],[4,5,6],[7,8,9]])
B=Matrix([[1,10,3],[4,65,6],[7,5,9]])

print(A*B)
print(A.det, B.det)
