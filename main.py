

import mysql.connector
from getpass import getpass

password = getpass("Enter your MySQL password: ")

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
        database="VehicleMaintenanceTracker"
    )

    cursor = connection.cursor()
    print("\nConnected to Vehicle Maintenance Tracker!")

    while True:
        print("\n--- Vehicle Maintenance Tracker ---")
        print("1. View All Vehicles")
        print("2. View Service Types")
        print("3. View Maintenance History")
        print("4. View Upcoming Maintenance")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            cursor.execute("SELECT * FROM Vehicle")
        elif choice == "2":
            cursor.execute("SELECT * FROM ServiceType")
        elif choice == "3":
            cursor.execute("SELECT * FROM MaintenanceRecord")
        elif choice == "4":
            cursor.execute("SELECT * FROM MaintenanceSchedule")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")
            continue

        results = cursor.fetchall()

        if results:
            for row in results:
                print(row)
        else:
            print("No records found.")

    cursor.close()
    connection.close()

except mysql.connector.Error as error:
    print("Database error:", error)
