"""Seed de datos de demostracion para el sistema EDD.

Crea usuarios por rol, clientes (PEP y no PEP), beneficiarios finales
compartidos entre empresas (para que el grafo muestre relaciones),
expedientes en distintos estados, documentos con hash SHA-256 real,
eventos de auditoria, alertas y funcionarios publicos para la busqueda PEP.

Uso:
    cd backend && python scripts/seed_demo.py
    # o con Docker:
    docker-compose exec backend python scripts/seed_demo.py

Idempotente: si ya existe el cliente marcador (cedula 8-701-2244) no hace nada.
"""
import hashlib
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine
from app.core.security import get_password_hash
from app.models.models import (
    Alerta,
    BeneficiarioFinal,
    Cliente,
    Documento,
    EstadoExpediente,
    EventoAuditoria,
    Expediente,
    FuncionarioPublico,
    NivelRiesgo,
    TipoIdentificacion,
    TipoPersona,
    Usuario,
)
from app.schemas.schemas import CalculoRiesgoRequest
from app.services.riesgo_service import riesgo_service

MARCADOR_SEED = "8-701-2244"

MINIMAL_PDF = (
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"xref\n0 4\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF\n"
)


def crear_usuarios(db: Session) -> None:
    usuarios = [
        ("oficial", "oficial@diligencia.pa", "Oficial de Cumplimiento", "oficial_cumplimiento", "oficial123"),
        ("gerencia", "gerencia@diligencia.pa", "Alta Gerencia", "alta_gerencia", "gerencia123"),
    ]
    for username, email, full_name, rol, password in usuarios:
        if not db.query(Usuario).filter(Usuario.username == username).first():
            db.add(Usuario(
                username=username,
                email=email,
                full_name=full_name,
                rol=rol,
                hashed_password=get_password_hash(password),
                is_active=True,
            ))
    db.commit()
    print("Usuarios: admin/admin123 (startup), oficial/oficial123, gerencia/gerencia123")


def crear_cliente_con_expediente(db: Session, datos: dict, vinculos_pep: int,
                                 estado_final: EstadoExpediente | None,
                                 numero: str) -> tuple[Cliente, Expediente]:
    """Replica la logica de POST /clientes/: riesgo calculado + regla PEP."""
    cliente = Cliente(**datos)
    db.add(cliente)
    db.flush()

    riesgo = riesgo_service.calcular_riesgo(CalculoRiesgoRequest(
        pais_residencia=datos.get("pais_residencia"),
        pais_residencia_fiscal=datos.get("pais_residencia_fiscal"),
        es_pep=datos.get("es_pep", False),
        cargo_pep=datos.get("cargo_pep"),
        sector_economico=datos.get("sector_economico"),
        actividad_economica=datos.get("actividad_economica"),
        vinculos_pep=vinculos_pep,
        origen_fondos_documentado=bool(datos.get("origen_fondos")),
    ))

    if datos.get("es_pep"):
        nivel = NivelRiesgo.ALTO
        requiere_gerencial = True
        estado = EstadoExpediente.PENDIENTE_GERENCIA
    else:
        nivel = riesgo.nivel_riesgo
        requiere_gerencial = riesgo.nivel_riesgo == NivelRiesgo.ALTO
        estado = (EstadoExpediente.PENDIENTE_GERENCIA
                  if requiere_gerencial else EstadoExpediente.BORRADOR)

    if estado_final is not None:
        estado = estado_final

    expediente = Expediente(
        cliente_id=cliente.id,
        numero_expediente=numero,
        nivel_riesgo=nivel,
        score_riesgo=riesgo.score_total,
        variables_riesgo=riesgo.variables,
        estado=estado,
        requiere_aprobacion_gerencial=requiere_gerencial,
        created_by="oficial",
    )
    db.add(expediente)
    db.flush()

    db.add(EventoAuditoria(
        expediente_id=expediente.id,
        usuario="oficial",
        accion="CREAR_CLIENTE_Y_EXPEDIENTE",
        detalles={
            "cliente_id": cliente.id,
            "numero_expediente": numero,
            "es_pep": datos.get("es_pep", False),
            "nivel_riesgo": nivel.value,
            "score_riesgo": riesgo.score_total,
            "origen": "seed_demo",
        },
        ip_address="127.0.0.1",
    ))
    return cliente, expediente


