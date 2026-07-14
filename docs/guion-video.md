# Guion del video: Scrum Review del cierre (máximo 10 minutos)

**Equipo:** César Santiago, Roberto López, Jean Suárez | Ingeniería de Software IV | Prof. María Mosquera | Salón 1GS242

## Requisitos de la profesora que este guion cumple

- Presentación del software actualizado y demostración de lo nuevo del Parcial 2.
- Explicación técnica del estado actual del producto.
- Los tres integrantes aparecen en cámara con participación equitativa (unos 3 minutos cada uno).
- Técnica Scrum Review para el incremento y formato Spick (3 preguntas: avances, aprendizajes, problemas) para el cierre.

## Preparación antes de grabar (checklist)

- [ ] `docker-compose up -d` y seed cargado (`docker-compose exec backend python scripts/seed_demo.py`).
- [ ] Probar el recorrido completo una vez antes de grabar, para no improvisar.
- [ ] Pestañas abiertas y listas: la app en /login, GitHub (pestaña Actions) y el tablero de Projects.
- [ ] Cerrar sesión en la app para empezar desde el login.
- [ ] Cada integrante con cámara y micrófono probados. Grabar en horizontal, pantalla compartida + cámaras.
- [ ] Tener a mano las credenciales: `oficial/oficial123` y `gerencia/gerencia123`.

---

## Bloque 1 (0:00 - 0:40) | Los tres en cámara | Apertura

**César:** "Buenas. Somos el equipo del Sistema de Diligencia Debida Reforzada: César Santiago, Roberto López y Jean Suárez, del salón 1GS242. Este es nuestro Scrum Review de cierre. Nuestro producto es una aplicación de cumplimiento contra el blanqueo de capitales para Panamá, basada en la Ley 23 de 2015. En este video mostramos el incremento del Parcial 2: seguridad por roles, auditoría inmutable, renovación de sesión, exportación a PDF y las pruebas automatizadas corriendo en integración continua. Empezamos con la demostración."

---

## Bloque 2 (0:40 - 4:30) | Demo del incremento (Scrum Review)

### 2.1 Roberto conduce (0:40 - 2:30): flujo del cliente PEP

Pantalla: la aplicación.

1. **Login** como `oficial`. *"Entramos como Oficial de Cumplimiento. El login ahora entrega dos tokens: uno de acceso de una hora y uno de renovación de siete días, así la sesión no se corta mientras trabajas. Además el sistema bloquea la fuerza bruta: más de diez intentos por minuto desde una misma IP y responde error 429."*
2. **Dashboard**. *"Este dashboard era uno de los defectos que corregimos: mostraba todo en cero por un error de serialización. Hoy se ven los 8 expedientes de demostración: 3 de riesgo alto, 2 medio y 3 bajo."*
3. **Nuevo cliente**: abrir el formulario, marcar la casilla **PEP**. *"Al marcar que la persona es políticamente expuesta, el sistema exige cargo, tipo de relación y país de residencia fiscal. Esto viene directo de la Ley 23: un PEP siempre es riesgo alto y siempre pasa por la alta gerencia, sin importar el puntaje."* (No hace falta guardarlo; con mostrar la validación basta.)
4. **Buscar PEP**: cédula `8-702-3355`. *"El sistema cruza contra los datos abiertos del gobierno. Aquí encuentra al ministro Juan Gómez con coincidencia exacta de cédula, score 100."*
5. **Grafo**: *"Y esta es la parte visual: Juan Gómez, el nodo naranja, aparece como accionista de dos empresas distintas. Así un oficial detecta redes societarias que en una tabla no se ven."*

### 2.2 Jean conduce (2:30 - 4:30): aprobación, PDF y auditoría inmutable

1. Cerrar sesión y entrar como `gerencia`. *"Ahora entro como Alta Gerencia, porque con el control de acceso por roles que agregamos, el oficial ya no puede aprobar: si lo intenta, el backend le responde 403 prohibido."*
2. Abrir el expediente **SEED0003** (pendiente de gerencia) → **Aprobar** → escribir el comentario. *"El comentario es obligatorio, el sistema no deja aprobar sin justificación. Queda registrado quién aprobó, cuándo y por qué."*
3. Abrir el expediente **SEED0002** → botón **Exportar PDF** → abrir el PDF descargado. *"Funcionalidad nueva del cierre: el expediente completo en PDF, con el nivel de riesgo, los beneficiarios, el hash de cada documento y la trazabilidad. Sirve para archivarlo o entregarlo al regulador."*
4. Pestaña **Trazabilidad** del mismo expediente. *"Cada acción queda en esta bitácora, y es inmutable: implementamos a nivel del ORM que cualquier intento de modificar o borrar un evento de auditoría lance una excepción. Es el requisito WORM del artículo 21 de la Ley 23, y tiene sus propias pruebas."*

---

## Bloque 3 (4:30 - 6:00) | César conduce: estado técnico del producto

Pantalla: GitHub.

