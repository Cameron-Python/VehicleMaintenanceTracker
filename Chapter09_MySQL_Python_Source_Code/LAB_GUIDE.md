# Chapter 9 — Five Practical Labs

These activities match the **Practical Lab Exercises** at the end of Chapter 9. Use the supplied code as a starting point, then make your own modifications and document your observations. Work in a dedicated practice database; never include credentials in screenshots or submissions.

## Lab 1 — Environment setup and secure configuration (§9.1)

**Files:** `.env.example`, `.gitignore`, `db_config.py`, `examples/ex01_show_config.py`.

Create a virtual environment; install `requirements.txt`; create your own `.env`; run `python -m examples.ex01_show_config`. **Verify:** it displays host/user/database and does not display the password. Explain why `.env` must not be committed to Git.

**Challenge:** Remove `DB_NAME` temporarily and record the readable startup error. Restore it afterward.

## Lab 2 — First MySQL connection with error handling (§9.2)

**File:** `examples/ex02_test_connection.py`.

Run the script with your correct settings; then temporarily test a bad password and an invalid database name. **Verify:** a clear message is printed, and successful connections are closed. Restore your working `.env` after testing.

**Challenge:** Add timing to report how long one successful connection attempt takes. Do not print secrets.

## Lab 3 — DDL, DML, commit and rollback (§9.3)

**Files:** `examples/ex03_create_departments.py`, `examples/ex04_department_crud.py`.

First create the schema using the setup SQL (or run `ex03` with CREATE privileges). Run the CRUD demo, observe the `rowcount` values, and confirm that the intentional duplicate primary-key error is rolled back. **Verify:** the temporary `CIS_DEMO` row is gone at the end.

**Challenge:** Insert a second temporary department ID, update only one of the two rows, then delete both using parameterized WHERE clauses. Write down what `lastrowid` means for a string primary key.

## Lab 4 — SELECT and fetching strategies (§9.4)

**File:** `examples/ex05_fetch_methods.py`.

Run `python -m examples.ex05_fetch_methods --id 2001 --batch-size 2`, then try `--id 99999` and `--batch-size 1`. **Verify:** `fetchone()` returns `None` when no row matches; `fetchmany()` terminates when it returns an empty collection; a dictionary cursor exposes column names.

**Challenge:** Add a cursor-iteration version, and compare it with `fetchall()` for a small result set. Explain why the latter may not be appropriate for millions of rows.

## Lab 5 — Mini Streamlit web app: read and write (§§9.6–9.7)

**Files:** `student_repository.py`, `streamlit_app.py`.

Run `python -m streamlit run streamlit_app.py`. Browse the seeded students; add a new student; verify it appears in your MySQL `Students` table; search by email; change its major; delete it using the confirmation text. **Verify:** list results, changes, and `rowcount` feedback are consistent with SQL queries in Workbench.

**Challenge:** Add a second filter for enrollment date. Keep the filter **parameterized**, set a page-size maximum, and show a helpful message for zero matches. Describe one security feature a real public-facing version would require.

## Optional extension — Atomicity and GenAI-safe tools

- **Atomic transfer (§9.5):** Before and after running `python -m examples.ex06_transfer_funds 101 999 10.00`, query `StudentAccounts`. Explain why the failed second UPDATE should undo the first.
- **Two-table insert:** Import `create_student_with_advisor` from `examples.ex10_atomic_advisor`; deliberately cause its second INSERT to fail and verify the student was not inserted.
- **Structured tool output:** Review `examples/ex09_structured_tools.py`. Explain why an LLM should receive allowlisted functions and structured results instead of the right to execute any SQL string.

## What to submit (suggested)

For each assigned lab: the code you changed, a screenshot or terminal log of the expected result (without credentials), a short explanation of which SQL statements ran, and evidence from a verification query or test.
