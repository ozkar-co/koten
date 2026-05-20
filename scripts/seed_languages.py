from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from koten.db.connection import get_connection
from koten.db.schema import create_schema
from koten.linguistics.service import canonical_root

LANGUAGE_LABEL_TO_CODE = {
    "lapag": "lapag",
    "gox'jix": "goxjix",
    "dekayun": "dekayun",
    "jobid'e": "jobide",
    "negelch": "negelch",
    "gornach-kagsha": "gornach_kagsha",
}

LANGUAGE_NAMES = {
    "lapag": "Lapag",
    "goxjix": "Gox'jix",
    "dekayun": "Dekayun",
    "jobide": "Jobid'e",
    "negelch": "Negelch",
    "gornach_kagsha": "Gornach-Kagsha",
}


# Seed data is embedded in this file on purpose.
TRANSLATION_HEADER = [
    "lapag",
    "gox'jix",
    "dekayun",
    "jobid'e",
    "negelch",
    "gornach-kagsha",
]

TRANSLATION_ROWS = [
    ["c", "m", "s", "l", "m", "rag"],
    ["d", "t", "f", "s", "k", "lar"],
    ["t", "k", "l", "m", "t", "kor"],
    ["s", "p", "m", "d", "s", "gor"],
    ["k", "c", "c", "t", "b", "gar"],
    ["r", "n", "t", "n", "f", "rek"],
    ["l", "g", "d", "j", "x", "kag"],
    ["n", "b", "p", "u", "r", "lok"],
    ["m", "j", "j", "o", "d", "nash"],
    ["j", "d", "b", "f", "l", "dur"],
    ["g", "l", "y", "y", "p", "tar"],
    ["b", "r", "k", "i", "n", "ket"],
    ["f", "s", "n", "a", "y", "gul"],
    ["y", "y", "s", "e", "g", "lug"],
    ["p", "x", "k", "b", "c", "sha"],
    ["x", "f", "t", "g", "j", "ruk"],
]

# Compatibility alias for legacy lore spelling.
GORNACH_ALIASES: dict[str, list[str]] = {
    "m": ["nach"],
}

# Negelch digraph aliases: 'ch' is the digraph form of the 'c' root.
NEGELCH_ALIASES: dict[str, list[str]] = {
    "c": ["ch"],
}

SEMANTIC_ROOTS_TEXT = """
c: diferente, alterado, contrario, otro
d: aire, aliento, esencia, espíritu
t: todo, abundancia, universo, vida
s: divino, sagrado, sobrenatural, luz, radiante
k: creador, ancestro, sustento, ser
r: cabeza, control, poseer, reglas, guía
l: sabiduría, información, conocimiento
n: tiempo, momento, situación, eternidad
m: ausente, aislado, alejado, ignorado
j: comunidad, compañía, grupo, sociedad
g: tierra, suelo, mundo, territorio
b: cosa, objeto, materia, fenómeno
f: consumir, ingerir, comer, beber
y: fuego, calor, feminidad
p: agua, líquido, fluido, humedad, masculino
x: círculo, ciclo, alrededor
cd: grande, pesado, alto, importante
cf: reptil, anfibio, insecto, bicho
cs: maldición, oscuridad, profano
ck: implemento, dispositivo, máquina, herramienta
cr: extraño, inusual, loco
cl: nuevo, descubrir, más
cn: diversión, arte, entretenimiento, juguetón
cm: igual, similar, parecido
cg: pequeño, corto, poco, joven
bc: no, negativo, malo, irrelevante
cy: dorado, roto, desordenado, alterado
cx: plano, superficie, horizontal
dt: nombre, palabra
ds: color, colorido, pintado
dk: pájaro, criatura voladora
dr: frente, cara, frontal
dl: producir sonido, ruido, grito, bulla
dm: contenedor, bolsa, caja
dj: único, único, uno
dg: polvo, arena
bd: centro, contenido, adentro, interno, entre
df: necesitar, querer, requerir, deber, obligación
dx: poder, permiso, capacidad, posibilidad
st: bueno, positivo, útil, pacífico, amigable
kt: semilla, origen
mt: muerte, muerto, cadáver, descomposición
ty: montaña, montículo, protuberancia
bt: mucho, cantidad, montón
ft: animal, bestia, criatura
pt: pescado, pescar, océano, lago
ks: dios, entidad suprema
ls: representación, imagen, marca, símbolo
ns: presente, real, verdadero, existente
ms: batalla, reto, competencia, dificultad, sombra
bs: tierno, inocente, dulce, adorable, lindo
fs: observar, examinar, mirar, buscar, ver
sy: amor, afecto, compasión | altura, arriba, encima, cielo
kr: detenerse, obstáculo, pared
kl: humano, persona, alguien
kn: inicio, comienzo, abierto
jk: compañero, amigo, camarada
gk: vía, camino, método, doctrina
bk: hacer, trabajar, emprender
fk: cazar, recolectar
ky: cubrir, cobertura, tejido, tela, ropa
kx: dar, proveer, entregar, emitir, enviar, poner
nr: protegido, seguro, guardar
mr: detrás, atrás, espalda
jr: humilde, dependiente, bajo
gr: casa, propiedad, habitación, edificio
br: tener, portar, contener, sostener, mantener
fr: caos, desorden, deambular, vagar
ry: fuerte, poderoso, confidente, intenso
rx: dinero, valor, riqueza
ln: pasado, fin, finalizado, completo, viejo
lm: ignorancia, misterio, oculto
jl: escuchar, oír, poner atención
fl: cuestionar, pregunta, duda
lp: comunicar, decir, hablar
lv: afuera, exterior, piel, cáscara, borde
mn: llegando, futuro, convertirse
bn: estado físico, cuerpo, corporalidad
fn: experiencia, sentimiento, emoción
np: movimiento, yendo hacia, dirección
nx: dolor, sufrimiento, enfermedad
jm: soledad, aislamiento, solitario
bm: orificio, agujero, faltante
fm: disgusto, obsceno, tóxico, sucio, contaminación
my: frío, fresco, crudo
mp: desierto, sed, hambre, deseo
mx: vara, rama, cosa larga y dura
bj: transacción, comercio, comprar, vender
jx: cerca, cercano, próximo, vecino
bg: roca, piedra, metal
fg: planta, vegetación, hierba
gp: semisólido, masa, pastoso, arcilla, barro
gx: bajo, abajo, fondo
bf: fruta, vegetal, comestible
by: energético, explosivo, electricidad
bp: cuerda, cosa larga y flexible
sx: sol, solar, día
px: luna, estrella, noche
py: reacción, relación, sexo
"""


