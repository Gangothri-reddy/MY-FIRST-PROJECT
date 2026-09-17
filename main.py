from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_tables, get_connection

app = FastAPI(title="Hotel Management System")

create_tables()


# =========================================================
# PYDANTIC MODELS
# =========================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class Customer(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    email: str
    address: str


class Room(BaseModel):
    room_number: str
    room_type: str
    price_per_night: float
    room_status: str


class Booking(BaseModel):
    customer_id: int
    room_id: int
    check_in_date: str
    check_out_date: str
    number_of_guests: int
    booking_status: str


class Payment(BaseModel):
    booking_id: int
    customer_id: int
    amount: float
    payment_method: str
    payment_date: str
    payment_status: str


class Service(BaseModel):
    service_name: str
    price: float
    description: str
    service_status: str


class BookingService(BaseModel):
    booking_id: int
    service_id: int
    quantity: int = 1


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "Hotel Management System API is running"
    }


# =========================================================
# LOGIN
# =========================================================
@app.post("/register")
def register(data: LoginRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE username = ?",
        (data.username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (data.username, data.password)
    )

    conn.commit()

    user_id = cursor.lastrowid

    conn.close()

    return {
        "message": "Registration successful",
        "user_id": user_id,
        "username": data.username
    }

@app.post("/login")
def login(data: LoginRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, username
        FROM users
        WHERE username = ? AND password = ?
        """,
        (data.username, data.password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        return {
            "message": "Login successful",
            "user_id": user[0],
            "username": user[1]
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"
    )


# =========================================================
# CUSTOMER CRUD
# =========================================================

@app.post("/customers")
def add_customer(customer: Customer):

    if customer.age <= 0:
        raise HTTPException(
            status_code=400,
            detail="Age must be greater than 0"
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO customers
        (name, age, gender, phone, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            customer.name,
            customer.age,
            customer.gender,
            customer.phone,
            customer.email,
            customer.address
        )
    )

    conn.commit()

    customer_id = cursor.lastrowid

    conn.close()

    return {
        "message": "Customer added successfully",
        "customer_id": customer_id
    }


@app.get("/customers")
def get_customers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()

    conn.close()

    return customers


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: Customer):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE customers
        SET name = ?, age = ?, gender = ?, phone = ?, email = ?, address = ?
        WHERE customer_id = ?
        """,
        (
            customer.name,
            customer.age,
            customer.gender,
            customer.phone,
            customer.email,
            customer.address,
            customer.customer_id if hasattr(customer, "customer_id") else customer_id
        )
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Customer updated successfully"
    }


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM customers WHERE customer_id = ?",
        (customer_id,)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Customer deleted successfully"
    }


# =========================================================
# ROOM CRUD
# =========================================================

@app.post("/rooms")
def add_room(room: Room):

    if room.price_per_night <= 0:
        raise HTTPException(
            status_code=400,
            detail="Room price must be greater than 0"
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO rooms
            (room_number, room_type, price_per_night, room_status)
            VALUES (?, ?, ?, ?)
            """,
            (
                room.room_number,
                room.room_type,
                room.price_per_night,
                room.room_status
            )
        )

        conn.commit()

        room_id = cursor.lastrowid

        return {
            "message": "Room added successfully",
            "room_id": room_id
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Room number already exists"
        )

    finally:
        conn.close()


@app.get("/rooms")
def get_rooms():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms")

    rooms = cursor.fetchall()

    conn.close()

    return rooms


@app.put("/rooms/{room_id}")
def update_room(room_id: int, room: Room):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE rooms
        SET room_number = ?,
            room_type = ?,
            price_per_night = ?,
            room_status = ?
        WHERE room_id = ?
        """,
        (
            room.room_number,
            room.room_type,
            room.price_per_night,
            room.room_status,
            room_id
        )
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Room updated successfully"
    }


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM rooms WHERE room_id = ?",
        (room_id,)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Room deleted successfully"
    }


# =========================================================
# BOOKING CRUD
# =========================================================

