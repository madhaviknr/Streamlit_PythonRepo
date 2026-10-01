import json
import csv
import time
from datetime import datetime
from pathlib import Path

EMPLOYEE_FILE = Path(__file__).parent / "employees.json"

# ---------------- Step 1: Persistence ----------------
def load_employees():
    """Load employee records from JSON file and auto-fix missing fields."""
    if EMPLOYEE_FILE.exists():
        with EMPLOYEE_FILE.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)

                # 🔹 Auto-migrate old leave requests
                for emp in data:
                    for req in emp.get("leave_requests", []):
                        # Add days_requested if missing
                        if "days_requested" not in req:
                            try:
                                start = datetime.strptime(req["start_date"], "%Y-%m-%d")
                                end = datetime.strptime(req["end_date"], "%Y-%m-%d")
                                req["days_requested"] = (end - start).days + 1
                            except Exception:
                                req["days_requested"] = "N/A"

                # print(f"Loaded {len(data)} employees from JSON.")
                return data
            except json.JSONDecodeError:
                return []
    else:
        return []

def save_employees(employees):
    """Save employee records to JSON file."""
    with EMPLOYEE_FILE.open("w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4)

# ---------------- Step 2: Structure & Auto-ID ----------------
def generate_employee_id(employees):
    """Generate a unique employee ID based on existing records."""
    if not employees:
        return 1
    else:
        max_id = max(emp["id"] for emp in employees)
        return max_id + 1

# ---------------- Step 3: Core Features ----------------
def register_employee(employees):
    emp_id = generate_employee_id(employees)
    name = input("Enter employee name: ")
    department = input("Enter department: ")
    position = input("Enter position: ")
    date_of_joining = input("Enter date of joining (YYYY-MM-DD): ")
    email = input("Enter email: ")
    phone = input("Enter phone number: ")
    salary = float(input("Enter salary: "))
    role = input("Enter role (Employee/Manager): ").strip().title()
    if role not in ["Employee", "Manager"]:
        role = "Employee"  # default
    
    employee = {
        "id": emp_id,
        "name": name,
        "department": department,
        "position": position,
        "date_of_joining": date_of_joining,
        "email": email,
        "phone": phone,
        "salary": salary,
        "role": role,
        "leave_balance": 20,
        "leave_requests": []
    }
    
    employees.append(employee)
    save_employees(employees) 
    print(f"{role} {name} registered successfully with ID {emp_id}.")

def view_employees(employees):
    if not employees:
        print("No employees found.")
        return
    
    print("\n--- Employee Records ---")
    for emp in employees:
        print(f"ID: {emp['id']}")
        print(f"Name: {emp['name']}")
        print(f"Department: {emp['department']}")
        print(f"Position: {emp['position']}")
        print(f"Date of Joining: {emp['date_of_joining']}")
        print(f"Email: {emp['email']}")
        print(f"Phone: {emp['phone']}")
        print(f"Salary: {emp['salary']}")
        print(f"Role: {emp['role']}")
        print(f"Leave Balance: {emp['leave_balance']}")
        # print(f"Leave Requests: {len(emp['leave_requests'])} request(s)")
        print("-" * 30)

def search_employee(employees):
    if not employees:
        print("No employees found.")
        return
    
    print("\nSearch by:")
    print("1. Employee ID")
    print("2. Employee Name")
    choice = input("Enter choice (1/2): ")
    
    if choice == "1":
        try:
            emp_id = int(input("Enter Employee ID: "))
            result = next((emp for emp in employees if emp["id"] == emp_id), None)
        except ValueError:
            print("Invalid ID format.")
            return
    elif choice == "2":
        name = input("Enter Employee Name: ").strip().lower()
        result = next((emp for emp in employees if emp["name"].lower() == name), None)
    else:
        print("Invalid choice.")
        return
    
    if result:
        print("\n--- Employee Found ---")
        for key, value in result.items():
            if key != "leave_requests":
                print(f"{key.capitalize()}: {value}")
        print(f"Leave Requests: {len(result['leave_requests'])} request(s)")
    else:
        print("Employee not found.")

def apply_for_leave(employees):
    if not employees:
        print("No employees found.")
        return
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid ID format.")
        return
    
    employee = next((emp for emp in employees if emp["id"] == emp_id), None)
    if not employee:
        print("Employee not found.")
        return
    
    start_date = input("Enter leave start date (YYYY-MM-DD): ")
    end_date = input("Enter leave end date (YYYY-MM-DD): ")
    reason = input("Enter reason for leave: ")
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days_requested = (end - start).days + 1
    except ValueError:
        print("Invalid date format.")
        return
    
    if days_requested <= 0:
        print("Invalid leave duration.")
        return
    
    if employee["leave_balance"] < days_requested:
        print("Insufficient leave balance.")
        return
    
    leave_request = {
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "days_requested": days_requested,
        "status": "Pending"
    }
    
    employee["leave_requests"].append(leave_request)
    # employee["leave_balance"] -= days_requested
    
    print(f"Leave request submitted for {employee['name']} ({days_requested} days).")

def check_leave_balance(employees):
    if not employees:
        print("No employees found.")
        return
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid ID format.")
        return
    
    employee = next((emp for emp in employees if emp["id"] == emp_id), None)
    if not employee:
        print("Employee not found.")
        return
    
    print(f"{employee['name']} has {employee['leave_balance']} leave days remaining.")

def view_leave_requests(employees):
    """View all leave requests for a specific employee, grouped by status."""
    if not employees:
        print("No employees found.")
        return
    
    try:
        emp_id = int(input("Enter Employee ID: "))
    except ValueError:
        print("Invalid ID format.")
        return
    
    employee = next((emp for emp in employees if emp["id"] == emp_id), None)
    if not employee:
        print("Employee not found.")
        return
    
    if not employee["leave_requests"]:
        print(f"{employee['name']} has no leave requests.")
        return
    
    # Summary counts
    pending = sum(1 for req in employee["leave_requests"] if req["status"] == "Pending")
    approved = sum(1 for req in employee["leave_requests"] if req["status"] == "Approved")
    rejected = sum(1 for req in employee["leave_requests"] if req["status"] == "Rejected")
    
    print(f"\n--- {employee['name']}'s Leave Requests ---")
    print(f"Summary: {pending} Pending | {approved} Approved | {rejected} Rejected\n")
    
    # Show all requests
    for i, req in enumerate(employee["leave_requests"], start=1):
        print(f"Request {i}:")
        print(f"  Start Date: {req['start_date']}")
        print(f"  End Date: {req['end_date']}")
        print(f"  Reason: {req['reason']}")
        print(f"  Days Requested: {req.get('days_requested', 'N/A')}")
        print(f"  Status: {req['status']}")
        print("-" * 30)

def manage_leave_requests(employees):
    """Approve or reject leave requests (Manager only)."""
    if not employees:
        print("No employees found.")
        return
    
    try:
        emp_id = int(input("Enter your Employee ID (Manager login): "))
    except ValueError:
        print("Invalid ID format.")
        return
    
    manager = next((emp for emp in employees if emp["id"] == emp_id), None)
    if not manager or manager["role"] != "Manager":
        print("Access denied. Only Managers can manage leave requests.")
        return
    
    try:
        target_id = int(input("Enter Employee ID to manage leave requests: "))
    except ValueError:
        print("Invalid ID format.")
        return
    
    employee = next((emp for emp in employees if emp["id"] == target_id), None)
    if not employee:
        print("Employee not found.")
        return
    
    if not employee["leave_requests"]:
        print(f"{employee['name']} has no leave requests.")
        return
    
    print(f"\n--- Leave Requests for {employee['name']} ---")
    for i, req in enumerate(employee["leave_requests"], start=1):
        print(f"{i}. {req['start_date']} to {req['end_date']} | Reason: {req['reason']} | Status: {req['status']}")
    
    try:
        choice = int(input("Select request number to manage: "))
        if choice < 1 or choice > len(employee["leave_requests"]):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return
    
    request = employee["leave_requests"][choice - 1]
    
    print("\n1. Approve")
    print("2. Reject")
    action = input("Enter choice (1/2): ")
    
    if action == "1":
        if employee["leave_balance"] >= request["days_requested"]:
            employee["leave_balance"] -= request["days_requested"]
            request["status"] = "Approved"
            print("Leave request approved and balance updated.")
        else:
            print("Insufficient leave balance. Cannot approve.")
    elif action == "2":
        request["status"] = "Rejected"
        print("Leave request rejected.")
    else:
        print("Invalid choice.")
    
    save_employees(employees)  # auto-save after decision

# ---------------- Step 6: Export ----------------
def export_records_csv(employees):
    """Export employee records to a CSV file."""
    if not employees:
        print("No employees to export.")
        return
        
    with open("employees.csv", "w", newline="") as f:
        writer = csv.writer(f)
        
        # Header row
        writer.writerow([
            "ID", "Name", "Department", "Position", "Date of Joining",
            "Email", "Phone", "Salary", "Role", "Leave Balance", "Leave Requests"
        ])
        
        # Data rows
        for emp in employees:
            writer.writerow([
                emp["id"],
                emp["name"],
                emp["department"],
                emp["position"],
                emp["date_of_joining"],
                emp["email"],
                emp["phone"],
                emp["salary"],
                emp["role"],
                emp["leave_balance"],
                len(emp["leave_requests"])  # Just count requests for CSV
            ])
    
    print("Records exported to employees.csv successfully.")
def main_menu():
    employees = load_employees()
    
    while True:
        print("\n--- Employee Management System ---")
        print("1. Register Employee")
        print("2. View Employees")
        print("3. Search Employee")
        print("4. Apply for Leave")
        print("5. Check Leave Balance")
        print("6. View Leave Requests")
        print("7. Save Records (JSON)")
        print("8. Export Records (CSV)")
        print("9. Manage Leave Requests (Manager only)")
        print("10. Manager Dashboard (View all pending requests)")
        print("11. Exit System")

        choice = input("Enter your choice (1-11): ")
        
        if choice == "1":
            register_employee(employees)
        elif choice == "2":
            view_employees(employees)
        elif choice == "3":
            search_employee(employees)
        elif choice == "4":
            apply_for_leave(employees)
        elif choice == "5":
            check_leave_balance(employees)
        elif choice == "6":
            view_leave_requests(employees)
        elif choice == "7":
            save_employees(employees)
            print("Records saved successfully.")
        elif choice == "8":
            export_records_csv(employees)
        elif choice == "9":
            manage_leave_requests(employees)
        elif choice == "10":
            manager_dashboard(employees)    
        elif choice == "11":
            save_employees(employees)
            print("Exiting system. Goodbye!")
            break            
        else:
            print("Invalid choice. Please try again.")

        if choice != "11":
            time.sleep(3)

def manager_dashboard(employees):
    """Show and manage all pending leave requests across employees (Manager only)."""
    if not employees:
        print("No employees found.")
        return
    
    try:
        emp_id = int(input("Enter your Employee ID (Manager login): "))
    except ValueError:
        print("Invalid ID format.")
        return
    
    manager = next((emp for emp in employees if emp["id"] == emp_id), None)
    if not manager or manager["role"] != "Manager":
        print("Access denied. Only Managers can view the dashboard.")
        return
    
    # Collect all pending requests
    pending_requests = []
    for emp in employees:
        for req in emp["leave_requests"]:
            if req["status"] == "Pending":
                pending_requests.append((emp, req))
    
    if not pending_requests:
        print("No pending leave requests across employees.")
        return
    
    # Summary line
    unique_employees = {emp["id"] for emp, _ in pending_requests}
    print(f"\n--- Manager Dashboard ---")
    print(f"Summary: {len(pending_requests)} pending requests across {len(unique_employees)} employees\n")
    
    # Show all pending requests
    for i, (emp, req) in enumerate(pending_requests, start=1):
        print(f"{i}. Employee: {emp['name']} (ID: {emp['id']})")
        print(f"   Start Date: {req['start_date']}")
        print(f"   End Date: {req['end_date']}")
        print(f"   Reason: {req['reason']}")
        print(f"   Days Requested: {req.get('days_requested', 'N/A')}")
        print(f"   Status: {req['status']}")
        print("-" * 40)
    
    # Batch processing
    print("\nBatch Actions:")
    print("1. Approve all pending requests")
    print("2. Reject all pending requests")
    print("3. Manage individually")
    action = input("Enter choice (1/2/3): ")
    
    if action == "1":
        for emp, request in pending_requests:
            if emp["leave_balance"] >= request["days_requested"]:
                emp["leave_balance"] -= request["days_requested"]
                request["status"] = "Approved"
            else:
                request["status"] = "Rejected (Insufficient Balance)"
        print("All pending requests processed: Approved where possible, rejected otherwise.")
    
    elif action == "2":
        for _, request in pending_requests:
            request["status"] = "Rejected"
        print("All pending requests rejected.")
    
    elif action == "3":
        try:
            choice = int(input("Select request number to manage (or 0 to exit): "))
            if choice == 0:
                return
            if choice < 1 or choice > len(pending_requests):
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input.")
            return
        
        emp, request = pending_requests[choice - 1]
        print("\n1. Approve")
        print("2. Reject")
        action = input("Enter choice (1/2): ")
        
        if action == "1":
            if emp["leave_balance"] >= request["days_requested"]:
                emp["leave_balance"] -= request["days_requested"]
                request["status"] = "Approved"
                print(f"Leave request approved for {emp['name']}. Balance updated.")
            else:
                print("Insufficient leave balance. Cannot approve.")
        elif action == "2":
            request["status"] = "Rejected"
            print(f"Leave request rejected for {emp['name']}.")
        else:
            print("Invalid choice.")
    
    else:
        print("Invalid choice.")
    
    save_employees(employees)  # auto-save after decision

if __name__ == "__main__":
    main_menu()