def crear_documento(db: Session, expediente: Expediente, tipo: str, nombre: str) -> None:
    contenido = MINIMAL_PDF + nombre.encode("utf-8")
    hash_sha256 = hashlib.sha256(contenido).hexdigest()
    os.makedirs(settings.upload_dir, exist_ok=True)
    ruta = os.path.join(settings.upload_dir, f"{hash_sha256}_{nombre}")
    with open(ruta, "wb") as f:
        f.write(contenido)
    db.add(Documento(
        expediente_id=expediente.id,
        tipo_documento=tipo,
        nombre_archivo=nombre,
        ruta_archivo=ruta,
        hash_sha256=hash_sha256,
        tamano_bytes=len(contenido),
        mime_type="application/pdf",
        uploaded_by="oficial",
    ))


def crear_funcionarios(db: Session) -> None:
    funcionarios = [
        ("8-702-3355", "Juan", "Gomez", "Ministro de Obras Publicas", "Ministerio de Obras Publicas", "alto"),
        ("8-410-0987", "Carmen", "Rodriguez", "Directora General", "Caja de Seguro Social", "alto"),
        ("4-215-6631", "Luis", "Herrera", "Magistrado", "Corte Suprema de Justicia", "alto"),
        ("6-118-4520", "Patricia", "Vega", "Jefa de Compras", "Ministerio de Gobierno", "medio"),
        ("8-830-1174", "Ernesto", "Salas", "Coordinador Regional", "Contraloria General", "medio"),
    ]
    for cedula, nombre, apellido, cargo, institucion, nivel in funcionarios:
        db.add(FuncionarioPublico(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            cargo_designacion=cargo,
            institucion=institucion,
            es_pep=True,
            nivel_cargo=nivel,
            source="seed_demo",
        ))
    print(f"Funcionarios publicos: {len(funcionarios)} (Juan Gomez 8-702-3355 coincide con cliente PEP)")


