import streamlit as st
import pandas as pd
from datetime import datetime
from LeaveManage_admin import (
    load_employees, save_employees, generate_employee_id,
    export_records_csv
)

# ---------------- Helper ----------------
def flatten_employees(employees):
    flat_records = []
    for emp in employees:
        flat_emp = emp.copy()
        # flat_emp["leave_requests"] = "; ".join(
        #     [f"{req.get('start_date','?')}→{req.get('end_date','?')} "
        #      f"({req.get('status','?')}, {req.get('days_requested','N/A')} days)"
        #      for req in emp.get("leave_requests", [])]
        # ) if emp.get("leave_requests") else "None"
        flat_emp.pop("leave_requests", None)
        flat_records.append(flat_emp)
        df = pd.DataFrame(flat_records).reset_index(drop=True)

        # Format column names: replace "_" with " " and capitalize first letter
        df.columns = [col.replace("_", " ").capitalize() for col in df.columns]
    # Drop index so no extra left-most column
    return df

# ---------------- Init ----------------
st.session_state["employees"] = load_employees()
if "menu" not in st.session_state:
    st.session_state["menu"] = "View Employees"  # default

employees = st.session_state["employees"]

# ---------------- Title ----------------
st.markdown(
    "<h1 style='text-align: center; color: #2E86C1;'>Employee Management System</h1>",
    unsafe_allow_html=True
)

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Menu Navigation")

if st.sidebar.button("Register Employee"): st.session_state["menu"] = "Register Employee"
if st.sidebar.button("View Employees"): st.session_state["menu"] = "View Employees"
if st.sidebar.button("Search Employee"): st.session_state["menu"] = "Search Employee"
if st.sidebar.button("Apply for Leave"): st.session_state["menu"] = "Apply for Leave"
if st.sidebar.button("Check Leave Balance"): st.session_state["menu"] = "Check Leave Balance"
if st.sidebar.button("View Leave Requests"): st.session_state["menu"] = "View Leave Requests"
if st.sidebar.button("Manage Leave Requests"): st.session_state["menu"] = "Manage Leave Requests"
if st.sidebar.button("Manager Dashboard"):
    st.session_state["menu"] = "Manager Dashboard"
    st.session_state["dashboard_loaded"] = True
if st.sidebar.button("Export Records (CSV)"): st.session_state["menu"] = "Export Records (CSV)"

menu = st.session_state["menu"]

# ---------------- Register Employee ----------------
if menu == "Register Employee":
    st.header("Register Employee")
    name = st.text_input("Name")
    department = st.text_input("Department")
    position = st.text_input("Position")
    date_of_joining = st.date_input("Date of Joining")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    salary = st.number_input("Salary", min_value=0.0)
    role = st.selectbox("Role", ["Employee", "Manager"])
    
    if st.button("Register"):
     #   st.info("Processing registration...")
        emp_id = generate_employee_id(employees)
        employee = {
            "id": emp_id,
            "name": name,
            "department": department,
            "position": position,
            "date_of_joining": str(date_of_joining),
            "email": email,
            "phone": phone,
            "salary": salary,
            "role": role,
            "leave_balance": 20,
            "leave_requests": []
        }
        employees.append(employee)
        save_employees(employees)
        st.success(f"{role} {name} registered successfully with ID {emp_id}.")

# ---------------- View Employees ----------------
elif menu == "View Employees":
    st.header("Employee Records")
    if employees:
        st.dataframe(flatten_employees(employees),hide_index=True)
    else:
        st.warning("No employees found.")

# ---------------- Search Employee ----------------
elif menu == "Search Employee":
    st.header("Search Employee")
    emp_id = st.number_input("Employee ID", min_value=1, step=1)
    if st.button("Search by ID"):
       # st.info("Searching...")
        result = next((emp for emp in employees if emp["id"] == emp_id), None)
        if result:
            # Convert to DataFrame and apply the same formatting
            df = pd.DataFrame([result]).reset_index(drop=True)

            # Clean up column names: replace "_" with space and capitalize first letter
            df.columns = [col.replace("_", " ").capitalize() for col in df.columns]

            # Drop leave_requests column if you don’t want it
            df = df.drop(columns=["leave_requests"], errors="ignore")

            st.dataframe(df, hide_index=True)

        else:
            st.error("Employee not found.")
    name = st.text_input("Employee Name")
    if st.button("Search by Name"):
       # st.info("Searching...")
        result = next((emp for emp in employees if emp["name"].lower() == name.lower()), None)
        if result:
            # Convert to DataFrame and apply the same formatting
            df = pd.DataFrame([result]).reset_index(drop=True)

            # Clean up column names: replace "_" with space and capitalize first letter
            df.columns = [col.replace("_", " ").capitalize() for col in df.columns]

            # Drop leave_requests column if you don’t want it
            df = df.drop(columns=["leave_requests"], errors="ignore")

            st.dataframe(df, hide_index=True)
        else:
            st.error("Employee not found.")

