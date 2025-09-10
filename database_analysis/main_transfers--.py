import pandas as pd

# This is a script for finding anomaly from bank accounts vs bank transfers
# --- Load datasets ---
accounts_df = pd.read_csv("data/db_bank_accounts.csv")
transactions_df = pd.read_csv("data/bank_transactions.csv")
transfers_df = pd.read_csv("data/db_bank_transfers.csv")

# --- Step 1: Transaction ending balances ---
completed_txn = transactions_df[transactions_df["status"] == "COMPLETED"].copy()
completed_txn.sort_values(by=["account_id", "id"], inplace=True)
txn_balances = completed_txn.groupby("account_id")["balance_after"].last().reset_index()
txn_balances.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# --- Step 2: Net internal transfer impact ---
completed_transfers = transfers_df[transfers_df["status"] == "COMPLETED"].copy()
debits = completed_transfers.groupby("from_account_id")["amount"].sum().reset_index()
debits.rename(columns={"from_account_id": "account_id", "amount": "total_debits"}, inplace=True)
credits = completed_transfers.groupby("to_account_id")["amount"].sum().reset_index()
credits.rename(columns={"to_account_id": "account_id", "amount": "total_credits"}, inplace=True)
transfer_impact = pd.merge(credits, debits, on="account_id", how="outer").fillna(0)
transfer_impact["net_transfer"] = transfer_impact["total_credits"] - transfer_impact["total_debits"]

# --- Step 3: Merge and compute adjusted balances ---
merged = accounts_df.merge(txn_balances, left_on="id", right_on="account_id", how="left")
merged = merged.merge(transfer_impact[["account_id", "net_transfer"]],
                      left_on="id", right_on="account_id", how="left")
merged["net_transfer"] = merged["net_transfer"].fillna(0)
merged["adjusted_balance"] = merged["ending_balance"] + merged["net_transfer"]
merged["adjusted_difference"] = merged["balance"] - merged["adjusted_balance"]

# --- Step 4: Find mismatched account IDs ---
mismatched_ids = merged[merged["adjusted_difference"].abs() > 0.01]["id"].tolist()
print("Accounts with mismatched balances:", mismatched_ids)