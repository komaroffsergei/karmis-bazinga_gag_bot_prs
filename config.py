from configparser import ConfigParser
import os


def config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    values = dict(parser.items(section)) if parser.has_section(section) else {}
    for key, variable in {"host": "DB_HOST", "database": "DB_DATABASE", "user": "DB_USER", "password": "DB_PASSWORD"}.items():
        if variable in os.environ:
            values[key] = os.environ[variable]
    missing = [key for key in ("host", "database", "user", "password") if not values.get(key)]
    if missing:
        raise ValueError("Configure database.ini or DB_* environment variables; missing: " + ", ".join(missing))
    return values
