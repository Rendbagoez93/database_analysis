# Database Analysis Project

This project provides tools and scripts for analyzing banking data, including accounts, transactions, and transfers. The data is sourced from CSV files and can be processed, combined, and analyzed using the provided Python scripts.

## Folder Structure

```
.
├── complete_main.py
├── main_transaction.py
├── main_transfers--.py
├── main4.py
├── main5.py
├── postgres.session.sql
├── pyproject.toml
├── README.md
├── uv.lock
└── data/
    ├── bank_accounts.csv
    ├── bank_transactions.csv
    ├── bank_transfers.csv
    ├── combined_bank_data.csv
    ├── db_bank_accounts.csv
    ├── db_bank_transactions.csv
    ├── db_bank_transfers.csv
    └── modified_bank_accounts.csv
```

## Data Files
- **bank_accounts.csv**: Raw bank account data.
- **bank_transactions.csv**: Raw transaction data.
- **bank_transfers.csv**: Raw transfer data.
- **combined_bank_data.csv**: Merged data from accounts, transactions, and transfers.
- **db_bank_accounts.csv**, **db_bank_transactions.csv**, **db_bank_transfers.csv**: Database-ready versions of the raw data.
- **modified_bank_accounts.csv**: Modified account data for analysis.

## Python Scripts
- **complete_main.py**: Main script for running the complete analysis workflow.
- **main_transaction.py**: Handles transaction-specific analysis.
- **main_transfers--.py**: Handles transfer-specific analysis.
- **main4.py**, **main5.py**: Additional scripts for extended analysis or experimentation.

## SQL
- **postgres.session.sql**: SQL session file for PostgreSQL database setup or queries.

## Setup
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   or if using Poetry:
   ```sh
   poetry install
   ```
3. Place your data files in the `data/` directory.

## Usage
Run the main analysis script:
```sh
python complete_main.py
```
Or run individual scripts as needed:
```sh
python main_transaction.py
python main_transfers--.py
```

## License
This project is licensed under the MIT License.

## Author
Rendbagoez93
