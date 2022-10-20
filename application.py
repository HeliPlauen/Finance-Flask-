import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import json
import csv

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


#create the global variable username and company
USER_ID = int
CASH = 10000


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # making local table free
    db.execute("DELETE FROM shoppings2")

    # getting values from the common table
    rows = db.execute("SELECT symbol, name, price, shares, cost FROM shoppings WHERE userID = :USER_ID ", USER_ID  = USER_ID)

    # creating the list of the symbols
    symbols = []

    # filling list by symbols
    for i in range(len(rows)):
        symb = rows[i]["symbol"]
        if symb not in symbols:
            symbols.append(symb)
    symbols.sort()

    # counting the sum number of shares and sum of costs and puting it into the local table "SELECT cash FROM users WHERE id = :USER_ID", USER_ID = USER_ID
    sum_cost = CASH
    for symbol in symbols:
        rows3 = db.execute("SELECT symbol, name, price, SUM(shares), SUM(cost) FROM shoppings WHERE userID = :USER_ID AND symbol = :symbol", USER_ID = USER_ID, symbol = symbol)
        symbol = rows3[0]["symbol"]
        name = rows3[0]["name"]

        #getting the share-price
        share_company = lookup(symbol)
        price = float(share_company["price"])

        shares = rows3[0]["SUM(shares)"]
        cost = rows3[0]["SUM(cost)"]
        sum_cost += cost
        db.execute("INSERT INTO shoppings2 (symbol, name, price, shares, cost) VALUES(:symbol, :name, :price, :shares, :cost)", symbol = symbol, name = name, price = usd(price), shares=shares, cost = usd(cost))

    # getting values from the local table
    rows2 = db.execute("SELECT symbol, name, price, shares, cost FROM shoppings2")

    # returning the html
    return render_template("index.html", USER_ID  = USER_ID, rows2 = rows2, sum_cost = usd(sum_cost), CASH = usd(CASH))
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # input the share symbol the user wants to buy
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("The symbol was not inputed", 400)

        # inputing the number of shares the user wants to buy
        shares0 = request.form.get("shares")
        if not shares0:
            return apology("The number of shares was not iputed", 400)
        if not shares0.isdecimal():
            return apology("The number of shares is not valid", 400)

        # converting shares into int
        shares = int(shares0)
        if shares < 1:
            return apology("The number of shares is not valid", 400)

        # getting the share-name and share-prise
        share_company = lookup(symbol)
        if not share_company:
            return apology("The sharename is not valid", 400)

        # getting the share-name and the share-price
        name = share_company["name"]
        price = float(share_company["price"])

        # defying the summ of user's money ("SELECT * FROM users WHERE username = :username", username = username)
        rows = db.execute("SELECT cash FROM users WHERE id = :USER_ID", USER_ID = USER_ID)
        if not rows:
            return apology("the row of the table was not inputed", 403)

        # getting from users-database user's id and cash
        f_sum_money =  rows[0]["cash"]

        # defying the amount of money needed for bying
        sum_money = f_sum_money
        cost_share = price * shares

        # if the user has not enough money
        if cost_share > sum_money:
            return apology("you have not enough money", 403)

        # the users summ of money after buying
        sum_money = sum_money - cost_share

        # putting the data into the shopping-table and the users-table
        db.execute("INSERT INTO shoppings (userID, symbol, name, price, shares, cost, Rest) VALUES(:USER_ID, :symbol, :name, :price, :shares, :cost, :sum_money)", USER_ID = USER_ID, symbol = symbol, name = name, price = price, shares = shares, cost = cost_share, sum_money = sum_money)
        db.execute("UPDATE users SET cash = :cash WHERE id = :USER_ID", cash = sum_money, USER_ID = USER_ID)

        # changing value bu CASH the global variable
        global CASH
        CASH = sum_money

        # getting the new information after the buying
        return redirect("/")

    else:

        # returning the html
        return render_template("buy.html")
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # getting the usrname from the user aA2@
    username = request.args.get("username")

    # create the bool value
    boolval = True

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username", username = username)
    print(f"check: {rows}")

    # Ensure username exists and password is correct
    if len(rows) > 0:
        boolval = False
        print(boolval)

    # returning data
    print(boolval)
    return json.dumps(boolval)

# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # making local table free
    db.execute("DELETE FROM History")

    # getting data from the global table
    rows = db.execute("SELECT symbol, price, shares, date, time FROM shoppings WHERE userID = :userID", userID = USER_ID)
    for i in range(len(rows)):
        symbol = rows[i]["symbol"]
        price = rows[i]["price"]
        shares = rows[i]["shares"]
        date = rows[i]["date"]
        time = rows[i]["time"]

        # inserting data into the History table
        db.execute("INSERT INTO History (symbol, price, shares, date, time) VALUES(:symbol, :price, :shares, :date, :time)", symbol = symbol, price = price, shares = shares, date = date, time = time)

    # getting data from the history-table
    rows2 = db.execute("SELECT symbol, price, shares, date, time FROM History")

    # returning the html
    return render_template("history.html", USER_ID  = USER_ID, rows2 = rows2)
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/login", methods=["GET", "POST"])
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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # getting value by the global variable USER_ID
        user_id_T = db.execute("SELECT id FROM users WHERE username = :username", username = request.form.get("username"))
        USER_ID0 = user_id_T[0]
        global USER_ID
        USER_ID = USER_ID0["id"]

        # geting value bu CASH the global variable
        id_max = db.execute("SELECT MAX(ID) FROM shoppings WHERE userID = :USER_ID", USER_ID = USER_ID)
        id_max_num = id_max[0]["MAX(ID)"]
        last_cash = db.execute("SELECT Rest FROM shoppings WHERE userID = :USER_ID AND ID = :ID", USER_ID = USER_ID, ID = id_max_num)
        global CASH
        if last_cash:
            CASH = last_cash[0]["Rest"]
        else:
            CASH = 10000

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # input the share symbol
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("the share-symbol was not inputed", 400)

        # getting information about company
        share_company = lookup(symbol)

        # if such shares do not exist
        if not share_company:
            return apology("you inputed the wrong share-symbol or this share-symbol does not exist", 400)

        # returning the html
        return render_template("quoted.html", share_company = share_company)

    else:

        # returning the html
        return render_template("quote.html")
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # asking user for username and checking if the username was not inputed
        username = request.form.get("username")
        if not username:
            return apology("you have not inputed a username", 400)

        # querry database for username and checking if the username already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = username)
        if len(rows) > 0:
            return apology("this username already exists", 400)

        # asking user for password and checking if the password was not inputed
        password = request.form.get("password")
        if not password:
            return apology("you have not inputed a password", 400)

        # asking user for password confirmation
        confirmation = request.form.get("confirmation")
        if confirmation != password:
            return apology("your password was not confirmed", 400)

        #hashing the password
        hash_pass = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # inserting the sum of money at start
        cash_dol = 10000

        # inserting data to data-base
        db.execute("INSERT INTO users (username, hash, cash) VALUES (:username, :hash_pass, :cash)", username = username, hash_pass = hash_pass, cash = cash_dol)

        # redirecting into main
        return redirect("/")

    else:

        # returning the html
        return render_template("register.html")
#  OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#  OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        # getting the share-symbol from user
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("the symbol has not been chosen", 400)

        #getting the share-price
        share_company = lookup(symbol)
        name = share_company["name"]
        price = float(share_company["price"])

        # getting the shares by symbol from the local table
        rows2 = db.execute("SELECT shares FROM shoppings2 WHERE symbol = :symbol", symbol = symbol)
        shares_MAX = rows2[0]["shares"]

        # getting the number of shars from user
        shares0 = request.form.get("shares")
        if not shares0:
            return apology("the number of shares has not been inputed", 400)

        # converting shares into integer
        shares = ( -1 ) * int(shares0)

        if abs(shares) > shares_MAX:
            return apology("you do not have so many shares", 400)

        # counting the cost of the shares were sold
        cost = price * shares

        # getting the maximum ID for the last Rest
        rows4 = db.execute("SELECT MAX(ID) FROM shoppings WHERE userID = :userID", userID = USER_ID)
        id_max_num = rows4[0]["MAX(ID)"]

        # geting the value of cash from the global table (last Rest)
        rows3 = db.execute("SELECT Rest FROM shoppings WHERE userID = :userID AND ID = :ID", userID = USER_ID, ID = id_max_num)
        sum_money = rows3[0]["Rest"]

        # the users summ of money after buying
        sum_money = sum_money - cost

        # putting the data into the shopping-table and the users-table
        db.execute("INSERT INTO shoppings (userID, symbol, name, price, shares, cost, Rest) VALUES(:userID, :symbol, :name, :price, :shares, :cost, :Rest)", userID = USER_ID, symbol = symbol, name = name, price = price, shares = shares, cost = cost, Rest = sum_money)
        db.execute("UPDATE users SET cash = :cash WHERE id = :USER_ID", cash = sum_money, USER_ID = USER_ID)

        # changing value bu CASH the global variable
        global CASH
        CASH = sum_money

        # getting the new information after the buying
        return redirect("/")

    else:

        #geting the symbols from the local table
        rows = db.execute("SELECT symbol FROM shoppings2")

        # creating the list of the symbols
        symbols = []

        # filling list by symbols
        for i in range(len(rows)):
            symb = rows[i]["symbol"]
            symbols.append(symb)

        # returning the html
        return render_template("sell.html", symbols = symbols)
#  OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
