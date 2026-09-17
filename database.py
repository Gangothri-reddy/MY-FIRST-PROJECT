import sqlite3

DATABASE = "hotel.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)

    # Rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price_per_night REAL NOT NULL,
            room_status TEXT NOT NULL
        )
    """)

    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            number_of_guests INTEGER NOT NULL,
            booking_status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)

    # Payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    # Services table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            service_status TEXT NOT NULL
        )
    """)

    # Booking_Services table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_services (
            booking_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (booking_id, service_id),
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
            FOREIGN KEY (service_id) REFERENCES services(service_id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")