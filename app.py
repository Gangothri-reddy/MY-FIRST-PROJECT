import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Hotel Management System",
    page_icon="🏨",
    layout="wide"
)

# ---------------- LOGIN ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:

    st.title("🏨 Hotel Management System")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
    st.write("---")
    st.subheader("New User? Register Here")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")

    if st.button("Register"):

        response = requests.post(
            f"{API_URL}/register",
            json={
                "username": new_username,
                "password": new_password
            }
        )

        if response.status_code == 200:
            st.success("Registration successful! Now you can login.")
        else:
            st.error(response.json().get("detail", "Registration failed"))

    else:
            st.error("Invalid username or password")

    st.stop()


# ---------------- SIDEBAR ----------------

st.sidebar.title("🏨 Hotel Management")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Customers",
        "Rooms",
        "Bookings",
        "Payments",
        "Services",
        "Reports",
        "Logout"
    ]
)


# ---------------- LOGOUT ----------------

if menu == "Logout":

    st.session_state.logged_in = False
    st.rerun()


# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.title("📊 Dashboard")

    response = requests.get(f"{API_URL}/dashboard")

    if response.status_code == 200:

        data = response.json()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Customers",
            data["total_customers"]
        )

        col2.metric(
            "Total Rooms",
            data["total_rooms"]
        )

        col3.metric(
            "Total Bookings",
            data["total_bookings"]
        )

        col4.metric(
            "Total Revenue",
            f"₹ {data['total_revenue']}"
        )

    else:
        st.error("Unable to load dashboard")


# ---------------- CUSTOMERS ----------------

elif menu == "Customers":

    st.title("👤 Customers")

    tab1, tab2 = st.tabs(["Add Customer", "View Customers"])

    # ---------------- ADD CUSTOMER ----------------

    with tab1:

        name = st.text_input("Name")
        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            key="add_customer_gender"
        )

        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_area("Address")

        if st.button("Add Customer"):

            response = requests.post(
                f"{API_URL}/customers",
                json={
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "email": email,
                    "address": address
                }
            )

            if response.status_code == 200:
                st.success("Customer added successfully!")
            else:
                st.error(response.text)

    # ---------------- VIEW / UPDATE / DELETE ----------------

    with tab2:

        response = requests.get(
            f"{API_URL}/customers"
        )

        if response.status_code == 200:

            customers = response.json()

            if customers:

                st.dataframe(
                    customers,
                    use_container_width=True
                )

                # -------- UPDATE CUSTOMER --------

                st.subheader("Update Customer")

                customer_options = {
                    f"{c[1]} (ID: {c[0]})": c
                    for c in customers
                }

                selected_customer = st.selectbox(
                    "Select Customer",
                    list(customer_options.keys()),
                    key="update_customer_select"
                )

                customer = customer_options[selected_customer]

                new_name = st.text_input(
                    "Name",
                    value=customer[1],
                    key="update_name"
                )

                new_age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=120,
                    value=customer[2],
                    key="update_age"
                )

                gender_list = ["Male", "Female", "Other"]

                new_gender = st.selectbox(
                    "Gender",
                    gender_list,
                    index=gender_list.index(customer[3]),
                    key="update_customer_gender"
                )

                new_phone = st.text_input(
                    "Phone",
                    value=customer[4],
                    key="update_phone"
                )

                new_email = st.text_input(
                    "Email",
                    value=customer[5],
                    key="update_email"
                )

                new_address = st.text_area(
                    "Address",
                    value=customer[6],
                    key="update_address"
                )

                if st.button("Update Customer"):

                    update_response = requests.put(
                        f"{API_URL}/customers/{customer[0]}",
                        json={
                            "name": new_name,
                            "age": new_age,
                            "gender": new_gender,
                            "phone": new_phone,
                            "email": new_email,
                            "address": new_address
                        }
                    )

                    if update_response.status_code == 200:
                        st.success(
                            "Customer updated successfully!"
                        )
                    else:
                        st.error(update_response.text)

                # -------- DELETE CUSTOMER --------

                st.subheader("Delete Customer")

                delete_customer_options = {
                    f"{c[1]} (ID: {c[0]})": c[0]
                    for c in customers
                }

                selected_delete_customer = st.selectbox(
                    "Select Customer to Delete",
                    list(delete_customer_options.keys()),
                    key="delete_customer_select"
                )

                delete_customer_id = delete_customer_options[
                    selected_delete_customer
                ]

                if st.button("Delete Customer"):

                    delete_response = requests.delete(
                        f"{API_URL}/customers/{delete_customer_id}"
                    )

                    if delete_response.status_code == 200:
                        st.success(
                            "Customer deleted successfully!"
                        )
                    else:
                        st.error(delete_response.text)

            else:
                st.info("No customers found.")


