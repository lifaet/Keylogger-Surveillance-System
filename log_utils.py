def log_console(message, level="INFO"):
    levels = {
        "INFO": "[*]",
        "ERROR": "[!]",
        "SUCCESS": "[+]",
        "WARNING": "[!]"
    }
    prefix = levels.get(level.upper(), "[*]")
    print(f"{prefix} {message}")