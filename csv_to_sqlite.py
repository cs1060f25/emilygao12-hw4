# Code written in conjunction with GenAI (ChatGPT)

#!/usr/bin/env python3
import sys
import sqlite3
import csv
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database_name.db> <csv_file>")
        sys.exit(1)

    db_name = sys.argv[1]
    csv_file = sys.argv[2]

    # derive table name from CSV file name
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    # read csv header + rows
    with open(csv_file, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # assumes header exists

        # prepare schema (all TEXT)
        columns = ", ".join([f"{col} TEXT" for col in header])
        placeholders = ", ".join(["?" for _ in header])

        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        # create table (drop if exists to overwrite)
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        cur.execute(f"CREATE TABLE {table_name} ({columns})")

        # insert rows
        cur.executemany(
            f"INSERT INTO {table_name} VALUES ({placeholders})",
            reader
        )

        conn.commit()
        conn.close()

if __name__ == "__main__":
    main()