# ---------------- ROOMS ----------------

elif menu == "Rooms":

    st.title("🏨 Rooms")

    tab1, tab2 = st.tabs(["Add Room", "View Rooms"])

    # ---------------- ADD ROOM ----------------

    with tab1:

        room_number = st.text_input("Room Number")

        room_type = st.selectbox(
            "Room Type",
            ["Single", "Double", "Deluxe", "Suite"],
            key="add_room_type"
        )

        price = st.number_input(
            "Price per Night",
            min_value=0.0
        )

        room_status = st.selectbox(
            "Room Status",
            ["Available", "Occupied", "Maintenance"],
            key="add_room_status"
        )

        if st.button("Add Room"):

            response = requests.post(
                f"{API_URL}/rooms",
                json={
                    "room_number": room_number,
                    "room_type": room_type,
                    "price_per_night": price,
                    "room_status": room_status
                }
            )

            if response.status_code == 200:
                st.success("Room added successfully!")
            else:
                st.error(response.text)

    # ---------------- VIEW / UPDATE / DELETE ----------------

    with tab2:

        response = requests.get(
            f"{API_URL}/rooms"
        )

        if response.status_code == 200:

            rooms = response.json()

            if rooms:

                st.dataframe(
                    rooms,
                    use_container_width=True
                )

                # -------- UPDATE ROOM --------

                st.subheader("Update Room")

                room_options = {
                    f"Room {r[1]} (ID: {r[0]})": r
                    for r in rooms
                }

                selected_room = st.selectbox(
                    "Select Room",
                    list(room_options.keys()),
                    key="update_room_select"
                )

                room = room_options[selected_room]

                new_room_number = st.text_input(
                    "Room Number",
                    value=room[1],
                    key="update_room_number"
                )

                room_types = [
                    "Single",
                    "Double",
                    "Deluxe",
                    "Suite"
                ]

                new_room_type = st.selectbox(
                    "Room Type",
                    room_types,
                    index=room_types.index(room[2]),
                    key="update_room_type"
                )

                new_price = st.number_input(
                    "Price per Night",
                    min_value=0.0,
                    value=float(room[3]),
                    key="update_room_price"
                )

                room_statuses = [
                    "Available",
                    "Occupied",
                    "Maintenance"
                ]

                new_room_status = st.selectbox(
                    "Room Status",
                    room_statuses,
                    index=room_statuses.index(room[4]),
                    key="update_room_status"
                )

                if st.button("Update Room"):

                    update_response = requests.put(
                        f"{API_URL}/rooms/{room[0]}",
                        json={
                            "room_number": new_room_number,
                            "room_type": new_room_type,
                            "price_per_night": new_price,
                            "room_status": new_room_status
                        }
                    )

                    if update_response.status_code == 200:
                        st.success(
                            "Room updated successfully!"
                        )
                    else:
                        st.error(update_response.text)

                # -------- DELETE ROOM --------

                st.subheader("Delete Room")

                delete_room_options = {
                    f"Room {r[1]} (ID: {r[0]})": r[0]
                    for r in rooms
                }

                selected_delete_room = st.selectbox(
                    "Select Room to Delete",
                    list(delete_room_options.keys()),
                    key="delete_room_select"
                )

                delete_room_id = delete_room_options[
                    selected_delete_room
                ]

                if st.button("Delete Room"):

                    delete_response = requests.delete(
                        f"{API_URL}/rooms/{delete_room_id}"
                    )

                    if delete_response.status_code == 200:
                        st.success(
                            "Room deleted successfully!"
                        )
                    else:
                        st.error(delete_response.text)

            else:
                st.info("No rooms found.")
   #-------------------Boooking------------
