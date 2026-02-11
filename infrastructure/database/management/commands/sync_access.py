"""
Management command to sync data from legacy Access database into PostgreSQL staging tables.

Usage examples::

    # Sync all tables (full reload)
    python manage.py sync_access

    # Sync specific tables
    python manage.py sync_access --tables modulos kilometrajes

    # Full reload (delete + re-insert, default behaviour)
    python manage.py sync_access --full

    # Incremental sync for kilometrajes and ot_simaf (append new rows only)
    python manage.py sync_access --tables kilometrajes ot_simaf --incremental

Available table names:
    modulos, kilometrajes, ot_simaf, coches, formaciones
"""

import hashlib
import io
import logging
import time
from datetime import date, datetime
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from etl.extractors.access_connection import (
    AccessConnectionError,
    get_access_connection,
    is_access_available,
)
from infrastructure.database.models import (
    StgCoche,
    StgFormacionModulo,
    StgKilometraje,
    StgModulo,
    StgOtSimaf,
    SyncLog,
)

logger = logging.getLogger("etl")

# ---------------------------------------------------------------------------
# SQL queries for bulk extraction (full table scans)
# ---------------------------------------------------------------------------

SQL_ALL_MODULES = """
SELECT
    m.Id_Módulos,
    m.Módulos,
    m.Clase_Vehículos,
    cv.Tipo_MR,
    cv.Marca_MR
FROM A_00_Módulos m
LEFT JOIN A_00_Clase_Vehículo cv ON m.Clase_Vehículos = cv.Id_Clase_Vehículo
ORDER BY m.Módulos
"""

SQL_ALL_KILOMETRAJES = """
SELECT
    k.[Módulo]      AS ModuloId,
    k.Fecha,
    k.kilometraje
FROM A_00_Kilometrajes AS k
WHERE k.kilometraje IS NOT NULL
ORDER BY k.[Módulo], k.Fecha
"""

SQL_KILOMETRAJES_SINCE = """
SELECT
    k.[Módulo]      AS ModuloId,
    k.Fecha,
    k.kilometraje
FROM A_00_Kilometrajes AS k
WHERE k.kilometraje IS NOT NULL
  AND k.Fecha >= ?
ORDER BY k.[Módulo], k.Fecha
"""

SQL_ALL_OT_SIMAF = """
SELECT
    ot.[Módulo]     AS ModuloId,
    ot.Tipo_Tarea,
    ot.Tarea,
    ot.Km,
    ot.Fecha_Inicio,
    ot.Fecha_Fin,
    ot.OT_SIMAF
FROM A_00_OT_Simaf AS ot
ORDER BY ot.[Módulo], ot.Fecha_Fin
"""

SQL_OT_SIMAF_SINCE = """
SELECT
    ot.[Módulo]     AS ModuloId,
    ot.Tipo_Tarea,
    ot.Tarea,
    ot.Km,
    ot.Fecha_Inicio,
    ot.Fecha_Fin,
    ot.OT_SIMAF
FROM A_00_OT_Simaf AS ot
WHERE ot.Fecha_Fin >= ?
ORDER BY ot.[Módulo], ot.Fecha_Fin
"""

SQL_ALL_COCHES = """
SELECT
    c.Coche,
    c.[Posición]    AS Posicion,
    c.Ubicación     AS Ubicacion,
    c.Descripción   AS Descripcion
FROM A_00_Coches AS c
ORDER BY c.Coche
"""

SQL_ALL_FORMACIONES = """
SELECT
    f.[Módulo]      AS ModuloId,
    f.Coches        AS Coche
FROM A_14_Estado_Formaciones_Consulta AS f
ORDER BY f.[Módulo], f.Coches
"""

