from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal, ROUND_DOWN
from flask_login import login_required, current_user
from .models import Metamask
from . import db
import re
import requests
import time

# Define the token mappings
TOKEN_MAPPING = {
    "eth": "ethereum",
    "btc": "bitcoin",
    "bnb": "binancecoin",
    "ape": "apecoin",
    "usdc": "usd-coin",
    "was": "wasder",
    "pepe": "pepe",
    # add more mappings as needed
}
MAX_RETRIES = 3
DELAY_SECONDS = 20

# API key for CoinMarketCap
api_key = "2b7c3cb0-e7f6-496e-aa1d-88359e6be374"
crypto_symbols = ["ETH", "BTC", "APE", "USDC", "BNB"]

url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={",".join(crypto_symbols)}'
headers = {"X-CMC_PRO_API_KEY": api_key}

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        address = request.form.get("address")
        balance = request.form.get("balance")
        token = request.form.get("token")
        network = request.form.get("network")
        pattern_eth = re.compile("^0x[a-fA-F0-9]{40}$")
        pattern_brc20 = re.compile("^bc1[a-zA-HJ-NP-Z0-9]{8,87}$")

        # check if wallet is already in the databasee
        existing_wallet = Metamask.query.filter_by(
            address=address, token=token, network=network, user_id=current_user.id
        ).first()
        if existing_wallet:
            existing_wallet.balance += Decimal(balance)
            db.session.commit()
            flash("Balance updated succesfully", category="success")
        elif not pattern_eth.match(address) and not pattern_brc20.match(address):
            flash("Please enter a valid address", category="error")
        elif Decimal(balance) <= 0:
            flash("Please enter a valid balance > 0", category="error")
        else:
            new_wallet = Metamask(
                address=address,
                balance=balance,
                token=token,
                network=network,
                user_id=current_user.id,
            )
            db.session.add(new_wallet)
            db.session.commit()
            flash("Added successfully", category="success")

    return render_template("home.html", user=current_user)


@views.route("/metamask", methods=["GET", "POST"])
@login_required
def metamask():
    # get all unique wallet addresses from the database
    wallets = (
        db.session.query(Metamask.address)
        .distinct()
        .filter_by(user_id=current_user.id)
        .all()
    )
    # sort the wallets in alphabetical order
    wallets = sorted(wallets)
    # create a list to store wallet data in the desired format
    wallet_data = []
    total = 0
    # loop through each wallet address
    for wallet in wallets:
        # get all rows with the current wallet address
        rows = Metamask.query.filter_by(
            address=wallet[0], user_id=current_user.id
        ).all()
        # sort the rows by token
        rows = sorted(rows, key=lambda x: x.token)
        # calculate the total value in USD for the wallet
        total_value = 0
        row_data_list = []
        for row in rows:
            token_name = TOKEN_MAPPING.get(row.token, row.token)
            token_price = Decimal(price(token_name))
            total_value += row.balance * token_price
            total_value = round(total_value, 2)
            token_value = round(row.balance * token_price, 2)
            row_data = {
                "token": row.token,
                "balance": row.balance,
                "network": row.network,
                "token_value": token_value,
            }
            row_data_list.append(row_data)
        # append the wallet data to the list
        row_data_list = sorted(
            row_data_list, key=lambda x: x["token_value"], reverse=True
        )
        wallet_data.append(
            {"address": wallet[0], "rows": row_data_list, "total_value": total_value}
        )
        # Calculate total value across all wallets
        total = sum(wallet["total_value"] for wallet in wallet_data)

    bitcoin_price = price("bitcoin")
    ethereum_price = price("ethereum")
    return render_template(
        "metamask.html",
        user=current_user,
        btc_price=bitcoin_price,
        eth_price=ethereum_price,
        total=total,
        wallet_data=wallet_data,
    )


def price(crypto):
    for retry in range(MAX_RETRIES):
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{crypto}?tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
        )
        if response.status_code == 200:
            price_data = response.json()
            if isinstance(price_data, list):
                # If the response is a list, access the first element and then the price data
                crypto_price = price_data[0]["market_data"]["current_price"]["usd"]
            else:
                # If the response is a dictionary, directly access the price data
                crypto_price = price_data["market_data"]["current_price"]["usd"]

            # Render the price
            return crypto_price

        else:
            print(
                f"Request failed with status code {response.status_code}. Retrying in {DELAY_SECONDS} seconds..."
            )
            time.sleep(DELAY_SECONDS)
    raise Exception("CoinGecko API is ass")


@views.route("/edit", methods=["POST", "GET"])
def edit():
    if request.method == "POST":
        address = request.form.get("address")
        token = request.form.get("token")
        network = request.form.get("network")
        new_balance = request.form.get("balance")

        wallet = Metamask.query.filter_by(
            address=address, token=token, network=network, user_id=current_user.id
        ).first()
        if wallet:
            wallet.balance = new_balance
            db.session.commit()
            flash("Balance updated successfully", category="success")
        else:
            flash("Wallet not found", category="error")

    return render_template("edit.html", user=current_user)


@views.route("/delete-wallet", methods=["POST"])
def delete_wallet():
    # Retrieve the wallet address and token from the request data
    wallet_address = request.json.get("address")
    token = request.json.get("token")

    try:
        # Find the specific row in the database with the given address and token
        row_to_delete = Metamask.query.filter_by(
            address=wallet_address, token=token
        ).first()

        if row_to_delete:
            # Delete the row from the database
            db.session.delete(row_to_delete)
            db.session.commit()
            return jsonify({"message": "Row deleted successfully"})
        else:
            return jsonify({"message": "Row not found"})

    except SQLAlchemyError as e:
        # Handle any potential database errors
        db.session.rollback()
        return jsonify({"message": "Error deleting row: " + str(e)}), 500
