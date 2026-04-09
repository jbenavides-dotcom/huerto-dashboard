"""
Generador de PDF: Guia del Bot Huerta & Animales
Para: Jhon (trabajador finca La Palma y El Tucan)
Libreria: reportlab (ya instalada)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT_PATH = r"C:\Users\USUARIO\Documents\cerebro-claude\huerto-dashboard\telegram-bot\guia-bot-jhon.pdf"

# ─── Colores ───────────────────────────────────────────────────────────────────
VERDE_OSCURO  = colors.HexColor("#1B5E20")
VERDE_MEDIO   = colors.HexColor("#388E3C")
VERDE_CLARO   = colors.HexColor("#C8E6C9")
NARANJA       = colors.HexColor("#E65100")
NARANJA_CLARO = colors.HexColor("#FFE0B2")
GRIS_FONDO    = colors.HexColor("#F5F5F5")
GRIS_LINEA    = colors.HexColor("#BDBDBD")
AZUL_CLARO    = colors.HexColor("#E3F2FD")
AZUL_MEDIO    = colors.HexColor("#1565C0")
NEGRO         = colors.HexColor("#212121")
BLANCO        = colors.white

# ─── Estilos ───────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "Titulo",
        parent=base["Title"],
        fontSize=22,
        textColor=VERDE_OSCURO,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        leading=26,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=base["Normal"],
        fontSize=13,
        textColor=VERDE_MEDIO,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName="Helvetica",
        leading=16,
    )
    seccion = ParagraphStyle(
        "Seccion",
        parent=base["Heading1"],
        fontSize=14,
        textColor=BLANCO,
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica-Bold",
        leading=18,
        leftIndent=0,
    )
    subseccion = ParagraphStyle(
        "Subseccion",
        parent=base["Heading2"],
        fontSize=11,
        textColor=VERDE_OSCURO,
        spaceBefore=8,
        spaceAfter=3,
        fontName="Helvetica-Bold",
        leading=14,
        leftIndent=0,
    )
    cuerpo = ParagraphStyle(
        "Cuerpo",
        parent=base["Normal"],
        fontSize=11,
        textColor=NEGRO,
        spaceAfter=4,
        fontName="Helvetica",
        leading=15,
        leftIndent=4,
    )
    codigo = ParagraphStyle(
        "Codigo",
        parent=base["Code"],
        fontSize=10,
        textColor=AZUL_MEDIO,
        backColor=AZUL_CLARO,
        fontName="Courier-Bold",
        leading=14,
        leftIndent=8,
        rightIndent=8,
        spaceAfter=2,
        spaceBefore=2,
        borderPad=4,
    )
    bot_resp = ParagraphStyle(
        "BotResp",
        parent=base["Normal"],
        fontSize=10,
        textColor=VERDE_OSCURO,
        backColor=VERDE_CLARO,
        fontName="Courier",
        leading=13,
        leftIndent=8,
        rightIndent=8,
        spaceAfter=2,
        spaceBefore=2,
        borderPad=4,
    )
    nota = ParagraphStyle(
        "Nota",
        parent=base["Normal"],
        fontSize=10,
        textColor=NARANJA,
        fontName="Helvetica-Oblique",
        leading=13,
        leftIndent=4,
        spaceAfter=3,
    )
    pie = ParagraphStyle(
        "Pie",
        parent=base["Normal"],
        fontSize=8,
        textColor=GRIS_LINEA,
        alignment=TA_CENTER,
        fontName="Helvetica",
        leading=11,
    )
    return {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "seccion": seccion,
        "subseccion": subseccion,
        "cuerpo": cuerpo,
        "codigo": codigo,
        "bot_resp": bot_resp,
        "nota": nota,
        "pie": pie,
    }


# ─── Helpers ───────────────────────────────────────────────────────────────────

def header_section(texto, st):
    """Encabezado de seccion con fondo verde."""
    data = [[Paragraph(texto, st["seccion"])]]
    tbl = Table(data, colWidths=[17.5 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VERDE_MEDIO),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tbl


def cmd(texto, st):
    """Bloque de comando (texto que escribe el usuario)."""
    return Paragraph(f"  Tu: {texto}", st["codigo"])


def bot(texto, st):
    """Bloque de respuesta del bot."""
    return Paragraph(f"  Bot: {texto}", st["bot_resp"])


def vieta(texto, st):
    """Punto con bullet."""
    return Paragraph(f"  * {texto}", st["cuerpo"])


def sp(n=4):
    return Spacer(1, n)


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=GRIS_LINEA, spaceAfter=4, spaceBefore=4)


def comando_tabla(filas, st):
    """Tabla compacta comando | descripcion."""
    data = [["Escribis", "Que hace el bot"]]
    for f in filas:
        data.append(f)
    tbl = Table(data, colWidths=[7.5 * cm, 10 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), VERDE_OSCURO),
        ("TEXTCOLOR",     (0, 0), (-1, 0), BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("FONTNAME",      (0, 1), (-1, -1), "Courier"),
        ("BACKGROUND",    (0, 1), (-1, -1), GRIS_FONDO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [GRIS_FONDO, BLANCO]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRIS_LINEA),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    return tbl


# ─── Construccion del contenido ────────────────────────────────────────────────

def build_story(st):
    story = []

    # ── Portada ────────────────────────────────────────────────────────────────
    story.append(sp(10))
    story.append(Paragraph("Guia del Bot", st["titulo"]))
    story.append(Paragraph("Huerta & Animales", st["titulo"]))
    story.append(sp(6))
    story.append(Paragraph("Finca La Palma y El Tucan", st["subtitulo"]))
    story.append(sp(4))
    story.append(Paragraph("Bot de Telegram: @HuertaInteligentebot", st["subtitulo"]))
    story.append(sp(6))
    story.append(HRFlowable(width="60%", thickness=2, color=VERDE_MEDIO, spaceAfter=6, spaceBefore=6))
    story.append(Paragraph("Guia para Jhon — escrita en lenguaje simple", st["nota"]))
    story.append(sp(20))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 1 — Como funciona
    # ══════════════════════════════════════════════════════════════════════════
    story.append(KeepTogether([
        header_section("1.  Como funciona el bot", st),
        sp(4),
        Paragraph("El bot es como un asistente por Telegram. Le escribis lo que queres hacer "
                  "con la huerta o los animales, y el entiende. No hay comandos complicados — "
                  "escribis en espanol normal.", st["cuerpo"]),
        sp(6),
    ]))

    reglas = [
        ("No importan mayusculas ni tildes",
         "Escribi  cama 1  o  CAMA 1  o  Cama 1  — es lo mismo."),
        ("El bot siempre confirma antes de guardar",
         "Te pregunta: Confirmas? (si/no). Responde  si  para guardar o  no  para cancelar."),
        ("Palabras para confirmar",
         "si / ok / dale / listo / confirmo  — todas sirven."),
        ("Palabras para cancelar",
         "no / cancela / cancelar"),
        ("Consultas no piden confirmacion",
         "Si solo estas mirando datos (ej: cuantos pollitos), el bot responde directo."),
        ("Si no respondes en 10 minutos",
         "El bot olvida la operacion. Hay que empezar de nuevo."),
    ]
    for titulo_r, desc in reglas:
        story.append(KeepTogether([
            Paragraph(f"<b>{titulo_r}</b>", st["cuerpo"]),
            Paragraph(f"    {desc}", st["nota"]),
            sp(3),
        ]))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 2 — Huerta: Consultas
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(6))
    story.append(header_section("2.  Huerta — Consultar informacion", st))
    story.append(sp(4))
    story.append(Paragraph("Estos comandos solo muestran informacion, no cambian nada:", st["cuerpo"]))
    story.append(sp(4))
    story.append(comando_tabla([
        ["cama 1",       "Muestra las plantas de la Cama 1"],
        ["cama 5",       "Muestra las plantas de la Cama 5 (cualquier numero 1-12)"],
        ["invernadero",  "Informacion del invernadero"],
        ["listar camas", "Resumen de todas las camas con sus plantas"],
        ["resumen",      "Igual que listar camas"],
    ], st))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 3 — Huerta: Cambiar plantas
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("3.  Huerta — Cambiar plantas", st))
    story.append(sp(4))

    cambios = [
        ("Reemplazar TODAS las plantas de una cama",
         "cama 1 cambiar plantas por repollo y cebollín",
         "Vas a cambiar Cama 1 a: Repollo, Cebollin. Confirmas?"),
        ("Dejar una cama vacia",
         "cama 9 sin ocupacion",
         "Vas a dejar Cama 9 vacia. Confirmas?"),
        ("Agregar una planta SIN borrar las otras",
         "cama 5 agregar albahaca",
         "Vas a agregar Albahaca a Cama 5. Confirmas?"),
        ("Quitar una planta especifica",
         "cama 1 quitar cebollin",
         "Vas a quitar Cebollin de Cama 1. Confirmas?"),
    ]
    for desc, ejemplo_cmd, ejemplo_bot in cambios:
        story.append(KeepTogether([
            Paragraph(f"<b>{desc}</b>", st["subseccion"]),
            cmd(ejemplo_cmd, st),
            bot(ejemplo_bot, st),
            sp(5),
        ]))

    story.append(Paragraph(
        "IMPORTANTE: Si escribis una planta generica (ej: repollo o tomate), el bot "
        "te pregunta que variedad. Solo responde: morado, verde, cherry, etc.",
        st["nota"]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 4 — Huerta: Bitacora
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(6))
    story.append(header_section("4.  Huerta — Registrar en bitacora", st))
    story.append(sp(4))
    story.append(Paragraph("Usa estos comandos para guardar lo que hiciste en la huerta:", st["cuerpo"]))
    story.append(sp(4))
    story.append(comando_tabla([
        ["cosecha cama 3 lechuga 2 kg",   "Registra una cosecha con peso"],
        ["coseche 20 tomates del invernadero", "Cosecha sin peso exacto"],
        ["riegue la cama 5",              "Registra que regaste esa cama"],
        ["sembre albahaca en la cama 9",  "Registra una siembra"],
        ["plaga cama 4 pulgones",         "Alerta de plaga en esa cama"],
        ["hay babosas en la cama 3",      "Tambien se registra como plaga"],
        ["la cama 6 se ve amarilla",      "Observacion general"],
        ["fertilice la cama 1 con compost", "Registra fertilizacion"],
    ], st))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 5 — Animales: Consultas
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("5.  Animales — Consultar inventario", st))
    story.append(sp(4))
    story.append(comando_tabla([
        ["animales",           "Resumen de todos los animales en la finca"],
        ["cuantos pollitos",   "Solo la cantidad de pollitos activos"],
        ["cuantas gallinas",   "Cantidad de gallinas activas"],
        ["cuantos gallos",     "Cantidad de gallos activos"],
        ["cuantos conejos",    "Cantidad de conejos activos"],
        ["cuantas larvas",     "Lotes de mosca soldado (BSF)"],
    ], st))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 6 — Animales: Nacimientos y muertes
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("6.  Animales — Nacimientos y muertes", st))
    story.append(sp(4))

    story.append(Paragraph("<b>Cuando nacen o llegan animales:</b>", st["subseccion"]))
    for ej in ["nacieron 3 pollitos", "compre 10 gallinas ponedoras", "me regalaron 2 conejos"]:
        story.append(cmd(ej, st))
    story.append(sp(6))

    story.append(Paragraph("<b>Cuando muere un animal:</b>", st["subseccion"]))
    for ej in ["murio 1 pollito", "se murieron 3 conejos", "perdi 1 gallo"]:
        story.append(cmd(ej, st))
    story.append(sp(4))
    story.append(Paragraph(
        "El bot marca automaticamente los ultimos animales activos de ese tipo como fallecidos.",
        st["nota"]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 7 — Animales: Huevos
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("7.  Animales — Registrar huevos", st))
    story.append(sp(4))

    story.append(Paragraph(
        "Si no decis cuantos estaban rotos, el bot pregunta:", st["cuerpo"]))
    story.append(sp(3))
    story.append(KeepTogether([
        cmd("hoy puse 14 huevos", st),
        bot("Hubo huevos rotos? (numero o 'no')", st),
        cmd("2", st),
        bot("Vas a registrar: 14 huevos (2 rotos). Confirmas?", st),
        cmd("si", st),
        bot("Huevos registrados: 14 (2 rotos).", st),
        sp(5),
    ]))

    story.append(Paragraph(
        "Si ya sabes los rotos, los pones directamente:", st["cuerpo"]))
    story.append(sp(3))
    for ej in ["14 huevos 2 rotos", "20 huevos ninguno roto", "hoy 10 huevos sin rotos"]:
        story.append(cmd(ej, st))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 8 — Animales: Ventas
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("8.  Animales — Ventas", st))
    story.append(sp(4))
    story.append(Paragraph(
        "Cuando vendes un animal, escribe cuantos y a que precio:", st["cuerpo"]))
    story.append(sp(3))
    for ej in ["vendi 2 gallinas a 30000 cada una", "vendi 1 gallo por 25000", "vendi 5 pollitos"]:
        story.append(cmd(ej, st))
    story.append(sp(4))
    story.append(Paragraph(
        "El bot marca esos animales como vendidos y registra el ingreso en actividades.",
        st["nota"]
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 9 — Animales: Gastos
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("9.  Animales — Gastos", st))
    story.append(sp(4))
    story.append(Paragraph(
        "Para registrar lo que gastaste en la finca:", st["cuerpo"]))
    story.append(sp(3))
    for ej in [
        "compre maiz por 75000",
        "pague veterinario 150000",
        "compre concentrado por 120000",
        "gaste 40000 en vacunas",
    ]:
        story.append(cmd(ej, st))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 10 — Animales: Vacunacion
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("10. Animales — Vacunacion y salud", st))
    story.append(sp(4))
    story.append(Paragraph(
        "Para registrar vacunas, desparasitaciones o revisiones:", st["cuerpo"]))
    story.append(sp(3))
    for ej in [
        "vacune las 4 gallinas contra newcastle",
        "desparasite los pollitos con ivermectina",
        "revision veterinaria de los conejos",
    ]:
        story.append(cmd(ej, st))

    # ══════════════════════════════════════════════════════════════════════════
    # SECCION 11 — Ejemplos de conversaciones reales
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sp(8))
    story.append(header_section("11. Ejemplos completos de conversacion", st))
    story.append(sp(4))

    # Ejemplo A
    story.append(KeepTogether([
        Paragraph("<b>Ejemplo A — Cambiar plantas de una cama</b>", st["subseccion"]),
        cmd("cama 11 cambiar plantas por rucula y espinaca", st),
        bot("Vas a cambiar Cama 11 a:  * Rucula  * Espinaca. Confirmas? (si/no)", st),
        cmd("si", st),
        bot("Cama actualizada.", st),
        sp(6),
    ]))

    # Ejemplo B
    story.append(KeepTogether([
        Paragraph("<b>Ejemplo B — Registrar cosecha</b>", st["subseccion"]),
        cmd("cosecha cama 3 lechuga crespa 2 kg", st),
        bot("Vas a registrar: Cosecha · Cama 3 — 2 kg de Lechuga Crespa. Confirmas?", st),
        cmd("si", st),
        bot("Registrado en bitacora.", st),
        sp(6),
    ]))

    # Ejemplo C
    story.append(KeepTogether([
        Paragraph("<b>Ejemplo C — Registrar huevos con rotos</b>", st["subseccion"]),
        cmd("hoy puse 14 huevos", st),
        bot("Hubo huevos rotos? (numero o 'no')", st),
        cmd("1", st),
        bot("Vas a registrar: 14 huevos (1 roto) en Gallinero. Confirmas?", st),
        cmd("si", st),
        bot("Huevos registrados: 14 (1 roto).", st),
        sp(6),
    ]))

    # Ejemplo D
    story.append(KeepTogether([
        Paragraph("<b>Ejemplo D — Nacimiento y despues consulta</b>", st["subseccion"]),
        cmd("nacieron 5 pollitos", st),
        bot("Vas a registrar: 5 pollitos nuevos. Confirmas?", st),
        cmd("dale", st),
        bot("Registrados 5 pollitos activos.", st),
        sp(4),
        cmd("cuantos pollitos", st),
        bot("34 pollitos activos", st),
        sp(6),
    ]))

    # Ejemplo E — planta ambigua
    story.append(KeepTogether([
        Paragraph("<b>Ejemplo E — El bot pregunta por variedad</b>", st["subseccion"]),
        cmd("cama 12 agregar tomate", st),
        bot("Que tomate?  * Tomate San Marzano  * Tomate Cherry  * Tomate Chonto", st),
        cmd("cherry", st),
        bot("Vas a agregar Tomate Cherry a Cama 12. Confirmas?", st),
        cmd("si", st),
        bot("Cama actualizada.", st),
        sp(6),
    ]))

    # ── Pie de pagina / nota final ─────────────────────────────────────────────
    story.append(sp(8))
    story.append(hr())
    story.append(Paragraph(
        "Si el bot no entiende, intenta escribir el comando mas parecido a los ejemplos de esta guia.",
        st["nota"]
    ))
    story.append(sp(3))
    story.append(Paragraph(
        "Finca La Palma y El Tucan — Zipacon, Cundinamarca  |  Bot: @HuertaInteligentebot  |  2026",
        st["pie"]
    ))

    return story


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Guia del Bot — Huerta & Animales",
        author="Cerebro Claude Code",
        subject="Finca La Palma y El Tucan",
    )

    st = build_styles()
    story = build_story(st)

    doc.build(story)
    print(f"PDF generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