VALID_TABLES = ("modulos", "kilometrajes", "ot_simaf", "coches", "formaciones")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(value: Any) -> Optional[date]:
    """Convert Access date value to Python date (or None)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _safe_str(value: Any) -> str:
    """Convert value to stripped string, or empty string if None."""
    if value is None:
        return ""
    return str(value).strip()


def _safe_int(value: Any) -> Optional[int]:
    """Convert value to int, or None."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _ot_row_hash(modulo_id: int, tarea: str, fecha_fin: Optional[date],
                 km: Optional[int], fecha_inicio: Optional[date],
                 ot_simaf: str) -> str:
    """
    Compute a stable MD5 hash for deduplication of OT rows.

    Fields included: modulo_access_id, tarea, fecha_fin, km, fecha_inicio, ot_simaf.
    """
    parts = [
        str(modulo_id),
        tarea,
        str(fecha_fin) if fecha_fin else "",
        str(km) if km is not None else "",
        str(fecha_inicio) if fecha_inicio else "",
        ot_simaf,
    ]
    raw = "|".join(parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Sync data from legacy Access database into PostgreSQL staging tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tables",
            nargs="+",
            choices=VALID_TABLES,
            default=None,
            help="Specific tables to sync (default: all). "
                 f"Choices: {', '.join(VALID_TABLES)}",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            default=True,
            help="Full reload: delete existing rows and re-insert (default).",
        )
        parser.add_argument(
            "--incremental",
            action="store_true",
            default=False,
            help="Incremental sync: only insert/update rows newer than "
                 "the latest existing record. Applies to kilometrajes and "
                 "ot_simaf only; other tables always do full reload.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Read from Access and report counts, but do not write to Postgres.",
        )

    def handle(self, *args, **options):
        tables = options["tables"] or list(VALID_TABLES)
        incremental = options["incremental"]
        dry_run = options["dry_run"]

        if incremental:
            full = False
        else:
            full = True

        if not is_access_available():
            raise CommandError(
                "Access database is not available. Check LEGACY_ACCESS_DB_PATH, "
                "LEGACY_ACCESS_DB_PASSWORD, and ODBC driver installation."
            )

        # Create SyncLog entry
        sync_log = SyncLog.objects.create(
            started_at=timezone.now(),
            status="running",
        )
        log_buffer = io.StringIO()

        def _log(msg: str) -> None:
            """Write to stdout AND capture in buffer for SyncLog."""
            self.stdout.write(msg)
            log_buffer.write(msg + "\n")

        _log(
            f"sync_access: tables={tables}, full={full}, "
            f"incremental={incremental}, dry_run={dry_run}"
        )

        try:
            conn = get_access_connection()
        except AccessConnectionError as e:
            sync_log.status = "failed"
            sync_log.finished_at = timezone.now()
            sync_log.error_message = str(e)
            sync_log.log_output = log_buffer.getvalue()
            sync_log.save()
            raise CommandError(f"Cannot connect to Access: {e}")

        total_start = time.monotonic()
        results: dict[str, tuple[int, float]] = {}
        had_errors = False

        try:
            cursor = conn.cursor()

            for table in tables:
                t0 = time.monotonic()
                try:
                    count = self._sync_table(
                        table, cursor, full=full,
                        incremental=incremental, dry_run=dry_run,
                    )
                    elapsed = time.monotonic() - t0
                    results[table] = (count, elapsed)
                    _log(f"  {table}: {count} rows synced in {elapsed:.1f}s")
                except Exception as e:
                    elapsed = time.monotonic() - t0
                    results[table] = (-1, elapsed)
                    had_errors = True
                    logger.exception("Error syncing table %s", table)
                    _log(f"  {table}: FAILED after {elapsed:.1f}s — {e}")
        finally:
            conn.close()

        total_elapsed = time.monotonic() - total_start

        summary_lines = [f"Done in {total_elapsed:.1f}s. Summary:"]
        for tbl, (cnt, sec) in results.items():
            status_str = f"{cnt} rows" if cnt >= 0 else "FAILED"
            summary_lines.append(f"  {tbl:20s} {status_str:>12s}  ({sec:.1f}s)")
        for line in summary_lines:
            _log(line)

        # Update SyncLog
        sync_log.finished_at = timezone.now()
        sync_log.status = "failed" if had_errors else "success"
        sync_log.tables_synced = {
            tbl: cnt for tbl, (cnt, _) in results.items()
        }
        sync_log.log_output = log_buffer.getvalue()
        if had_errors:
            failed = [t for t, (c, _) in results.items() if c < 0]
            sync_log.error_message = f"Failed tables: {', '.join(failed)}"
        sync_log.save()

    # ------------------------------------------------------------------
    # Per-table sync dispatchers
    # ------------------------------------------------------------------

    def _sync_table(
        self,
        table: str,
        cursor: Any,
        *,
        full: bool,
        incremental: bool,
        dry_run: bool,
    ) -> int:
        """Dispatch to the correct sync method and return row count."""
        dispatch = {
            "modulos": self._sync_modulos,
            "kilometrajes": self._sync_kilometrajes,
            "ot_simaf": self._sync_ot_simaf,
            "coches": self._sync_coches,
            "formaciones": self._sync_formaciones,
        }
        fn = dispatch[table]
        return fn(cursor, full=full, incremental=incremental, dry_run=dry_run)

    # ------------------------------------------------------------------
    # modulos — always full reload (~111 rows)
    # ------------------------------------------------------------------

    def _sync_modulos(self, cursor, *, full, incremental, dry_run) -> int:
        cursor.execute(SQL_ALL_MODULES)
        rows = cursor.fetchall()
        logger.info("Access: A_00_Módulos returned %d rows", len(rows))

        if dry_run:
            return len(rows)

        objects = []
        for row in rows:
            access_id = row.Id_Módulos
            nombre = _safe_str(getattr(row, "Módulos", ""))
            clase_vehiculo = _safe_int(getattr(row, "Clase_Vehículos", None))
            tipo_mr = _safe_str(getattr(row, "Tipo_MR", ""))
            marca_mr = _safe_str(getattr(row, "Marca_MR", ""))

            if not access_id:
                continue

            objects.append(StgModulo(
                access_id=access_id,
                nombre=nombre,
                clase_vehiculo=clase_vehiculo,
                tipo_mr=tipo_mr,
                marca_mr=marca_mr,
            ))

        with transaction.atomic():
            StgModulo.objects.all().delete()
            StgModulo.objects.bulk_create(objects, batch_size=500)

        return len(objects)

    # ------------------------------------------------------------------
    # kilometrajes — full or incremental
    # ------------------------------------------------------------------

    def _sync_kilometrajes(self, cursor, *, full, incremental, dry_run) -> int:
        if incremental and not full:
            # Find the latest date already in Postgres
            latest = StgKilometraje.objects.order_by("-fecha").values_list(
                "fecha", flat=True
            ).first()
            if latest:
                logger.info(
                    "Incremental kilometrajes: fetching rows since %s", latest
                )
                cursor.execute(SQL_KILOMETRAJES_SINCE, (latest,))
            else:
                logger.info(
                    "Incremental kilometrajes: no existing data, fetching all."
                )
                cursor.execute(SQL_ALL_KILOMETRAJES)
        else:
            cursor.execute(SQL_ALL_KILOMETRAJES)

        rows = cursor.fetchall()
        logger.info("Access: A_00_Kilometrajes returned %d rows", len(rows))

        if dry_run:
            return len(rows)

        # Deduplicate: Access may have multiple rows for the same
        # (modulo, fecha) combination.  Keep the highest km value.
        dedup: dict[tuple[int, date], int | None] = {}
        skipped = 0
        for row in rows:
            modulo_id = _safe_int(row.ModuloId)
            fecha = _parse_date(row.Fecha)
            km = _safe_int(row.kilometraje)

            if modulo_id is None or fecha is None:
                skipped += 1
                continue

            key = (modulo_id, fecha)
            existing = dedup.get(key)
            if existing is None or (km is not None and (existing is None or km > existing)):
                dedup[key] = km

        if skipped:
            logger.info("Kilometrajes: skipped %d rows with NULL modulo/fecha", skipped)

        objects = [
            StgKilometraje(modulo_access_id=mid, fecha=f, kilometraje=k)
            for (mid, f), k in dedup.items()
        ]
        logger.info(
            "Kilometrajes: %d unique (modulo, fecha) pairs from %d Access rows",
            len(objects), len(rows),
        )

        with transaction.atomic():
            if full and not incremental:
                StgKilometraje.objects.all().delete()
                StgKilometraje.objects.bulk_create(objects, batch_size=2000)
            else:
                # Upsert: update_or_create in batches
                created = 0
                updated = 0
                for obj in objects:
                    _, was_created = StgKilometraje.objects.update_or_create(
                        modulo_access_id=obj.modulo_access_id,
                        fecha=obj.fecha,
                        defaults={"kilometraje": obj.kilometraje},
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                logger.info(
                    "Incremental kilometrajes: %d created, %d updated",
                    created, updated,
                )

        return len(objects)

    # ------------------------------------------------------------------
    # ot_simaf — full or incremental (by hash)
    # ------------------------------------------------------------------

    def _sync_ot_simaf(self, cursor, *, full, incremental, dry_run) -> int:
        if incremental and not full:
            latest_fecha = StgOtSimaf.objects.exclude(
                fecha_fin__isnull=True
            ).order_by("-fecha_fin").values_list(
                "fecha_fin", flat=True
            ).first()
            if latest_fecha:
                logger.info(
                    "Incremental ot_simaf: fetching rows since %s", latest_fecha
                )
                cursor.execute(SQL_OT_SIMAF_SINCE, (latest_fecha,))
            else:
                logger.info(
                    "Incremental ot_simaf: no existing data, fetching all."
                )
                cursor.execute(SQL_ALL_OT_SIMAF)
        else:
            cursor.execute(SQL_ALL_OT_SIMAF)

        rows = cursor.fetchall()
        logger.info("Access: A_00_OT_Simaf returned %d rows", len(rows))

        if dry_run:
            return len(rows)

        objects = []
        for row in rows:
            modulo_id = _safe_int(row.ModuloId)
            if modulo_id is None:
                continue

            tipo_tarea = _safe_str(getattr(row, "Tipo_Tarea", ""))
            tarea = _safe_str(getattr(row, "Tarea", ""))
            km = _safe_int(getattr(row, "Km", None))
            fecha_inicio = _parse_date(getattr(row, "Fecha_Inicio", None))
            fecha_fin = _parse_date(getattr(row, "Fecha_Fin", None))
            ot_simaf = _safe_str(getattr(row, "OT_SIMAF", ""))

            row_hash = _ot_row_hash(
                modulo_id, tarea, fecha_fin, km, fecha_inicio, ot_simaf
            )

            objects.append(StgOtSimaf(
                modulo_access_id=modulo_id,
                tipo_tarea=tipo_tarea,
                tarea=tarea,
                km=km,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                ot_simaf=ot_simaf,
                access_row_hash=row_hash,
            ))

        with transaction.atomic():
            if full and not incremental:
                StgOtSimaf.objects.all().delete()
                StgOtSimaf.objects.bulk_create(objects, batch_size=2000)
            else:
                # Incremental: skip rows whose hash already exists
                existing_hashes = set(
                    StgOtSimaf.objects.values_list("access_row_hash", flat=True)
                )
                new_objects = [
                    obj for obj in objects
                    if obj.access_row_hash not in existing_hashes
                ]
                if new_objects:
                    StgOtSimaf.objects.bulk_create(new_objects, batch_size=2000)
                logger.info(
                    "Incremental ot_simaf: %d new rows (skipped %d duplicates)",
                    len(new_objects), len(objects) - len(new_objects),
                )

        return len(objects)

    # ------------------------------------------------------------------
    # coches — always full reload
    # ------------------------------------------------------------------

    def _sync_coches(self, cursor, *, full, incremental, dry_run) -> int:
        cursor.execute(SQL_ALL_COCHES)
        rows = cursor.fetchall()
        logger.info("Access: A_00_Coches returned %d rows", len(rows))

        if dry_run:
            return len(rows)

        objects = []
        for row in rows:
            coche = _safe_int(row.Coche)
            if coche is None:
                continue

            posicion = _safe_int(getattr(row, "Posicion", None))
            ubicacion = _safe_str(getattr(row, "Ubicacion", ""))
            descripcion = _safe_str(getattr(row, "Descripcion", ""))

            objects.append(StgCoche(
                coche=coche,
                posicion=posicion,
                ubicacion=ubicacion,
                descripcion=descripcion,
            ))

        with transaction.atomic():
            StgCoche.objects.all().delete()
            StgCoche.objects.bulk_create(objects, batch_size=500)

        return len(objects)

    # ------------------------------------------------------------------
    # formaciones — always full reload
    # ------------------------------------------------------------------

    def _sync_formaciones(self, cursor, *, full, incremental, dry_run) -> int:
        cursor.execute(SQL_ALL_FORMACIONES)
        rows = cursor.fetchall()
        logger.info(
            "Access: A_14_Estado_Formaciones_Consulta returned %d rows", len(rows)
        )

        if dry_run:
            return len(rows)

        objects = []
        for row in rows:
            modulo_id = _safe_int(row.ModuloId)
            coche = _safe_int(row.Coche)
            if modulo_id is None or coche is None:
                continue

            objects.append(StgFormacionModulo(
                modulo_access_id=modulo_id,
                coche=coche,
            ))

        with transaction.atomic():
            StgFormacionModulo.objects.all().delete()
            StgFormacionModulo.objects.bulk_create(objects, batch_size=500)

        return len(objects)
