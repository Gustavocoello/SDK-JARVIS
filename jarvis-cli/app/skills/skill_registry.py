"""
skill_registry.py — Auto-descubrimiento de skills para JARVIS CLI
Port del sistema de skill-registry.ts (gentle-pi) a Python.

Qué hace:
  1. Escanea directorios conocidos de skills (tuyos + de otros agentes: Claude, Cursor, etc.)
  2. Parsea el frontmatter de cada SKILL.md (name, description)
  3. Cachea con fingerprint (hash de mtime+size) para no re-escanear si nada cambió
  4. Genera un registro en markdown (.jarvis/skill-registry.md)
  5. Expone count_skills() para el banner (reemplaza el contar_skills() de antes)
"""
import os
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from datetime import date

# ============================================================
# CONFIG DE PATHS
# ============================================================

REGISTRY_REL_PATH = ".jarvis/skill-registry.md"
CACHE_REL_PATH = ".jarvis/.skill-registry.cache.json"
SECTION_MARKER = "## Skills"
SCHEMA_VERSION = 1
JARVIS_SKILLS_DIR = os.environ.get(
    "JARVIS_SKILLS_DIR",
    r"C:\work\mcp-nexus\mcp-scratch\backend\src\services\agent\skills",  # default para Windows dev
)

# Nombres/prefijos que NO queremos indexar (igual que EXCLUDE_NAMES/PREFIXES del TS)
EXCLUDE_NAMES = {"_shared", "skill-registry"}
EXCLUDE_PREFIXES = ("sdd-",)


def directorios_skills_usuario() -> list[Path]:
    """
    Carpetas globales (~/.algo/skills) de TODOS los agentes que puedan
    tener skills instaladas — así si el usuario ya usa Claude Code o
    Cursor, JARVIS las reconoce automáticamente sin duplicar trabajo.
    Agregá/quitá líneas según qué herramientas te interese soportar.
    """
    home = Path.home()
    return [
        home / ".jarvis" / "skills",          # las tuyas, propias de JARVIS
        home / ".claude" / "skills",
        home / ".cursor" / "skills",
        home / ".codeium" / "windsurf" / "skills",
        home / ".gemini" / "skills",
        home / ".codex" / "skills",
        home / ".config" / "opencode" / "skills",
    ]


def directorios_skills_proyecto(cwd: Path) -> list[Path]:
    """
    Carpetas locales del proyecto actual — tienen prioridad sobre las
    globales si hay una skill con el mismo nombre (dedupe_por_nombre).
    """
    return [
        cwd / "skills",
        cwd / ".jarvis" / "skills",
        cwd / ".claude" / "skills",
        cwd / ".cursor" / "skills",
        Path(JARVIS_SKILLS_DIR)
    ]


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class SkillEntry:
    name: str
    path: Path
    description: str
    scope: str = ""  # "project" o "user"


# ============================================================
# DESCUBRIMIENTO DE ARCHIVOS
# ============================================================

def encontrar_archivos_skill(root: Path) -> list[Path]:
    """Busca recursivamente todos los SKILL.md bajo `root`."""
    if not root.exists():
        return []
    return sorted(root.rglob("SKILL.md"))


def directorios_existentes_unicos(dirs: list[Path]) -> list[Path]:
    """Dedupea y filtra los que no existen — evita escanear basura."""
    vistos: set[str] = set()
    out: list[Path] = []
    for d in dirs:
        resolved = str(d.resolve()) if d.exists() else None
        if resolved and resolved not in vistos:
            vistos.add(resolved)
            out.append(d)
    return out


# ============================================================
# PARSEO DE FRONTMATTER (versión simple del parser YAML manual del TS)
# ============================================================

def parsear_frontmatter(source: str) -> tuple[str | None, str | None, str]:
    """
    Devuelve (name, description, body). No usa un parser YAML completo
    a propósito —igual que el original— porque solo necesitamos 2 campos
    y así evitamos una dependencia extra (pyyaml) solo para esto.
    👈 Si después necesitás más campos del frontmatter, conviene migrar
       a `pyyaml` con safe_load en vez de seguir agregando regex acá.
    """
    if not source.startswith("---\n"):
        return None, None, source

    end = source.find("\n---", 4)
    if end == -1:
        return None, None, source

    fm_block = source[4:end]
    body = source[end + 4:].lstrip("\n")

    name = None
    description = None
    for line in fm_block.split("\n"):
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "name":
            name = value
        elif key == "description":
            description = value

    return name, description, body


def normalizar_descripcion(desc: str) -> str:
    return " ".join(desc.split())


def es_excluido(name: str) -> bool:
    if name in EXCLUDE_NAMES:
        return True
    return any(name.startswith(p) for p in EXCLUDE_PREFIXES)


def cargar_skill(file: Path) -> SkillEntry | None:
    try:
        source = file.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return None

    name, description, _ = parsear_frontmatter(source)
    nombre_final = name or file.parent.name  # si no hay "name:", usa el nombre de la carpeta

    if es_excluido(nombre_final):
        return None

    return SkillEntry(
        name=nombre_final,
        path=file,
        description=normalizar_descripcion(description or ""),
    )


