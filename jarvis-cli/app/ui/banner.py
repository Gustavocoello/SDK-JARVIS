"""
banner.py — Banner de arranque robusto para JARVIS CLI
Inspirado en el sistema de banner de pi-coding-agent (TS), portado a Python/Rich.

Estructura:
  1. Config (persistente en disco, igual que banner.json en el original)
  2. Paletas de color
  3. Recolección de stats del sistema (git, mcp, skills, etc.)
  4. Layout adaptativo (horizontal si hay espacio, vertical si no)
  5. Animación (typewriter + fade-in)
"""

import json
from string import capwords
import subprocess
import asyncio
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

from rich.console import Console, Group
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.table import Table
from rich.live import Live

from app.skills.skill_registry import count_skills

console = Console()

# ============================================================
# 1. CONFIG — equivalente a BannerConfig + banner.json del TS
# ============================================================

BannerColor = Literal["pink", "cyan", "yellow", "green", "white"]
CONFIG_PATH = Path.home() / ".jarvis" / "banner.json"


@dataclass
class BannerConfig:
    show_art: bool = True          
    show_text_logo: bool = True
    color: BannerColor = "white"    # 👈 CAMBIAR ACÁ el color default


def leer_config() -> BannerConfig:
    """Lee la config persistida, o devuelve la default si no existe/está corrupta."""
    try:
        data = json.loads(CONFIG_PATH.read_text())
        return BannerConfig(
            show_art=data.get("show_art", True),
            show_text_logo=data.get("show_text_logo", True),
            color=data.get("color", "cyan"),
        )
    except (FileNotFoundError, json.JSONDecodeError):
        return BannerConfig()


def guardar_config(config: BannerConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(config), indent=2))


# ============================================================
# 2. PALETAS — 👈 ACÁ se agregan/editan colores fácilmente
# ============================================================

PALETAS: dict[BannerColor, dict[str, str]] = {
    "pink"  : {"art": "#FF76C3", "label": "#C864A0", "value": "#FF8CD2", "logo": "#FF8ACE"},
    "cyan"  : {"art": "#5FD2FF", "label": "#55AACD", "value": "#82E1FF", "logo": "#69DCFF"},
    "yellow": {"art": "#FFD25F", "label": "#D2A541", "value": "#FFE187", "logo": "#FFD769"},
    "green" : {"art": "#6EDC91", "label": "#55AF73", "value": "#91F0AA", "logo": "#78E696"},
    "white" : {"art": "#8E8E93", "label": "#D2A541", "value": "#D1D1D6", "logo": "#FFFFFF"},
}


# ============================================================
# 3. STATS DEL SISTEMA — equivalente a las llamadas async del TS
#    (git branch, mcp servers, skills, agentes sdd, etc.)
# ============================================================

def obtener_git_branch(cwd: str = ".") -> str:
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True, text=True, timeout=1,
        )
        branch = result.stdout.strip()
        return f"On branch {branch}" if branch else "Detached HEAD"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Not a git repo"


def contar_mcp_servers() -> int:
    """👈 Ajustar el path según dónde guardes tu config de MCPs."""
    try:
        mcp_path = Path.home() / ".jarvis" / "mcp.json"
        cfg = json.loads(mcp_path.read_text())
        return len(cfg.get("mcpServers", {}))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def contar_skills(cwd:str = ".") -> int:
    return count_skills(cwd)


def recolectar_stats(cwd: str = ".") -> dict[str, str]:
    """Junta todos los stats en un dict — fácil de extender con más filas."""
    return {
        "GIT": obtener_git_branch(cwd),
        "PATH": str(Path(cwd).resolve()),
        "MCP": f"{contar_mcp_servers()} server(s)",
        "SKILLS": f"{contar_skills()} loaded",
        "VER": "v0.0.1",  # 👈 reemplazar por tu versión real (ej. desde pyproject.toml)
    }


# ============================================================
# 4. LOGO Y ARTE — tus assets ASCII
# ============================================================

LOGO_TEXTO = """
       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
       ██║███████║██████╔╝██║   ██║██║███████╗
  ███  ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
"""