elif menu == "Bookings":

    st.title("📅 Bookings")

    tab1, tab2 = st.tabs(
        ["Add Booking", "View Bookings"]
    )

    # ---------------- ADD BOOKING ----------------

    with tab1:

        customers_response = requests.get(
            f"{API_URL}/customers"
        )

        rooms_response = requests.get(
            f"{API_URL}/rooms"
        )

        customers = customers_response.json()
        rooms = rooms_response.json()

        if customers and rooms:

            customer_options = {
                f"{c[1]} (ID: {c[0]})": c[0]
                for c in customers
            }

            room_options = {
                f"Room {r[1]} (ID: {r[0]})": r[0]
                for r in rooms
                if r[4] == "Available"
            }

            if room_options:

                selected_customer = st.selectbox(
                    "Customer",
                    list(customer_options.keys()),
                    key="booking_customer"
                )

                selected_room = st.selectbox(
                    "Room",
                    list(room_options.keys()),
                    key="booking_room"
                )

                check_in = st.date_input(
                    "Check-in Date",
                    key="booking_check_in"
                )

                check_out = st.date_input(
                    "Check-out Date",
                    key="booking_check_out"
                )

                guests = st.number_input(
                    "Number of Guests",
                    min_value=1,
                    value=1,
                    key="booking_guests"
                )

                status = st.selectbox(
                    "Booking Status",
                    [
                        "Confirmed",
                        "Checked-In",
                        "Checked-Out",
                        "Cancelled"
                    ],
                    key="booking_status"
                )

                if st.button("Add Booking"):

                    response = requests.post(
                        f"{API_URL}/bookings",
                        json={
                            "customer_id":
                                customer_options[selected_customer],
                            "room_id":
                                room_options[selected_room],
                            "check_in_date":
                                str(check_in),
                            "check_out_date":
                                str(check_out),
                            "number_of_guests":
                                guests,
                            "booking_status":
                                status
                        }
                    )

                    if response.status_code == 200:
                        st.success(
                            "Booking added successfully!"
                        )
                    else:
                        st.error(response.text)

            else:
                st.warning(
                    "No available rooms."
                )

        else:
            st.warning(
                "First add customers and rooms."
            )

    # ---------------- VIEW / UPDATE / DELETE ----------------

    with tab2:

        response = requests.get(
            f"{API_URL}/bookings"
        )

        if response.status_code == 200:

            bookings = response.json()

            if bookings:

                st.dataframe(
                    bookings,
                    use_container_width=True
                )

                # -------- UPDATE BOOKING --------

                st.subheader("Update Booking")

                booking_options = {
                    f"Booking ID: {b[0]} - {b[1]} - Room {b[2]}": b
                    for b in bookings
                }

                selected_booking = st.selectbox(
                    "Select Booking",
                    list(booking_options.keys()),
                    key="update_booking_select"
                )

                booking = booking_options[selected_booking]

                new_check_in = st.date_input(
                    "Check-in Date",
                    value=booking[4],
                    key="update_booking_check_in"
                )

                new_check_out = st.date_input(
                    "Check-out Date",
                    value=booking[5],
                    key="update_booking_check_out"
                )

                new_guests = st.number_input(
                    "Number of Guests",
                    min_value=1,
                    value=int(booking[6]),
                    key="update_booking_guests"
                )

                booking_statuses = [
                    "Confirmed",
                    "Checked-In",
                    "Checked-Out",
                    "Cancelled"
                ]

                new_status = st.selectbox(
                    "Booking Status",
                    booking_statuses,
                    index=booking_statuses.index(booking[7]),
                    key="update_booking_status"
                )

                if st.button("Update Booking"):

                    # Get all customers
                    customer_response = requests.get(
                        f"{API_URL}/customers"
                    )

                    customers = customer_response.json()

                    # Find customer ID using customer name
                    customer_id = None

                    for c in customers:
                        if c[1] == booking[1]:
                            customer_id = c[0]
                            break

                    # Get all rooms
                    room_response = requests.get(
                        f"{API_URL}/rooms"
                    )

                    rooms = room_response.json()

                    # Find room ID using room number
                    room_id = None

                    for r in rooms:
                        if r[1] == booking[2]:
                            room_id = r[0]
                            break

                    if customer_id and room_id:

                        update_response = requests.put(
                            f"{API_URL}/bookings/{booking[0]}",
                            json={
                                "customer_id": customer_id,
                                "room_id": room_id,
                                "check_in_date":
                                    str(new_check_in),
                                "check_out_date":
                                    str(new_check_out),
                                "number_of_guests":
                                    new_guests,
                                "booking_status":
                                    new_status
                            }
                        )

                        if update_response.status_code == 200:
                            st.success(
                                "Booking updated successfully!"
                            )
                        else:
                            st.error(
                                update_response.text
                            )

                    else:
                        st.error(
                            "Customer or room not found."
                        )

                # -------- DELETE BOOKING --------

                st.subheader("Delete Booking")

                delete_booking_options = {
                    f"Booking ID: {b[0]} - {b[1]}": b[0]
                    for b in bookings
                }

                selected_delete_booking = st.selectbox(
                    "Select Booking to Delete",
                    list(delete_booking_options.keys()),
                    key="delete_booking_select"
                )

                delete_booking_id = delete_booking_options[
                    selected_delete_booking
                ]

                if st.button("Delete Booking"):

                    delete_response = requests.delete(
                        f"{API_URL}/bookings/{delete_booking_id}"
                    )

                    if delete_response.status_code == 200:
                        st.success(
                            "Booking deleted successfully!"
                        )
                    else:
                        st.error(
                            delete_response.text
                        )

            else:
                st.info(
                    "No bookings found."
                )


