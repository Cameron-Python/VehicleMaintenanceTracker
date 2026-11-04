# Chapter 9 — Connecting MySQL with Python Applications

**Companion source code** for Chapter 9 of the database management textbook.

The examples are designed for students to **read, run, modify, and verify**. They use the chapter's university-themed tables and demonstrate Python's `mysql.connector` API, parameterized SQL, transaction control, fetching results, console apps, and a Streamlit dashboard. No cloud account or generative-AI API is required.

> **Practice environment only.** Run these examples against a dedicated local MySQL database. They include `INSERT`, `UPDATE`, and `DELETE` commands that change data. The Streamlit app has no login/authentication and should **not** be deployed publicly as-is.

## 1. What you need

- **Python 3.10 or newer** (the examples use modern type hints).
- **MySQL Server 8.0.16+**, preferably MySQL 8.4 LTS or another compatible modern MySQL 8+ version. MySQL Workbench is optional.
- Terminal/PowerShell or an editor such as VS Code.
- A local MySQL account permitted to create the teaching database and tables **for initial setup**. The application can use a separate, less-privileged account afterward.

### Package layout

```text
Chapter09_MySQL_Python_Source_Code/
├── README.md                         This guide
├── LAB_GUIDE.md                      Five activities aligned with the chapter
├── requirements.txt                  Python dependencies
├── .env.example                      Safe, placeholder configuration
├── .gitignore                        Excludes credentials and Python caches
├── .streamlit/
│   └── secrets.toml.example          Optional Streamlit secret configuration
├── db_config.py                      Loads .env and opens connections
├── student_repository.py             Reusable, parameterized student operations
├── streamlit_app.py                  Interactive student dashboard
├── sql/
│   ├── 00_create_database.sql        Creates MyUniversityDB
│   ├── 01_schema.sql                 Creates Departments, Students, ...
│   ├── 02_seed_data.sql              Adds safe sample data if missing
│   └── 03_optional_app_user.sql      Optional low-privilege local DB user
├── examples/
│   ├── ex01_show_config.py           Check env vars, never show password
│   ├── ex02_test_connection.py       First connection and error handling
│   ├── ex03_create_departments.py    CREATE TABLE IF NOT EXISTS
│   ├── ex04_department_crud.py       INSERT, UPDATE, DELETE, rollback
│   ├── ex05_fetch_methods.py         fetchone/fetchmany/fetchall/dictionaries
│   ├── ex06_transfer_funds.py        Atomic transfer + conditional UPDATE
│   ├── ex07_student_intake.py        Interactive console form
│   ├── ex08_student_report.py        Filtered/paginated console report
│   ├── ex09_structured_tools.py      Example allowlisted AI-style functions
│   └── ex10_atomic_advisor.py        Optional two-insert transaction extension
└── tests/
    └── test_chapter9.py              Unit tests (no MySQL server needed)
```

## 2. One-time setup

All commands in this guide assume your terminal is **inside the extracted `Chapter09_MySQL_Python_Source_Code` folder**. Run examples with `python -m examples.NAME` rather than `python examples/NAME.py`; the `-m` form makes the shared modules import correctly.

### A. Create a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, use Command Prompt and `.venv\Scripts\activate.bat`, or consult your organization's PowerShell execution policy. You can always run `.venv\Scripts\python.exe` directly.

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

When finished, run `deactivate`.

### B. Create the database and sample tables

**Option 1: MySQL Workbench (all platforms)**

1. Open Workbench and connect to your **local development** MySQL instance using a setup account.
2. Run `sql/00_create_database.sql` in a SQL tab.
3. Run `sql/01_schema.sql` in a SQL tab.
4. Run `sql/02_seed_data.sql` in a SQL tab.
5. Check the result with:

```sql
USE MyUniversityDB;
SELECT StudentID, FirstName, LastName, Major FROM Students;
SELECT * FROM StudentAccounts;
```

**Option 2: MySQL command-line client (macOS/Linux/bash)**

```bash
mysql -u root -p < sql/00_create_database.sql
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_seed_data.sql
```

On Windows, Workbench is often simpler. In **Command Prompt** (not PowerShell), the same redirection syntax can be used if `mysql.exe` is on your PATH.

**What the SQL creates**

| Table | Purpose |
| --- | --- |
| `Departments` | Section 9.3 DDL/DML exercises |
| `Students` | Sections 9.4, 9.6, and 9.7; `StudentID` is `AUTO_INCREMENT`, `Email` is `UNIQUE` |
| `StudentAccounts` | Section 9.5 atomic transfer; balances use `DECIMAL(10,2)` |
| `AdvisorAssignments` | Optional project activity: insert a student and advisor atomically |

