import csv
import os
from datetime import datetime
import shutil

FILENAME = "plumbing_fixtures_inventory.csv"
BACKUP_FILENAME = "plumbing_fixtures_inventory_backup.csv"

# Define inventory thresholds (for example, minimum stock levels)
MIN_STOCK = 5

# User information section (now only asking for name)
def collect_user_information():
    print("=== Welcome to the Plumbing Fixtures Inventory System ===")
    user_name = input("Enter your name: ")
    print(f"\nWelcome, {user_name}! You are now logged in.")
    print("You can begin managing the inventory.\n")
    return user_name

# Collect user information before the program starts
user_name = collect_user_information()

def display_menu():
    print("\n=== PLUMBING FIXTURES & FITTINGS INVENTORY ===")
    print("1. Add new stock")
    print("2. View inventory")
    print("3. Edit stock")
    print("4. Remove stock")
    print("5. Search material")
    print("6. View low stock items")
    print("7. View inventory summary")
    print("8. Export inventory to CSV")
    print("9. Import inventory from CSV")
    print("10. View stock adjustment report")
    print("11. Sort inventory")
    print("12. Clear all data")
    print("13. Backup inventory")
    print("14. Exit")

def add_stock():
    try:
        material_name = input("Material name (e.g., Faucet, Toilet, Sink): ")
        quantity = int(input("Quantity: "))
        price_per_unit = float(input("Price per unit: "))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(FILENAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, material_name, quantity, price_per_unit])
        print("Stock added successfully.")
    except ValueError:
        print("Please enter valid numerical values.")

def view_inventory():
    if not os.path.exists(FILENAME):
        print("No inventory data found.")
        return
    print("\n--- Inventory Records ---")
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

def edit_stock():
    material_name = input("Enter material name to edit: ")
    try:
        with open(FILENAME, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        edited = False
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                if row[1] == material_name:
                    old_quantity = int(row[2])
                    old_price = float(row[3])
                    new_quantity = int(input(f"Current quantity of {material_name} is {old_quantity}. Enter new quantity: "))
                    new_price = float(input(f"Current price per unit of {material_name} is ₱{old_price:.2f}. Enter new price per unit: "))
                    
                    row[2] = str(new_quantity)
                    row[3] = str(new_price)
                    writer.writerow(row)
                    
                    # Log adjustment
                    with open("stock_adjustments.csv", mode='a', newline='') as adjust_file:
                        adjust_writer = csv.writer(adjust_file)
                        adjust_writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            material_name,
                            f"{old_quantity} → {new_quantity}",
                            f"₱{old_price:.2f} → ₱{new_price:.2f}",
                            "Edited",
                            user_name
                        ])
                    edited = True
                else:
                    writer.writerow(row)

        if edited:
            print(f"{material_name} stock edited successfully.")
        else:
            print(f"Material {material_name} not found.")
    except ValueError:
        print("Invalid input.")

def remove_stock():
    material_name = input("Enter material name to remove: ")
    try:
        with open(FILENAME, mode='r') as file:
            lines = list(csv.reader(file))

        removed = False
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in lines:
                if row[1] == material_name:
                    old_quantity = int(row[2])
                    remove_quantity = int(input(f"Current quantity of {material_name} is {old_quantity}. Enter quantity to remove: "))
                    new_quantity = max(0, old_quantity - remove_quantity)
                    
                    row[2] = str(new_quantity)
                    writer.writerow(row)

                    # Log adjustment
                    with open("stock_adjustments.csv", mode='a', newline='') as adjust_file:
                        adjust_writer = csv.writer(adjust_file)
                        adjust_writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            material_name,
                            f"{old_quantity} → {new_quantity}",
                            "-",
                            "Removed Quantity",
                            user_name
                        ])
                    removed = True
                else:
                    writer.writerow(row)

        if removed:
            print(f"{material_name} stock updated successfully.")
        else:
            print(f"Material {material_name} not found.")
    except ValueError:
        print("Invalid input.")

def search_material():
    search_term = input("Enter material name to search: ").lower()
    if not os.path.exists(FILENAME):
        print("No inventory data found.")
        return
    print(f"\n--- Search Results for '{search_term}' ---")
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        found = False
        for row in reader:
            if search_term in row[1].lower():  # Case-insensitive search
                print(row)
                found = True
        if not found:
            print("No materials found matching the search term.")