1. **Pestaña Actions**: *"Todo lo que mostramos está verificado automáticamente. Tenemos cuatro workflows: el del backend corre 91 pruebas con 70% de cobertura, el del frontend compila el proyecto, y el nuevo de extremo a extremo levanta el sistema completo en Docker y ejecuta 25 pruebas con un navegador real. Ningún cambio entra si algo de esto falla."*
2. **Pull Request #101**: *"El trabajo del cierre entró en tres Pull Requests. Este es el último: exportación a PDF y las pruebas E2E. Aquí se ven los tres checks en verde y los issues que se cerraron con el merge."*
3. **Tablero de Projects**: *"Y este es el tablero con el backlog: lo entregado está en Done, y lo que queda documentado como trabajo futuro, como las notificaciones por correo, está en Backlog."*
4. Cifras de cierre (puede ser diapositiva o dicho a cámara): *"En números: 91 pruebas de backend más 25 de extremo a extremo, todas en verde; cobertura del 70%; complejidad promedio 2.48, calificación A; y cero vulnerabilidades según el análisis estático."*

---

## Bloque 4 (6:00 - 9:20) | Spick: cada integrante responde las 3 preguntas (en cámara)

> Cada uno habla ~65 segundos. Las respuestas siguen el orden: ¿qué avances logramos?, ¿qué aprendí?, ¿qué problemas tuvimos? Pueden decirlo con sus palabras; esto es la base.

### César (6:00 - 7:05)
- **Avances:** "Cerramos las cinco fases planificadas: datos de demostración, seguridad por roles, límite de intentos, renovación de tokens, PDF y las pruebas E2E en integración continua. Todo entró por Pull Request con el CI en verde, y el documento final quedó con las métricas medidas, no estimadas."
- **Aprendizaje:** "Aprendí que el entorno es parte del producto: la mitad de nuestros bloqueos fueron versiones, ramas y puertos, no lógica. Y que cerrar una tarea significa tener la evidencia, no la sensación de que funciona."
- **Problemas:** "El CI estuvo días sin correr porque los workflows apuntaban a una rama que no existía, y perdimos tiempo hasta detectarlo. Lo resolvimos y de ahí salió la regla de verificar el pipeline antes que el código."

### Roberto (7:05 - 8:10)
- **Avances:** "Del lado de la interfaz: el botón de exportar a PDF, la leyenda y accesibilidad del grafo, las etiquetas para lectores de pantalla, y dejé las 25 pruebas de navegador estables y corriendo en cada Pull Request."
- **Aprendizaje:** "Que probar piezas no es probar el sistema. Teníamos 63 pruebas unitarias en verde y aun así nadie podía crear un cliente desde la pantalla, por cómo maneja el navegador un campo numérico vacío. Eso solo lo encontró una prueba de extremo a extremo."
- **Problemas:** "Las pruebas E2E estaban escritas desde antes pero nunca habían pasado completas: 17 de 25 corrían sin iniciar sesión por un error en el fixture. Reescribirlas fue trabajoso, pero al hacerlo destaparon tres defectos críticos reales."

### Jean (8:10 - 9:20)
- **Avances:** "Implementé la capa de seguridad del cierre: control de acceso por roles según el principio de menor privilegio, la auditoría inmutable que exige la Ley 23, la rotación de los tokens de renovación y sus 28 pruebas nuevas."
- **Aprendizaje:** "Que la seguridad se diseña pensando en quién va a intentar saltársela. El hallazgo que más me marcó fue que el registro de usuarios era público: cualquiera podía crearse una cuenta de administrador. Usando la aplicación normal eso no se nota; apareció al preguntarnos qué haría un atacante."
- **Problemas:** "Los entornos: un PostgreSQL local interceptaba el puerto de la base de datos de Docker y las pruebas de integración se conectaban a otro servidor. La solución fue correrlas dentro del contenedor, y quedó documentado para el que siga el proyecto."

---

## Bloque 5 (9:20 - 10:00) | Los tres en cámara | Cierre

**César:** "En resumen: entregamos un producto que cumple los controles de la Ley 23, con 116 pruebas automatizadas en verde, integración continua completa y siete defectos reales encontrados y corregidos durante el cierre."

**Roberto:** "El repositorio, el tablero y el documento final con las métricas están en los enlaces de la entrega."

**Jean:** "Gracias, profesora, por el acompañamiento durante el semestre. Quedamos atentos a sus comentarios."

---

## Notas de grabación

- Si el video se pasa de 10 minutos, recortar primero del Bloque 2 (la demo tolera ir más rápido) y nunca del Bloque 4, porque la participación individual es requisito.
- Grabar la demo a ritmo tranquilo pero sin pausas muertas; se puede editar acelerando las esperas de carga.
- Si algo falla en vivo durante la grabación, no pasa nada: `docker-compose down -v`, volver a levantar, correr el seed y repetir la toma.
- Subir el video a YouTube (oculto) o Drive con acceso público y verificar el enlace en una ventana de incógnito antes de entregarlo.
