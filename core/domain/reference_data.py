"""Reference data for RG/commissioning dates by module.

This module contains static reference data for the last RG (Revision General)
or commissioning date for each EMU module in the fleet.

CSR modules use their commissioning date ("Puesta en Servicio") as reference
since no DA (Desarmado A) has been performed yet on this fleet.

Toshiba modules use their last RG date as reference.

Data source: Originally from URG-Modulos.csv, now internalized for portability
and self-containedness. This data only changes when a new RG (Toshiba) or
DA (CSR) intervention is performed, which would be reflected in the Access DB.

Notes:
    - M67 is excluded: never commissioned, used as parts donor for active fleet
    - M47 is included: out of service but was commissioned on 2016-01-31
"""
from datetime import date

# Module ID format: M## for CSR (85 modules), T## for Toshiba (25 modules)
# Value: (reference_date, reference_type)
# reference_type: "Puesta en Servicio" for CSR, "RG" for Toshiba
RG_REFERENCE_DATES: dict[str, tuple[date, str]] = {
    # ==========================================================================
    # CSR modules (85 entries): M01-M86, excluding M67
    # Reference type: "Puesta en Servicio" (commissioning date)
    # ==========================================================================
    "M01": (date(2017, 9, 30), "Puesta en Servicio"),
    "M02": (date(2015, 8, 31), "Puesta en Servicio"),
    "M03": (date(2015, 10, 31), "Puesta en Servicio"),
    "M04": (date(2015, 9, 30), "Puesta en Servicio"),
    "M05": (date(2016, 8, 31), "Puesta en Servicio"),
    "M06": (date(2015, 8, 31), "Puesta en Servicio"),
    "M07": (date(2015, 8, 31), "Puesta en Servicio"),
    "M08": (date(2016, 8, 31), "Puesta en Servicio"),
    "M09": (date(2016, 7, 31), "Puesta en Servicio"),
    "M10": (date(2016, 7, 31), "Puesta en Servicio"),
    "M11": (date(2015, 9, 30), "Puesta en Servicio"),
    "M12": (date(2015, 10, 31), "Puesta en Servicio"),
    "M13": (date(2016, 3, 31), "Puesta en Servicio"),
    "M14": (date(2015, 9, 30), "Puesta en Servicio"),
    "M15": (date(2016, 1, 31), "Puesta en Servicio"),
    "M16": (date(2015, 9, 30), "Puesta en Servicio"),
    "M17": (date(2015, 9, 30), "Puesta en Servicio"),
    "M18": (date(2016, 3, 31), "Puesta en Servicio"),
    "M19": (date(2015, 9, 30), "Puesta en Servicio"),
    "M20": (date(2016, 1, 31), "Puesta en Servicio"),
    "M21": (date(2016, 10, 31), "Puesta en Servicio"),
    "M22": (date(2016, 6, 30), "Puesta en Servicio"),
    "M23": (date(2015, 10, 31), "Puesta en Servicio"),
    "M24": (date(2015, 9, 30), "Puesta en Servicio"),
    "M25": (date(2015, 9, 30), "Puesta en Servicio"),
    "M26": (date(2015, 9, 30), "Puesta en Servicio"),
    "M27": (date(2015, 9, 30), "Puesta en Servicio"),
    "M28": (date(2015, 9, 30), "Puesta en Servicio"),
    "M29": (date(2016, 1, 31), "Puesta en Servicio"),
    "M30": (date(2015, 9, 30), "Puesta en Servicio"),
    "M31": (date(2017, 6, 30), "Puesta en Servicio"),
    "M32": (date(2016, 1, 31), "Puesta en Servicio"),
    "M33": (date(2015, 9, 30), "Puesta en Servicio"),
    "M34": (date(2015, 9, 30), "Puesta en Servicio"),
    "M35": (date(2019, 12, 28), "Puesta en Servicio"),
    "M36": (date(2015, 9, 30), "Puesta en Servicio"),
    "M37": (date(2015, 9, 30), "Puesta en Servicio"),
    "M38": (date(2016, 8, 31), "Puesta en Servicio"),
    "M39": (date(2015, 9, 30), "Puesta en Servicio"),
    "M40": (date(2015, 9, 30), "Puesta en Servicio"),
    "M41": (date(2016, 2, 29), "Puesta en Servicio"),
    "M42": (date(2016, 2, 29), "Puesta en Servicio"),
    "M43": (date(2016, 1, 31), "Puesta en Servicio"),
    "M44": (date(2016, 1, 31), "Puesta en Servicio"),
    "M45": (date(2017, 8, 31), "Puesta en Servicio"),
    "M46": (date(2016, 1, 31), "Puesta en Servicio"),
    "M47": (date(2016, 1, 31), "Puesta en Servicio"),  # Out of service but was commissioned
    "M48": (date(2016, 1, 31), "Puesta en Servicio"),
    "M49": (date(2017, 6, 30), "Puesta en Servicio"),
    "M50": (date(2017, 7, 31), "Puesta en Servicio"),
    "M51": (date(2016, 11, 30), "Puesta en Servicio"),
    "M52": (date(2016, 8, 31), "Puesta en Servicio"),
    "M53": (date(2016, 11, 30), "Puesta en Servicio"),
    "M54": (date(2016, 3, 31), "Puesta en Servicio"),
    "M55": (date(2017, 8, 31), "Puesta en Servicio"),
    "M56": (date(2019, 12, 23), "Puesta en Servicio"),
    "M57": (date(2017, 9, 30), "Puesta en Servicio"),
    "M58": (date(2016, 8, 31), "Puesta en Servicio"),
    "M59": (date(2016, 3, 31), "Puesta en Servicio"),
    "M60": (date(2016, 12, 31), "Puesta en Servicio"),
    "M61": (date(2016, 1, 31), "Puesta en Servicio"),
    "M62": (date(2016, 1, 31), "Puesta en Servicio"),
    "M63": (date(2016, 1, 31), "Puesta en Servicio"),
    "M64": (date(2016, 1, 31), "Puesta en Servicio"),
    "M65": (date(2016, 1, 31), "Puesta en Servicio"),
    "M66": (date(2017, 1, 31), "Puesta en Servicio"),
    # M67 excluded: never commissioned, used as parts donor
    "M68": (date(2017, 2, 28), "Puesta en Servicio"),
    "M69": (date(2016, 8, 31), "Puesta en Servicio"),
    "M70": (date(2017, 9, 30), "Puesta en Servicio"),
    "M71": (date(2017, 6, 30), "Puesta en Servicio"),
    "M72": (date(2016, 11, 30), "Puesta en Servicio"),
    "M73": (date(2017, 9, 30), "Puesta en Servicio"),
    "M74": (date(2016, 1, 31), "Puesta en Servicio"),
    "M75": (date(2016, 1, 31), "Puesta en Servicio"),
    "M76": (date(2018, 6, 29), "Puesta en Servicio"),
    "M77": (date(2016, 6, 30), "Puesta en Servicio"),
    "M78": (date(2017, 1, 31), "Puesta en Servicio"),
    "M79": (date(2016, 4, 30), "Puesta en Servicio"),
    "M80": (date(2016, 4, 30), "Puesta en Servicio"),
    "M81": (date(2016, 1, 31), "Puesta en Servicio"),
    "M82": (date(2016, 12, 31), "Puesta en Servicio"),
    "M83": (date(2017, 2, 28), "Puesta en Servicio"),
    "M84": (date(2017, 8, 31), "Puesta en Servicio"),
    "M85": (date(2016, 11, 30), "Puesta en Servicio"),
    "M86": (date(2017, 6, 30), "Puesta en Servicio"),
    # ==========================================================================
    # Toshiba modules (25 entries)
    # Reference type: "RG" (last Revision General date)
    # ==========================================================================
    "T04": (date(2023, 12, 15), "RG"),
    "T06": (date(2023, 5, 10), "RG"),
    "T09": (date(2025, 10, 14), "RG"),
    "T11": (date(2019, 3, 15), "RG"),
    "T12": (date(2011, 6, 28), "RG"),
    "T15": (date(2018, 10, 11), "RG"),
    "T16": (date(2017, 9, 15), "RG"),
    "T19": (date(2018, 2, 7), "RG"),
    "T20": (date(2021, 12, 10), "RG"),
    "T21": (date(2020, 8, 28), "RG"),
    "T22": (date(2020, 2, 24), "RG"),
    "T24": (date(2020, 12, 29), "RG"),
    "T28": (date(2019, 12, 13), "RG"),
    "T29": (date(2022, 12, 7), "RG"),
    "T31": (date(2022, 8, 15), "RG"),
    "T34": (date(2017, 11, 9), "RG"),
    "T36": (date(2023, 8, 31), "RG"),
    "T39": (date(2021, 7, 23), "RG"),
    "T40": (date(2012, 1, 9), "RG"),
    "T43": (date(2022, 5, 12), "RG"),
    "T45": (date(2025, 10, 14), "RG"),
    "T46": (date(2025, 1, 8), "RG"),
    "T47": (date(2019, 2, 24), "RG"),
    "T49": (date(2019, 8, 30), "RG"),
    "T52": (date(2024, 8, 30), "RG"),
}