ARTE_DECORATIVO = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠄⠄⠤⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠉⠈⠀⠂⠀⠄⠀⢀⠀⠀⠀⠀⠀⢀⠄⠐⠉⠉⠀⠠⠀⠘⠁⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠐⠀⠀⢼⣶⠤⢐⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠂⣠⡾⣶⣒⢀⠡⢄⠠⠄⠐⡀⠀⠄⠀⠀⠐⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠘⠂⠁⠂⠀⡀⠀⠀⠈⠀⠀⠀⢀⣾⣁⣀⡐⠀⠤⠐⢂⡀⠉⣀⠀⠀⠀⠀⠀⠀⢀⠁⢀⣀⣀⠀⠠⠤⠤⠤⠀⢤⠤⠤⣄⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠄⢀⡀⡾⠿⠓⠂⠓⠀⠠⠤⠂⠉⠁⡀⠀⠤⠀⠀⠀⠀⠀⠀⠡⠒⠒⠐⠘⠃⠉⠙⣶⠄⠈⡱⠀⠄⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠀⠀⠀⠀⠀⣀⢸⣧⡤⠌⠤⠤⠤⠤⠀⠀⠀⢀⠀⠀⠄⠀⠐⠀⠀⠀⠀⠀⣄⡀⠄⣀⠠⢀⡨⢀⠠⡄⠠⠐⠁⠀⠀⠀⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠠⠄⠲⠈⢔⡀⠸⠛⠭⠤⠤⠄⠐⠀⠒⠀⠁⢁⡀⠀⠄⢀⡀⠠⠄⣰⠢⠽⣒⠫⠁⠲⢌⠲⠜⠓⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⠐⠨⢀⡀⠊⡐⠀⠀⠀⠀⡄⡤⠄⠀⠀⣀⡈⠀⣤⠄⡐⠐⠠⠅⠀⠠⡌⠐⣠⡈⢠⠀⠐⠈⠀⠀⠀⠀⠀⠀⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⡀⠠⢀⣘⠓⠶⠾⠽⠥⠤⠴⠞⠋⡋⠓⣒⣊⡉⠉⠐⢰⣔⠘⠤⠌⠙⠂⠈⠀⠀⠀⠂⠀⠀⠀⠀⠁⠐⠄⢀⠀⣀⠀⠀⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠒⠁⠠⠴⠓⠃⠁⠈⠀⠀⠐⠈⠁⠈⠐⠒⠒⠂⠈⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠄⠁⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⠃⠈⡄⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⡀⠀⠀⠀⠀⠐⠀⢀⠠⠀⠀⠀⠀⠀⠐⠀⠀⢀⢀⠀⠀⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠐⠂⠀⠠⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
""" 


# ============================================================
# 5. LAYOUT ADAPTATIVO — equivalente a horizontal/minimal/skip del TS
# ============================================================

# Umbrales de terminal — 👈 AJUSTAR según qué tan grande es tu arte
ANCHO_MIN_HORIZONTAL = 80
ANCHO_MIN_MINIMO = 40


def elegir_modo_layout() -> Literal["full", "minimal", "skip"]:
    """Decide cómo renderizar según el tamaño real de la terminal."""
    ancho = console.size.width
    alto = console.size.height
    if ancho >= ANCHO_MIN_HORIZONTAL and alto >= 25:
        return "full"
    if ancho >= ANCHO_MIN_MINIMO:
        return "minimal"
    return "skip"  # terminal muy chica: no mostramos banner, vamos directo al prompt


def construir_tabla_stats(stats: dict[str, str], color: BannerColor) -> Table:
    paleta = PALETAS[color]
    tabla = Table.grid(padding=(0, 2))
    tabla.add_column(justify="right", style=f"bold {paleta['label']}")
    tabla.add_column(style=paleta["value"])
    for label, valor in stats.items():
        tabla.add_row(f"{label}:", valor)
    return tabla


def construir_banner_estatico(config: BannerConfig, cwd: str = ".") -> Group:
    """Versión sin animación — útil para terminales chicas o tests."""
    paleta = PALETAS[config.color]
    modo = elegir_modo_layout()

    if modo == "skip":
        return Group(Text(""))  # banner vacío, no perdemos tiempo

    logo = Text(LOGO_TEXTO, style=f"bold {paleta['logo']}")
    arte = Text(ARTE_DECORATIVO, style="dim white")

    elementos = []

    if modo == "full" and config.show_art and config.show_text_logo:
        alto_arte = arte.plain.count("\n") + 1
        logo_centrado = Align(logo, vertical="middle", height=alto_arte)
        elementos.append(Columns([logo_centrado, arte], align="center", expand=True))
    elif config.show_text_logo:
        elementos.append(Align.center(logo))
    elif config.show_art:
        elementos.append(Align.center(arte))

    if modo == "full":
        stats = recolectar_stats(cwd)
        elementos.append(Align.center(construir_tabla_stats(stats, config.color)))

    return Group(*elementos)


# ============================================================
# 6. ANIMACIÓN — typewriter + fade-in (versión simplificada del
#    sistema de "tinta fresca / tinta seca" del original en TS)
# ============================================================

async def mostrar_banner_animado(config: BannerConfig, cwd: str = ".") -> None:
    """
    Anima el logo letra por letra con un efecto de 'tinta fresca'.
    👈 Si querés MÁS fidelidad al original (trazos curvos reales),
       ese algoritmo de stroke-order es mucho más código — avisame
       y te lo armo aparte, pero este typewriter ya da buen efecto.
    """
    paleta = PALETAS[config.color]
    modo = elegir_modo_layout()
    if modo == "skip":
        return

    lineas = LOGO_TEXTO.strip("\n").split("\n")
    total_chars = sum(len(l) for l in lineas)

    with Live(console=console, refresh_per_second=30, transient=False) as live:
        for tick in range(0, total_chars + 10, 3):  # 👈 ajustar paso para más/menos velocidad
            texto_animado = Text()
            chars_mostrados = 0

            for linea in lineas:
                for i, char in enumerate(linea):
                    if chars_mostrados < tick - 5:
                        estilo = paleta["logo"]            # tinta ya seca
                    elif chars_mostrados < tick:
                        estilo = "bold white"               # tinta fresca (highlight)
                    else:
                        char = " "                          # todavía no escrito
                        estilo = "none"
                    texto_animado.append(char, style=estilo)
                    chars_mostrados += 1
                texto_animado.append("\n")

            live.update(Align.center(texto_animado))
            await asyncio.sleep(0.015)  # 👈 ajustar duración total acá

        # Frame final: logo completo + stats (si el modo lo permite)
        contenido_final = construir_banner_estatico(config, cwd)
        live.update(contenido_final)
        await asyncio.sleep(0.3)


# ============================================================
# 7. PUNTO DE ENTRADA
# ============================================================

async def welcome(cwd: str = ".") -> None:
    console.clear()
    config = leer_config()
    await mostrar_banner_animado(config, cwd)
    console.print()


if __name__ == "__main__":
    asyncio.run(welcome())