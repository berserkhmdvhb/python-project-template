def dummy_function() -> str:
    return "Hello from core!"


def sanitize_input(value: str | None) -> str:
    """
    Ensure the input string is not None or empty.
    Raise ValueError for invalid cases.
    """
    if value is None or not value.strip():
        raise ValueError("Query string cannot be empty.")
    return value.strip()


def process_query(query: str | None) -> str:
    """
    Example core function that sanitizes and processes a query.
    """
    clean_query = sanitize_input(query)
    # Dummy logic — replace this with actual processing later
    return f"Processed query: {clean_query}"
