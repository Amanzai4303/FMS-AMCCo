# core/utils.py
import jdatetime
from datetime import date, datetime


def get_afghan_date():
    """Return today's date as 'day/month/year' in Afghan calendar, e.g. '31/3/1404'."""
    today = jdatetime.date.today()
    return f"{today.day}/{today.month}/{today.year}"


def gregorian_to_afghan_date(greg_date):
    """
    Convert a Gregorian date to Afghan calendar string.
    Returns format: 'day/month/year' e.g. '15/4/1404'
    """
    if greg_date is None:
        return "—"
    
    if isinstance(greg_date, str):
        try:
            greg_date = date.fromisoformat(greg_date)
        except (ValueError, TypeError):
            return str(greg_date)
    
    if isinstance(greg_date, (date, datetime)):
        try:
            afg_date = jdatetime.date.fromgregorian(date=greg_date)
            return f"{afg_date.day}/{afg_date.month}/{afg_date.year}"
        except Exception:
            return str(greg_date)
    
    return str(greg_date)