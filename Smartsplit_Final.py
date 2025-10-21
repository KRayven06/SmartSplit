import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, PRIMARY, DANGER, INFO, SECONDARY, WARNING
from tkinter import messagebox, filedialog, simpledialog, ttk as tkttk
import csv
from datetime import datetime
import matplotlib.pyplot as plt

class Member:
    def __init__(self, name):
        self.name = name
        self.balance = 0.0

class Expense:
    def __init__(self, payer, amount, shared_with, description="", date=None):
        self.payer = payer
        self.amount = amount
        self.shared_with = shared_with
        self.description = description
        self.date = date or datetime.now()

class SmartSplit:
    def __init__(self, currency="₹"):
        self.members = {}
        self.expenses = []
        self.currency = currency

    def set_currency(self, currency):
        self.currency = currency

    def add_member(self, name):
        if name and name not in self.members:
            self.members[name] = Member(name)

    def remove_member(self, name):
        if name in self.members:
            if abs(self.members[name].balance) < 0.01:
                del self.members[name]
                return True
            else:
                return False
        return None

    def add_expense(self, payer, amount, shared_with, description=""):
        if payer not in self.members:
            messagebox.showerror("Error", f"Payer '{payer}' not found!")
            return
        if len(shared_with) == 0:
            messagebox.showerror("Error", "No people to share the expense!")
            return
        # Add expense
        self.expenses.append(Expense(payer, amount, shared_with, description))
        # Calculate split
        split_amount = amount / len(shared_with)
        for person in shared_with:
            if person not in self.members:
                messagebox.showwarning("Warning", f"Member '{person}' not found!")
                continue
            if person == payer:
                self.members[payer].balance += amount - split_amount
            else:
                self.members[person].balance -= split_amount

    def delete_expense(self, idx):
        "Remove an expense by index. Rollback balances for that expense."
        if idx < 0 or idx >= len(self.expenses):
            return False
        expense = self.expenses.pop(idx)
        split_amount = expense.amount / len(expense.shared_with)
        for person in expense.shared_with:
            if person not in self.members:
                continue
            if person == expense.payer:
                self.members[person].balance -= expense.amount - split_amount
            else:
                self.members[person].balance += split_amount
        return True

    def get_balances(self):
        result = "Final Balances:\n"
        for name, member in self.members.items():
            sign = "+" if member.balance >= 0 else "-"
            result += f"{name:<10}: {sign}{self.currency}{abs(member.balance):.2f}\n"
        return result

    def get_members(self):
        if not self.members:
            return "No members yet."
        return "Members:\n" + "\n".join(self.members.keys())

    def get_expense_history(self):
        if not self.expenses:
            return "No expenses recorded."
        result = "Expense History:\n"
        for idx, e in enumerate(self.expenses):
            dstr = e.date.strftime("%Y-%m-%d %H:%M")
            result += f"[{idx+1}] {dstr} | {e.payer} paid {self.currency}{e.amount:.2f} ({e.description}) split among {', '.join(e.shared_with)}\n"
        return result

    def get_settle_up_instructions(self):
        # Greedy algorithm to settle debts: positive = should receive, negative = should pay
        balances = {name: round(mem.balance, 2) for name, mem in self.members.items()}
        payers = []
        receivers = []
        for name, bal in balances.items():
            if abs(bal) < 0.01:
                continue
            if bal > 0:
                receivers.append([name, bal])
            else:
                payers.append([name, -bal])
        receivers.sort(key=lambda x: -x[1])
        payers.sort(key=lambda x: -x[1])
        instructions = []
        i, j = 0, 0
        while i < len(payers) and j < len(receivers):
            pay_name, pay_amt = payers[i]
            rec_name, rec_amt = receivers[j]
            amt = min(pay_amt, rec_amt)
            instructions.append(f"{pay_name} pays {rec_name} {self.currency}{amt:.2f}")
            payers[i][1] -= amt
            receivers[j][1] -= amt
            if payers[i][1] < 0.01:
                i += 1
            if receivers[j][1] < 0.01:
                j += 1
        if not instructions:
            return "Everyone is settled up!"
        return "Settle Up Suggestions:\n" + "\n".join(instructions)

    def get_expenses_for_table(self):
        return [
            [
                e.date.strftime("%Y-%m-%d %H:%M"),
                e.payer,
                f"{self.currency}{e.amount:.2f}",
                ", ".join(e.shared_with),
                e.description
            ]
            for e in self.expenses
        ]

    def clear_all(self):
        self.members = {}
        self.expenses = []

    def export_balances(self):
        export_text = self.get_balances()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(export_text)
            messagebox.showinfo("Exported", f"Balances exported to {file_path}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", encoding="utf-8", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Date", "Payer", "Amount", "Shared With", "Description"])
                for e in self.expenses:
                    writer.writerow([
                        e.date.strftime("%Y-%m-%d %H:%M"),
                        e.payer,
                        e.amount,
                        "|".join(e.shared_with),
                        e.description
                    ])
            messagebox.showinfo("Exported", f"Expense history exported to {file_path}")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        self.clear_all()
        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                payer = row["Payer"]
                amount = float(row["Amount"])
                shared_with = row["Shared With"].split("|")
                description = row.get("Description", "")
                date = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M")
                for name in shared_with + [payer]:
                    self.add_member(name)
                e = Expense(payer, amount, shared_with, description, date)
                self.expenses.append(e)
                # Manually update balances as in add_expense
                split_amount = amount / len(shared_with)
                for person in shared_with:
                    if person not in self.members:
                        continue
                    if person == payer:
                        self.members[payer].balance += amount - split_amount
                    else:
                        self.members[person].balance -= split_amount

class SmartSplitApp:
    def __init__(self, root):
        self.app = SmartSplit()
        self.root = root
        self.root.title("SmartSplit Expense Splitter")
        self.style = ttk.Style("superhero")  # try 'flatly', 'vapor', etc.

        entry_width = 25
        btn_width = 16
        text_width = 70
        padx = 10
        pady = 8

        # --- Currency selector
        ttk.Label(root, text="Currency:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=padx, pady=pady, sticky="w")
        self.currency_var = ttk.StringVar(value="₹")
        self.currency_combo = ttk.Combobox(root, textvariable=self.currency_var, values=["₹", "$", "€", "£", "¥"], width=4, font=("Segoe UI", 11))
        self.currency_combo.grid(row=0, column=1, padx=padx, pady=pady, sticky="w")
        self.currency_combo.bind("<<ComboboxSelected>>", self.update_currency)
        row_offset = 1

        # --- Add Member
        ttk.Label(root, text="Add Member:", font=("Segoe UI", 11, "bold")).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="w")
        self.member_entry = ttk.Entry(root, width=entry_width, font=("Segoe UI", 11))
        self.member_entry.grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Add", bootstyle=SUCCESS, width=btn_width, command=self.add_member).grid(row=row_offset, column=2, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        # --- Add Expense
        ttk.Label(root, text="Payer:", font=("Segoe UI", 10)).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="w")
        self.payer_entry = ttk.Entry(root, width=entry_width, font=("Segoe UI", 11))
        self.payer_entry.grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        ttk.Label(root, text="Amount:", font=("Segoe UI", 10)).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="w")
        self.amount_entry = ttk.Entry(root, width=entry_width, font=("Segoe UI", 11))
        self.amount_entry.grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        ttk.Label(root, text="Description:", font=("Segoe UI", 10)).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="w")
        self.description_entry = ttk.Entry(root, width=entry_width, font=("Segoe UI", 11))
        self.description_entry.grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        ttk.Label(root, text="Shared With (comma separated):", font=("Segoe UI", 10)).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="w")
        self.shared_entry = ttk.Entry(root, width=entry_width, font=("Segoe UI", 11))
        self.shared_entry.grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Add Expense", bootstyle=PRIMARY, width=btn_width, command=self.add_expense).grid(row=row_offset, column=2, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        # --- Remove Member
        ttk.Label(root, text="Remove Member:", font=("Segoe UI", 10)).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="w")
        self.remove_entry = ttk.Entry(root, width=entry_width, font=("Segoe UI", 11))
        self.remove_entry.grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Remove", bootstyle=DANGER, width=btn_width, command=self.remove_member).grid(row=row_offset, column=2, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        # --- Separator
        ttk.Separator(root, orient="horizontal").grid(row=row_offset, column=0, columnspan=3, sticky="ew", padx=padx, pady=(5,10))
        row_offset += 1

        # --- Control Buttons
        ttk.Button(root, text="Show Balances", bootstyle=INFO, width=btn_width, command=self.show_balances).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="View Members", bootstyle=INFO, width=btn_width, command=self.view_members).grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="View History", bootstyle=INFO, width=btn_width, command=self.view_expenses).grid(row=row_offset, column=2, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        ttk.Button(root, text="Export Balances", bootstyle=SECONDARY, width=btn_width, command=self.export_balances).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Export CSV", bootstyle=SECONDARY, width=btn_width, command=self.export_csv).grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Import CSV", bootstyle=SECONDARY, width=btn_width, command=self.import_csv).grid(row=row_offset, column=2, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        ttk.Button(root, text="Settle Up", bootstyle=WARNING, width=btn_width, command=self.show_settle_up).grid(row=row_offset, column=0, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Pie Chart", bootstyle=INFO, width=btn_width, command=self.show_pie_chart).grid(row=row_offset, column=1, padx=padx, pady=pady, sticky="ew")
        ttk.Button(root, text="Clear All", bootstyle=DANGER, width=btn_width, command=self.clear_all_data).grid(row=row_offset, column=2, padx=padx, pady=pady, sticky="ew")
        row_offset += 1

        # --- Output Text Area (READ ONLY)
        self.result_text = ttk.Text(root, height=15, width=text_width, font=("Consolas", 11), wrap="word")
        self.result_text.grid(row=row_offset, column=0, columnspan=3, padx=padx, pady=padx, sticky="nsew")
        self.result_text.config(state="disabled")

        # --- Expense Table/Listbox for Deletion (new feature)
        row_offset += 1
        ttk.Label(root, text="Expenses (select to delete):", font=("Segoe UI", 10, "bold")).grid(row=row_offset, column=0, columnspan=2, padx=padx, pady=(15, 5), sticky="w")
        self.expense_tree = tkttk.Treeview(root, columns=("Date", "Payer", "Amount", "Shared", "Desc"), show="headings", height=5)
        for col, width in zip(["Date", "Payer", "Amount", "Shared", "Desc"], [125, 80, 70, 180, 150]):
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, minwidth=10, width=width, anchor="w")
        self.expense_tree.grid(row=row_offset + 1, column=0, columnspan=2, padx=padx, pady=5, sticky="nsew")
        ttk.Button(root, text="Delete Expense", bootstyle=WARNING, width=btn_width, command=self.delete_selected_expense).grid(row=row_offset + 1, column=2, padx=padx, pady=(5, 25), sticky="ew")

        # --- Responsive/stretchy layout for all rows
        for col in range(3):
            root.grid_columnconfigure(col, weight=1)
        for r in range(row_offset + 3):
            root.grid_rowconfigure(r, weight=1)
        root.grid_rowconfigure(row_offset + 1, weight=3)

        self.refresh_expense_tree()

    # --- UI event handlers

    def update_currency(self, event=None):
        currency = self.currency_var.get()
        self.app.set_currency(currency)
        self.show_balances()
        self.refresh_expense_tree()

    def add_member(self):
        name = self.member_entry.get().strip()
        if name:
            self.app.add_member(name)
            messagebox.showinfo("Added", f"Member '{name}' added.")
            self.member_entry.delete(0, ttk.END)

    def add_expense(self):
        payer = self.payer_entry.get().strip()
        try:
            amount = float(self.amount_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid amount.")
            return
        shared_with = [n.strip() for n in self.shared_entry.get().split(",") if n.strip()]
        description = self.description_entry.get().strip()
        self.app.add_expense(payer, amount, shared_with, description)
        self.payer_entry.delete(0, ttk.END)
        self.amount_entry.delete(0, ttk.END)
        self.shared_entry.delete(0, ttk.END)
        self.description_entry.delete(0, ttk.END)
        self.refresh_expense_tree()

    def remove_member(self):
        name = self.remove_entry.get().strip()
        result = self.app.remove_member(name)
        if result is True:
            messagebox.showinfo("Removed", f"Member '{name}' removed.")
        elif result is False:
            messagebox.showwarning("Balance Exists", f"Can't remove '{name}', balance not settled.")
        else:
            messagebox.showerror("Error", f"Member '{name}' not found.")
        self.remove_entry.delete(0, ttk.END)

    def show_balances(self):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, ttk.END)
        self.result_text.insert(ttk.END, self.app.get_balances())
        self.result_text.config(state="disabled")

    def view_members(self):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, ttk.END)
        self.result_text.insert(ttk.END, self.app.get_members())
        self.result_text.config(state="disabled")

    def view_expenses(self):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, ttk.END)
        self.result_text.insert(ttk.END, self.app.get_expense_history())
        self.result_text.config(state="disabled")

    def show_settle_up(self):
        instructions = self.app.get_settle_up_instructions()
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, ttk.END)
        self.result_text.insert(ttk.END, instructions)
        self.result_text.config(state="disabled")

    def export_balances(self):
        self.app.export_balances()

    def export_csv(self):
        self.app.export_csv()

    def import_csv(self):
        self.app.import_csv()
        self.refresh_expense_tree()

    def clear_all_data(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            self.app.clear_all()
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, ttk.END)
            self.result_text.config(state="disabled")
            self.refresh_expense_tree()
            messagebox.showinfo("Cleared", "All data has been cleared.")

    def refresh_expense_tree(self):
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        for row in self.app.get_expenses_for_table():
            self.expense_tree.insert("", "end", values=row)

    def delete_selected_expense(self):
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select an expense to delete.")
            return
        index = self.expense_tree.index(selected[0])
        if messagebox.askyesno("Delete", "Are you sure you want to delete this expense?"):
            self.app.delete_expense(index)
            self.refresh_expense_tree()
            self.show_balances()

    def show_pie_chart(self):
        totals = {}
        for e in self.app.expenses:
            for name in e.shared_with:
                totals[name] = totals.get(name, 0) + e.amount / len(e.shared_with)
        if not totals:
            messagebox.showinfo("No data", "No expenses to chart.")
            return
        plt.figure(figsize=(5, 5))
        plt.pie(list(totals.values()), labels=list(totals.keys()), autopct="%1.1f%%")
        plt.title("Share of Total Expenses")
        plt.show()

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = SmartSplitApp(root)
    root.mainloop()
