# Currently: Finished putting personal touch (Password reset)
# export API_KEY="Api Key provided by https://iexcloud.io/"
# This program is not considering race conditions
# Flask run to run the code


import os
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Get sum shares summarized by stock from db
    stock_summary = db.execute(
        "SELECT user_id, SUM(shares) as sumshares, stock, cash FROM stock_assignments JOIN stocks ON stocks.id = stock_assignments.stock_id JOIN users ON users.id = stock_assignments.user_id WHERE users.id = ? GROUP BY stock", session["user_id"])

    i = 0
    gtotal = float(0)
    # for each dictionary in list of dictionaries stock_summary
    for element in stock_summary:
        # look for the current stock price using lookup
        result = lookup(element["stock"])
        # print(result)

        # creates new value in dictionary in the "index" i, and adds the current price
        stock_summary[i]["price"] = usd(result["price"])

        # print(type(result["price"]))

        # stores the name of the share
        namesh = result["name"]
        stock_summary[i]["namesh"] = namesh

        # Variable to store the total value of each holding (shares times price). Then is stored in the dictionary
        valueshares = result["price"] * stock_summary[i]["sumshares"]
        stock_summary[i]["valueshares"] = usd(valueshares)

        # Variable to store grand totaal by summing the value of the shares
        gtotal = gtotal + valueshares

        # print(stock_summary)

        # adds 1 to keep updating the next value
        i = i + 1

    # Get the current cash stored in the dictionary and stores it in a value
    rows = db.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
    cash = float(rows[0]["cash"])

    # gtotal previously stored the sum of the value + cash. Notice if the stock changes you may have more or less GTOTAL dependind n the behaviour of the stock
    gtotal = gtotal + cash

    # pass stock_summary information to be iterated in JINJA
    return render_template("index.html", stock_summaryp=stock_summary, cashp=usd(cash), gtotalp=usd(gtotal))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # Store the results of the API call in results
        result = lookup(request.form.get("symbol"))

        # if field is blank or the symbol doesn't provide anything in result. Error is triggered
        if not request.form.get("symbol") or not result:
            return apology("Symbol not valid", 400)

        # if field is blank. Apology is triggered
        if not request.form.get("shares"):
            return apology("Shares not valid", 400)

        # if input is negative int. Apology is triggered. Step 1 removed from html

        sharestb = request.form.get("shares")

        if not sharestb.isnumeric():
            return apology("input is not a a number", 400)

        # We check if the number has a decimal place and return an error if so.
        if float(sharestb) <= 0 or not float(sharestb).is_integer():
            return apology("input is not a positive integer digit", 400)

        # Store values colected from API
        price = result["price"]
        symbol = result["symbol"]

        # Store current epoch time. Multiplied by 1000 to get milissecs accuracy. Reference: https://pynative.com/python-current-date-time/
        t = time.time()
        epoch = int(t * 1000)
        # print('Current time in milliseconds:', epoch)

        # Store values collected from HTML web. The number of shares to buy
        shares = int(request.form.get("shares"))

        # Consult the cash that user has available and stores it in a variable
        rows = db.execute("SELECT cash FROM users WHERE id = ?",
                          session["user_id"])

        cash = rows[0]["cash"]

        # Check how much money is available
        # print(price * shares)
        # print(cash)

        # If user doesn't have enough money to buy system will throw an error

        if price * shares > cash:
            return apology("You don't have enough cash to perform this transaction", 403)

        # If user has enough money to buy
        else:
            # Check if Symbol exists in DB table "stocks" otherwise it will get added
            rows = db.execute("SELECT * FROM stocks WHERE stock = ?", symbol)

            # If stock symbol doesn't exist. It will create one in the DB
            if len(rows) == 0:
                db.execute("INSERT INTO stocks (stock) VALUES (?);", symbol)

                # consult db to retrieve the id assigned by the table
                rows = db.execute(
                    "SELECT * FROM stocks WHERE stock = ?", symbol)

            # stockid to be used to insert value in stock_assignments table
            stockid = rows[0]["id"]

            # creates an entry in DB specifying user_id, stock_id, shares, bought_price, epoch_time
            db.execute("INSERT INTO stock_assignments (user_id, stock_id, shares, price, epoch_time) VALUES (?, ?, ?, ?, ?);",
                       session["user_id"], stockid, shares, price, epoch)

            # substract value from current cash and updates users' cash value in DB with current value
            cash = cash - (price * shares)
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       cash, session["user_id"])

        return redirect("/")

    else:
        # Quote accepts a Symbol to be quoted
        return render_template("buy.html")


@ app.route("/history")
@ login_required
def history():
    """Show history of transactions"""

    # Epoch time is used in the sql database. Therefore, the data is manipulated so it can be human readable in UTC
    # I realized time must be divided by 1000 otherwise datetime doesn't work. It seems it has a limit with 13 digits epoch time
    stock_summary = db.execute(
        "SELECT stock, shares, price, datetime(epoch_time/1000, 'unixepoch', 'utc') AS time_utc, user_id FROM stock_assignments JOIN stocks ON stocks.id = stock_assignments.stock_id JOIN users ON users.id = stock_assignments.user_id WHERE users.id = ?", session["user_id"])

    # print(stock_summary)

    # Create a new item "listprice" in list of dictionaries "stock_summary". We grab the price column then transform it applying usd function then append the result in the key:value pair "listprice": Price modified.
    i = 0
    for element in stock_summary:
        price = stock_summary[i]["price"]
        stock_summary[i]["listprice"] = usd(price)
        i = i + 1

    # print(stock_summary)

    return render_template("history.html", stock_summaryp=stock_summary)