@app.post("/bookings")
def add_booking(booking: Booking):

    if booking.number_of_guests <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of guests must be greater than 0"
        )

    conn = get_connection()
    cursor = conn.cursor()

    # Check customer
    cursor.execute(
        "SELECT customer_id FROM customers WHERE customer_id = ?",
        (booking.customer_id,)
    )

    customer = cursor.fetchone()

    if not customer:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Check room
    cursor.execute(
        """
        SELECT room_id, room_status
        FROM rooms
        WHERE room_id = ?
        """,
        (booking.room_id,)
    )

    room = cursor.fetchone()

    if not room:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    if room[1] != "Available":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Room is not available"
        )

    # Insert booking
    cursor.execute(
        """
        INSERT INTO bookings
        (
            customer_id,
            room_id,
            check_in_date,
            check_out_date,
            number_of_guests,
            booking_status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            booking.customer_id,
            booking.room_id,
            booking.check_in_date,
            booking.check_out_date,
            booking.number_of_guests,
            booking.booking_status
        )
    )

    booking_id = cursor.lastrowid

    # Change room status
    cursor.execute(
        """
        UPDATE rooms
        SET room_status = 'Occupied'
        WHERE room_id = ?
        """,
        (booking.room_id,)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Booking added successfully",
        "booking_id": booking_id
    }


@app.get("/bookings")
def get_bookings():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            b.booking_id,
            c.name AS customer_name,
            r.room_number,
            r.room_type,
            b.check_in_date,
            b.check_out_date,
            b.number_of_guests,
            b.booking_status
        FROM bookings b
        JOIN customers c
            ON b.customer_id = c.customer_id
        JOIN rooms r
            ON b.room_id = r.room_id
        """
    )

    bookings = cursor.fetchall()

    conn.close()

    return bookings


@app.put("/bookings/{booking_id}")
def update_booking(booking_id: int, booking: Booking):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bookings
        SET customer_id = ?,
            room_id = ?,
            check_in_date = ?,
            check_out_date = ?,
            number_of_guests = ?,
            booking_status = ?
        WHERE booking_id = ?
        """,
        (
            booking.customer_id,
            booking.room_id,
            booking.check_in_date,
            booking.check_out_date,
            booking.number_of_guests,
            booking.booking_status,
            booking_id
        )
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Booking updated successfully"
    }


@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT room_id FROM bookings WHERE booking_id = ?",
        (booking_id,)
    )

    booking = cursor.fetchone()

    if not booking:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    cursor.execute(
        "DELETE FROM bookings WHERE booking_id = ?",
        (booking_id,)
    )

    cursor.execute(
        """
        UPDATE rooms
        SET room_status = 'Available'
        WHERE room_id = ?
        """,
        (booking[0],)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Booking deleted successfully"
    }


# =========================================================
# PAYMENT CRUD
# =========================================================

@app.post("/payments")
def add_payment(payment: Payment):

    if payment.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than 0"
        )

    conn = get_connection()
    cursor = conn.cursor()

    # Check booking
    cursor.execute(
        "SELECT booking_id FROM bookings WHERE booking_id = ?",
        (payment.booking_id,)
    )

    booking = cursor.fetchone()

    if not booking:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Check customer
    cursor.execute(
        "SELECT customer_id FROM customers WHERE customer_id = ?",
        (payment.customer_id,)
    )

    customer = cursor.fetchone()

    if not customer:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    cursor.execute(
        """
        INSERT INTO payments
        (
            booking_id,
            customer_id,
            amount,
            payment_method,
            payment_date,
            payment_status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            payment.booking_id,
            payment.customer_id,
            payment.amount,
            payment.payment_method,
            payment.payment_date,
            payment.payment_status
        )
    )

    payment_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "message": "Payment added successfully",
        "payment_id": payment_id
    }


@app.get("/payments")
def get_payments():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.payment_id,
            p.booking_id,
            c.name AS customer_name,
            p.amount,
            p.payment_method,
            p.payment_date,
            p.payment_status
        FROM payments p
        JOIN customers c
            ON p.customer_id = c.customer_id
        """
    )

    payments = cursor.fetchall()

    conn.close()

    return payments


@app.put("/payments/{payment_id}")
def update_payment(payment_id: int, payment: Payment):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE payments
        SET booking_id = ?,
            customer_id = ?,
            amount = ?,
            payment_method = ?,
            payment_date = ?,
            payment_status = ?
        WHERE payment_id = ?
        """,
        (
            payment.booking_id,
            payment.customer_id,
            payment.amount,
            payment.payment_method,
            payment.payment_date,
            payment.payment_status,
            payment_id
        )
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Payment updated successfully"
    }


@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM payments WHERE payment_id = ?",
        (payment_id,)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Payment deleted successfully"
    }


# =========================================================
# SERVICES CRUD
# =========================================================

@app.post("/services")
def add_service(service: Service):

    if service.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Service price must be greater than 0"
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO services
        (
            service_name,
            price,
            description,
            service_status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            service.service_name,
            service.price,
            service.description,
            service.service_status
        )
    )

    service_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "message": "Service added successfully",
        "service_id": service_id
    }


@app.get("/services")
def get_services():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM services")

    services = cursor.fetchall()

    conn.close()

    return services


