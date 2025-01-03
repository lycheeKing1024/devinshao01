from datetime import datetime, date
from typing import Optional

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

async def verify_age(birth_date_str: str, minimum_age: int = 21) -> bool:
    """Verify user meets minimum age requirement."""
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        return calculate_age(birth_date) >= minimum_age
    except ValueError:
        return False
