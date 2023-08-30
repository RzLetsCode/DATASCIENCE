import psycopg2


# ---- Enter your password or change the required parameters based on your connection
def establish_connection():
    return psycopg2.connect(
        dbname="Bitcoin",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )
