# core/context_processors.py
from .utils import get_afghan_date

def afghan_date(request):
    """Return today's date in Afghan calendar numeric format."""
    return {
        'afghan_date': get_afghan_date()
    }