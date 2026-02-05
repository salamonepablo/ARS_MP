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
