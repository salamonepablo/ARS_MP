"""
Microsoft Access database introspection tool.

This module provides functionality to extract metadata from Microsoft Access
databases (.mdb and .accdb files) in read-only mode, generating CSV and
Markdown documentation of the database schema.

Usage:
    py -m etl.extractors.access_introspect --db "path/to/db.accdb" --out "output/dir"
"""

import argparse
import csv
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyodbc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class TableInfo:
    """Represents metadata for a database table."""

    name: str
    table_type: str
    remarks: str | None = None


@dataclass
class ColumnInfo:
    """Represents metadata for a table column."""

    table_name: str
    column_name: str
    data_type: str
    type_name: str
    column_size: int | None
    nullable: bool
    ordinal_position: int
    default_value: str | None = None
    remarks: str | None = None


@dataclass
class IndexInfo:
    """Represents metadata for a table index."""

    table_name: str
    index_name: str | None
    column_name: str
    is_unique: bool
    ordinal_position: int
    index_type: str | None = None


@dataclass
class RelationshipInfo:
    """Represents a foreign key relationship."""

    pk_table: str
    pk_column: str
    fk_table: str
    fk_column: str
    fk_name: str | None = None
    pk_name: str | None = None


@dataclass
class QueryInfo:
    """Represents a saved query/view."""

    name: str
    query_type: str
    remarks: str | None = None


@dataclass
class DatabaseSchema:
    """Complete schema information for a database."""

    db_path: Path
    db_name: str
    tables: list[TableInfo] = field(default_factory=list)
    columns: list[ColumnInfo] = field(default_factory=list)
    indexes: list[IndexInfo] = field(default_factory=list)
    relationships: list[RelationshipInfo] = field(default_factory=list)
    queries: list[QueryInfo] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# =============================================================================
# Database Introspection
# =============================================================================


def get_connection_string(db_path: Path) -> str:
    """
    Build ODBC connection string for Access database.

    Args:
        db_path: Path to the Access database file.

    Returns:
        ODBC connection string with read-only mode.
    """
    driver = "Microsoft Access Driver (*.mdb, *.accdb)"
    return (
        f"DRIVER={{{driver}}};"
        f"DBQ={db_path.resolve()};"
        f"ReadOnly=1;"
    )


def extract_tables(cursor: pyodbc.Cursor) -> list[TableInfo]:
    """
    Extract table metadata from database.

    Args:
        cursor: Active database cursor.

    Returns:
        List of TableInfo objects for all user tables.
    """
    tables = []

    # Get regular tables
    for row in cursor.tables(tableType="TABLE"):
        tables.append(
            TableInfo(
                name=row.table_name,
                table_type=row.table_type,
                remarks=row.remarks,
            )
        )

    return tables


def extract_queries(cursor: pyodbc.Cursor) -> list[QueryInfo]:
    """
    Extract saved queries/views from database.

    Args:
        cursor: Active database cursor.

    Returns:
        List of QueryInfo objects for saved queries.
    """
    queries = []

    # Try to get views (Access queries appear as views in ODBC)
    try:
        for row in cursor.tables(tableType="VIEW"):
            queries.append(
                QueryInfo(
                    name=row.table_name,
                    query_type=row.table_type,
                    remarks=row.remarks,
                )
            )
    except pyodbc.Error as e:
        logger.warning(f"Could not extract queries: {e}")

    return queries


def extract_columns(cursor: pyodbc.Cursor, table_name: str) -> list[ColumnInfo]:
    """
    Extract column metadata for a specific table.

    Args:
        cursor: Active database cursor.
        table_name: Name of the table to inspect.

    Returns:
        List of ColumnInfo objects for all columns in the table.
    """
    columns = []

    try:
        for row in cursor.columns(table=table_name):
            columns.append(
                ColumnInfo(
                    table_name=row.table_name,
                    column_name=row.column_name,
                    data_type=str(row.data_type),
                    type_name=row.type_name,
                    column_size=row.column_size,
                    nullable=row.nullable == 1,
                    ordinal_position=row.ordinal_position,
                    default_value=row.column_def,
                    remarks=row.remarks,
                )
            )
    except pyodbc.Error as e:
        logger.warning(f"Could not extract columns for {table_name}: {e}")

    return columns