def view_low_stock_items():
    if not os.path.exists(FILENAME):
        print("No inventory data found.")
        return
    print(f"\n--- Low Stock Items (below {MIN_STOCK} units) ---")
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            _, material_name, quantity, _ = row
            if int(quantity) < MIN_STOCK:
                print(f"{material_name}: {quantity} units")

def view_summary():
    if not os.path.exists(FILENAME):
        print("No inventory data to summarize.")
        return

    total_items = 0
    low_stock_count = 0
    total_value = 0
    value_breakdown = {}

    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            _, material_name, quantity, price_per_unit = row
            quantity = int(quantity)
            price_per_unit = float(price_per_unit)

            total_items += quantity
            total_value += quantity * price_per_unit

            if quantity < MIN_STOCK:
                low_stock_count += 1

            if material_name not in value_breakdown:
                value_breakdown[material_name] = 0
            value_breakdown[material_name] += quantity * price_per_unit

    print("\n--- Inventory Summary ---")
    print(f"Total Materials: {total_items}")
    print(f"Low Stock Items (less than {MIN_STOCK} units): {low_stock_count}")
    print(f"Total Inventory Value: ${total_value:.2f}")
    print("\n--- Inventory Value Breakdown by Material ---")
    for material, value in value_breakdown.items():
        print(f"{material}: ${value:.2f}")

def export_inventory():
    try:
        with open(FILENAME, mode='r') as file:
            data = file.readlines()
        
        with open("exported_inventory.csv", mode='w', newline='') as file:
            file.writelines(data)
        
        print("Inventory exported successfully to 'exported_inventory.csv'.")
    except Exception as e:
        print(f"Error exporting inventory: {e}")

def import_inventory():
    try:
        file_name = input("Enter the filename to import (e.g., 'inventory.csv'): ")
        with open(file_name, mode='r') as file:
            data = file.readlines()

        with open(FILENAME, mode='a', newline='') as file:
            file.writelines(data)

        print(f"Inventory imported successfully from '{file_name}'.")
    except Exception as e:
        print(f"Error importing inventory: {e}")

def view_stock_adjustment_report():
    print("\n--- Stock Adjustment Report ---")
    if not os.path.exists("stock_adjustments.csv"):
        print("No stock adjustments have been made yet.")
        return
    
    with open("stock_adjustments.csv", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(f"Time: {row[0]} | Material: {row[1]} | Quantity: {row[2]} | Price: {row[3]} | Type: {row[4]} | By: {row[5]}")

def sort_inventory():
    try:
        sort_choice = input("Sort by (1) Material Name, (2) Quantity, or (3) Price per Unit: ")
        if sort_choice == '1':
            sort_key = 1
        elif sort_choice == '2':
            sort_key = 2
        elif sort_choice == '3':
            sort_key = 3
        else:
            print("Invalid choice.")
            return
        
        with open(FILENAME, mode='r') as file:
            inventory = list(csv.reader(file))
        
        inventory.sort(key=lambda row: row[sort_key].lower() if sort_key == 1 else float(row[sort_key]))
        
        print("\n--- Sorted Inventory ---")
        for row in inventory:
            print(row)
    except Exception as e:
        print(f"Error sorting inventory: {e}")

def clear_all_data():
    confirm = input("Are you sure you want to clear ALL inventory data? This action cannot be undone (yes/no): ").strip().lower()
    if confirm == 'yes':
        try:
            if os.path.exists(FILENAME):
                os.remove(FILENAME)
            print("All inventory data cleared.")
        except Exception as e:
            print(f"Error clearing data: {e}")
    else:
        print("Clear operation canceled. No changes have been made to the inventory data.")

def backup_inventory():
    try:
        shutil.copy(FILENAME, BACKUP_FILENAME)
        print(f"Inventory backed up successfully to '{BACKUP_FILENAME}'.")
    except Exception as e:
        print(f"Error backing up inventory: {e}")

def main():
    while True:
        display_menu()
        choice = input("Select an option: ")
        if choice == '1':
            add_stock()
        elif choice == '2':
            view_inventory()
        elif choice == '3':
            edit_stock()
        elif choice == '4':
            remove_stock()
        elif choice == '5':
            search_material()
        elif choice == '6':
            view_low_stock_items()
        elif choice == '7':
            view_summary()
        elif choice == '8':
            export_inventory()
        elif choice == '9':
            import_inventory()
        elif choice == '10':
            view_stock_adjustment_report()
        elif choice == '11':
            sort_inventory()
        elif choice == '12':
            clear_all_data()
        elif choice == '13':
            backup_inventory()
        elif choice == '14':
            print(f"The session has ended. Thank you for using the inventory system, {user_name}!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