def scope_para_path(cwd: Path, path: Path) -> str:
    try:
        path.resolve().relative_to(cwd.resolve())
        return "project"
    except ValueError:
        return "user"


def dedupe_por_nombre(entries: list[SkillEntry], cwd: Path) -> list[SkillEntry]:
    """Si hay una skill con el mismo nombre en project Y user, gana la del proyecto."""
    buckets: dict[str, list[SkillEntry]] = {}
    for e in entries:
        buckets.setdefault(e.name, []).append(e)

    out: list[SkillEntry] = []
    for name, candidatos in buckets.items():
        proyecto = next((c for c in candidatos if scope_para_path(cwd, c.path) == "project"), None)
        elegido = proyecto or candidatos[0]
        elegido.scope = scope_para_path(cwd, elegido.path)
        out.append(elegido)

    return sorted(out, key=lambda e: e.name)


# ============================================================
# FINGERPRINT / CACHE — evita re-escanear si nada cambió
# ============================================================

def calcular_fingerprint(files: list[Path]) -> str:
    lines = [f"schema:{SCHEMA_VERSION}"]
    for f in files:
        try:
            info = f.stat()
            lines.append(f"{f}:{info.st_mtime}:{info.st_size}")
        except FileNotFoundError:
            lines.append(f"{f}:missing")
    lines.sort()
    return hashlib.sha1("\n".join(lines).encode()).hexdigest()


def leer_cache(cache_path: Path) -> str | None:
    try:
        data = json.loads(cache_path.read_text())
        return data.get("fingerprint")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def guardar_cache(cache_path: Path, fingerprint: str) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"fingerprint": fingerprint}, indent=2))


# ============================================================
# RENDER DEL REGISTRO (markdown, igual formato que el TS)
# ============================================================

def renderizar_registro(cwd: Path, sources: list[str], entries: list[SkillEntry]) -> str:
    project_name = cwd.name
    today = date.today().isoformat()

    lines = [
        f"# Skill Registry — {project_name}",
        "",
        "<!-- Auto-generado por jarvis-cli/skill_registry.py. Correr `jarvis skills refresh` para regenerar. -->",
        "",
        f"Última actualización: {today}",
        "",
        "## Fuentes escaneadas",
        "",
        *[f"- {s}" for s in sources],
        "",
        SECTION_MARKER,
        "",
        "| Skill | Descripción / trigger | Scope | Path |",
        "| --- | --- | --- | --- |",
    ]
    for e in entries:
        desc = e.description or "—"
        lines.append(f"| `{e.name}` | {desc} | {e.scope} | `{e.path}` |")

    return "\n".join(lines) + "\n"


# ============================================================
# REGENERACIÓN PRINCIPAL
# ============================================================

@dataclass
class ResultadoRegen:
    regenerado: bool
    cantidad_skills: int
    razon: str


def regenerar_registro(cwd: Path, forzar: bool = False) -> ResultadoRegen:
    dirs = directorios_existentes_unicos([
        *directorios_skills_proyecto(cwd),
        *directorios_skills_usuario(),
    ])

    files: list[Path] = []
    for d in dirs:
        files.extend(encontrar_archivos_skill(d))

    cache_path = cwd / CACHE_REL_PATH
    registry_path = cwd / REGISTRY_REL_PATH
    fp = calcular_fingerprint(files)
    cached_fp = leer_cache(cache_path)

    if not forzar and cached_fp == fp and registry_path.exists():
        return ResultadoRegen(regenerado=False, cantidad_skills=0, razon="cache-hit")

    entries = [e for f in files if (e := cargar_skill(f)) is not None]
    deduped = dedupe_por_nombre(entries, cwd)

    sources = []
    for d in dirs:
        try:
            rel = d.resolve().relative_to(cwd.resolve())
            sources.append(str(rel))
        except ValueError:
            sources.append(str(d))  # fuera del proyecto (ej. ~/.claude/skills): path absoluto

    md = renderizar_registro(cwd, sources, deduped)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(md, encoding="utf-8")
    guardar_cache(cache_path, fp)

    return ResultadoRegen(
        regenerado=True,
        cantidad_skills=len(deduped),
        razon="forzado" if forzar else "fingerprint-cambió",
    )


# ============================================================
# INTEGRACIÓN CON EL BANNER — reemplaza el contar_skills() de antes
# ============================================================

def count_skills(cwd: str = ".") -> int:
    """👈 Esta es la función que banner.py debería llamar en vez del placeholder."""
    cwd_path = Path(cwd)
    registry_path = cwd_path / REGISTRY_REL_PATH
    if not registry_path.exists():
        regenerar_registro(cwd_path, forzar=False)
    try:
        contenido = registry_path.read_text(encoding="utf-8")
        # Cuenta filas de la tabla markdown (todas las que empiezan con "| `")
        return sum(1 for line in contenido.split("\n") if line.startswith("| `"))
    except FileNotFoundError:
        return 0


if __name__ == "__main__":
    resultado = regenerar_registro(Path("."), forzar=True)
    print(f"Skills encontradas: {resultado.cantidad_skills} ({resultado.razon})")