def extract_indexes(cursor: pyodbc.Cursor, table_name: str) -> list[IndexInfo]:
    """
    Extract index metadata for a specific table.

    Args:
        cursor: Active database cursor.
        table_name: Name of the table to inspect.

    Returns:
        List of IndexInfo objects for all indexes on the table.
    """
    indexes = []

    try:
        # Get all indexes (unique and non-unique)
        for row in cursor.statistics(table=table_name, unique=False):
            # Skip table statistics rows (when index_name is None and type is 0)
            if row.index_name is None and row.type == 0:
                continue

            indexes.append(
                IndexInfo(
                    table_name=row.table_name,
                    index_name=row.index_name,
                    column_name=row.column_name or "",
                    is_unique=not row.non_unique if row.non_unique is not None else False,
                    ordinal_position=row.ordinal_position or 0,
                    index_type=_get_index_type_name(row.type),
                )
            )
    except pyodbc.Error as e:
        logger.warning(f"Could not extract indexes for {table_name}: {e}")

    return indexes


def _get_index_type_name(type_code: int | None) -> str:
    """Convert ODBC index type code to human-readable name."""
    type_map = {
        0: "STATISTIC",
        1: "CLUSTERED",
        2: "HASHED",
        3: "OTHER",
    }
    return type_map.get(type_code, "UNKNOWN") if type_code is not None else "UNKNOWN"


def extract_relationships(
    cursor: pyodbc.Cursor, table_name: str
) -> list[RelationshipInfo]:
    """
    Extract foreign key relationships for a specific table.

    Args:
        cursor: Active database cursor.
        table_name: Name of the table to inspect.

    Returns:
        List of RelationshipInfo objects for foreign keys.

    Note:
        Access ODBC driver may have limited support for this.
    """
    relationships = []

    try:
        # Get foreign keys where this table is the FK table
        for row in cursor.foreignKeys(foreignTable=table_name):
            relationships.append(
                RelationshipInfo(
                    pk_table=row.pktable_name,
                    pk_column=row.pkcolumn_name,
                    fk_table=row.fktable_name,
                    fk_column=row.fkcolumn_name,
                    fk_name=row.fk_name,
                    pk_name=row.pk_name,
                )
            )
    except (pyodbc.Error, AttributeError) as e:
        logger.debug(f"Could not extract foreign keys for {table_name}: {e}")

    try:
        # Also get foreign keys where this table is the PK table
        for row in cursor.foreignKeys(table=table_name):
            rel = RelationshipInfo(
                pk_table=row.pktable_name,
                pk_column=row.pkcolumn_name,
                fk_table=row.fktable_name,
                fk_column=row.fkcolumn_name,
                fk_name=row.fk_name,
                pk_name=row.pk_name,
            )
            # Avoid duplicates
            if rel not in relationships:
                relationships.append(rel)
    except (pyodbc.Error, AttributeError) as e:
        logger.debug(f"Could not extract primary key refs for {table_name}: {e}")

    return relationships


