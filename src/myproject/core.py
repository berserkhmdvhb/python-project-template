"""Core logic for myproject."""


def sanitize_input(value: str | None) -> str:
    """
    Sanitize user input to ensure it's non-empty and not just whitespace.

    Args:
        value: Input string, possibly None or empty.

    Returns:
        A stripped, validated string.

    Raises:
        ValueError: If input is None or contains only whitespace.
    """
    if value is None or not value.strip():
        raise ValueError("Query string cannot be empty.")
    return value.strip()


def process_query(query: str | None) -> str:
    """
    Process the sanitized input query and return a result.

    Args:
        query: Raw user input.

    Returns:
        A safely formatted string based on the query.
    """
    clean_query = sanitize_input(query)
    # Placeholder logic — replace with real implementation
    return f"Processed query: {clean_query}"


def example_hello() -> str:
    """
    Dummy function for template demonstration purposes.

    Returns:
        A static greeting string.
    """
    return "Hello from core!"
