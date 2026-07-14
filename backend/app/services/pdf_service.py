"""Generacion de PDF de expediente EDD (issue #92, prueba UX-05).

Usa fpdf2 (puro Python). Los core fonts son latin-1, por lo que todo texto
pasa por _s() para reemplazar caracteres fuera de ese rango.
"""
from datetime import datetime

from fpdf import FPDF

from app.models.models import Cliente, Documento, EventoAuditoria, Expediente

_GRIS = (100, 100, 100)
_NEGRO = (0, 0, 0)
_COLOR_RIESGO = {
    "bajo": (22, 163, 74),
    "medio": (202, 138, 4),
    "alto": (220, 38, 38),
}


def _s(texto) -> str:
    if texto is None or texto == "":
        return "N/A"
    return str(texto).encode("latin-1", "replace").decode("latin-1")


class _ExpedientePDF(FPDF):

    def header(self):
        self.set_font("helvetica", "B", 14)
        self.cell(0, 8, "Sistema de Diligencia Debida Reforzada (EDD)", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.set_text_color(*_GRIS)
        self.cell(0, 5, "Cumplimiento AML/CFT - Ley 23/2015 y Ley 254/2021 - Panama",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*_NEGRO)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(*_GRIS)
        self.cell(0, 10, f"Documento confidencial - Pagina {self.page_no()}/{{nb}}", align="C")

    def titulo_seccion(self, texto: str):
        self.set_font("helvetica", "B", 11)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 7, _s(texto), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def fila(self, etiqueta: str, valor):
        self.set_font("helvetica", "", 9)
        self.set_text_color(*_GRIS)
        self.cell(60, 5.5, _s(etiqueta))
        self.set_text_color(*_NEGRO)
        self.set_font("helvetica", "B", 9)
        self.multi_cell(0, 5.5, _s(valor), new_x="LMARGIN", new_y="NEXT")


def generar_pdf_expediente(
    expediente: Expediente,
    cliente: Cliente,
    documentos: list[Documento],
    eventos: list[EventoAuditoria],
) -> bytes:
    pdf = _ExpedientePDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Encabezado del expediente
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 7, _s(f"Expediente {expediente.numero_expediente}"),
             new_x="LMARGIN", new_y="NEXT")
    nivel = expediente.nivel_riesgo.value if expediente.nivel_riesgo else "N/A"
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(*_COLOR_RIESGO.get(nivel, _NEGRO))
    score = f" (score {expediente.score_riesgo:.0f})" if expediente.score_riesgo is not None else ""
    pdf.cell(0, 6, _s(f"Nivel de riesgo: {nivel.upper()}{score}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_NEGRO)
    pdf.ln(3)

    pdf.titulo_seccion("I. Identificacion del Cliente")
    nombre = f"{cliente.nombre} {cliente.apellido or ''}".strip()
    if cliente.razon_social:
        nombre = f"{cliente.razon_social} ({nombre})"
    pdf.fila("Nombre / Razon social:", nombre)
    pdf.fila("Tipo de persona:", cliente.tipo_persona.value if cliente.tipo_persona else None)
    tipo_id = cliente.tipo_identificacion.value if cliente.tipo_identificacion else ""
    pdf.fila("Identificacion:", f"{tipo_id} {cliente.numero_identificacion}")
    pdf.fila("Nacionalidad:", cliente.nacionalidad)
    pdf.fila("Pais de residencia:", cliente.pais_residencia)
    pdf.fila("PEP:", "SI - " + (cliente.cargo_pep or cliente.relacion_pep or "sin detalle")
             if cliente.es_pep else "No")
    pdf.ln(2)

    pdf.titulo_seccion("II. Informacion Financiera")
    pdf.fila("Actividad economica:", cliente.actividad_economica)
    pdf.fila("Sector economico:", cliente.sector_economico)
    pdf.fila("Ingresos anuales:", f"${cliente.ingresos_anuales:,.2f}"
             if cliente.ingresos_anuales is not None else None)
    pdf.fila("Patrimonio:", f"${cliente.patrimonio:,.2f}"
             if cliente.patrimonio is not None else None)
    pdf.fila("Origen de fondos:", cliente.origen_fondos)
    pdf.ln(2)

    beneficiarios = cliente.beneficiarios_finales or []
    pdf.titulo_seccion(f"III. Beneficiarios Finales ({len(beneficiarios)})")
    if beneficiarios:
        for bf in beneficiarios:
            pep = " [PEP]" if bf.es_pep else ""
            pdf.fila(
                f"{bf.porcentaje_participacion:.0f}% - {bf.tipo_control or 'Accionista'}:",
                f"{bf.nombre} {bf.apellido or ''} ({bf.numero_identificacion}){pep}",
            )
    else:
        pdf.fila("Sin beneficiarios registrados", "")
    pdf.ln(2)

    pdf.titulo_seccion("IV. Estado del Expediente")
    pdf.fila("Estado:", expediente.estado.value if expediente.estado else None)
    pdf.fila("Requiere aprobacion gerencial:",
             "Si" if expediente.requiere_aprobacion_gerencial else "No")
    pdf.fila("Aprobado por:", expediente.aprobado_por)
    pdf.fila("Comentario:", expediente.comentario_aprobacion)
    pdf.fila("Creado:", expediente.created_at.strftime("%Y-%m-%d %H:%M UTC")
             if expediente.created_at else None)
    pdf.fila("Version:", expediente.version)
    pdf.ln(2)

    pdf.titulo_seccion(f"V. Documentos Adjuntos ({len(documentos)})")
    if documentos:
        for doc in documentos:
            pdf.fila(f"{doc.tipo_documento}:", doc.nombre_archivo)
            pdf.set_font("helvetica", "", 7)
            pdf.set_text_color(*_GRIS)
            pdf.cell(60, 4, "")
            pdf.cell(0, 4, _s(f"SHA-256: {doc.hash_sha256}"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*_NEGRO)
    else:
        pdf.fila("Sin documentos adjuntos", "")
    pdf.ln(2)

    ultimos = sorted(eventos, key=lambda e: e.created_at or datetime.min, reverse=True)[:15]
    pdf.titulo_seccion(f"VI. Trazabilidad (ultimos {len(ultimos)} de {len(eventos)} eventos)")
    for ev in ultimos:
        fecha = ev.created_at.strftime("%Y-%m-%d %H:%M") if ev.created_at else "N/A"
        pdf.fila(f"{fecha} - {ev.usuario}:", ev.accion)

    pdf.ln(4)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(*_GRIS)
    pdf.multi_cell(
        0, 4,
        _s("Generado por el Sistema EDD. Registro sujeto a conservacion minima de 5 anos "
           "segun Ley 23 de 2015. La trazabilidad completa es inmutable (WORM)."),
    )

    return bytes(pdf.output())
