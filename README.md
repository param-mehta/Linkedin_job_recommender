# Algorithmic Trading Bot

## Overview

This repository contains the code to implement an automated data pipenline that scraps latest jobs from Linkedin and performs a similarity search between job descriptions and resume to return the top 5 most relevant jobs

## Features

- Automated trading based on predefined conditions. 
- Execute trades across multiple accounts.
- Historical and live data analysis for decision making.
- Supports multiple instruments including futures and options.
- Deploy complex strategies with a trailing stop loss, detect candlestick patterns like hammer and shooting star, place GTT (good till triggered) orders

## Requirements

To run the trading strategy, you need to do the following:

- Get Zerodha Kite Connect API credentials from https://kite.trade/
- Enable TOTP verification in your kite account
- Install the dependencies as shown below

## Installation

1. Make an environment:

    ```bash
    conda create --name algo_trading python=3.11.7
    ```
    
    ```bash
    conda activate algo_trading
    ```
    
2. Clone the repository and install dependencies:
   
    ```bash
    cd algorithmic-trading-strategy
    ```
    
    ```bash
    git clone https://github.com/yourusername/Algo_trading_bot.git
    ```

    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. Run `bash env.sh` to set environment variables
2. Run `setup.py` (do this just once)
3. Every day before the market starts, run `access_tokens.py` and `premarket.py` 
4. Run `strategy.py` to deploy the strategy
5. Run `streamlit run app.py` to monitor your trades


## Guide

`utils.py`: 

This contains helper functions to:
- Place and modify normal orders, stop loss orders or gtt orders
- Calculate technical indicators such as bollinger bands and Volume Weighted Average Price
- Fetch historical data and perform error handling

While the helper functions are using the Kite Connect's python client, the main strategy code has been written in a way that one can switch to another platform's API with minimal changes.

`setup.py`:

This script initializes the data structures and files needed to store trade details and trading parameters relevant to the strategy. 

`access_tokens.py`:

This script uses Selenium to automate the process of logging into the account of kite and fetching the access_tokens for multiple accounts.

`premarket.py`:

This script fetches daily instrument data and initializes files to store trade details and strategy paramters for a single trading session

`strategy.py`:

This script contains the main strategy loop that checks conditions, executes trades and updates the trailing stop loss. The script stops running when either the max no. of cycles is reached or when the trading session concludes. 

`app.py`: 

This contains a simple streamlit dashboard that displays the open positions, completed orders, failer orders and runtime errors.

