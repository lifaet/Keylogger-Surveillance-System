def log_console(message, level="INFO"):
    levels = {
        "INFO": "[INFO]",
        "ERROR": "[ERROR]",
        "SUCCESS": "[SUCCESS]",
        "WARNING": "[WARNING]"
    }
    prefix = levels.get(level.upper(), "[*]")
    print(f"{prefix} {message}")