The seed includes sample `Students` **2001–2003** and two independent teaching accounts, **101 ($200.00)** and **105 ($100.00)**. The accounts deliberately do not reference `Students`; they reproduce the chapter's simplified transfer example, **not** a real financial system. All SQL setup files are non-destructive on rerun. Seed reruns **do not reset** modified balances or overwrite existing sample records.

### C. Configure local MySQL credentials

Create your own `.env` file from the example:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux**

```bash
cp .env.example .env
```

Edit `.env` with your actual MySQL connection settings:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=chapter9_app
DB_PASSWORD=your_actual_local_password
DB_NAME=MyUniversityDB
```

You can use a development MySQL account that already has the needed permissions. For a **separate local practice account**, open `sql/03_optional_app_user.sql`, **replace the placeholder password**, and execute it as your MySQL administrator. Then set the same username/password in `.env`. This account is allowed to read/write teaching rows, **but not create database objects**. Therefore run the initial schema SQL as your administrative setup account, and run `ex03_create_departments` with a schema-creation-capable account only if you specifically want to practice DDL.

**Never commit, upload, email, or screenshot your real `.env` or `.streamlit/secrets.toml` file.** `.gitignore` excludes them. Configuration files are convenience tools, not encryption.

### D. Verify connectivity

```bash
python -m examples.ex01_show_config
python -m examples.ex02_test_connection
```

Expected shape of output (your host, username, and database may differ):

```text
host: localhost
port: 3306
user: chapter9_app
database: MyUniversityDB
Password is configured but deliberately not displayed.

