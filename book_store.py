import streamlit as st

# ================= APP CONFIG =================
st.set_page_config(page_title="Online Book Store", layout="wide")

# ================= SIDEBAR =================
st.sidebar.title("📘 Online Book Store")
st.sidebar.caption("Buy • Read • Learn")

# ================= SESSION INIT =================
if "users" not in st.session_state:
    st.session_state.users = {
        "user": {
            "password": "1234",
            "name": "",
            "phone": "",
            "address": ""
        }
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

if "books" not in st.session_state:
    st.session_state.books = [
        {"id": 1, "title": "Python Programming", "price": 450, "stock": 5, "discount": 10},
        {"id": 2, "title": "Data Structures", "price": 550, "stock": 4, "discount": 0},
        {"id": 3, "title": "Machine Learning", "price": 650, "stock": 3, "discount": 15},
    ]

if "cart" not in st.session_state:
    st.session_state.cart = []

if "orders" not in st.session_state:
    st.session_state.orders = []

# ================= REGISTER =================
def register_page():
    st.title("📝 Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    if st.button("Register"):
        if not username or not password or not name or not phone or not address:
            st.error("All fields required")
        elif username in st.session_state.users:
            st.error("User already exists")
        else:
            st.session_state.users[username] = {
                "password": password,
                "name": name,
                "phone": phone,
                "address": address
            }
            st.success("Registered successfully ✅")

# ================= LOGIN =================
def login_page():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["User", "Admin"])

    if st.button("Login"):
        if role == "Admin" and username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.session_state.current_user = "admin"
            st.rerun()

        elif role == "User" and username in st.session_state.users and st.session_state.users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = "User"
            st.session_state.current_user = username
            st.rerun()
        else:
            st.error("Invalid login ❌")

# ================= ADMIN =================
def admin_page():
    st.title("🛠 Admin Panel")

    st.subheader("➕ Add New Book")
    title = st.text_input("Book Title")
    price = st.number_input("Price", min_value=1)
    stock = st.number_input("Stock", min_value=1)
    discount = st.number_input("Discount (%)", min_value=0, max_value=100)

    if st.button("Add Book"):
        st.session_state.books.append({
            "id": len(st.session_state.books) + 1,
            "title": title,
            "price": price,
            "stock": stock,
            "discount": discount
        })
        st.success("Book added successfully ✅")

    st.divider()
    st.subheader("📦 All Orders")
    for o in st.session_state.orders:
        st.write(o)

# ================= USER =================
def user_page():
    menu = st.sidebar.radio("Menu", ["Books", "Cart", "My Orders"])

    # -------- BOOKS --------
    if menu == "Books":
        st.title("📚 Books")

        for b in st.session_state.books:
            discount_price = int(b["price"] - (b["price"] * b["discount"] / 100))

            col1, col2, col3, col4 = st.columns(4)
            col1.write(b["title"])

            if b["discount"] > 0:
                col2.markdown(
                    f"""
                    ~~₹{b['price']}~~  
                    **₹{discount_price}**  
                    🟢 **{b['discount']}% OFF**
                    """
                )
            else:
                col2.markdown(f"**₹{b['price']}**")

            col3.write(f"Stock: {b['stock']}")

            if col4.button("Add to Cart", key=b["id"]):
                if b["stock"] > 0:
                    st.session_state.cart.append({
                        "id": b["id"],
                        "title": b["title"],
                        "price": discount_price
                    })
                    b["stock"] -= 1
                    st.success("Added to cart 🛒")

    # -------- CART --------
    elif menu == "Cart":
        st.title("🛒 Cart")

        if not st.session_state.cart:
            st.info("Cart is empty")
            return

        total = 0
        for i in st.session_state.cart:
            st.write(i["title"], "-", i["price"])
            total += i["price"]

        st.subheader(f"Total Amount: ₹{total}")

        payment = st.selectbox(
            "Select Payment Method",
            ["Cash on Delivery", "UPI", "Debit/Credit Card", "Net Banking"]
        )

        details = ""

        if payment == "UPI":
            details = st.text_input("UPI ID / Transaction ID")
        elif payment == "Debit/Credit Card":
            st.text_input("Card Number")
            st.text_input("Expiry Date")
            details = st.text_input("CVV", type="password")
        elif payment == "Net Banking":
            details = st.selectbox("Select Bank", ["SBI", "HDFC", "ICICI", "Axis"])

        if st.button("Pay Now"):
            st.session_state.orders.append({
                "user": st.session_state.current_user,
                "items": st.session_state.cart.copy(),
                "total": total,
                "payment": payment,
                "details": details,
                "status": "Placed"
            })
            st.session_state.cart = []
            st.success("Order placed successfully ✅")

    # -------- MY ORDERS --------
    elif menu == "My Orders":
        st.title("📦 My Orders")

        for idx, o in enumerate(st.session_state.orders):
            if o["user"] == st.session_state.current_user:
                st.write("Items:")
                for item in o["items"]:
                    st.write("-", item["title"])

                st.write("Total:", o["total"])
                st.write("Payment:", o["payment"])
                st.write("Status:", o["status"])

                # ❌ CANCEL + REFUND LOGIC
                if o["status"] == "Placed":
                    if st.button("Cancel Order", key=f"cancel_{idx}"):
                        if o["payment"] == "Cash on Delivery":
                            o["status"] = "Cancelled"
                        else:
                            o["status"] = "Cancelled – Refund Initiated"

                        # 🔁 Stock back
                        for item in o["items"]:
                            for b in st.session_state.books:
                                if b["id"] == item["id"]:
                                    b["stock"] += 1

                        st.success("Order cancelled successfully")
                        st.rerun()

                st.divider()

# ================= MAIN =================
if not st.session_state.logged_in:
    page = st.sidebar.radio("Menu", ["Register", "Login"])
    register_page() if page == "Register" else login_page()
else:
    admin_page() if st.session_state.role == "Admin" else user_page()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()