@ app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@ app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@ app.route("/quote", methods=["GET", "POST"])
@ login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Store the results of the API call in results
        result = lookup(request.form.get("symbol"))

        # if field is blank or the symbol doesn't provide anything in result. Error is triggered
        if not request.form.get("symbol") or not result:
            return apology("Symbol not valid", 400)

        # Provide a name for every result in the dictionary

        name = result["name"]
        price = result["price"]
        symbol = result["symbol"]

        # Pass the calues to the HTML page so they can be rendered. "namep" = nameplaceholder
        return render_template("quoted.html", namep=name, pricep=usd(price), symbolp=symbol)

    else:
        # Quote accepts a Symbol to be quoted
        return render_template("quote.html")


@ app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted not blank
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted not blank
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted not blank
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)

        # Ensure password and password confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation don't match", 400)

        # Query database for username. To check if already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # If result of the previous query is different than 0 it means the username already exists
        if len(rows) != 0:
            return apology("username is already taken", 400)

        else:
            # Hash the password to avoid store plain text passwords in the DB
            passworddb = generate_password_hash(request.form.get("password"))

            # Insert into the finance db the username and password hashed. In summary, the username and password are created in the db
            db.execute("INSERT INTO users (username, hash) VALUES (?,?);",
                       request.form.get("username"), passworddb)

            # Recovers the data for the user that just registered from the DB
            rows = db.execute("SELECT * FROM users WHERE username = ?",
                              request.form.get("username"))

            # Log the user in.
            # From that recovered data the ID is extracted to be stored in the session.
            session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # If the request is a GET
    else:
        return render_template("registration.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        result = request.form.get("symbol")
        shares = request.form.get("shares")

        # If user didn't select and Stock form the drop down
        if not result:
            return apology("Symbol not valid", 400)

        if not shares or int(shares) <= 0:
            return apology("Shares was not selected or is not a positive number", 400)

        stock_summary = db.execute(
            "SELECT stock FROM stock_assignments JOIN stocks ON stocks.id = stock_assignments.stock_id JOIN users ON users.id = stock_assignments.user_id WHERE users.id = ? GROUP BY stock", session["user_id"])

        n = 0
        for element in stock_summary:
            symbol = element["stock"]
            # Protecting in case user passes information editing the HTML that can affect the db
            if result == symbol:
                # If we found user owns a share we will add 1
                n = n + 1

        # If result is > 1 means users own a share. Otherwise user doesn't own the stock
        if n == 0:
            return apology("User does not own shares of this stock", 400)

        rows = db.execute(
            "SELECT user_id, SUM(shares) as sumshares, stock FROM stock_assignments JOIN stocks ON stocks.id = stock_assignments.stock_id JOIN users ON users.id = stock_assignments.user_id WHERE users.id = ? AND stock = ? GROUP BY stock", session["user_id"], result)

        sumshares = rows[0]["sumshares"]

        if int(shares) > sumshares:
            return apology("You don't own enough shares to proceed with this transaction, consult your summary page", 400)
        else:
            # UPDATE DB with the number of shares bought
            # Stores the results of the API call in result1
            result1 = lookup(request.form.get("symbol"))

            # Store values colected from API
            sale_price = result1["price"]
            symbol = result1["symbol"]

            # Store current epoch time. Multiplied by 1000 to get milissecs accuracy. Reference: https://pynative.com/python-current-date-time/
            t = time.time()
            epoch = int(t * 1000)
            # print('Current time in milliseconds:', epoch)

            # consult db to retrieve the id assigned by the table
            rows = db.execute(
                "SELECT * FROM stocks WHERE stock = ?", symbol)

            # stockid to be used to insert value in stock_assignments table
            stockid = rows[0]["id"]

            # creates an entry in DB specifying user_id, stock_id, shares, bought_price, epoch_time
            # notice we update the value of the shares with a negative symbol "-" indicating that it was sell something and that the user no longer owns that share
            db.execute("INSERT INTO stock_assignments (user_id, stock_id, shares, price, epoch_time) VALUES (?, ?, ?, ?, ?);",
                       session["user_id"], stockid, -int(shares), sale_price, epoch)

            # Consult the cash that user has available and stores it in a variable
            rows = db.execute("SELECT cash FROM users WHERE id = ?",
                              session["user_id"])

            cash = rows[0]["cash"]

            # Adds value from the sell of the shares and updates users' cash value in DB with current value
            cash = cash + (sale_price * int(shares))
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       cash, session["user_id"])

        # Redirect to home page
        return redirect("/")

    else:

        # Collect information of the stocks owned by the user and then pass that info to sell.html so it can be rendered
        stock_summary = db.execute(
            "SELECT user_id, SUM(shares) as sumshares, stock FROM stock_assignments JOIN stocks ON stocks.id = stock_assignments.stock_id JOIN users ON users.id = stock_assignments.user_id WHERE users.id = ? GROUP BY stock", session["user_id"])

        return render_template("sell.html", stock_summaryp=stock_summary)


@ app.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    """Change password user"""

    if request.method == "POST":

        # Username is not asked because user is already logged in
        # Ensure password was submitted not blank
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted not blank
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)

        # Ensure password and password confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation don't match", 400)

        # hash the new password
        passworddb = generate_password_hash(request.form.get("password"))

        # updates the password in the DB using the session["user_id"]
        db.execute("UPDATE users SET hash = ? WHERE id = ?;",
                   passworddb, session["user_id"])

        # Logs out the user so it can login again
        session.clear()

        # Redirect user to home page so it can login again
        return redirect("/")

    # If the request is a GET
    else:
        return render_template("changepassword.html")