@app.put("/services/{service_id}")
def update_service(service_id: int, service: Service):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE services
        SET service_name = ?,
            price = ?,
            description = ?,
            service_status = ?
        WHERE service_id = ?
        """,
        (
            service.service_name,
            service.price,
            service.description,
            service.service_status,
            service_id
        )
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Service updated successfully"
    }


@app.delete("/services/{service_id}")
def delete_service(service_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM services WHERE service_id = ?",
        (service_id,)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Service deleted successfully"
    }


# =========================================================
# BOOKING SERVICES
# =========================================================

@app.post("/booking-services")
def add_booking_service(data: BookingService):

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT booking_id FROM bookings WHERE booking_id = ?",
        (data.booking_id,)
    )

    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    cursor.execute(
        "SELECT service_id FROM services WHERE service_id = ?",
        (data.service_id,)
    )

    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    try:
        cursor.execute(
            """
            INSERT INTO booking_services
            (booking_id, service_id, quantity)
            VALUES (?, ?, ?)
            """,
            (
                data.booking_id,
                data.service_id,
                data.quantity
            )
        )

        conn.commit()

    except Exception:
        conn.rollback()
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Service already added to this booking"
        )

    conn.close()

    return {
        "message": "Service added to booking successfully"
    }


@app.get("/booking-services")
def get_booking_services():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            bs.booking_id,
            c.name AS customer_name,
            s.service_name,
            s.price,
            bs.quantity,
            (s.price * bs.quantity) AS total
        FROM booking_services bs
        JOIN bookings b
            ON bs.booking_id = b.booking_id
        JOIN customers c
            ON b.customer_id = c.customer_id
        JOIN services s
            ON bs.service_id = s.service_id
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


@app.delete("/booking-services/{booking_id}/{service_id}")
def delete_booking_service(booking_id: int, service_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM booking_services
        WHERE booking_id = ? AND service_id = ?
        """,
        (booking_id, service_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Booking service not found"
        )

    conn.commit()
    conn.close()

    return {
        "message": "Booking service deleted successfully"
    }


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/dashboard")
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE payment_status = 'Paid'
        """
    )

    total_revenue = cursor.fetchone()[0]

    conn.close()

    return {
        "total_customers": total_customers,
        "total_rooms": total_rooms,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue
    }


# =========================================================
# ROOM AVAILABILITY
# =========================================================

@app.get("/rooms/available")
def available_rooms():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM rooms
        WHERE room_status = 'Available'
        """
    )

    rooms = cursor.fetchall()

    conn.close()

    return rooms


# =========================================================
# CUSTOMER SEARCH
# =========================================================

@app.get("/customers/search/{name}")
def search_customer(name: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE name LIKE ?
        """,
        ("%" + name + "%",)
    )

    customers = cursor.fetchall()

    conn.close()

    return customers


# =========================================================
# CUSTOMER BOOKING HISTORY
# =========================================================

@app.get("/customers/{customer_id}/history")
def customer_history(customer_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.name,
            r.room_number,
            b.check_in_date,
            b.check_out_date,
            b.booking_status,
            COALESCE(p.amount, 0) AS payment_amount,
            COALESCE(p.payment_status, 'No Payment') AS payment_status
        FROM customers c
        JOIN bookings b
            ON c.customer_id = b.customer_id
        JOIN rooms r
            ON b.room_id = r.room_id
        LEFT JOIN payments p
            ON b.booking_id = p.booking_id
        WHERE c.customer_id = ?
        """,
        (customer_id,)
    )

    history = cursor.fetchall()

    conn.close()

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Customer history not found"
        )

    return history


# =========================================================
# REPORT - MONTHLY REVENUE
# =========================================================

@app.get("/reports/monthly-revenue")
def monthly_revenue():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            substr(payment_date, 1, 7) AS month,
            SUM(amount) AS revenue
        FROM payments
        WHERE payment_status = 'Paid'
        GROUP BY substr(payment_date, 1, 7)
        ORDER BY month
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


# =========================================================
# REPORT - MOST BOOKED ROOMS
# =========================================================

@app.get("/reports/most-booked-room")
def most_booked_room():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            r.room_number,
            r.room_type,
            COUNT(b.booking_id) AS booking_count
        FROM rooms r
        JOIN bookings b
            ON r.room_id = b.room_id
        GROUP BY r.room_id
        ORDER BY booking_count DESC
        LIMIT 1
        """
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No booking data available"
        )

    return {
        "room_number": result[0],
        "room_type": result[1],
        "booking_count": result[2]
    }


# =========================================================
# PAYMENT STATUS FILTER
# =========================================================

@app.get("/payments/status/{status}")
def payment_status(status: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM payments
        WHERE payment_status = ?
        """,
        (status,)
    )

    payments = cursor.fetchall()

    conn.close()

    return payments