import random
from datetime import datetime


# ==============================
# BANKING SYSTEM
# ==============================

# Dictionary to store all bank accounts
accounts = {}


# ==============================
# CREATE ACCOUNT
# ==============================

def create_account():
    print("\n========== CREATE ACCOUNT ==========")

    name = input("Enter your name: ")
    phone = input("Enter your phone number: ")

    while True:
        pin = input("Create a 4-digit PIN: ")

        if pin.isdigit() and len(pin) == 4:
            break
        else:
            print("❌ PIN must contain exactly 4 digits.")

    # Generate unique 6-digit account number
    while True:
        account_number = str(random.randint(100000, 999999))

        if account_number not in accounts:
            break

    accounts[account_number] = {
        "name": name,
        "phone": phone,
        "pin": pin,
        "balance": 0.0,
        "transactions": []
    }

    print("\n✅ Account created successfully!")
    print("Your Account Number:", account_number)
    print("Please remember your Account Number and PIN.")


# ==============================
# LOGIN
# ==============================

def login():
    print("\n========== LOGIN ==========")

    account_number = input("Enter Account Number: ")
    pin = input("Enter PIN: ")

    if account_number in accounts:
        if accounts[account_number]["pin"] == pin:
            print("\n✅ Login successful!")
            print("Welcome,", accounts[account_number]["name"])
            account_menu(account_number)
        else:
            print("❌ Incorrect PIN.")
    else:
        print("❌ Account not found.")


# ==============================
# CHECK BALANCE
# ==============================

# def check_balance(account_number):
#     balance = accounts[account_number]["balance"]

#     print("\n========== ACCOUNT BALANCE ==========")
#     print("Account Holder:", accounts[account_number]["name"])
#     print("Current Balance: ₹", format(balance, ".2f"))
def check_balance(account_number):
    print("\n========== ACCOUNT BALANCE ==========")

    balance = accounts[account_number]["balance"]

    print("Account Holder :", accounts[account_number]["name"])
    print("Account Number :", account_number)
    print("Current Balance: ₹", balance)

    input("\nPress Enter to continue...")


# ==============================
# DEPOSIT MONEY
# ==============================

def deposit(account_number):
    print("\n========== DEPOSIT MONEY ==========")

    try:
        amount = float(input("Enter amount to deposit: ₹"))

        if amount <= 0:
            print("❌ Amount must be greater than 0.")
            return

        accounts[account_number]["balance"] += amount

        transaction = {
            "type": "Deposit",
            "amount": amount,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        accounts[account_number]["transactions"].append(transaction)

        print("✅ Deposit successful!")
        print("Deposited: ₹", format(amount, ".2f"))
        print("New Balance: ₹",
              format(accounts[account_number]["balance"], ".2f"))

    except ValueError:
        print("❌ Please enter a valid amount.")


# ==============================
# WITHDRAW MONEY
# ==============================

def withdraw(account_number):
    print("\n========== WITHDRAW MONEY ==========")

    try:
        amount = float(input("Enter amount to withdraw: ₹"))

        if amount <= 0:
            print("❌ Amount must be greater than 0.")
            return

        if amount > accounts[account_number]["balance"]:
            print("❌ Insufficient balance.")
            return

        accounts[account_number]["balance"] -= amount

        transaction = {
            "type": "Withdrawal",
            "amount": amount,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        accounts[account_number]["transactions"].append(transaction)

        print("✅ Withdrawal successful!")
        print("Withdrawn: ₹", format(amount, ".2f"))
        print("Remaining Balance: ₹",
              format(accounts[account_number]["balance"], ".2f"))

    except ValueError:
        print("❌ Please enter a valid amount.")


# ==============================
# TRANSFER MONEY
# ==============================

def transfer(account_number):
    print("\n========== TRANSFER MONEY ==========")

    receiver = input("Enter receiver's Account Number: ")

    if receiver not in accounts:
        print("❌ Receiver account not found.")
        return

    if receiver == account_number:
        print("❌ You cannot transfer money to your own account.")
        return

    try:
        amount = float(input("Enter amount to transfer: ₹"))

        if amount <= 0:
            print("❌ Amount must be greater than 0.")
            return

        if amount > accounts[account_number]["balance"]:
            print("❌ Insufficient balance.")
            return

        # Deduct from sender
        accounts[account_number]["balance"] -= amount

        # Add to receiver
        accounts[receiver]["balance"] += amount

        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Sender transaction
        sender_transaction = {
            "type": "Transfer Sent",
            "amount": amount,
            "to": receiver,
            "date": current_time
        }

        accounts[account_number]["transactions"].append(
            sender_transaction
        )

        # Receiver transaction
        receiver_transaction = {
            "type": "Transfer Received",
            "amount": amount,
            "from": account_number,
            "date": current_time
        }

        accounts[receiver]["transactions"].append(
            receiver_transaction
        )

        print("\n✅ Transfer successful!")
        print("Transferred: ₹", format(amount, ".2f"))
        print("To Account:", receiver)
        print("Remaining Balance: ₹",
              format(accounts[account_number]["balance"], ".2f"))

    except ValueError:
        print("❌ Please enter a valid amount.")


# ==============================
# TRANSACTION HISTORY
# ==============================

def transaction_history(account_number):
    print("\n========== TRANSACTION HISTORY ==========")

    transactions = accounts[account_number]["transactions"]

    if len(transactions) == 0:
        print("No transactions found.")
        return

    for i, transaction in enumerate(transactions, start=1):

        print("\nTransaction", i)
        print("Type:", transaction["type"])
        print("Amount: ₹", format(transaction["amount"], ".2f"))
        print("Date:", transaction["date"])

        if "to" in transaction:
            print("To Account:", transaction["to"])

        if "from" in transaction:
            print("From Account:", transaction["from"])


# ==============================
# CHANGE PIN
# ==============================

def change_pin(account_number):
    print("\n========== CHANGE PIN ==========")

    old_pin = input("Enter old PIN: ")

    if old_pin != accounts[account_number]["pin"]:
        print("❌ Incorrect old PIN.")
        return

    while True:
        new_pin = input("Enter new 4-digit PIN: ")

        if new_pin.isdigit() and len(new_pin) == 4:
            break
        else:
            print("❌ PIN must contain exactly 4 digits.")

    confirm_pin = input("Confirm new PIN: ")

    if new_pin != confirm_pin:
        print("❌ New PINs do not match.")
        return

    accounts[account_number]["pin"] = new_pin

    print("✅ PIN changed successfully!")


# ==============================
# ACCOUNT MENU
# ==============================

def account_menu(account_number):

    while True:

        print("\n")
        print("======================================")
        print("          ACCOUNT MENU")
        print("======================================")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Transaction History")
        print("6. Change PIN")
        print("7. Logout")
        print("======================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            check_balance(account_number)

        elif choice == "2":
            deposit(account_number)

        elif choice == "3":
            withdraw(account_number)

        elif choice == "4":
            transfer(account_number)

        elif choice == "5":
            transaction_history(account_number)

        elif choice == "6":
            change_pin(account_number)

        elif choice == "7":
            print("\n✅ Logged out successfully.")
            break

        else:
            print("❌ Invalid choice. Please try again.")


# ==============================
# MAIN MENU
# ==============================

def main():

    while True:

        print("\n")
        print("======================================")
        print("          BANKING SYSTEM")
        print("======================================")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        print("======================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_account()

        elif choice == "2":
            login()

        elif choice == "3":
            print("\nThank you for using the Banking System!")
            print("Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


# ==============================
# START PROGRAM
# ==============================

if __name__ == "__main__":
    main()