from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
import os
from datetime import datetime

app = Flask(__name__)

# Demo secret key.
# For production, use an environment variable.
app.secret_key = os.environ.get("SECRET_KEY", "banking-demo-secret-key")

DATA_FILE = "accounts.json"


# ==========================================
# LOAD ACCOUNTS
# ==========================================

def load_accounts():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


# ==========================================
# SAVE ACCOUNTS
# ==========================================

def save_accounts(accounts):
    with open(DATA_FILE, "w") as file:
        json.dump(accounts, file, indent=4)


# ==========================================
# GENERATE ACCOUNT NUMBER
# ==========================================

def generate_account_number(accounts):

    while True:
        account_number = str(random.randint(100000, 999999))

        if account_number not in accounts:
            return account_number


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# CREATE ACCOUNT
# ==========================================

@app.route("/create-account", methods=["GET", "POST"])
def create_account():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        pin = request.form.get("pin", "").strip()

        if not name or not phone or not pin:
            flash("All fields are required.", "error")
            return redirect(url_for("create_account"))

        if not pin.isdigit() or len(pin) != 4:
            flash("PIN must contain exactly 4 digits.", "error")
            return redirect(url_for("create_account"))

        accounts = load_accounts()

        account_number = generate_account_number(accounts)

        accounts[account_number] = {
            "name": name,
            "phone": phone,
            "pin": pin,
            "balance": 0.0,
            "transactions": []
        }

        save_accounts(accounts)

        return render_template(
            "create_account.html",
            success=True,
            account_number=account_number
        )

    return render_template("create_account.html", success=False)


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        account_number = request.form.get("account_number", "").strip()
        pin = request.form.get("pin", "").strip()

        accounts = load_accounts()

        if account_number not in accounts:
            flash("Account not found.", "error")
            return redirect(url_for("login"))

        if accounts[account_number]["pin"] != pin:
            flash("Incorrect PIN.", "error")
            return redirect(url_for("login"))

        session["account_number"] = account_number

        flash("Login successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ==========================================
# LOGIN CHECK
# ==========================================

def get_logged_in_account():

    account_number = session.get("account_number")

    if not account_number:
        return None, None

    accounts = load_accounts()

    if account_number not in accounts:
        session.clear()
        return None, None

    return account_number, accounts


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    account_number, accounts = get_logged_in_account()

    if not account_number:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    account = accounts[account_number]

    return render_template(
        "dashboard.html",
        account=account,
        account_number=account_number
    )


# ==========================================
# DEPOSIT
# ==========================================

@app.route("/deposit", methods=["GET", "POST"])
def deposit():

    account_number, accounts = get_logged_in_account()

    if not account_number:
        return redirect(url_for("login"))

    if request.method == "POST":

        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        if amount <= 0:
            flash("Enter a valid amount.", "error")
            return redirect(url_for("deposit"))

        accounts[account_number]["balance"] += amount

        transaction = {
            "type": "Deposit",
            "amount": amount,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        accounts[account_number]["transactions"].append(transaction)

        save_accounts(accounts)

        flash(f"₹{amount:.2f} deposited successfully.", "success")

        return redirect(url_for("dashboard"))

    return render_template("deposit.html")


# ==========================================
# WITHDRAW
# ==========================================

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():

    account_number, accounts = get_logged_in_account()

    if not account_number:
        return redirect(url_for("login"))

    if request.method == "POST":

        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        if amount <= 0:
            flash("Enter a valid amount.", "error")
            return redirect(url_for("withdraw"))

        if amount > accounts[account_number]["balance"]:
            flash("Insufficient balance.", "error")
            return redirect(url_for("withdraw"))

        accounts[account_number]["balance"] -= amount

        transaction = {
            "type": "Withdrawal",
            "amount": amount,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        accounts[account_number]["transactions"].append(transaction)

        save_accounts(accounts)

        flash(f"₹{amount:.2f} withdrawn successfully.", "success")

        return redirect(url_for("dashboard"))

    return render_template("withdraw.html")


# ==========================================
# TRANSFER
# ==========================================

@app.route("/transfer", methods=["GET", "POST"])
def transfer():

    account_number, accounts = get_logged_in_account()

    if not account_number:
        return redirect(url_for("login"))

    if request.method == "POST":

        receiver = request.form.get("receiver", "").strip()

        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        if receiver not in accounts:
            flash("Receiver account not found.", "error")
            return redirect(url_for("transfer"))

        if receiver == account_number:
            flash("You cannot transfer money to your own account.", "error")
            return redirect(url_for("transfer"))

        if amount <= 0:
            flash("Enter a valid amount.", "error")
            return redirect(url_for("transfer"))

        if amount > accounts[account_number]["balance"]:
            flash("Insufficient balance.", "error")
            return redirect(url_for("transfer"))

        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Sender
        accounts[account_number]["balance"] -= amount

        accounts[account_number]["transactions"].append({
            "type": "Transfer Sent",
            "amount": amount,
            "to": receiver,
            "date": current_time
        })

        # Receiver
        accounts[receiver]["balance"] += amount

        accounts[receiver]["transactions"].append({
            "type": "Transfer Received",
            "amount": amount,
            "from": account_number,
            "date": current_time
        })

        save_accounts(accounts)

        flash(
            f"₹{amount:.2f} transferred successfully.",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template("transfer.html")


# ==========================================
# TRANSACTION HISTORY
# ==========================================

@app.route("/transactions")
def transactions():

    account_number, accounts = get_logged_in_account()

    if not account_number:
        return redirect(url_for("login"))

    account = accounts[account_number]

    transactions = account["transactions"]

    return render_template(
        "transactions.html",
        transactions=transactions
    )


# ==========================================
# CHANGE PIN
# ==========================================

@app.route("/change-pin", methods=["GET", "POST"])
def change_pin():

    account_number, accounts = get_logged_in_account()

    if not account_number:
        return redirect(url_for("login"))

    if request.method == "POST":

        old_pin = request.form.get("old_pin", "").strip()
        new_pin = request.form.get("new_pin", "").strip()
        confirm_pin = request.form.get("confirm_pin", "").strip()

        if accounts[account_number]["pin"] != old_pin:
            flash("Incorrect old PIN.", "error")
            return redirect(url_for("change_pin"))

        if not new_pin.isdigit() or len(new_pin) != 4:
            flash("New PIN must contain exactly 4 digits.", "error")
            return redirect(url_for("change_pin"))

        if new_pin != confirm_pin:
            flash("New PINs do not match.", "error")
            return redirect(url_for("change_pin"))

        accounts[account_number]["pin"] = new_pin

        save_accounts(accounts)

        flash("PIN changed successfully.", "success")

        return redirect(url_for("dashboard"))

    return render_template("change_pin.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("index"))


# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)