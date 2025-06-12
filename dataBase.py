import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from datetime import datetime
seaSalt = "D3crypt_M3_53np411_UwU"


def createDataBase(dbFileName):  # db creation
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS USER(
            userName TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            fullName TEXT NOT NULL,
            email TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight FLOAT NOT NULL,
            height FLOAT NOT NULL,
            salt BLOB NOT NULL)
            """)

    c.execute("""CREATE TABLE IF NOT EXISTS STATS(
            username TEXT NOT NULL,
            score Float NOT NULL,
            exerciseDate DATETIME NOT NULL,
            FOREIGN KEY (userName) REFERENCES USER(userName),
            PRIMARY KEY (username, exerciseDate)
            )""")

    conn.commit()
    conn.close()

def createExerciseTable(dbFileName):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS EXERCISE(
                    name TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    textName TEXT NOT NULL
                    )
                    """)
    conn.commit()
    conn.close()


# inserting into database
def insertUser(dbFileName, values):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    try:
        # Checking if the user exists
        c.execute("SELECT * FROM USER WHERE userName = ?", (values[0],))
        if c.fetchone() is not None:
            return "user already exists"

        # Encrypted password
        encrypted_data, salt = encrypt(values[1], seaSalt)


        values[1] = encrypted_data  # Storing the encrypted password
        values.append(salt)  # Adding salt to the end

        # Inserting all sql fields
        c.execute("""
                INSERT INTO USER 
                (userName, password, fullName, email, age, gender, weight, height, salt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

        conn.commit()
        return "user registered successfully"

    except sqlite3.Error as e:
        return f"database error: {str(e)}"
    finally:
        conn.close()


def insertExercise(dbFileName, values):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO EXERCISE VALUES(?,?,?)", values)
        conn.commit()
    finally:    
        conn.close()


def insertStats(dbFileName, values):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO STATS VALUES(?,?,?)", values)
        conn.commit()
    finally:
        conn.close()


# reading from database
def readUser(dbFileName, username):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()

    c.execute("SELECT userName, fullName, email, gender, age, weight, height FROM USER WHERE userName = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row if row else None


def validateUser(dbFileName, username, password):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()

    c.execute("SELECT salt FROM USER WHERE userName = ?", (username,))
    row = c.fetchone()
    if (row == None):
        return False

    c.execute("SELECT userName, password, salt FROM USER WHERE userName = ?", (username,))
    row = c.fetchone()
    conn.close()
    pword = decrypt_data(row[1],seaSalt, row[2])
    if(pword == password):# username password match
        return True
    else:
        return False


def updateUserWeight(dbFileName, username, weight):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    c.execute("UPDATE user SET weight = ? WHERE username = ?",(weight, username,))
    conn.commit()
    conn.close()

def updateUserHeight(dbFileName, username, height):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    c.execute("UPDATE user SET Height = ? WHERE username = ?",(height, username,))
    conn.commit()
    conn.close()

def updateUserAge(dbFileName, username, age):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()
    c.execute("UPDATE user SET age = ? WHERE username = ?",(age, username,))
    conn.commit()
    conn.close()
def getExercisesByType(dbFileName, type):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()

    c.execute("SELECT name FROM EXERCISE WHERE type = ?", (type,))

    exercises = []
    for row in c.fetchall():
        exercises.append(row)
    conn.close()
    return exercises


def getSpecificExerciseText(dbFileName, name):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()

    c.execute("SELECT text FROM EXERCISE WHERE name = ?", (name,))

    row = c.fetchone()
    conn.close()

    return row if row else None

def getUserStats(dbFileName, username, dateUntil = datetime(2024,10,1).strftime('%Y-%m-%d %H:%M:%S'), dateFrom = datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
    conn = sqlite3.connect(dbFileName)
    c = conn.cursor()

    # Converting string to datetime format
    dateFrom_dt = datetime.strptime(dateFrom, '%Y-%m-%d %H:%M:%S')
    dateFromStr = dateFrom_dt.strftime('%Y-%m-%d %H:%M:%S')

    dateUntil_dt = datetime.strptime(dateUntil, '%Y-%m-%d %H:%M:%S')
    dateUntilStr = dateUntil_dt.strftime('%Y-%m-%d %H:%M:%S')

    c.execute(f"""
           SELECT score, exerciseDate
           FROM STATS 
           WHERE userName = '{username}' 
           AND exerciseDate BETWEEN '{dateFromStr}' AND '{dateUntilStr}'
           ORDER BY exerciseDate DESC
           """)

    rows = c.fetchall()
    conn.close()


    return rows if rows else []
def decrypt_data(encrypted_data: bytes, secret_key: str, salt: bytes = None) -> str:
    if (salt == None):
        # Generate a random salt (16 bytes recommended for PBKDF2)
        return "Please enter salt"
    # Prepare the key derivation
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    # Derive key from the secret
    derived_key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))

    # Decrypt the data
    try:
        cipher_suite = Fernet(derived_key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def encrypt(plaintext: str, secret_key: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if (salt == None):
        # Generate a random salt (16 bytes recommended for PBKDF2)
        salt = os.urandom(16)

    # Derive a secure key from the secret_key + salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,  # Slows down brute-force attacks
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))

    # Encrypt the data
    cipher = Fernet(derived_key)
    encrypted_data = cipher.encrypt(plaintext.encode())

    return encrypted_data, salt  # Return both for storage
