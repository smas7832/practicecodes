import tkinter as tk
from tkinter import messagebox, ttk

# Main expense list
expenses = []

# Function to update expense list display
def update_expense_list():
    for row in tree.get_children():
        tree.delete(row)
    total = 0
    for idx, (desc, amt, cat) in enumerate(expenses, start=1):
        tree.insert("", "end", values=(idx, desc, cat, amt))
        total += amt
    total_label.config(text=f"Total: ₹{total}")

# Function to add expense
def add_expense():
    desc = desc_entry.get()
    category = category_var.get()
    try:
        amt = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid amount!")
        return
    
    if desc.strip() == "":
        messagebox.showerror("Error", "Description cannot be empty!")
        return
    
    expenses.append((desc, amt, category))
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    update_expense_list()

# Function to delete selected expense
def delete_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an expense to delete!")
        return
    index = int(tree.item(selected[0])['values'][0]) - 1
    del expenses[index]
    update_expense_list()

# Dark mode colors
bg_color = "#1E1E1E"
fg_color = "#FFFFFF"
entry_bg = "#2D2D2D"
btn_bg = "#3A3A3A"
highlight_color = "#007ACC"

# GUI setup
root = tk.Tk()
root.title("Expense Manager (Dark Mode)")
root.geometry("550x450")
root.configure(bg=bg_color)

# Labels & Entries
tk.Label(root, text="Description:", bg=bg_color, fg=fg_color).pack(pady=2)
desc_entry = tk.Entry(root, width=40, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
desc_entry.pack()

tk.Label(root, text="Amount (₹):", bg=bg_color, fg=fg_color).pack(pady=2)
amount_entry = tk.Entry(root, width=40, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
amount_entry.pack()

# Category dropdown
tk.Label(root, text="Category:", bg=bg_color, fg=fg_color).pack(pady=2)
category_var = tk.StringVar()
categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
category_dropdown = ttk.Combobox(root, textvariable=category_var, values=categories, state="readonly")
category_dropdown.set("Other")
category_dropdown.pack()

# Buttons
tk.Button(root, text="Add Expense", command=add_expense, bg=highlight_color, fg="white").pack(pady=5)
tk.Button(root, text="Delete Selected", command=delete_expense, bg="red", fg="white").pack(pady=5)

# Expense list (Treeview)
columns = ("No", "Description", "Category", "Amount")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("No", text="No")
tree.heading("Description", text="Description")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount (₹)")
tree.pack(fill="both", expand=True, pady=10)

# Apply dark mode style to Treeview
style = ttk.Style(root)
style.theme_use("default")
style.configure("Treeview",
                background=entry_bg,
                foreground=fg_color,
                rowheight=25,
                fieldbackground=entry_bg)
style.map("Treeview",
          background=[('selected', highlight_color)],
          foreground=[('selected', 'white')])

# Total label
total_label = tk.Label(root, text="Total: ₹0", font=("Arial", 14, "bold"), bg=bg_color, fg=fg_color)
total_label.pack()

root.mainloop()
