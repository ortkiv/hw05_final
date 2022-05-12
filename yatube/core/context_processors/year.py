from typing import Dict

from django.http import HttpRequest
from django.utils import timezone


def year(request: HttpRequest) -> Dict[str, int]:
    """Добавляет переменную с текущим годом."""
    year = timezone.now().strftime("%Y")
    return {
        'year': year
    }
