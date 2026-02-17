from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

def mostrar_resumen_calidad():
    # 1. Crear la tabla principal
    table = Table(box=box.ROUNDED, title="ARS_MP - Reporte de Calidad", title_style="bold cyan")

    table.add_column("Métrica", style="cyan", no_wrap=True)
    table.add_column("Resultado", style="green", justify="right")
    table.add_column("Detalle", style="white")

    # Datos reales de tu ejecución
    table.add_row("Total Tests", "214", "✅ Todos Pasaron")
    table.add_row("Tiempo Ejecución", "8.30s", "⚡ Feedback inmediato")
    table.add_row("Cobertura Core", "98%", "core/services/grid_projection.py")
    table.add_row("Cobertura Dominio", "100%", "core/domain/entities")
    table.add_row("Cobertura Proyección", "97%", "core/services/maintenance.py")
    table.add_row("Estado del Build", "PASSING", "Lista para deploy")

    # 2. Panel de resumen
    resumen = Panel(
        table,
        title="[bold green]✔ SUITE DE TESTS EXITOSA[/bold green]",
        subtitle="Backend: Python 3.11 + Django 5",
        border_style="green"
    )

    console.print("\n")
    console.print(resumen, justify="center")
    console.print("\n")

if __name__ == "__main__":
    mostrar_resumen_calidad()