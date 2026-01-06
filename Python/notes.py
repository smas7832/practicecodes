import csv

with open("saved_note.txt", "w+") as data:
    data.write(input("Enter the input: "))
    for line in data:
        print(line.strip())

