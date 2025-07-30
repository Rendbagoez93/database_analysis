import pandas as pd

# This is a script for finding anomaly and point out which is the anomaly from bank accounts vs bank transactions
# --- Load datasets ---
accounts_df = pd.read_csv("data/db_bank_accounts.csv")             # Contains recorded balances
transactions_df = pd.read_csv("data/db_bank_transactions.csv")     # Contains transaction history

# --- Step 1: Filter completed transactions ---
completed_txn = transactions_df[transactions_df["status"] == "COMPLETED"].copy()

# --- Step 2: Sort to get latest transaction per account ---
completed_txn.sort_values(by=["account_id", "id"], inplace=True)

# --- Step 3: Get ending balance per account from transactions ---
completed_txn.sort_values(by=["account_id", "id"], inplace=True)

# --- Step 3: Get ending balance per account from transactions ---
txn_balances = completed_txn.groupby("account_id")["balance_after"].last().reset_index()
txn_balances.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# --- Step 4: Merge with bank account balances ---
comparison_df = accounts_df.merge(txn_balances, left_on="id", right_on="account_id", how="left")

# --- Step 5: Calculate discrepancy ---
comparison_df["balance_difference"] = comparison_df["balance"] - comparison_df["ending_balance"]

# --- Step 6: Show mismatched accounts ---
mismatches = comparison_df[comparison_df["balance_difference"].abs() > 0.01]  # Tolerance for float rounding
print("Accounts with mismatched balances:")
print(mismatches[["id", "balance", "ending_balance", "balance_difference"]])
print("=" * 50)

# Filter only COMPLETED transactions
completed_txn = transactions_df[transactions_df["status"] == "COMPLETED"].copy()

# Sort to get latest transaction per account
completed_txn.sort_values(by=["account_id", "id"], inplace=True)

# Get ending balance per account
txn_balances = completed_txn.groupby("account_id")["balance_after"].last().reset_index()
txn_balances.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# Merge with account balances
comparison_df = accounts_df.merge(txn_balances, left_on="id", right_on="account_id", how="left")
comparison_df["balance_difference"] = comparison_df["balance"] - comparison_df["ending_balance"]

# Identify mismatched accounts
mismatched_ids = comparison_df[comparison_df["balance_difference"].abs() > 0.01]["id"].tolist()

# Trace last completed transaction for each mismatched account
last_txns = completed_txn[completed_txn["account_id"].isin(mismatched_ids)] \
    .sort_values(by=["account_id", "id"]) \
    .groupby("account_id").tail(1)

# Display key transaction details
print("Last completed transactions causing mismatch:")
print(last_txns[["account_id", "id", "balance_after", "status"]])
