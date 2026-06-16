# Plan de Pruebas - Sistema de Diligencia Reforzada (EDD)

---

## 1. Metricas

| Area | Metrica | Definicion Tecnica | Formula de Calculo |
|------|---------|---------------------|-------------------|
| Requerimientos | Cobertura | % de requisitos documentados vs. identificados | (Requisitos documentados ÷ Requisitos identificados) × 100 |
| Requerimientos | Volatilidad | Nº de cambios en requisitos durante el ciclo | Conteo de modificaciones registradas |
| Requerimientos | Trazabilidad | % de requisitos vinculados a fuente legal | (Requisitos con referencia legal ÷ Total requisitos) × 100 |
| Diseno | Complejidad ciclomatica | Nº de caminos independientes en el flujo | V(G) = E − N + 2 (E=aristas, N=nodos) |
| Diseno | Acoplamiento y cohesion | Dependencia entre modulos y especializacion interna | Evaluacion cualitativa (bajo/medio/alto) |
| Diseno | Diagramas actualizados | % de diagramas UML alineados con requisitos | (Diagramas actualizados ÷ Total diagramas) × 100 |
| Codigo | Densidad de defectos | Defectos por cada mil lineas de codigo (KLOC) | Nº defectos ÷ KLOC |
| Codigo | Code smells | Patrones que afectan mantenibilidad | Conteo de incidencias detectadas |
| Codigo | Vulnerabilidades | Fallos de seguridad detectados | Conteo de vulnerabilidades |

---

## 2. Pruebas Alfa

| ID | Descripcion | Criterio de Exito | Tipo |
|----|-------------|-------------------|------|
| ALF-01 | Validar sumatoria de participaciones BeneficiarioFinal <= 100% | La suma de porcentajes no puede exceder 100%; error si > 100% | Unitario |
| ALF-02 | Verificar obligatoriedad de campos criticos | No permite guardar si nombre, numero_identificacion o tipo_identificacion estan vacios | Unitario |
| ALF-03 | Validar coherencia entre ingresos y volumen transaccional | Si ingresos < volumen esperado, mostrar warning | Integracion |
| ALF-04 | Confirmar que no se pueda cerrar formulario sin aprobacion si riesgo = alto | Expedientes con nivel_riesgo=alto requieren estado=APROBADO con comentario | Integracion |
| ALF-05 | Validar integridad del log de auditoria | Cada evento tiene fecha UTC, hora, usuario e ip_address completos | Sistema |
| ALF-06 | Validar autenticacion por roles | Admin, Oficial Cumplimiento y Alta Gerencia tienen permisos diferenciados | Seguridad |
| ALF-07 | Confirmar cifrado de datos sensibles | hashed_password y mfa_secret nunca se retornan en responses API | Seguridad |
| ALF-08 | Verificar trazabilidad de modificaciones | Cada PUT genera EventoAuditoria con detalles del cambio | Integracion |
| ALF-09 | Validar conservacion automatica de registros por 5 anos | Registros tienen created_at; duracion minima 5 anos segun Ley 23 | Sistema |

---

## 3. Pruebas Beta

| ID | Descripcion | Criterio de Exito | Tipo |
|----|-------------|-------------------|------|
| BET-01 | Validar adjunto de evidencia documental de origen de fondos | Modulo financiera requiere documento adjunto antes de guardar | Funcional |
| BET-02 | Confirmar aprobacion de alta gerencia en clientes de alto riesgo | Si es_pep=true, expediente requiere_aprobacion_gerencial=true | Funcional |
| BET-03 | Validar contra listas restrictivas (OFAC, ONU, UE) | Sin API gratuita disponible - marcar como No implementado en documentacion | N/A |
| BET-04 | Confirmar trazabilidad legal de cada campo del formulario | Cada campo tiene referencia a articulo legal (Ley 23, Ley 254) | Documentacion |

---

## 4. Pruebas UX

| ID | Descripcion | Criterio de Exito | Tipo |
|----|-------------|-------------------|------|
| UX-01 | Validar feedback inmediato en campos obligatorios | Errores visibles en tiempo real al perder foco de campo vacio | UX |
| UX-02 | Confirmar activacion automatica de secciones ampliadas si cliente es PEP | Checkbox es_pep activa campos cargo_pep, relacion_pep, pais_residencia_fiscal | Funcional |
| UX-03 | Validar consistencia visual (colores, iconografia, dark mode) | Paleta de colores consistente en todas las paginas | UX |
| UX-04 | Prueba de navegacion en grafo societario con multiples niveles | Grafo permite drill-down 3+ niveles de profundidad (drag, zoom, pan) | UX |
| UX-05 | Validar exportacion de expediente en PDF/XML | Boton exportar genera archivo descargable valido | Sistema |
| UX-06 | Confirmar responsividad en moviles y tablets | Layout funcional en 320px (mobile), 768px (tablet), 1024px+ (desktop) | UX |
| UX-07 | Validar accesibilidad (lectores de pantalla, contraste WCAG) | aria-labels presentes, focus visible, contraste 4.5:1 | Accesibilidad |

---

## 5. Resumen

| Categoria | Pruebas |
|-----------|---------|
| Alfa | 9 |
| Beta | 4 |
| UX | 7 |
| **Total** | **20** |

---

## 6. Estados de Prueba

| Estado | Descripcion |
|--------|-------------|
| PENDIENTE | Prueba no ejecutada |
| EN EJECUCION | Prueba en curso |
| APROBADO | Prueba Passed |
| FALLIDO | Prueba failed - requiere fix |
| N/A | No aplicable |

---

**Fecha creacion:** 2026-05-31
**Proyecto:** Diligencia Reforzada EDD - Panama AML/CFT