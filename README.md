# SmartSplit: Expense Splitting Application

SmartSplit is a desktop application built with Python and Tkinter (using ttkbootstrap) to help groups track shared expenses and calculate who owes whom.

## Features

* **Member Management:** Add and remove members from the group.
* **Expense Tracking:** Record expenses, specifying the payer, amount, description, date, and who shared the expense.
* **Balance Calculation:** Automatically calculates the balance for each member (how much they owe or are owed).
* **Expense History:** View a chronological list of all recorded expenses.
* **Settlement Suggestions:** Provides clear instructions on the simplest way for members to settle their debts with each other using a greedy algorithm.
* **Expense Deletion:** Allows removing specific expenses, automatically recalculating balances.
* **Currency Selection:** Supports multiple currencies (₹, $, €, £, ¥).
* **Data Export:**
    * Export current balances to a text file (.txt).
    * Export the complete expense history to a CSV file (.csv).
* **Data Import:** Import expense history from a CSV file (clears existing data before import).
* **Visualization:** Generate a pie chart showing the share of total expenses per member.
* **Clear Data:** Option to reset all members and expenses.
* **Themed Interface:** Uses `ttkbootstrap` for a modern look and feel (defaults to "superhero" theme).

## Requirements

* Python 3.x
* Tkinter (usually included with Python)
* ttkbootstrap (`pip install ttkbootstrap`)
* Matplotlib (`pip install matplotlib`)

## How to Run

1.  **Ensure Requirements:** Make sure you have Python and the required libraries (`ttkbootstrap`, `matplotlib`) installed.
2.  **Save the Code:** Save the script as a Python file (e.g., `smartsplit_app.py`).
3.  **Run from Terminal:** Execute the script using Python:
    ```bash
    python smartsplit_app.py
    ```
    (Replace `smartsplit_app.py` with the actual filename if you saved it differently).
4.  **Use the GUI:** The application window will appear, allowing you to manage members and expenses.

## Usage Guide

1.  **Select Currency:** Choose your desired currency from the dropdown at the top.
2.  **Add Members:** Enter a member's name in the "Add Member" field and click "Add". Add all participants.
3.  **Add Expenses:**
    * Enter the name of the person who paid in the "Payer" field.
    * Enter the total amount paid.
    * (Optional) Add a description for the expense.
    * In the "Shared With" field, enter the names of *all* members who participated in this expense (including the payer if applicable), separated by commas.
    * Click "Add Expense".
4.  **View Information:** Use the buttons ("Show Balances", "View Members", "View History", "Settle Up") to display information in the text area below.
5.  **Delete Expenses:** Select an expense from the table at the bottom and click "Delete Expense". Confirm the deletion.
6.  **Export/Import:** Use the corresponding buttons to save or load expense data.
7.  **Visualize:** Click "Pie Chart" to see a visual breakdown of expense shares.
8.  **Clear Data:** Use the "Clear All" button (with confirmation) to reset the application.

## CSV Format (for Import/Export)

The CSV file uses the following columns:

* `Date`: Date and time of the expense (Format: `YYYY-MM-DD HH:MM`).
* `Payer`: Name of the member who paid.
* `Amount`: The total amount of the expense (numeric).
* `Shared With`: A pipe-separated (`|`) list of member names who shared the expense.
* `Description`: (Optional) Description of the expense.

**Note:** Importing a CSV will clear any existing data in the application.
