# Function to add two numbers
def add_two_numbers(num1, num2):
    return num1 + num2

# Get user input
try:
    number1 = float(input("Enter the first number: "))
    number2 = float(input("Enter the second number: "))

    # Call the function and store the result
    result = add_two_numbers(number1, number2)

    # Print the result
    print(f"The sum of {number1} and {number2} is {result}")

except ValueError:
    print("Please enter valid numbers.")
    
