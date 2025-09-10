import pandas as pd

# This is a script for finding anomaly from bank accounts vs bank transactions
# --- Load datasets ---
accounts_df = pd.read_csv("data/db_bank_accounts.csv")
transactions_df = pd.read_csv("data/db_bank_transactions.csv")
transfers_df = pd.read_csv("data/db_bank_transfers.csv")

# Filter only completed transactions
completed = transactions_df[transactions_df["status"] == "COMPLETED"].copy()

# Sort to ensure we get the latest transaction per account
completed.sort_values(by=["account_id", "id"], inplace=True)

# Get final balance per account from transaction history
final_balances = completed.groupby("account_id")["balance_after"].last().reset_index()
final_balances.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# Merge with account info
comparison = accounts_df.merge(final_balances, left_on="id", right_on="account_id", how="left")

# Calculate the difference
comparison["balance_difference"] = comparison["balance"] - comparison["ending_balance"]

# Display accounts with mismatches
mismatches = comparison[comparison["balance_difference"].abs() > 0.01]

print(mismatches)
print ("=" * 50)

# This Script is to identify accounts where the balance in the accounts table does not match the latest transaction balance.
# Filter for COMPLETED transactions only
completed = transactions_df[transactions_df["status"] == "COMPLETED"].copy()
# Sort to ensure latest transactions are used
completed.sort_values(by=["account_id", "id"], inplace=True)

# Get latest 'balance_after' per account
txn_balances = completed.groupby("account_id")["balance_after"].last().reset_index()
txn_balances.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# Merge with accounts
merged = accounts_df.merge(txn_balances, left_on="id", right_on="account_id", how="left")

# Calculate balance difference
merged["balance_difference"] = merged["balance"] - merged["ending_balance"]

# Filter mismatches with tolerance for float rounding
mismatched_ids = merged[merged["balance_difference"].abs() > 0.01]["id"].tolist()

print("Accounts with mismatched balances:", mismatched_ids)