# ---------------- PAYMENTS --------
elif menu == "Payments":

    st.title("💳 Payments")

    tab1, tab2 = st.tabs(
        ["Add Payment", "View / Update / Delete"]
    )

    # ---------------- ADD PAYMENT ----------------

    with tab1:

        booking_response = requests.get(
            f"{API_URL}/bookings"
        )

        customer_response = requests.get(
            f"{API_URL}/customers"
        )

        bookings = booking_response.json()
        customers = customer_response.json()

        if bookings and customers:

            booking_options = {
                f"Booking {b[0]} - {b[1]} - Room {b[2]}": b[0]
                for b in bookings
            }

            customer_options = {
                f"{c[1]} (ID: {c[0]})": c[0]
                for c in customers
            }

            selected_booking = st.selectbox(
                "Booking",
                list(booking_options.keys()),
                key="payment_booking"
            )

            selected_customer = st.selectbox(
                "Customer",
                list(customer_options.keys()),
                key="payment_customer"
            )

            amount = st.number_input(
                "Amount",
                min_value=1.0,
                value=1000.0,
                key="payment_amount"
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "UPI",
                    "Card",
                    "Net Banking"
                ],
                key="payment_method"
            )

            payment_date = st.date_input(
                "Payment Date",
                key="payment_date"
            )

            payment_status = st.selectbox(
                "Payment Status",
                [
                    "Paid",
                    "Pending",
                    "Failed"
                ],
                key="payment_status"
            )

            if st.button("Add Payment"):

                response = requests.post(
                    f"{API_URL}/payments",
                    json={
                        "booking_id":
                            booking_options[selected_booking],
                        "customer_id":
                            customer_options[selected_customer],
                        "amount":
                            amount,
                        "payment_method":
                            payment_method,
                        "payment_date":
                            str(payment_date),
                        "payment_status":
                            payment_status
                    }
                )

                if response.status_code == 200:
                    st.success(
                        "Payment added successfully!"
                    )
                else:
                    st.error(response.text)

        else:
            st.warning(
                "First add customers and bookings."
            )

    # ---------------- VIEW / UPDATE / DELETE ----------------

    with tab2:

        response = requests.get(
            f"{API_URL}/payments"
        )

        if response.status_code == 200:

            payments = response.json()

            if payments:

                st.dataframe(
                    payments,
                    use_container_width=True
                )

                # -------- UPDATE PAYMENT --------

                st.subheader("Update Payment")

                payment_options = {
                    f"Payment ID: {p[0]} - Amount: {p[3]}": p
                    for p in payments
                }

                selected_payment = st.selectbox(
                    "Select Payment",
                    list(payment_options.keys()),
                    key="update_payment_select"
                )

                payment = payment_options[
                    selected_payment
                ]

                new_amount = st.number_input(
                    "Amount",
                    min_value=1.0,
                    value=float(payment[3]),
                    key="update_payment_amount"
                )

                payment_methods = [
                    "Cash",
                    "UPI",
                    "Card",
                    "Net Banking"
                ]

                new_method = st.selectbox(
                    "Payment Method",
                    payment_methods,
                    index=payment_methods.index(
                        payment[4]
                    ),
                    key="update_payment_method"
                )

                new_status = st.selectbox(
                    "Payment Status",
                    [
                        "Paid",
                        "Pending",
                        "Failed"
                    ],
                    index=[
                        "Paid",
                        "Pending",
                        "Failed"
                    ].index(payment[6]),
                    key="update_payment_status"
                )

                if st.button("Update Payment"):

                    # Get booking and customer IDs
                    booking_response = requests.get(
                        f"{API_URL}/bookings"
                    )

                    bookings = booking_response.json()

                    customer_response = requests.get(
                        f"{API_URL}/customers"
                    )

                    customers = customer_response.json()

                    booking_id = None
                    customer_id = None

                    # Find booking ID
                    for b in bookings:
                        if b[1] == payment[2]:
                            booking_id = b[0]
                            break

                    # Find customer ID
                    for c in customers:
                        if c[1] == payment[2]:
                            customer_id = c[0]
                            break

                    if booking_id and customer_id:

                        update_response = requests.put(
                            f"{API_URL}/payments/{payment[0]}",
                            json={
                                "booking_id":
                                    booking_id,
                                "customer_id":
                                    customer_id,
                                "amount":
                                    new_amount,
                                "payment_method":
                                    new_method,
                                "payment_date":
                                    payment[5],
                                "payment_status":
                                    new_status
                            }
                        )

                        if update_response.status_code == 200:
                            st.success(
                                "Payment updated successfully!"
                            )
                        else:
                            st.error(
                                update_response.text
                            )

                    else:
                        st.error(
                            "Booking or customer not found."
                        )

                # -------- DELETE PAYMENT --------

                st.subheader("Delete Payment")

                delete_payment_options = {
                    f"Payment ID: {p[0]} - {p[2]}": p[0]
                    for p in payments
                }

                selected_delete_payment = st.selectbox(
                    "Select Payment to Delete",
                    list(delete_payment_options.keys()),
                    key="delete_payment_select"
                )

                delete_payment_id = (
                    delete_payment_options[
                        selected_delete_payment
                    ]
                )

                if st.button("Delete Payment"):

                    delete_response = requests.delete(
                        f"{API_URL}/payments/{delete_payment_id}"
                    )

                    if delete_response.status_code == 200:
                        st.success(
                            "Payment deleted successfully!"
                        )
                    else:
                        st.error(
                            delete_response.text
                        )

            else:
                st.info("No payments found.")
    

