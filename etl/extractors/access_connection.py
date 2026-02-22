"""
Access database connection management.

Provides secure, read-only connections to legacy Access databases.
All connections are explicitly read-only to prevent accidental modifications.

Note: pyodbc is imported lazily to allow the application to run on systems
without ODBC drivers (e.g., Railway Linux deployment).
"""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Lazy import: pyodbc may not be available on all platforms (e.g., Railway Linux)
# Import only for type hints, actual import happens in functions that need it
if TYPE_CHECKING:
    import pyodbc

logger = logging.getLogger(__name__)

# Module-level cache for pyodbc availability
_pyodbc_module: Optional[Any] = None
_pyodbc_checked: bool = False


def _get_pyodbc() -> Optional[Any]:
    """
    Lazily import pyodbc module.
    
    Returns:
        pyodbc module if available, None otherwise.
    """
    global _pyodbc_module, _pyodbc_checked
    
    if _pyodbc_checked:
        return _pyodbc_module
    
    try:
        import pyodbc as _pyodbc
        _pyodbc_module = _pyodbc
    except ImportError:
        logger.debug("pyodbc not available - Access database support disabled")
        _pyodbc_module = None
    
    _pyodbc_checked = True
    return _pyodbc_module


class AccessConnectionError(Exception):
    """Raised when Access database connection fails."""

    pass


def _get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable value."""
    return os.environ.get(name, default)


def _get_access_driver() -> Optional[str]:
    """
    Get the Access ODBC driver name.
    
    Returns:
        Driver name if available, None otherwise.
    """
    pyodbc = _get_pyodbc()
    if pyodbc is None:
        return None
    
    # Check if user specified a driver
    user_driver = _get_env_var("LEGACY_ACCESS_ODBC_DRIVER")
    if user_driver:
        available_drivers = pyodbc.drivers()
        if user_driver in available_drivers:
            return user_driver
        logger.warning(f"Specified driver '{user_driver}' not found in system")
        return None

    # Try to find a suitable Access driver
    available_drivers = pyodbc.drivers()
    access_drivers = [d for d in available_drivers if "Access" in d and ".accdb" in d]
    
    if access_drivers:
        return access_drivers[0]
    
    return None


def is_access_available() -> bool:
    """
    Check if Access database connection is available.
    
    Checks:
    1. pyodbc module is available
    2. Required environment variables are set (path is required)
    3. Password is set (required for protected databases)
    4. Database file exists
    5. ODBC driver is installed
    
    Returns:
        True if all requirements are met, False otherwise.
    """
    # Check pyodbc availability first
    if _get_pyodbc() is None:
        logger.debug("Access connection not available: pyodbc not installed")
        return False
    
    # Check environment variables (only path is required)
    db_path = _get_env_var("LEGACY_ACCESS_DB_PATH")
    
    if not db_path:
        logger.debug("Access connection not configured: LEGACY_ACCESS_DB_PATH not set")
        return False
    
    # Check file exists
    path_obj = Path(db_path)
    if not path_obj.is_absolute():
        path_obj = Path.cwd() / db_path
    
    if not path_obj.exists():
        logger.debug(f"Access database file not found: {path_obj}")
        return False
    
    # Check driver availability
    driver = _get_access_driver()
    if not driver:
        logger.debug("No suitable Access ODBC driver found")
        return False
    
    # Check password (required for protected databases)
    password = _get_env_var("LEGACY_ACCESS_DB_PASSWORD")
    if not password:
        logger.debug("Access database password not set (LEGACY_ACCESS_DB_PASSWORD)")
        return False
    
    return True


def get_access_connection() -> "pyodbc.Connection":
    """
    Get a read-only connection to the Access database.
    
    The connection is configured with:
    - ReadOnly=1: Prevents any write operations
    - PWD: Database password from environment (optional)
    
    Returns:
        pyodbc.Connection object
        
    Raises:
        AccessConnectionError: If connection cannot be established
    """
    pyodbc = _get_pyodbc()
    if pyodbc is None:
        raise AccessConnectionError(
            "pyodbc is not available. Access database support requires pyodbc "
            "and ODBC drivers, which are not available on this platform."
        )
    
    # Get configuration
    db_path = _get_env_var("LEGACY_ACCESS_DB_PATH")
    db_password = _get_env_var("LEGACY_ACCESS_DB_PASSWORD", "")  # Optional
    
    if not db_path:
        raise AccessConnectionError(
            "Access database not configured. Set LEGACY_ACCESS_DB_PATH "
            "environment variable."
        )
    
    # Resolve path
    db_path_resolved = Path(db_path)
    if not db_path_resolved.is_absolute():
        db_path_resolved = Path.cwd() / db_path
    
    if not db_path_resolved.exists():
        raise AccessConnectionError(
            f"Access database file not found: {db_path_resolved}"
        )
    
    # Get driver
    driver = _get_access_driver()
    if not driver:
        raise AccessConnectionError(
            "No suitable Access ODBC driver found. Install Microsoft Access "
            "Database Engine (ACE) from: "
            "https://www.microsoft.com/en-us/download/details.aspx?id=54920"
        )
    
    # Build connection string
    # ReadOnly=1 ensures we never modify the legacy database
    conn_string = (
        f"DRIVER={{{driver}}};"
        f"DBQ={db_path_resolved};"
        f"ReadOnly=1;"
    )
    
    # Add password only if provided
    if db_password:
        conn_string += f"PWD={db_password};"
    
    try:
        logger.info(f"Connecting to Access database: {db_path_resolved.name}")
        connection = pyodbc.connect(conn_string)
        logger.info("Access database connection established (read-only)")
        return connection
    except pyodbc.Error as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "password" in error_msg.lower():
            raise AccessConnectionError(
                "Authentication failed for Access database. Check password."
            ) from e
        raise AccessConnectionError(
            f"Failed to connect to Access database: {error_msg}"
        ) from e
    except Exception as e:
        raise AccessConnectionError(
            f"Failed to connect to Access database: {e}"
        ) from e
