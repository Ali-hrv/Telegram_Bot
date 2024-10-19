import mysql.connector

def create_database():
    conn = mysql.connector.connect(user='root', password='password', host='localhost')
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS register")
    cursor.execute("CREATE DATABASE register")
    conn.commit()
    cursor.close()
    conn.close()
    print("Database created successfully")

def create_user_table():
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='register')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id                  INT AUTO_INCREMENT PRIMARY KEY,
        telegram_id         BIGINT NOT NULL UNIQUE,
        usd_balance         DECIMAL(10, 2) DEFAULT 0.00,
        btc_balance         DECIMAL(20, 8) DEFAULT 0.00,
        eth_balance         DECIMAL(20, 8) DEFAULT 0.00,
        usdt_balance        DECIMAL(20, 8) DEFAULT 0.00,
        registration_date   DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("User table created or updated successfully")

def create_wallet_table():
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='register')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet (
        id              INT AUTO_INCREMENT PRIMARY KEY,
        telegram_id     BIGINT NOT NULL,
        wallet_address  VARCHAR(255) NOT NULL,
        FOREIGN KEY (telegram_id) REFERENCES user(telegram_id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Wallet table created or updated successfully")

def create_transactions_table():
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='register')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        telegram_id BIGINT NOT NULL,  
        currency VARCHAR(10),
        amount DECIMAL(20,8),
        transaction_type ENUM('buy', 'sell', 'transfer'),  
        new_balance DECIMAL(20, 8),  
        to_wallet_address VARCHAR(255),
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (telegram_id) REFERENCES user(telegram_id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Transactions table created or updated successfully")

if __name__ == "__main__":
    create_database()
    create_user_table()
    create_wallet_table()
    create_transactions_table()
