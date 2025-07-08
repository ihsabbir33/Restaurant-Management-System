# Enhanced Restaurant Management System with Inventory Tracking

import json
import os
from datetime import datetime

USERS_FILE = "data/users.json"
MENU_FILE = "data/menu.json"
ORDERS_FILE = "data/orders.json"


def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def print_header(title):
    print("\n" + "="*40)
    print(f"{title.center(40)}")
    print("="*40 + "\n")


# User account creation and login
def create_account():
    users = load_data(USERS_FILE)
    print_header("Create New Account")
    name = input("Full Name: ").strip()
    phone = input("Phone Number: ").strip()
    while True:
        user_id = input("Choose User ID: ").strip()
        if any(u["user_id"] == user_id for u in users):
            print("User ID already exists! Try another.")
        else:
            break
    password = input("Password: ").strip()
    role = ""
    while role not in ["admin", "customer"]:
        role = input("Role (admin/customer): ").strip().lower()
    users.append({
        "user_id": user_id,
        "name": name,
        "phone": phone,
        "password": password,
        "role": role
    })
    save_data(USERS_FILE, users)
    print(f"Account created successfully for {user_id} as {role}.\n")


def login():
    users = load_data(USERS_FILE)
    print_header("Login")
    user_id = input("User ID: ").strip()
    password = input("Password: ").strip()
    for user in users:
        if user["user_id"] == user_id and user["password"] == password:
            print(f"Login successful! Welcome, {user['name']} ({user['role']})\n")
            return user
    print("Invalid credentials!\n")
    return None


# Admin Menu
def admin_menu():
    while True:
        print("""
Admin Menu:
1. View Menu Items
2. Add Menu Item
3. Update Menu Item
4. Delete Menu Item
5. Update Stock Quantity
6. View All Orders
7. Logout
        """)
        choice = input("Choose (1-7): ").strip()
        if choice == '1': view_menu()
        elif choice == '2': add_menu_item()
        elif choice == '3': update_menu_item()
        elif choice == '4': delete_menu_item()
        elif choice == '5': update_stock()
        elif choice == '6': view_all_orders()
        elif choice == '7': print("Logging out...\n"); break
        else: print("Invalid choice.\n")


def view_menu():
    menu = load_data(MENU_FILE)
    print_header("Menu Items")
    if not menu:
        print("Menu is empty.\n"); return
    for item in menu:
        print(f"ID: {item['item_id']} | {item['name']} - {item['price']} BDT | Stock: {item['quantity']}")
    print()


def add_menu_item():
    menu = load_data(MENU_FILE)
    item_id = input("New Item ID: ").strip()
    if any(i["item_id"] == item_id for i in menu):
        print("Item ID already exists!\n"); return
    name = input("Item Name: ").strip()
    try:
        price = float(input("Price: ").strip())
        quantity = int(input("Initial Stock Quantity: ").strip())
    except ValueError:
        print("Invalid input!\n"); return
    menu.append({"item_id": item_id, "name": name, "price": price, "quantity": quantity})
    save_data(MENU_FILE, menu)
    print("Item added successfully.\n")


def update_menu_item():
    menu = load_data(MENU_FILE)
    item_id = input("Item ID to update: ").strip()
    for item in menu:
        if item["item_id"] == item_id:
            name = input(f"New Name (leave blank to keep '{item['name']}'): ").strip()
            price_input = input(f"New Price (leave blank to keep {item['price']}): ").strip()
            if name: item['name'] = name
            if price_input:
                try: item['price'] = float(price_input)
                except ValueError: print("Invalid price."); return
            save_data(MENU_FILE, menu)
            print("Item updated.\n"); return
    print("Item ID not found.\n")


def delete_menu_item():
    menu = load_data(MENU_FILE)
    item_id = input("Item ID to delete: ").strip()
    for i, item in enumerate(menu):
        if item["item_id"] == item_id:
            menu.pop(i)
            save_data(MENU_FILE, menu)
            print("Item deleted.\n"); return
    print("Item ID not found.\n")


