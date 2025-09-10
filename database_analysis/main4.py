import pandas as pd

# This is a script for finding anomaly and point out which is the anomaly from bank accounts vs bank transfers
# Load datasets
accounts_df = pd.read_csv("data/db_bank_accounts.csv")
transfers_df = pd.read_csv("data/db_bank_transfers.csv")

# Filter only COMPLETED transfers
completed_transfers = transfers_df[transfers_df["status"] == "COMPLETED"].copy()

# Calculate total debits (outgoing) per account
debits = completed_transfers.groupby("from_account_id")["amount"].sum().reset_index()
debits.rename(columns={"from_account_id": "account_id", "amount": "total_debits"}, inplace=True)

# Calculate total credits (incoming) per account
credits = completed_transfers.groupby("to_account_id")["amount"].sum().reset_index()
credits.rename(columns={"to_account_id": "account_id", "amount": "total_credits"}, inplace=True)

# Merge and compute net transfer impact
transfer_summary = pd.merge(credits, debits, on="account_id", how="outer").fillna(0)
transfer_summary["net_transfer_balance"] = transfer_summary["total_credits"] - transfer_summary["total_debits"]

# Merge with bank account balances
comparison = accounts_df.merge(transfer_summary, left_on="id", right_on="account_id", how="left")
comparison["net_transfer_balance"] = comparison["net_transfer_balance"].fillna(0)

# Calculate discrepancy
comparison["transfer_balance_difference"] = comparison["balance"] - comparison["net_transfer_balance"]

# Show mismatched accounts
mismatches = comparison[comparison["transfer_balance_difference"].abs() > 0.01]
print("Accounts with mismatched transfer-based balances:")
print(mismatches[["id", "balance", "net_transfer_balance", "transfer_balance_difference"]])
print ("=" * 50)

# Filter only COMPLETED transfers
completed_transfers = transfers_df[transfers_df["status"] == "COMPLETED"].copy()

# Calculate net transfer per account
debits = completed_transfers.groupby("from_account_id")["amount"].sum().reset_index()
debits.rename(columns={"from_account_id": "account_id", "amount": "total_debits"}, inplace=True)

credits = completed_transfers.groupby("to_account_id")["amount"].sum().reset_index()
credits.rename(columns={"to_account_id": "account_id", "amount": "total_credits"}, inplace=True)

transfer_summary = pd.merge(credits, debits, on="account_id", how="outer").fillna(0)
transfer_summary["net_transfer_balance"] = transfer_summary["total_credits"] - transfer_summary["total_debits"]

# Merge with account balances
comparison = accounts_df.merge(transfer_summary, left_on="id", right_on="account_id", how="left")
comparison["net_transfer_balance"] = comparison["net_transfer_balance"].fillna(0)
comparison["transfer_balance_difference"] = comparison["balance"] - comparison["net_transfer_balance"]

# Identify mismatched accounts
mismatched_ids = comparison[comparison["transfer_balance_difference"].abs() > 0.01]["id"].tolist()

# Trace transfers involving mismatched accounts
trace_transfers = completed_transfers[
    completed_transfers["from_account_id"].isin(mismatched_ids) |
    completed_transfers["to_account_id"].isin(mismatched_ids)
]

# Display relevant transfer details
print("Transfers potentially causing imbalance:")
print(trace_transfers[[
    "id", "from_account_id", "to_account_id", "amount", "status", "memo", "completed_at"
]])
print("=" * 50)