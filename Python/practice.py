
list = ["Maniac", "Morning", "Pythonic", "Nachde Ne Saare"]
mini_list = ["Gangsta", "Arijit Singh", "Mohit Chauhan"]

print(*list[1:3])
print(list + mini_list, end= "\n\n")

#------------------------------------------------------------------#

with open("Python/output.txt", "a") as output:
    print(*list, *mini_list, sep = "\t", file = output)
    text = output.read()
    print(text)

#------------------------------------------------------------------#

meta = 35.98
print(int(meta))