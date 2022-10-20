import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

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


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("SELECT symbol, price, shares, cost, Rest FROM shoppings WHERE userID = :USER_ID ", USER_ID  = USER_ID )
    length_rows = len(rows)
    symbol_i = rows[0]["symbol"]
    price_i = rows[0]["price"]
    shares_i = rows[0]["shares"]
    cost_i = rows[0]["cost"]
    rest_i = rows[0]["Rest"]
    return render_template("index.html",  rows = rows)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # input the share symbol the user wants to buy
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("The symbol was not inputed")

        # inputing the number of shares the user wants to buy
        shares = int(request.form.get("shares"))
        if not shares:
            return apology("The number of shares was not iputed")

        # getting the share-price
        share_company = lookup(symbol)
        price = float(share_company["price"])

        # defying the summ of user's money ("SELECT * FROM users WHERE username = :username", username = username)
        rows = db.execute("SELECT username, cash FROM users WHERE id = :USER_ID", USER_ID = USER_ID)
        if not rows:
            return apology("the row of the table was not inputed")

        # getting from users-database user's id and cash
        username0 = rows[0]
        username = username0["username"]
        f_sum_money0 = rows[0]
        f_sum_money = f_sum_money0["cash"]

        # defying the amount of money needed for bying
        sum_money = f_sum_money
        price = float(share_company["price"])
        cost_share = price * shares

        # if the user has not enough money
        if cost_share > sum_money:
            return apology("you have not enough money")

        # the users summ of money after buying
        sum_money = sum_money - cost_share

        # putting the data into the shopping-table and the users-table
        db.execute("INSERT INTO shoppings (userID, username, symbol, price, shares, cost, Rest) VALUES(:USER_ID, :username, :symbol, :price, :shares, :cost, :sum_money)", USER_ID = USER_ID, username = username, symbol = symbol, price = price, shares = shares, cost = cost_share, sum_money = sum_money)
        db.execute("UPDATE users SET cash = :cash WHERE id = :USER_ID", cash = sum_money, USER_ID = USER_ID)

        # getting the new information after the buying
        return render_template("bought.html", USER_ID = USER_ID, username = username, symbol = symbol, price = price, shares = shares, cost_share = cost_share, sum_money = sum_money, f_sum_money = f_sum_money)

    else:
        return render_template("buy.html")
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    return jsonify("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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

        # getting the value by the global variable user_id
        user_id_T = db.execute("SELECT id FROM users WHERE username = :username", username = request.form.get("username"))
        USER_ID0 = user_id_T[0]
        global USER_ID
        USER_ID = USER_ID0["id"]

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
            return apology("the share-symbol was not inputed")

        # getting information about company
        share_company = lookup(symbol)

        return render_template("quoted.html", share_company = share_company)

    else:
        return render_template("quote.html")
# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


# OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # asking user for username and checking if the text-field is empty
        username = request.form.get("username")

        # querry database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = username)

        # if username already exists or was not inputed
        if not username:
            return apology("you have not inputed a username", 403)
        elif len(rows) > 0:
            return apology("this username already exists", 403)

        # asking user for password
        password = request.form.get("password")
        if not password:
            return apology("you have not inputed a password", 403)

        # asking user for password confirmation
        confirmation = request.form.get("confirmation")
        if confirmation != password:
            return apology("your password was not confirmed", 403)

        #hashing the password
        hash_pass = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # inserting the sum of money at start
        cash_dol = 10000

        # inserting data to data-base
        db.execute("INSERT INTO users (username, hash, cash) VALUES (:username, :hash_pass, :cash_dol)", username = username, hash_pass = hash_pass, cash_dol = cash_dol)

        # redirecting into main
        return redirect("/")

    else:
        return render_template("register.html")
#  OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK OK


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
