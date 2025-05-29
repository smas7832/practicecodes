from sympy import*

# Define A and B
A = Matrix(input("A="))
B = Matrix(input("B"))

# Define the solution x
x = symbols('x0:3')

# Verify if A * x equals B
Ax = A * x

print("Verify if Ax equals B: ", Eq(Ax, B))

# Print the result of solving for x
solution = solve(Eq(Ax, B), x)

