'''An Slot machine which Can Do Operations:
        ~Deposit Money
        ~Store The balance
        ~Make Bet on lines
        ~remove balance
'''
import random
MAX_LINES = 3
MIN_BET = 1
MAX_BET = 100

def deposit():
    while True:
        amount = input("Enter Amount to store: \n")
        if amount.isdigit():
            amount = int(amount)
            if amount > 0:
                print(f"Amount Stored!! (${amount})")
                break
            else: print("Amount Must Be Greater than 0")
        else:
            print("Enter Valid Amount")
    return amount

def get_lines():
    while True:
        line= input("Enter No Of lines, Choose between 1-" + str(MAX_LINES) + "?: ")
        if line.isdigit():
            line=int(line)
            if 1 <= line <= MAX_LINES:
                print("Selected No. Of Lines", str(line))
                break
        else: print("Enter Valid Number: ")
    return line

def get_bet():
    while True:
        amount = input("Enter Bet amount: $")
        if amount.isdigit():
            amount = int(amount)
            if MIN_BET <= amount <= MAX_BET:
                break
            else: print(f"Enter Amount Between Range ${MIN_BET} - ${MAX_BET}")
        else: print("Enter Valid Amount: ")
    return amount

reels = {
    1:["A", "B", "C"],
    2:["A", "B", "C"],
    3:["A", "B", "C"],
    4:["A", "B", "C"]
}


def spin():
    output=[]
    for _ in len(reels-1):
        spin_result = [random.choice(reels[i]) for i in range(3)]
        output.append(spin_result)
    return output


def main():
    balance = deposit()
    line = get_lines()
    while True:
        bet = get_bet()
        total_bet= bet * line
        if total_bet >= balance:
            print(f"Insufficient balance (Balnce is ${balance})")
        else: break
    print(f"Bet Placed on {line} lines of ${bet}, Total ${total_bet}")
    spin = spin()
    print("spinning")

    if spin[0] == spin[1] == spin[2] == spin [3]:
        for _ in range(spin):
            print(f"{spin[0]} | {spin[1]} | {spin[2]} | {spin[3]}")
            print("You've Won The Bet")
    else:
        print(f"{spin[0]} | {spin[1]} | {spin[2]} | {spin[3]}")
        print("Try Again")