# ---------------- Apply for Leave ----------------
elif menu == "Apply for Leave":
    st.header("Apply for Leave")
    emp_id = st.number_input("Employee ID", min_value=1, step=1)
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    reason = st.text_area("Reason")
    
    if st.button("Submit Request"):
       # st.info("Processing leave request...")
        employee = next((emp for emp in employees if emp["id"] == emp_id), None)
        if not employee:
            st.error("Employee not found.")
        else:
            days_requested = (end_date - start_date).days + 1
            if days_requested <= 0:
                st.error("Invalid date range.")
            elif employee["leave_balance"] < days_requested:
                st.error("Insufficient leave balance.")
            else:
                leave_request = {
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "reason": reason,
                    "days_requested": days_requested,
                    "status": "Pending"
                }
                employee["leave_requests"].append(leave_request)
                save_employees(employees)
                st.success(f"Leave request submitted ({days_requested} day(s)).")

# ---------------- Check Leave Balance ----------------
elif menu == "Check Leave Balance":
    st.header("Check Leave Balance")
    emp_id = st.number_input("Employee ID", min_value=1, step=1)
    if st.button("Check Balance"):
        employee = next((emp for emp in st.session_state["employees"] if emp["id"] == emp_id), None)
        if employee:
            st.info(f"{employee['name']} has {employee['leave_balance']} leave days remaining.")
        else:
            st.error("Employee not found.")


# ---------------- View Leave Requests ----------------
elif menu == "View Leave Requests":
    st.header("View Leave Requests")
    emp_id = st.number_input("Employee ID", min_value=1, step=1)
    if st.button("View Requests"):
        employee = next((emp for emp in employees if emp["id"] == emp_id), None)
        if employee:
            if employee["leave_requests"]:
                # Summary counts
                pending_count = sum(1 for r in employee["leave_requests"] if r["status"] == "Pending")
                approved_count = sum(1 for r in employee["leave_requests"] if r["status"] == "Approved")
                rejected_count = sum(1 for r in employee["leave_requests"] if r["status"].startswith("Rejected"))

                st.write(f"Summary: {pending_count} Pending | {approved_count} Approved | {rejected_count} Rejected")

                # Show pending requests separately
                pending_requests = [r for r in employee["leave_requests"] if r["status"] == "Pending"]
                if pending_requests:
                    st.subheader("⏳ Pending Requests")
                    st.table(pending_requests)
                else:
                    st.info("No pending requests.")

                # Show history (approved/rejected)
                history = [r for r in employee["leave_requests"] if r["status"] != "Pending"]
                if history:
                    st.subheader("📜 Leave History")
                    st.table(history)

            else:
                st.warning("No leave requests.")
        else:
            st.error("Employee not found.")