def introspect_database(db_path: Path) -> DatabaseSchema:
    """
    Perform full introspection of an Access database.

    Args:
        db_path: Path to the Access database file.

    Returns:
        DatabaseSchema object containing all extracted metadata.

    Raises:
        FileNotFoundError: If the database file doesn't exist.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    schema = DatabaseSchema(
        db_path=db_path,
        db_name=db_path.stem,
    )

    conn_str = get_connection_string(db_path)
    logger.info(f"Connecting to: {db_path.name}")

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            # Extract tables
            schema.tables = extract_tables(cursor)
            logger.info(f"  Found {len(schema.tables)} tables")

            # Extract queries/views
            schema.queries = extract_queries(cursor)
            logger.info(f"  Found {len(schema.queries)} queries/views")

            # Extract columns, indexes, and relationships for each table
            for table in schema.tables:
                cols = extract_columns(cursor, table.name)
                schema.columns.extend(cols)

                idxs = extract_indexes(cursor, table.name)
                schema.indexes.extend(idxs)

                rels = extract_relationships(cursor, table.name)
                schema.relationships.extend(rels)

            logger.info(f"  Found {len(schema.columns)} columns")
            logger.info(f"  Found {len(schema.indexes)} index entries")
            logger.info(f"  Found {len(schema.relationships)} relationships")

    except pyodbc.Error as e:
        error_msg = f"Failed to connect to {db_path.name}: {e}"
        logger.error(error_msg)
        schema.errors.append(error_msg)

    return schema


# =============================================================================
# Output Generation
# =============================================================================


def write_tables_csv(schema: DatabaseSchema, output_dir: Path) -> None:
    """Write tables metadata to CSV file."""
    filepath = output_dir / "tables.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["table_name", "table_type", "remarks"])
        for table in schema.tables:
            writer.writerow([table.name, table.table_type, table.remarks or ""])
    logger.debug(f"  Wrote {filepath}")


def write_columns_csv(schema: DatabaseSchema, output_dir: Path) -> None:
    """Write columns metadata to CSV file."""
    filepath = output_dir / "columns.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "table_name",
            "column_name",
            "data_type",
            "type_name",
            "column_size",
            "nullable",
            "ordinal_position",
            "default_value",
            "remarks",
        ])
        for col in schema.columns:
            writer.writerow([
                col.table_name,
                col.column_name,
                col.data_type,
                col.type_name,
                col.column_size or "",
                col.nullable,
                col.ordinal_position,
                col.default_value or "",
                col.remarks or "",
            ])
    logger.debug(f"  Wrote {filepath}")


def write_indexes_csv(schema: DatabaseSchema, output_dir: Path) -> None:
    """Write indexes metadata to CSV file."""
    filepath = output_dir / "indexes.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "table_name",
            "index_name",
            "column_name",
            "is_unique",
            "ordinal_position",
            "index_type",
        ])
        for idx in schema.indexes:
            writer.writerow([
                idx.table_name,
                idx.index_name or "",
                idx.column_name,
                idx.is_unique,
                idx.ordinal_position,
                idx.index_type or "",
            ])
    logger.debug(f"  Wrote {filepath}")


def write_relationships_csv(schema: DatabaseSchema, output_dir: Path) -> None:
    """Write relationships metadata to CSV file."""
    filepath = output_dir / "relationships.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pk_table",
            "pk_column",
            "fk_table",
            "fk_column",
            "fk_name",
            "pk_name",
        ])
        for rel in schema.relationships:
            writer.writerow([
                rel.pk_table,
                rel.pk_column,
                rel.fk_table,
                rel.fk_column,
                rel.fk_name or "",
                rel.pk_name or "",
            ])
    logger.debug(f"  Wrote {filepath}")


def write_queries_csv(schema: DatabaseSchema, output_dir: Path) -> None:
    """Write queries/views metadata to CSV file."""
    filepath = output_dir / "queries.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query_name", "query_type", "remarks"])
        for query in schema.queries:
            writer.writerow([query.name, query.query_type, query.remarks or ""])
    logger.debug(f"  Wrote {filepath}")


def write_summary_md(schema: DatabaseSchema, output_dir: Path) -> None:
    """Write human-readable summary in Markdown format."""
    filepath = output_dir / "summary.md"

    # Identify potential primary keys (unique indexes named PrimaryKey or similar)
    pk_candidates: dict[str, list[str]] = {}
    for idx in schema.indexes:
        if idx.is_unique and idx.index_name:
            idx_name_lower = idx.index_name.lower()
            if "primarykey" in idx_name_lower or "pk" in idx_name_lower:
                if idx.table_name not in pk_candidates:
                    pk_candidates[idx.table_name] = []
                pk_candidates[idx.table_name].append(idx.column_name)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Database Schema: {schema.db_name}\n\n")
        f.write(f"**Source file:** `{schema.db_path.name}`\n\n")

        # Summary stats
        f.write("## Summary\n\n")
        f.write(f"- **Tables:** {len(schema.tables)}\n")
        f.write(f"- **Queries/Views:** {len(schema.queries)}\n")
        f.write(f"- **Total Columns:** {len(schema.columns)}\n")
        f.write(f"- **Index Entries:** {len(schema.indexes)}\n")
        f.write(f"- **Relationships:** {len(schema.relationships)}\n")
        f.write("\n")

        # Errors if any
        if schema.errors:
            f.write("## Errors\n\n")
            for error in schema.errors:
                f.write(f"- {error}\n")
            f.write("\n")

        # Tables detail
        f.write("## Tables\n\n")
        if schema.tables:
            for table in schema.tables:
                f.write(f"### {table.name}\n\n")

                # Get columns for this table
                table_cols = [c for c in schema.columns if c.table_name == table.name]
                if table_cols:
                    f.write("| Column | Type | Size | Nullable | Default |\n")
                    f.write("|--------|------|------|----------|--------|\n")
                    for col in sorted(table_cols, key=lambda x: x.ordinal_position):
                        size = col.column_size if col.column_size else "-"
                        nullable = "YES" if col.nullable else "NO"
                        default = col.default_value if col.default_value else "-"
                        f.write(
                            f"| {col.column_name} | {col.type_name} | {size} | "
                            f"{nullable} | {default} |\n"
                        )
                    f.write("\n")

                # Primary key candidates
                if table.name in pk_candidates:
                    f.write(f"**Primary Key (inferred):** {', '.join(pk_candidates[table.name])}\n\n")

                # Indexes for this table
                table_idxs = [i for i in schema.indexes if i.table_name == table.name]
                if table_idxs:
                    f.write("**Indexes:**\n")
                    # Group by index name
                    idx_groups: dict[str, list[IndexInfo]] = {}
                    for idx in table_idxs:
                        key = idx.index_name or "(unnamed)"
                        if key not in idx_groups:
                            idx_groups[key] = []
                        idx_groups[key].append(idx)

                    for idx_name, idx_list in idx_groups.items():
                        cols = [i.column_name for i in sorted(idx_list, key=lambda x: x.ordinal_position)]
                        unique_str = "UNIQUE" if idx_list[0].is_unique else ""
                        f.write(f"- `{idx_name}` ({', '.join(cols)}) {unique_str}\n")
                    f.write("\n")
        else:
            f.write("No tables found.\n\n")

        # Queries
        if schema.queries:
            f.write("## Queries/Views\n\n")
            for query in schema.queries:
                f.write(f"- **{query.name}** ({query.query_type})\n")
            f.write("\n")

        # Relationships
        if schema.relationships:
            f.write("## Relationships\n\n")
            f.write("| FK Table | FK Column | PK Table | PK Column | FK Name |\n")
            f.write("|----------|-----------|----------|-----------|----------|\n")
            for rel in schema.relationships:
                f.write(
                    f"| {rel.fk_table} | {rel.fk_column} | {rel.pk_table} | "
                    f"{rel.pk_column} | {rel.fk_name or '-'} |\n"
                )
            f.write("\n")

    logger.debug(f"  Wrote {filepath}")


def export_schema(schema: DatabaseSchema, output_base: Path) -> Path:
    """
    Export all schema information to files.

    Args:
        schema: DatabaseSchema object to export.
        output_base: Base output directory.

    Returns:
        Path to the database-specific output directory.
    """
    # Create output directory for this database
    output_dir = output_base / schema.db_name
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting schema to: {output_dir}")

    write_tables_csv(schema, output_dir)
    write_columns_csv(schema, output_dir)
    write_indexes_csv(schema, output_dir)
    write_relationships_csv(schema, output_dir)
    write_queries_csv(schema, output_dir)
    write_summary_md(schema, output_dir)

    return output_dir


# =============================================================================
# CLI Interface
# =============================================================================


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Introspect Microsoft Access databases and export schema metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py -m etl.extractors.access_introspect --db "path/to/db.accdb" --out "docs/introspection"
  py -m etl.extractors.access_introspect --db "db1.mdb" --db "db2.accdb" --out "output"
        """,
    )
    parser.add_argument(
        "--db",
        action="append",
        required=True,
        dest="databases",
        metavar="PATH",
        help="Path to Access database file (can be specified multiple times)",
    )
    parser.add_argument(
        "--out",
        required=True,
        dest="output_dir",
        metavar="DIR",
        help="Output directory for generated files",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """
    Main entry point for the introspection tool.

    Args:
        args: Command line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    parsed = parse_args(args)

    if parsed.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    output_base = Path(parsed.output_dir)
    output_base.mkdir(parents=True, exist_ok=True)

    schemas: list[DatabaseSchema] = []
    errors_count = 0

    for db_path_str in parsed.databases:
        db_path = Path(db_path_str)

        try:
            schema = introspect_database(db_path)
            schemas.append(schema)
            export_schema(schema, output_base)

            if schema.errors:
                errors_count += len(schema.errors)

        except FileNotFoundError as e:
            logger.error(str(e))
            errors_count += 1
        except Exception as e:
            logger.error(f"Unexpected error processing {db_path}: {e}")
            errors_count += 1

    # Print summary
    logger.info("=" * 60)
    logger.info("INTROSPECTION COMPLETE")
    logger.info(f"  Databases processed: {len(schemas)}")
    logger.info(f"  Total tables: {sum(len(s.tables) for s in schemas)}")
    logger.info(f"  Total columns: {sum(len(s.columns) for s in schemas)}")
    logger.info(f"  Output directory: {output_base.resolve()}")
    if errors_count:
        logger.warning(f"  Errors encountered: {errors_count}")

    return 1 if errors_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
