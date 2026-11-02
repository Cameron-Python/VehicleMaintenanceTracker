"""Lab 1 / §9.1.4: load nonsecret settings without printing the password."""

from db_config import load_db_config


def main():
    config = load_db_config()
    for name in ("host", "port", "user", "database"):
        print(f"{name}: {config[name]}")
    print("Password is configured but deliberately not displayed.")


if __name__ == "__main__":
    main()
