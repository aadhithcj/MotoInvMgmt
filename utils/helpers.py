import re
import datetime

def clean_number(value):
    """
    Cleans a string representation of a number and returns a float.
    Removes currency symbols, commas, and spaces.
    Returns 0.0 if parsing fails.
    """
    if not value:
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
        
    value_str = str(value)
    # Remove everything except digits, decimal point, and minus sign
    cleaned = re.sub(r'[^\d.-]', '', value_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def clean_quantity(value):
    """
    Cleans a quantity string and returns an integer.
    """
    if not value:
        return 0
    
    if isinstance(value, (int, float)):
        return int(value)
        
    value_str = str(value)
    cleaned = re.sub(r'[^\d.-]', '', value_str)
    try:
        return int(float(cleaned))
    except ValueError:
        return 0

def format_currency(value):
    return f"₹ {float(value):,.2f}"

def format_date(date_str):
    if not date_str:
        return ""
    # Truncate time if exists
    return date_str.split(' ')[0]

def parse_date(text):
    """Attempts to find and parse a date from a text block."""
    if not text:
        return None
    # Look for DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
    match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', text)
    if match:
        day, month, year = match.groups()
        # Basic sanity check
        if len(year) == 4:
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
    match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', text)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
    return datetime.date.today().strftime('%Y-%m-%d')