# ---------------- Manage Leave Requests ----------------
elif menu == "Manage Leave Requests":
    st.header("Manage Leave Requests (Manager only)")
    manager_id = st.number_input("Manager ID", min_value=1, step=1)
    target_id = st.number_input("Employee ID to manage", min_value=1, step=1)

    load_requests_clicked = st.button("Load Requests")
    reload_requests = st.session_state.pop("reload_requests", False)
    if load_requests_clicked:
        st.session_state["requests_loaded"] = True
    if st.session_state.get("requests_loaded", False) or reload_requests:
        manager = next((emp for emp in st.session_state["employees"] if emp["id"] == manager_id and emp["role"] == "Manager"), None)
        employee = next((emp for emp in st.session_state["employees"] if emp["id"] == target_id), None)

        if not manager:
            st.error("Access denied. Only Managers can manage leave requests.")
        elif not employee:
            st.error("Employee not found.")
        else:
            pending_requests = [req for req in employee["leave_requests"] if req["status"] == "Pending"]

            if not pending_requests:
                st.info("No pending requests.")
            else:
                for idx, req in enumerate(pending_requests):
                    st.write(f"{req['start_date']} → {req['end_date']} | Reason: {req['reason']} | Status: {req['status']}")
                    col1, col2 = st.columns(2)

                    if col1.button("Approve", key=f"approve_{employee['id']}_{idx}"):
                        if employee["leave_balance"] >= req["days_requested"]:
                            employee["leave_balance"] -= req["days_requested"]
                            req["status"] = "Approved"
                        else:
                            req["status"] = "Rejected (Insufficient Balance)"

                        employee["leave_requests"] = employee["leave_requests"][:]
                        save_employees(st.session_state["employees"])
                        st.session_state["employees"] = load_employees()
                        st.session_state["reload_requests"] = True
                        if req["status"] == "Approved":
                            st.success(f"Approved. New balance: {employee['leave_balance']} days")
                        else:
                            st.error("Cannot approve: insufficient leave balance.")
                        st.rerun()

                    if col2.button("Reject", key=f"reject_{employee['id']}_{idx}"):
                        req["status"] = "Rejected"
                        employee["leave_requests"] = employee["leave_requests"][:]
                        save_employees(st.session_state["employees"])
                        st.session_state["employees"] = load_employees()
                        st.session_state["reload_requests"] = True
                        st.warning("Rejected.")
                        st.rerun()

            history = [req for req in employee["leave_requests"] if req["status"] != "Pending"]
            if history:
                st.subheader("📜 Leave History")
                st.table(history)


# ---------------- Manager Dashboard ----------------
elif menu == "Manager Dashboard":
    st.header("Manager Dashboard")
    manager_id = st.number_input("Manager ID", min_value=1, step=1)

    load_dashboard_clicked = st.button("Load Dashboard")
    reload_dashboard = st.session_state.pop("reload_dashboard", False)
    if load_dashboard_clicked:
        st.session_state["dashboard_loaded"] = True
    if st.session_state.get("dashboard_loaded", False) or reload_dashboard:
        manager = next((emp for emp in st.session_state["employees"] if emp["id"] == manager_id and emp["role"] == "Manager"), None)

        if not manager:
            st.error("Access denied.")
        else:
            pending_requests = [(emp, req) for emp in st.session_state["employees"] for req in emp["leave_requests"] if req["status"] == "Pending"]

            if not pending_requests:
                st.info("No pending requests.")
            else:
                st.write(f"Summary: {len(pending_requests)} pending requests across {len({emp['id'] for emp,_ in pending_requests})} employees")

                for idx, (emp, req) in enumerate(pending_requests):
                    st.write(f"{emp['name']} ({emp['id']}) | {req['start_date']}→{req['end_date']} | {req['reason']} | {req.get('days_requested','N/A')} days")
                    col1, col2 = st.columns(2)

                    if col1.button("Approve", key=f"approve_{emp['id']}_{idx}"):
                        if emp["leave_balance"] >= req["days_requested"]:
                            emp["leave_balance"] -= req["days_requested"]
                            req["status"] = "Approved"
                        else:
                            req["status"] = "Rejected (Insufficient Balance)"

                        emp["leave_requests"] = emp["leave_requests"][:]
                        save_employees(st.session_state["employees"])
                        st.session_state["employees"] = load_employees()
                        st.session_state["reload_dashboard"] = True
                        if req["status"] == "Approved":
                            st.success(f"Approved for {emp['name']}. New balance: {emp['leave_balance']} days")
                        else:
                            st.error(f"Cannot approve for {emp['name']}: insufficient leave balance.")
                        st.rerun()

                    if col2.button("Reject", key=f"reject_{emp['id']}_{idx}"):
                        req["status"] = "Rejected"
                        emp["leave_requests"] = emp["leave_requests"][:]
                        save_employees(st.session_state["employees"])
                        st.session_state["employees"] = load_employees()
                        st.session_state["reload_dashboard"] = True
                        st.warning(f"Rejected for {emp['name']}")
                        st.rerun()

            history = [(emp, req) for emp in st.session_state["employees"] for req in emp["leave_requests"] if req["status"] != "Pending"]
            if history:
                st.subheader("📜 Leave History")
                st.table([{**req, "Employee": emp["name"]} for emp, req in history])


# ---------------- Export Records ----------------
elif menu == "Export Records (CSV)":
    st.header("Export Records")
    if st.button("Export"):
        # st.info("Exporting records...")
        export_records_csv(employees)
        st.success("Records exported to employees.csv successfully.")
