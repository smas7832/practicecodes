'''An Slot machine which Can Do Operations:
        ~Deposit Money- Done
        ~Store The balance - Done
        ~Make Bet on lines - Done
        ~Output Result - Done
        ~Store Win/Loss Money - Done
'''

import random

MAX_LINES = 3
MIN_BET = 1
MAX_BET = 100

reels = {
    1: ["A", "B", "C", "D"],
    2: ["A", "B", "C", "D"],
    3: ["A", "B", "C", "D"]
}

def deposit():
    while True:
        amount = input("Enter Amount to store: $")
        if amount.isdigit():
            amount = int(amount)
            if amount > 0:
                print(f"Amount Stored! (${amount})")
                return amount
            else:
                print("Amount must be greater than 0.")
        else:
            print("Enter a valid amount.")

def get_lines():
    while True:
        lines = input(f"Enter number of lines (1-{MAX_LINES}): ")
        if lines.isdigit():
            lines = int(lines)
            if 1 <= lines <= MAX_LINES:
                return lines
        print("Enter a valid number.")

def get_bet():
    while True:
        amount = input(f"Enter bet amount (${MIN_BET} - ${MAX_BET}): $")
        if amount.isdigit():
            amount = int(amount)
            if MIN_BET <= amount <= MAX_BET:
                return amount
        print("Enter a valid amount.")


def spin():
    output = []
    for _ in range(3):
        spin_result = [random.choice(reels[i+1]) for i in range(MAX_LINES)]  # Picking symbols
        output.append(spin_result)
    return output


def print_slot_machine(slot_result):
    for row in zip(*slot_result):
        print(" | ".join(row))


def main():
    balance = deposit()

    while True:
        lines = get_lines()

        while True:
            bet = get_bet()
            total_bet = bet * lines
            if total_bet > balance:
                print(f"Insufficient balance! (Balance: ${balance})")
            else:
                break

        balance -= total_bet
        print(f"Bet placed on {lines} lines of ${bet}, Total: ${total_bet}")

        result = spin()
        print("Spinning...")
        print_slot_machine(result)

        first_row = result[0]
        if first_row.count(first_row[0]) == len(first_row):
            print("Congratulations! You won the bet!")
            balance += total_bet * 2
        else:
            print("Try Again!")

        if balance <= 0:
            print("You're out of money! Game Over.")
            break


        choice = input(f"Your balance: ${balance}. Do you want to continue? (y/n): ").lower()
        if choice != "y":
            break

    print("Thanks for playing!")

main()