def update_stock():
    menu = load_data(MENU_FILE)
    item_id = input("Enter Item ID to update stock: ").strip()
    for item in menu:
        if item["item_id"] == item_id:
            try:
                qty = int(input(f"Enter new stock quantity for {item['name']}: "))
                item['quantity'] = qty
                save_data(MENU_FILE, menu)
                print("Stock updated successfully.\n")
                return
            except ValueError:
                print("Invalid quantity!\n"); return
    print("Item ID not found.\n")


def view_all_orders():
    orders = load_data(ORDERS_FILE)
    print_header("All Orders")
    for o in orders:
        print(f"Order ID: {o['order_id']}, User: {o['user_id']}, Time: {o['timestamp']}, Total: {o['total']} BDT")
        for item in o['items']:
            print(f"  - {item['name']} x{item['quantity']} = {item['price'] * item['quantity']} BDT")
        print()


# Customer Menu
def customer_menu(user):
    while True:
        print("""
Customer Menu:
1. View Menu
2. Place Order
3. View My Orders
4. Logout
        """)
        choice = input("Choose (1-4): ").strip()
        if choice == '1': view_menu()
        elif choice == '2': place_order(user)
        elif choice == '3': view_my_orders(user)
        elif choice == '4': print("Logging out...\n"); break
        else: print("Invalid choice.\n")


def place_order(user):
    menu = load_data(MENU_FILE)
    cart = []
    while True:
        item_id = input("Enter Item ID (or 'done'): ").strip()
        if item_id.lower() == 'done': break
        matched = next((i for i in menu if i["item_id"] == item_id), None)
        if not matched:
            print("Invalid Item ID.\n"); continue
        try:
            qty = int(input(f"Enter quantity for {matched['name']}: ").strip())
            if qty <= 0:
                print("Quantity must be positive.\n"); continue
            if qty > matched["quantity"]:
                print(f"❌ Only {matched['quantity']} in stock.\n"); continue
        except ValueError:
            print("Invalid quantity.\n"); continue
        cart.append({"item_id": matched["item_id"], "name": matched["name"], "price": matched["price"], "quantity": qty})
        matched["quantity"] -= qty
        print(f"Added {qty} x {matched['name']}\n")

    if not cart:
        print("No items selected.\n"); return

    total = sum(i['price'] * i['quantity'] for i in cart)
    print_header("Order Summary")
    for item in cart:
        print(f"{item['name']} x{item['quantity']} = {item['price'] * item['quantity']} BDT")
    print(f"Total: {total} BDT\n")

    confirm = input("Confirm order? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Order cancelled.\n"); return

    orders = load_data(ORDERS_FILE)
    order_id = (max([o['order_id'] for o in orders]) + 1) if orders else 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orders.append({
        "order_id": order_id,
        "user_id": user["user_id"],
        "items": cart,
        "total": total,
        "timestamp": timestamp
    })
    save_data(ORDERS_FILE, orders)
    save_data(MENU_FILE, menu)
    print(f"Order placed successfully. Order ID: {order_id}\n")


def view_my_orders(user):
    orders = load_data(ORDERS_FILE)
    my_orders = [o for o in orders if o["user_id"] == user["user_id"]]
    print_header("My Orders")
    if not my_orders:
        print("No orders found.\n")
        return
    for o in my_orders:
        print(f"Order ID: {o['order_id']}, Time: {o['timestamp']}, Total: {o['total']} BDT")
        for item in o['items']:
            print(f"  - {item['name']} x{item['quantity']} = {item['price'] * item['quantity']} BDT")
        print()


# Main Entry Point
def main():
    print_header("Welcome to PyRestaurant")
    while True:
        print("1. Create Account\n2. Login\n3. Exit")
        choice = input("Choose (1-3): ").strip()
        if choice == '1': create_account()
        elif choice == '2':
            user = login()
            if user:
                if user["role"] == "admin": admin_menu()
                else: customer_menu(user)
        elif choice == '3': print("Goodbye!"); break
        else: print("Invalid option.\n")


if __name__ == "__main__":
    main()
