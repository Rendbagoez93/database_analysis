import pandas as pd

# This is a script for finding anomaly from bank accounts vs bank transactions vs bank transfers
# --- Load datasets ---
accounts_df = pd.read_csv("data/db_bank_accounts.csv")
transactions_df = pd.read_csv("data/db_bank_transactions.csv")
transfers_df = pd.read_csv("data/db_bank_transfers.csv")

# --- STEP 1: Calculate ending balance from transactions ---
# Filter only COMPLETED transactions
completed_txn = transactions_df[transactions_df["status"] == "COMPLETED"].copy()

# Sort to get latest balance per account
completed_txn.sort_values(by=["account_id", "id"], inplace=True)

# Get the last balance_after per account
txn_balance_df = completed_txn.groupby("account_id")["balance_after"].last().reset_index()
txn_balance_df.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# --- STEP 2: Calculate net transfer impact ---
# Only COMPLETED transfers affect balances
completed_transfers = transfers_df[transfers_df["status"] == "COMPLETED"].copy()

# Debit: outgoing transfer per account
debits = completed_transfers.groupby("from_account_id")["amount"].sum().reset_index()
debits.rename(columns={"from_account_id": "account_id", "amount": "total_debits"}, inplace=True)

# Credit: incoming transfer per account
credits = completed_transfers.groupby("to_account_id")["amount"].sum().reset_index()
credits.rename(columns={"to_account_id": "account_id", "amount": "total_credits"}, inplace=True)

# Merge and calculate net transfer
transfer_impact_df = pd.merge(credits, debits, on="account_id", how="outer").fillna(0)
transfer_impact_df["net_transfer"] = transfer_impact_df["total_credits"] - transfer_impact_df["total_debits"]

# --- STEP 3: Merge everything together ---
# Merge accounts with transaction balances
comparison_df = accounts_df.merge(txn_balance_df, left_on="id", right_on="account_id", how="left")

# Add transfer impact
comparison_df = comparison_df.merge(transfer_impact_df[["account_id", "net_transfer"]],
                                    left_on="id", right_on="account_id", how="left")
comparison_df["net_transfer"] = comparison_df["net_transfer"].fillna(0)

# --- STEP 4: Calculate expected balance and discrepancy ---
comparison_df["adjusted_ending_balance"] = comparison_df["ending_balance"] + comparison_df["net_transfer"]
comparison_df["adjusted_difference"] = comparison_df["balance"] - comparison_df["adjusted_ending_balance"]

# --- STEP 5: Show mismatched accounts ---
mismatches = comparison_df[comparison_df["adjusted_difference"].abs() > 0.01]  # Tolerance for rounding
print("Mismatched account balances:\n")
print(mismatches[["id", "balance", "adjusted_ending_balance", "adjusted_difference"]])
print("=" * 50)

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
print("=" * 50)

# --- Transaction Balance ---
completed_txn = transactions_df[transactions_df["status"] == "COMPLETED"].copy()
completed_txn.sort_values(by=["account_id", "id"], inplace=True)
txn_balances = completed_txn.groupby("account_id")["balance_after"].last().reset_index()
txn_balances.rename(columns={"balance_after": "ending_balance"}, inplace=True)

# --- Transfer Net Impact ---
completed_transfers = transfers_df[transfers_df["status"] == "COMPLETED"].copy()

debits = completed_transfers.groupby("from_account_id")["amount"].sum().reset_index()
debits.rename(columns={"from_account_id": "account_id", "amount": "debit_total"}, inplace=True)

credits = completed_transfers.groupby("to_account_id")["amount"].sum().reset_index()
credits.rename(columns={"to_account_id": "account_id", "amount": "credit_total"}, inplace=True)

transfer_net = pd.merge(credits, debits, on="account_id", how="outer").fillna(0)
transfer_net["net_transfer"] = transfer_net["credit_total"] - transfer_net["debit_total"]

# --- Merge All Together ---
merged = accounts_df.merge(txn_balances, left_on="id", right_on="account_id", how="left")
merged = merged.merge(transfer_net[["account_id", "net_transfer"]], left_on="id", right_on="account_id", how="left")
merged["net_transfer"] = merged["net_transfer"].fillna(0)

# --- Comparison Logic ---
merged["transaction_diff"] = merged["balance"] - merged["ending_balance"]
merged["transfer_adjusted_balance"] = merged["ending_balance"] + merged["net_transfer"]
merged["transfer_diff"] = merged["balance"] - merged["transfer_adjusted_balance"]

# --- Diagnostic Result ---
txn_mismatch_ids = merged[merged["transaction_diff"].abs() > 0.01]["id"].tolist()
transfer_mismatch_ids = merged[merged["transfer_diff"].abs() > 0.01]["id"].tolist()

print("Mismatch due to TRANSACTIONS:", txn_mismatch_ids)
print("Mismatch after including TRANSFERS:", transfer_mismatch_ids)
print("=" * 50)

# Find accounts where transaction mismatch exists
txn_mismatched = merged[merged["transaction_diff"].abs() > 0.01]["id"].tolist()

# Pull last completed transaction per mismatched account
last_txns = completed_txn[completed_txn["account_id"].isin(txn_mismatched)] \
    .sort_values(by=["account_id", "id"]) \
    .groupby("account_id").tail(1)

print("Last completed transactions causing mismatch:")
print(last_txns[["account_id", "id", "balance_after", "status"]])

# Accounts where transfer adjustment still doesn't fix mismatch
transfer_mismatched = merged[merged["transfer_diff"].abs() > 0.01]["id"].tolist()

# Show related completed transfers for these accounts
related_transfers = completed_transfers[
    completed_transfers["from_account_id"].isin(transfer_mismatched) |
    completed_transfers["to_account_id"].isin(transfer_mismatched)
]

print("Completed transfers potentially impacting mismatched balances:")
print(related_transfers[["id", "from_account_id", "to_account_id", "amount", "status"]])
