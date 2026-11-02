"""Chapter 9 / §9.7: student management dashboard backed by MySQL."""

import math
from datetime import date

import mysql.connector
import pandas as pd
import streamlit as st
from mysql.connector.pooling import MySQLConnectionPool

from db_config import load_db_config
from student_repository import (
    add_student, count_students, delete_student, get_student,
    list_students, update_major,
)

st.set_page_config(page_title="Chapter 9 | Student Dashboard", layout="wide")


def dashboard_db_config() -> dict:
    """Use .streamlit/secrets.toml when present; otherwise use local .env."""
    try:
        if "database" in st.secrets:
            db = st.secrets["database"]
            config = {
                "host": db.get("host", "localhost"),
                "port": int(db.get("port", 3306)),
                "user": db["user"],
                "password": db["password"],
                "database": db["name"],
                "autocommit": False,
                "connection_timeout": 10,
            }
            return config
    except FileNotFoundError:
        # No secrets.toml: this is normal for a local .env-based project.
        pass
    return load_db_config()


@st.cache_resource(show_spinner=False)
def get_pool() -> MySQLConnectionPool:
    """Share a small reusable pool across Streamlit reruns/sessions (demo)."""
    return MySQLConnectionPool(pool_size=5, **dashboard_db_config())


def connection_factory():
    """Borrow a connection. Repository close() returns it to the pool."""
    return get_pool().get_connection()


def show_error(context: str, err: Exception):
    """Display a user-friendly message without exposing database credentials."""
    if isinstance(err, RuntimeError):
        st.error(f"{context}: {err}")
    elif isinstance(err, mysql.connector.Error):
        st.error(f"{context}: MySQL operation failed. Check the server/schema and input.")
    elif isinstance(err, ValueError):
        st.warning(f"{context}: {err}")
    else:
        st.error(f"{context}: unexpected error. Check the console for details.")


st.title("University Student Management Dashboard")
st.caption("Chapter 9: parameterized SQL, commit/rollback, pooling, and basic CRUD")
st.info("Classroom demo only. Use a dedicated practice database, not production records.")

tab_view, tab_add, tab_manage = st.tabs(["Browse students", "Add student", "Manage student"])

with tab_view:
    st.subheader("Browse and search")
    col_a, col_b, col_c = st.columns([2, 2, 1])
    with col_a:
        search_text = st.text_input("Search first/last name or email")
    with col_b:
        major_filter = st.text_input("Exact major (optional)")
    with col_c:
        page_size = st.selectbox("Rows per page", [10, 25, 50], index=1)

    try:
        selected_major = major_filter.strip() or None
        search = search_text.strip() or None
        total = count_students(selected_major, search, connection_factory=connection_factory)
        if total == 0:
            st.info("No matching student records.")
        else:
            total_pages = math.ceil(total / page_size)
            page = st.number_input(
                "Page", min_value=1, max_value=total_pages, value=1, step=1,
            )
            rows = list_students(
                selected_major, search, limit=page_size,
                offset=(int(page) - 1) * page_size,
                connection_factory=connection_factory,
            )
            frame = pd.DataFrame(rows)
            st.caption(f"Page {page} of {total_pages}; {total} matching student(s)")
            st.dataframe(frame, use_container_width=True, hide_index=True)
            st.download_button(
                "Export current page as CSV",
                frame.to_csv(index=False).encode("utf-8"),
                file_name="chapter9_students_page.csv",
                mime="text/csv",
            )
    except Exception as err:
        show_error("Could not load students", err)

with tab_add:
    st.subheader("Add a new student")
    with st.form("student_add_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            first = st.text_input("First name *")
            major = st.text_input("Major (optional)")
            email = st.text_input("Email *")
        with right:
            last = st.text_input("Last name *")
            when = st.date_input("Enrollment date *", value=date.today())
        submitted = st.form_submit_button("Add student")
    if submitted:
        try:
            result = add_student(
                first, last, major, when, email,
                connection_factory=connection_factory,
            )
            st.success(f"Student #{result['lastrowid']} added ({result['rowcount']} row).")
        except mysql.connector.IntegrityError:
            st.warning("Could not add this record; email may already exist.")
        except Exception as err:
            show_error("Could not add student", err)

with tab_manage:
    st.subheader("Update major or delete a student")
    selected_id = st.number_input("StudentID", min_value=1, step=1, value=2001)
    selected_id = int(selected_id)

    # Do not accidentally act on a previously loaded ID after the input changes.
    if st.session_state.get("loaded_student_id") != selected_id:
        st.session_state["loaded_student"] = None

    if st.button("Load student"):
        try:
            st.session_state["loaded_student"] = get_student(
                selected_id, connection_factory=connection_factory,
            )
            st.session_state["loaded_student_id"] = selected_id
        except Exception as err:
            show_error("Unable to load student", err)
            st.session_state["loaded_student"] = None

    student = st.session_state.get("loaded_student")
    if student is None:
        st.caption("Load an existing StudentID to enable editing/deleting.")
    else:
        st.info(
            f"Loaded #{student['StudentID']}: {student['FirstName']} "
            f"{student['LastName']} | Major: {student['Major'] or 'N/A'}"
        )
        with st.form("change_major_form"):
            new_major = st.text_input("New major (blank = NULL)", value=student["Major"] or "")
            change = st.form_submit_button("Update major")
        if change:
            try:
                affected = update_major(
                    selected_id, new_major, connection_factory=connection_factory,
                )
                if affected:
                    st.success(f"Updated {affected} row(s).")
                    st.session_state["loaded_student"] = get_student(
                        selected_id, connection_factory=connection_factory,
                    )
                else:
                    st.warning("0 rows changed (record missing or value unchanged).")
            except Exception as err:
                show_error("Unable to update major", err)

        st.warning("Delete is permanent and may cascade to AdvisorAssignments.")
        with st.form("delete_student_form"):
            confirmation = st.text_input('Type DELETE to confirm')
            do_delete = st.form_submit_button("Delete student")
        if do_delete:
            if confirmation.strip() != "DELETE":
                st.error('Deletion cancelled: type exactly "DELETE".')
            else:
                try:
                    affected = delete_student(
                        selected_id, connection_factory=connection_factory,
                    )
                    if affected:
                        st.success(f"Deleted {affected} student record(s).")
                        st.session_state["loaded_student"] = None
                    else:
                        st.warning("0 rows deleted (record may no longer exist).")
                except Exception as err:
                    show_error("Unable to delete student", err)