# ---------------- SERVICES ----------------
elif menu == "Services":

    st.title("🛎️ Services")

    tab1, tab2 = st.tabs(
        ["Add Service", "View Services"]
    )

    # ---------------- ADD SERVICE ----------------

    with tab1:

        service_name = st.text_input(
            "Service Name"
        )

        price = st.number_input(
            "Price",
            min_value=0.0
        )

        description = st.text_area(
            "Description"
        )

        status = st.selectbox(
            "Service Status",
            ["Available", "Unavailable"],
            key="add_service_status"
        )

        if st.button("Add Service"):

            response = requests.post(
                f"{API_URL}/services",
                json={
                    "service_name": service_name,
                    "price": price,
                    "description": description,
                    "service_status": status
                }
            )

            if response.status_code == 200:
                st.success(
                    "Service added successfully!"
                )
            else:
                st.error(response.text)

    # ---------------- VIEW / UPDATE / DELETE ----------------

    with tab2:

        response = requests.get(
            f"{API_URL}/services"
        )

        if response.status_code == 200:

            services = response.json()

            if services:

                st.dataframe(
                    services,
                    use_container_width=True
                )

                # -------- UPDATE SERVICE --------

                st.subheader("Update Service")

                service_options = {
                    f"{s[1]} (ID: {s[0]})": s
                    for s in services
                }

                selected_service = st.selectbox(
                    "Select Service",
                    list(service_options.keys()),
                    key="update_service_select"
                )

                service = service_options[selected_service]

                new_service_name = st.text_input(
                    "Service Name",
                    value=service[1],
                    key="update_service_name"
                )

                new_price = st.number_input(
                    "Price",
                    min_value=0.0,
                    value=float(service[2]),
                    key="update_service_price"
                )

                new_description = st.text_area(
                    "Description",
                    value=service[3] if service[3] else "",
                    key="update_service_description"
                )

                service_statuses = [
                    "Available",
                    "Unavailable"
                ]

                new_status = st.selectbox(
                    "Service Status",
                    service_statuses,
                    index=service_statuses.index(service[4]),
                    key="update_service_status"
                )

                if st.button("Update Service"):

                    update_response = requests.put(
                        f"{API_URL}/services/{service[0]}",
                        json={
                            "service_name": new_service_name,
                            "price": new_price,
                            "description": new_description,
                            "service_status": new_status
                        }
                    )

                    if update_response.status_code == 200:
                        st.success(
                            "Service updated successfully!"
                        )
                    else:
                        st.error(update_response.text)

                # -------- DELETE SERVICE --------

                st.subheader("Delete Service")

                delete_service_options = {
                    f"{s[1]} (ID: {s[0]})": s[0]
                    for s in services
                }

                selected_delete_service = st.selectbox(
                    "Select Service to Delete",
                    list(delete_service_options.keys()),
                    key="delete_service_select"
                )

                delete_service_id = delete_service_options[
                    selected_delete_service
                ]

                if st.button("Delete Service"):

                    delete_response = requests.delete(
                        f"{API_URL}/services/{delete_service_id}"
                    )

                    if delete_response.status_code == 200:
                        st.success(
                            "Service deleted successfully!"
                        )
                    else:
                        st.error(delete_response.text)

            else:
                st.info("No services found.")

# ---------------- REPORTS ----------------

elif menu == "Reports":

    st.title("📈 Reports")

    st.subheader("Monthly Revenue")

    response = requests.get(
        f"{API_URL}/reports/monthly-revenue"
    )

    if response.status_code == 200:

        data = response.json()

        if data:
            st.bar_chart(data)
        else:
            st.info("No revenue data available.")

    st.subheader("Most Booked Room")

    response = requests.get(
        f"{API_URL}/reports/most-booked-room"
    )

    if response.status_code == 200:
        st.write(response.json())