def seed() -> None:
    fecha = datetime.now().strftime("%Y%m%d")
    with Session(engine) as db:
        if db.query(Cliente).filter(Cliente.numero_identificacion == MARCADOR_SEED).first():
            print("El seed ya fue aplicado (existe cliente 8-701-2244). Nada que hacer.")
            return

        crear_usuarios(db)

        # --- Personas naturales ---
        maria, exp_maria = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.NATURAL, nombre="Maria", apellido="Fernandez",
            tipo_identificacion=TipoIdentificacion.CEDULA, numero_identificacion=MARCADOR_SEED,
            nacionalidad="Panama", pais_residencia="Panama",
            direccion="Bella Vista, Ciudad de Panama", telefono="6612-4455",
            correo="maria.fernandez@example.com",
            actividad_economica="Comercio minorista", sector_economico="Comercio",
            ingresos_anuales=48000, patrimonio=120000,
            origen_fondos="Salario y ahorros documentados", created_by="oficial",
        ), vinculos_pep=0, estado_final=EstadoExpediente.PENDIENTE_REVISION,
            numero=f"EDD-{fecha}-SEED0001")

        juan, exp_juan = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.NATURAL, nombre="Juan", apellido="Gomez",
            tipo_identificacion=TipoIdentificacion.CEDULA, numero_identificacion="8-702-3355",
            nacionalidad="Panama", pais_residencia="Panama",
            direccion="Costa del Este, Ciudad de Panama", telefono="6890-1122",
            correo="juan.gomez@example.com",
            es_pep=True, cargo_pep="Ministro de Obras Publicas",
            pais_residencia_fiscal="Panama",
            actividad_economica="Servidor publico", sector_economico="Gobierno",
            ingresos_anuales=96000, patrimonio=850000,
            origen_fondos="Salario publico", created_by="oficial",
        ), vinculos_pep=2, estado_final=None,  # regla PEP: pendiente_gerencia
            numero=f"EDD-{fecha}-SEED0002")

        ana, exp_ana = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.NATURAL, nombre="Ana", apellido="Castillo",
            tipo_identificacion=TipoIdentificacion.CEDULA, numero_identificacion="8-655-7788",
            nacionalidad="Panama", pais_residencia="Panama",
            direccion="San Francisco, Ciudad de Panama", telefono="6755-3344",
            correo="ana.castillo@example.com",
            es_pep=True, cargo_pep=None, relacion_pep="Conyuge de Ministro de Obras Publicas",
            pais_residencia_fiscal="Panama",
            actividad_economica="Bienes raices", sector_economico="Real Estate",
            ingresos_anuales=150000, patrimonio=600000, created_by="oficial",
        ), vinculos_pep=1, estado_final=None,
            numero=f"EDD-{fecha}-SEED0003")

        roberto, exp_roberto = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.NATURAL, nombre="Roberto", apellido="Chen",
            tipo_identificacion=TipoIdentificacion.PASAPORTE, numero_identificacion="PA-9034821",
            nacionalidad="Costa Rica", pais_residencia="Costa Rica",
            direccion="San Jose, Costa Rica", telefono="+506 8822-1100",
            correo="roberto.chen@example.com",
            actividad_economica="Consultoria de software", sector_economico="Servicios",
            ingresos_anuales=72000, patrimonio=200000,
            origen_fondos="Contratos de consultoria documentados", created_by="oficial",
        ), vinculos_pep=0, estado_final=EstadoExpediente.APROBADO,
            numero=f"EDD-{fecha}-SEED0004")
        exp_roberto.aprobado_por = "gerencia"
        exp_roberto.fecha_aprobacion = datetime.utcnow() - timedelta(days=3)
        exp_roberto.comentario_aprobacion = (
            "Cliente de bajo riesgo con origen de fondos completamente documentado. Aprobado."
        )

        # --- Personas juridicas (los beneficiarios compartidos arman el grafo) ---
        constructora, exp_constructora = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.JURIDICA, nombre="Constructora Istmo",
            razon_social="Constructora Istmo S.A.",
            tipo_identificacion=TipoIdentificacion.RUC, numero_identificacion="155612345-2-2019",
            pais_residencia="Panama", direccion="Obarrio, Ciudad de Panama",
            telefono="264-7788", correo="info@constructoraistmo.example.com",
            actividad_economica="Construccion de obras civiles", sector_economico="Construccion",
            ingresos_anuales=2500000, patrimonio=5800000, created_by="oficial",
        ), vinculos_pep=2, estado_final=None,
            numero=f"EDD-{fecha}-SEED0005")

        caribe, exp_caribe = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.JURIDICA, nombre="Inversiones Caribe",
            razon_social="Inversiones Caribe Corp.",
            tipo_identificacion=TipoIdentificacion.RUC, numero_identificacion="155698811-1-2021",
            pais_residencia="Islas Caiman", pais_residencia_fiscal="Islas Caiman",
            direccion="George Town, Islas Caiman", correo="contact@invcaribe.example.com",
            actividad_economica="Inversiones y servicios financieros",
            sector_economico="Servicios Financieros",
            ingresos_anuales=4200000, patrimonio=12000000, created_by="oficial",
        ), vinculos_pep=2, estado_final=None,
            numero=f"EDD-{fecha}-SEED0006")

        orinoco, exp_orinoco = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.JURIDICA, nombre="Comercializadora Orinoco",
            razon_social="Comercializadora Orinoco C.A.",
            tipo_identificacion=TipoIdentificacion.RUC, numero_identificacion="J-40887766-0",
            pais_residencia="Venezuela", pais_residencia_fiscal="Venezuela",
            direccion="Caracas, Venezuela", correo="ventas@orinoco.example.com",
            actividad_economica="Compra y venta de metales preciosos",
            sector_economico="Metales Preciosos",
            ingresos_anuales=1800000, patrimonio=3100000, created_by="oficial",
        ), vinculos_pep=4, estado_final=None,  # alto por score -> pendiente_gerencia
            numero=f"EDD-{fecha}-SEED0007")

        logistica, exp_logistica = crear_cliente_con_expediente(db, dict(
            tipo_persona=TipoPersona.JURIDICA, nombre="Logistica del Pacifico",
            razon_social="Logistica del Pacifico S.A.",
            tipo_identificacion=TipoIdentificacion.RUC, numero_identificacion="155644321-3-2018",
            pais_residencia="Panama", direccion="Zona Libre de Colon",
            telefono="441-2299", correo="operaciones@logpacifico.example.com",
            actividad_economica="Transporte y logistica de carga",
            sector_economico="Transporte",
            ingresos_anuales=980000, patrimonio=1500000,
            origen_fondos="Facturacion comercial documentada", created_by="oficial",
        ), vinculos_pep=0, estado_final=EstadoExpediente.PENDIENTE_REVISION,
            numero=f"EDD-{fecha}-SEED0008")

        # --- Beneficiarios finales: Juan Gomez (PEP) participa en 2 empresas ---
        db.add_all([
            BeneficiarioFinal(cliente_id=constructora.id, nombre="Juan", apellido="Gomez",
                              numero_identificacion="8-702-3355", porcentaje_participacion=40,
                              tipo_control="Accionista", pais_residencia="Panama", es_pep=True),
            BeneficiarioFinal(cliente_id=constructora.id, nombre="Ana", apellido="Castillo",
                              numero_identificacion="8-655-7788", porcentaje_participacion=30,
                              tipo_control="Accionista", pais_residencia="Panama", es_pep=True),
            BeneficiarioFinal(cliente_id=constructora.id, nombre="Felipe", apellido="Mendoza",
                              numero_identificacion="8-512-9900", porcentaje_participacion=30,
                              tipo_control="Accionista", pais_residencia="Panama"),
            BeneficiarioFinal(cliente_id=caribe.id, nombre="Juan", apellido="Gomez",
                              numero_identificacion="8-702-3355", porcentaje_participacion=25,
                              tipo_control="Accionista", pais_residencia="Panama", es_pep=True),
            BeneficiarioFinal(cliente_id=caribe.id, nombre="Sofia", apellido="Duarte",
                              numero_identificacion="8-390-6712", porcentaje_participacion=55,
                              tipo_control="Control efectivo", pais_residencia="Islas Caiman"),
            BeneficiarioFinal(cliente_id=orinoco.id, nombre="Hector", apellido="Rivas",
                              numero_identificacion="V-14556677", porcentaje_participacion=100,
                              tipo_control="Propietario unico", pais_residencia="Venezuela"),
            BeneficiarioFinal(cliente_id=logistica.id, nombre="Roberto", apellido="Chen",
                              numero_identificacion="PA-9034821", porcentaje_participacion=60,
                              tipo_control="Accionista", pais_residencia="Costa Rica"),
            BeneficiarioFinal(cliente_id=logistica.id, nombre="Felipe", apellido="Mendoza",
                              numero_identificacion="8-512-9900", porcentaje_participacion=40,
                              tipo_control="Accionista", pais_residencia="Panama"),
        ])

        # --- Documentos con hash SHA-256 real ---
        crear_documento(db, exp_maria, "identificacion", "cedula_maria_fernandez.pdf")
        crear_documento(db, exp_juan, "declaracion_patrimonial", "declaracion_juan_gomez.pdf")
        crear_documento(db, exp_constructora, "estructura_societaria", "pacto_social_istmo.pdf")
        crear_documento(db, exp_roberto, "origen_fondos", "contratos_consultoria_chen.pdf")

        # --- Alertas ---
        db.add_all([
            Alerta(expediente_id=exp_juan.id, tipo_alerta="pep_detectado", nivel="alta",
                   mensaje="Cliente Juan Gomez identificado como PEP (Ministro de Obras Publicas). "
                           "Requiere aprobacion de Alta Gerencia."),
            Alerta(expediente_id=exp_orinoco.id, tipo_alerta="riesgo_alto", nivel="alta",
                   mensaje="Comercializadora Orinoco: score de riesgo alto (pais sancionado + "
                           "metales preciosos + origen de fondos no documentado)."),
            Alerta(expediente_id=exp_caribe.id, tipo_alerta="vinculo_pep", nivel="media",
                   mensaje="Inversiones Caribe Corp. tiene como beneficiario final a un PEP "
                           "(Juan Gomez, 25% de participacion)."),
            Alerta(expediente_id=exp_maria.id, tipo_alerta="actualizacion_pendiente", nivel="baja",
                   mensaje="Expediente de Maria Fernandez pendiente de revision documental."),
        ])

        # --- Eventos de auditoria adicionales (trazabilidad demo) ---
        db.add_all([
            EventoAuditoria(expediente_id=exp_roberto.id, usuario="gerencia", accion="APROBAR_EXPEDIENTE",
                            detalles={"comentario": exp_roberto.comentario_aprobacion},
                            ip_address="127.0.0.1"),
            EventoAuditoria(expediente_id=exp_juan.id, usuario="oficial", accion="CONSULTA_PEP",
                            detalles={"resultado": "match exacto por cedula 8-702-3355", "score": 100},
                            ip_address="127.0.0.1"),
        ])

        crear_funcionarios(db)
        db.commit()

        resumen = {}
        for exp in db.query(Expediente).all():
            resumen[exp.nivel_riesgo.value] = resumen.get(exp.nivel_riesgo.value, 0) + 1
        print("Seed aplicado: 8 clientes, 8 expedientes, 8 beneficiarios, 4 documentos, "
              "4 alertas y 5 funcionarios publicos.")
        print(f"Distribucion de riesgo: {resumen}")


if __name__ == "__main__":
    seed()