def _split_row(line: str) -> list[str]:
    raw = [item.strip() for item in re.split(r"\s+", line.strip()) if item.strip()]
    return raw


def parse_translation_rows(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [line for line in text.splitlines() if line.strip()]
    start = next(
        i for i, line in enumerate(lines) if line.lower().startswith("lapag")
    )

    header = _split_row(lines[start])
    rows: list[list[str]] = []

    for line in lines[start + 1 :]:
        if line.startswith("El carácter") or line.startswith("##"):
            break

        parts = _split_row(line)
        if len(parts) == len(header):
            rows.append(parts)

    return header, rows


def parse_semantic_roots(text: str) -> dict[str, str]:
    in_section = "## Raíces Semánticas" not in text
    roots: dict[str, list[str]] = {}

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Raíces Semánticas":
            in_section = True
            continue

        if in_section and stripped.startswith("Combinando estas raíces"):
            break

        if not in_section or not stripped:
            continue

        match = re.match(r"^([a-z]{1,2}):\s*(.+)$", stripped, flags=re.IGNORECASE)
        if not match:
            continue

        root = canonical_root(match.group(1))
        meaning = match.group(2).strip()
        roots.setdefault(root, []).append(meaning)

    return {key: " | ".join(dict.fromkeys(values)) for key, values in roots.items()}


def seed() -> None:
    header = TRANSLATION_HEADER
    translation_rows = TRANSLATION_ROWS
    semantic_roots = parse_semantic_roots(SEMANTIC_ROOTS_TEXT)

    language_codes = [LANGUAGE_LABEL_TO_CODE[label] for label in header]

    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        create_schema(connection)

        for code in language_codes:
            connection.execute(
                """
                INSERT INTO languages(code, name, parser)
                VALUES (?, ?, 'greedy')
                ON CONFLICT(code) DO UPDATE SET name = excluded.name
                """,
                (code, LANGUAGE_NAMES.get(code, code.capitalize())),
            )

        for lapag_root, meaning in semantic_roots.items():
            connection.execute(
                """
                INSERT INTO roots(lapag_root, meaning)
                VALUES (?, ?)
                ON CONFLICT(lapag_root) DO UPDATE SET meaning = excluded.meaning
                """,
                (lapag_root, meaning),
            )

        lapag_index = header.index("lapag")

        for row in translation_rows:
            lapag_root = canonical_root(row[lapag_index])
            for idx, language_label in enumerate(header):
                language_code = LANGUAGE_LABEL_TO_CODE[language_label]
                raw_language_root = row[idx].strip().lower()
                if language_code == "lapag":
                    language_root = canonical_root(raw_language_root)
                else:
                    language_root = raw_language_root

                connection.execute(
                    """
                    INSERT INTO root_equivalences(language_code, language_root, lapag_root)
                    VALUES (?, ?, ?)
                    ON CONFLICT(language_code, language_root, lapag_root) DO NOTHING
                    """,
                    (language_code, language_root, lapag_root),
                )

            # Add explicit aliases for gornach-kagsha roots when configured.
            for alias in GORNACH_ALIASES.get(lapag_root, []):
                connection.execute(
                    """
                    INSERT INTO root_equivalences(language_code, language_root, lapag_root)
                    VALUES (?, ?, ?)
                    ON CONFLICT(language_code, language_root, lapag_root) DO NOTHING
                    """,
                    ("gornach_kagsha", alias.strip().lower(), lapag_root),
                )

            # Add explicit aliases for negelch roots when configured.
            for alias in NEGELCH_ALIASES.get(lapag_root, []):
                connection.execute(
                    """
                    INSERT INTO root_equivalences(language_code, language_root, lapag_root)
                    VALUES (?, ?, ?)
                    ON CONFLICT(language_code, language_root, lapag_root) DO NOTHING
                    """,
                    ("negelch", alias.strip().lower(), lapag_root),
                )

        connection.commit()

    print(f"Languages seeded: {len(language_codes)}")
    print(f"Semantic roots seeded: {len(semantic_roots)}")
    print(f"Root equivalences seeded: {len(translation_rows) * len(language_codes)}")


if __name__ == "__main__":
    seed()
