from datetime import datetime

def parse_date(date_string):
    """
    Tenta converter uma string de data em diferentes formatos para o formato brasileiro.
    """
    if date_string is None:
        raise ValueError("Date format not recognized: None")
    
    date_string = date_string.strip()  # Remove leading/trailing whitespace

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_string, fmt).strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue

    raise ValueError(f"Date format not recognized: {date_string}")