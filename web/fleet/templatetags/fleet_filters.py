"""
Custom template filters for fleet module display.

Provides European number formatting (dot as thousands separator).
"""

from django import template

register = template.Library()


@register.filter
def euro_number(value):
    """
    Format a number with European style (dot as thousands separator).
    
    Examples:
        13826 -> "13.826"
        1294221 -> "1.294.221"
        0 -> "0"
    
    Args:
        value: Number to format (int or float)
        
    Returns:
        Formatted string with dots as thousands separators
    """
    if value is None:
        return "0"
    
    try:
        # Convert to int to remove decimals
        num = int(value)
        # Format with dots as thousands separator
        return f"{num:,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)


@register.filter
def divide(value, divisor):
    """
    Divide a number by a divisor.
    
    Examples:
        12000|divide:30 -> 400
    
    Args:
        value: Number to divide
        divisor: Number to divide by
        
    Returns:
        Integer result of division, or 0 if invalid
    """
    if value is None or divisor is None:
        return 0
    
    try:
        num = int(value)
        div = int(divisor)
        if div == 0:
            return 0
        return num // div
    except (ValueError, TypeError):
        return 0