Connected to MyUniversityDB on localhost:3306
Connection closed.
```

`ex02_test_connection` also explains access-denied or unknown-database errors. For Lab 2, briefly try an incorrect password/DB name, observe the response, and then **restore your correct `.env`**.

## 3. Run the Chapter 9 examples

Run these from the project root with the virtual environment activated.

| Chapter | Command | What to observe |
| --- | --- | --- |
| §9.1 | `python -m examples.ex01_show_config` | Loads environment variables without exposing password |
| §9.2 | `python -m examples.ex02_test_connection` | Opens and closes MySQL connection |
| §9.3.3 | `python -m examples.ex03_create_departments` | DDL and implicit commit; needs CREATE privilege |
| §9.3.4–9.3.5 | `python -m examples.ex04_department_crud` | `rowcount`, duplicate-key error, rollback, cleanup |
| §9.4 | `python -m examples.ex05_fetch_methods --id 2001 --batch-size 2` | Tuple/dict rows and fetch strategies |
| §9.5 | `python -m examples.ex06_transfer_funds 101 105 10.00` | Two updates commit as one transaction |
| §9.6.1 | `python -m examples.ex07_student_intake` | Interactive, parameterized student INSERT |
| §9.6.2 | `python -m examples.ex08_student_report --major "Computer Science"` | Dictionary cursor with a WHERE filter |
| GenAI tie-in | `python -m examples.ex09_structured_tools` | Fixed, limited read tool; JSON-like return object |
| Extra project | `python -m examples.ex10_atomic_advisor` | Importable two-table transaction example |

### Try rollback with a missing transfer receiver

First inspect account balances in MySQL Workbench:

```sql
SELECT StudentID, Balance FROM StudentAccounts ORDER BY StudentID;
```

Then run:

```bash
python -m examples.ex06_transfer_funds 101 999 10.00
```

Account `999` is intentionally absent. The sender's debit happens first, the receiver update affects **0 rows**, and `rollback()` should preserve the original balance of account `101`. Query `StudentAccounts` again to verify. This is a good demonstration of **atomicity**. Each *successful* run changes the demo account balances, so do not expect them to remain at the seeded values.

### Try paging and date filtering

```bash
python -m examples.ex08_student_report --page 1 --page-size 2
python -m examples.ex08_student_report --major "Computer Science" --from-date 2025-01-01
```

The reporting script issues `SELECT ... LIMIT %s OFFSET %s`, not `SELECT *` for the entire table. The fetch-method script demonstrates an **unbuffered** cursor with `fetchmany()`.

## 4. Start the Streamlit dashboard (§9.7)

From the package root:

```bash
python -m streamlit run streamlit_app.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`). Explore three tabs:

1. **Browse students:** search by name/email; filter by major; choose page size; export the current page to CSV.
2. **Add student:** validate name, email, and enrollment date; use a parameterized INSERT with commit/rollback.
3. **Manage student:** look up an ID, edit the major, or delete a student after typing the exact confirmation `DELETE`.

The dashboard uses a small **connection pool** rather than opening a new network connection on every rerun. The underlying repository **closes each borrowed connection**, returning it to the pool. `rowcount` reports how many rows changed (which can be zero when the new value equals the old one).

**Optional Streamlit credentials:** copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and edit its `[database]` section. If that file is present, the dashboard prefers its database settings over `.env`; console scripts still use `.env`. Otherwise, the dashboard also uses `.env`. Restart Streamlit after changing credentials; resource caches can retain old connections.

> **Security limitation:** This dashboard has no user authentication/authorization and exposes data-changing controls. Run it only on a trusted local machine or isolated classroom environment. A real deployed app needs authentication, finer permissions, audit logging, and an appropriate secrets-management system.

## 5. Check the code without MySQL

The standard-library unit tests **mock the database connection**, so they do not need a running MySQL server or a configured `.env`:

```bash
python -m unittest discover -s tests -v
```

They check date/field validation, parameterized-filter construction, pagination limits, and that success commits while failures roll back and close resources. The tests use `mysql-connector-python` imports, so install `requirements.txt` first.

You can also check Python syntax without starting MySQL:

```bash
python -m compileall -q db_config.py student_repository.py streamlit_app.py examples tests
```

**Important:** These tests do not replace a live end-to-end test with MySQL. For the full learning objectives, run the examples and dashboard against the teaching database and verify the expected table changes with SQL queries.

## 6. Chapter lessons and safe habits

- **Parameterize all values.** Use `WHERE StudentID = %s` with `(student_id,)`, not concatenation or Python string formatting of SQL values. Dynamic optional WHERE fragments in `student_repository.py` come only from fixed code, never from arbitrary user-supplied SQL.
- **Commit after successful DML; rollback on failure.** `db_session()` provides a consistent cleanup pattern. MySQL DDL has different implicit-commit rules, so treat CREATE/ALTER/DROP separately.
- **Close cursors and connections.** For pooled connections, `close()` *returns the connection to the pool*.
- **Do not assume a query changed data.** Always inspect `rowcount` on UPDATE/DELETE, and `lastrowid` for AUTO_INCREMENT inserts.
- **Use least-privilege MySQL users.** Even parameterized inputs cannot make an unrestricted AI-generated SQL statement safe. The `ex09_structured_tools` example uses only approved, fixed SQL operations and a hard cap on returned rows. It does **not** grant an LLM raw SQL access.
- **Validate with SQL.** Do not infer correctness from a success message alone. Query the tables before and after running scripts.

## 7. Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'mysql'` | Activate the venv and run `python -m pip install -r requirements.txt` |
| `Missing database setting(s)` | Create/edit `.env` in the project root; check variable names |
| `Access denied for user` | Correct DB_USER/password, verify MySQL permissions, check user host |
| `Unknown database` | Run the 00/01 SQL scripts and confirm DB_NAME |
| `Can't connect to MySQL server` | Start MySQL; verify DB_HOST and DB_PORT; inspect firewall/socket settings |
| `CREATE command denied` | Expected with the low-privilege `chapter9_app` account; run schema setup as an administrator |
| `Table '...Students' doesn't exist` | Run `sql/01_schema.sql` and make sure the active database is MyUniversityDB |
| `Duplicate entry ... for key ...Email` | The email is unique; enter another email, or query existing records |
| Streamlit shows an old connection or credentials | Stop/restart Streamlit to recreate its connection pool |
| PowerShell complains about `<` SQL redirection | Use MySQL Workbench or Windows Command Prompt instead |

## 8. Student experiments and lab activities

See **[LAB_GUIDE.md](LAB_GUIDE.md)** for the five practical labs corresponding to the end of Chapter 9, with suggested checks and extension challenges. Useful experiments include comparing `fetchmany(1)` versus `fetchmany(5)`, inserting duplicate emails, testing `rowcount == 0`, measuring the effects of pagination, and deliberately failing the *second* statement in a transaction to verify rollback.

## 9. Notes for instructors

- SQL setup is intentionally non-destructive and can be re-run. For a truly clean class reset, make a **fresh dedicated practice database** and reapply the schema/seed files; these scripts do not delete students' work.
- This is an instructional code package derived from Chapter 9's concepts and examples. Some examples are reorganized to share configuration and validation code, and the transfer uses `Decimal` to avoid binary floating-point issues.
- The optional `AdvisorAssignments` table and `ex10_atomic_advisor.py` support the chapter's multi-step transaction project question.
- No cloud LLM key, remote API calls, database migrations framework, or production authentication system is included; §9.8 is a conceptual preview rather than an ORM implementation.
