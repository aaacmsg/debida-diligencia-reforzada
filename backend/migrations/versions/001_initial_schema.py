"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'clientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_persona', sa.Enum('NATURAL', 'JURIDICA', name='tipopersona'), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('apellido', sa.String(255), nullable=True),
        sa.Column('razon_social', sa.String(255), nullable=True),
        sa.Column('tipo_identificacion', sa.Enum('CEDULA', 'PASAPORTE', 'RUC', name='tipoidentificacion'), nullable=False),
        sa.Column('numero_identificacion', sa.String(50), nullable=False),
        sa.Column('fecha_nacimiento', sa.DateTime(), nullable=True),
        sa.Column('nacionalidad', sa.String(100), nullable=True),
        sa.Column('pais_residencia', sa.String(100), nullable=True),
        sa.Column('direccion', sa.Text(), nullable=True),
        sa.Column('telefono', sa.String(50), nullable=True),
        sa.Column('correo', sa.String(255), nullable=True),
        sa.Column('es_pep', sa.Boolean(), default=False),
        sa.Column('cargo_pep', sa.String(255), nullable=True),
        sa.Column('relacion_pep', sa.String(255), nullable=True),
        sa.Column('pais_residencia_fiscal', sa.String(100), nullable=True),
        sa.Column('actividad_economica', sa.String(255), nullable=True),
        sa.Column('sector_economico', sa.String(100), nullable=True),
        sa.Column('ingresos_anuales', sa.Float(), nullable=True),
        sa.Column('patrimonio', sa.Float(), nullable=True),
        sa.Column('origen_fondos', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clientes_numero_identificacion', 'clientes', ['numero_identificacion'], unique=True)
    op.create_index('ix_clientes_id', 'clientes', ['id'])

    op.create_table(
        'funcionarios_publicos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cedula', sa.String(50), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('apellido', sa.String(255), nullable=False),
        sa.Column('cargo_permanente', sa.String(255), nullable=True),
        sa.Column('cargo_designacion', sa.String(255), nullable=False),
        sa.Column('institucion', sa.String(255), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=True),
        sa.Column('fecha_final', sa.DateTime(), nullable=True),
        sa.Column('numero_resolucion', sa.String(100), nullable=True),
        sa.Column('es_pep', sa.Boolean(), default=False),
        sa.Column('nivel_cargo', sa.String(50), nullable=True),
        sa.Column('downloaded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('source', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_funcionarios_publicos_cedula', 'funcionarios_publicos', ['cedula'])
    op.create_index('ix_funcionarios_publicos_id', 'funcionarios_publicos', ['id'])

    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('rol', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('mfa_enabled', sa.Boolean(), default=False),
        sa.Column('mfa_secret', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usuarios_username', 'usuarios', ['username'], unique=True)
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)
    op.create_index('ix_usuarios_id', 'usuarios', ['id'])

    op.create_table(
        'expedientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('numero_expediente', sa.String(50), nullable=False),
        sa.Column('nivel_riesgo', sa.Enum('BAJO', 'MEDIO', 'ALTO', name='nivelriesgo'), default='BAJO'),
        sa.Column('score_riesgo', sa.Float(), nullable=True),
        sa.Column('variables_riesgo', sa.JSON(), nullable=True),
        sa.Column('estado', sa.Enum('BORRADOR', 'PENDIENTE_INFO', 'PENDIENTE_REVISION', 'PENDIENTE_GERENCIA', 'APROBADO', 'RECHAZADO', name='estadoexpediente'), default='BORRADOR'),
        sa.Column('requiere_aprobacion_gerencial', sa.Boolean(), default=False),
        sa.Column('aprobado_por', sa.String(100), nullable=True),
        sa.Column('fecha_aprobacion', sa.DateTime(), nullable=True),
        sa.Column('comentario_aprobacion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_expedientes_numero_expediente', 'expedientes', ['numero_expediente'], unique=True)
    op.create_index('ix_expedientes_id', 'expedientes', ['id'])

    op.create_table(
        'beneficiarios_finales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('apellido', sa.String(255), nullable=True),
        sa.Column('numero_identificacion', sa.String(50), nullable=False),
        sa.Column('porcentaje_participacion', sa.Float(), nullable=False),
        sa.Column('tipo_control', sa.String(100), nullable=True),
        sa.Column('pais_residencia', sa.String(100), nullable=True),
        sa.Column('es_pep', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_beneficiarios_finales_id', 'beneficiarios_finales', ['id'])

    op.create_table(
        'documentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=False),
        sa.Column('tipo_documento', sa.String(100), nullable=False),
        sa.Column('nombre_archivo', sa.String(255), nullable=False),
        sa.Column('ruta_archivo', sa.String(500), nullable=False),
        sa.Column('hash_sha256', sa.String(64), nullable=False),
        sa.Column('tamano_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('uploaded_by', sa.String(100), nullable=True),
        sa.Column('malware_scan_result', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documentos_id', 'documentos', ['id'])

    op.create_table(
        'eventos_auditoria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=True),
        sa.Column('usuario', sa.String(100), nullable=False),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('detalles', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eventos_auditoria_created_at', 'eventos_auditoria', ['created_at'])
    op.create_index('ix_eventos_auditoria_id', 'eventos_auditoria', ['id'])

    op.create_table(
        'alertas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=True),
        sa.Column('tipo_alerta', sa.String(100), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('nivel', sa.String(20), nullable=False),
        sa.Column('leida', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alertas_created_at', 'alertas', ['created_at'])
    op.create_index('ix_alertas_id', 'alertas', ['id'])


def downgrade() -> None:
    op.drop_table('alertas')
    op.drop_table('eventos_auditoria')
    op.drop_table('documentos')
    op.drop_table('beneficiarios_finales')
    op.drop_table('expedientes')
    op.drop_table('usuarios')
    op.drop_table('funcionarios_publicos')
    op.drop_table('clientes')