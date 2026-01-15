let timer; // para búsquedas con delay

// --- Función para obtener CSRF ---
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

// --- Cambiar estatus de la orden ---
function cambiarEstatus(ordenId, nuevoEstatus) {
    const csrftoken = getCookie("csrftoken");
    let datos = { orden_id: ordenId, estatus: nuevoEstatus };

    if (nuevoEstatus === "T") {
        datos.solucion = document.getElementById("solucion")?.value || "";
    }

    fetch('/ordenes/actualizar_estatus/proceso/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams(datos)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showModal('Estatus actualizado correctamente.', 'success', function (){
                    location.reload();
                });
            } else {
                showModal(data.error || 'Error al actualizar estatus', 'error');
            }
        })
        .catch(err => console.error(err));
}

function guardarComentario(ordenId) {
    const comentario = document.getElementById(`comentario_${ordenId}`).value.trim();

    if (!comentario) {
        alert('Debes escribir un comentario');
        return;
    }

    fetch('/ordenes/guardar_comentario/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken"),
        },
        body: JSON.stringify({
            orden: ordenId,
            comentario: comentario
        })
    })
    .then(r => r.json())
    .then(r => {
        if (r.ok) {
            showModal('Comentario agregado correctamente.', 'success', function (){
                    location.reload();
                });
        }
    });
}

// --- Abrir modal para imprimir orden ---
function imprimirOrden(ordenId) {
    window.open(`/ordenes/imprimir/${ordenId}/`, '_blank');
}

// --- Funciones de búsqueda de empleados (si las necesitas) ---
function buscarEmpleado(inputTextId, inputHiddenId, resultsId, prefix) {
    clearTimeout(timer);
    const input = document.getElementById(inputTextId);
    const q = input.value.trim().toUpperCase();
    if (q.length < 3) return;

    timer = setTimeout(() => {
        fetch(`/ordenes/empleados/buscar/?q=${encodeURIComponent(q)}`)
            .then(res => res.json())
            .then(data => cargarResultados(data.resultados, inputTextId, inputHiddenId, resultsId, prefix))
            .catch(console.error);
    }, 400);
}

function cargarResultados(lista, inputTextId, inputHiddenId, resultsId, prefix) {
    const cont = document.getElementById(resultsId);
    cont.innerHTML = "";
    if (!lista || lista.length === 0) { cont.style.display = "none"; return; }

    lista.forEach(emp => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "list-group-item list-group-item-action";
        btn.innerHTML = `<b>${emp.Numero_Empleado}</b> - ${emp.Nombre_Empleado}`;
        btn.onclick = () => seleccionarEmpleado(emp, inputTextId, inputHiddenId, resultsId, prefix);
        cont.appendChild(btn);
    });

    cont.style.display = "block";
}

function seleccionarEmpleado(emp, inputTextId, inputHiddenId, resultsId, prefix) {
    document.getElementById(inputTextId).value = emp.Nombre_Empleado;
    document.getElementById(inputHiddenId).value = emp.Numero_Empleado;

    const campos = [
        { id: `${prefix}_dependencia`, value: emp.Dependencia },
        { id: `${prefix}_departamento`, value: emp.Id_Departamento },
        { id: `${prefix}_area`, value: emp.Area }
    ];
    campos.forEach(c => {
        const input = document.getElementById(c.id);
        if (input) input.value = c.value || "";
    });
    document.getElementById(resultsId).style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {

    const modalProcesar = document.getElementById("procesarOrdenModal");
    modalProcesar.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const ordenId = button.getAttribute("data-orden-id");
        const modalBody = document.getElementById("modal-procesar-contenido");

        modalBody.innerHTML = `<div class="text-center text-muted py-5">
            <div class="spinner-border text-primary mb-3"></div>
            <p>Cargando datos...</p>
        </div>`;

        fetch(`/ordenes/cargar_detalles/proceso/${ordenId}/`)
            .then(res => res.json())
            .then(data => {
                const progreso = obtenerProgreso(data.estatus);
                console.log(data.estatus);

                modalBody.innerHTML = `
                    <div class="modal-body p-4">
                        <!-- Sección 1: Información General -->
                        <div class="card border-0 shadow-sm mb-4">
                            <div class="card-body">
                                <div class="d-flex align-items-center mb-3">
                                    <i class="bi bi-info-circle-fill text-primary me-2"></i>
                                    <h6 class="card-title mb-0 title-secondary">Información General</h6>
                                </div>

                                <div class="row g-3 mb-4">
                                    <div class="col-md-6">
                                        <div class="info-item">
                                            <span class="info-label fw-bold">Orden:</span>
                                            <span class="info-value">${data.orden}</span>
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label fw-bold">Oficio:</span>
                                            <span class="info-value">${data.oficio}</span>
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label fw-bold">Aplicación:</span>
                                            <span class="info-value">${data.aplicacion}</span>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item">
                                            <span class="info-label fw-bold">Clasificación:</span>
                                            <span class="info-value">${data.clasificacion}</span>
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label fw-bold">Prioridad:</span>
                                            <span class="badge priority-badge bg-warning text-dark">
                                                ${data.prioridad}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Descripción -->
                                <div class="mb-4">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="bi bi-card-text text-muted me-2"></i>
                                        <strong>Descripción</strong>
                                    </div>
                                    <div class="description-box p-3 rounded">
                                        ${data.descripcion}
                                    </div>
                                </div>

                                <!-- Barra de progreso -->
                                <div class="progress-section">
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <div>
                                            <i class="bi bi-speedometer2 me-2"></i>
                                            <strong>Estatus:</strong>
                                        </div>
                                        <span class="status-text fw-semibold">${progreso.texto}</span>
                                    </div>
                                    <div class="progress custom-progress" style="height: 24px;">
                                        <div class="progress-bar ${progreso.color} ${progreso.porcentaje < 100 ? 'progress-bar-striped progress-bar-animated' : ''}"
                                            role="progressbar"
                                            style="width: ${progreso.porcentaje}%;"
                                            aria-valuenow="${progreso.porcentaje}"
                                            aria-valuemin="0"
                                            aria-valuemax="100">
                                            <span class="progress-text">${progreso.porcentaje}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Sección 2: Equipo (condicional) -->
                        ${data.equipo === "true" ? `
                            <div class="card border-0 shadow-sm mb-4">
                                <div class="card-body">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="bi bi-pc-display text-primary me-2"></i>
                                        <h6 class="card-title mb-0 title-secondary">Equipo Asignado</h6>
                                    </div>
                                    <div class="row g-2">
                                        <div class="col-md-6">
                                            <div class="info-item">
                                                <span class="info-label">Equipo:</span>
                                                <span class="info-value">${data.detalle_equipo?.equipo || "N/A"}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label">Marca:</span>
                                                <span class="info-value">${data.detalle_equipo?.marca || "N/A"}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label">Color:</span>
                                                <span class="info-value">${data.detalle_equipo?.color || "N/A"}</span>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="info-item">
                                                <span class="info-label">Número de serie:</span>
                                                <span class="info-value">${data.detalle_equipo?.serie || "N/A"}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label">Patrimonio:</span>
                                                <span class="info-value">${data.detalle_equipo?.patrimonio || "N/A"}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label">Descripción:</span>
                                                <span class="info-value">${data.detalle_equipo?.descripcion || "N/A"}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ` : ""}

                        <!-- Sección 3: Solicitante y Beneficiado en columnas -->
                        <div class="row g-4 mb-4">
                            <div class="col-md-6">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <i class="bi bi-person-badge text-primary me-2"></i>
                                            <h6 class="card-title mb-0 title-secondary">Solicitante</h6>
                                        </div>
                                        <div class="contact-info">
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Nombre:</span>
                                                <span class="info-value">${data.solicitante.nombre}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Puesto:</span>
                                                <span class="info-value">${data.solicitante.puesto}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Dependencia:</span>
                                                <span class="info-value">${data.solicitante.dependencia}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Correo:</span>
                                                <a href="mailto:${data.solicitante.correo}" class="info-value text-decoration-none">
                                                    ${data.solicitante.correo}
                                                </a>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Teléfono:</span>
                                                <a href="tel:${data.solicitante.telefono}" class="info-value text-decoration-none">
                                                    ${data.solicitante.telefono}
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <i class="bi bi-person-heart text-primary me-2"></i>
                                            <h6 class="card-title mb-0 title-secondary">Beneficiado</h6>
                                        </div>
                                        <div class="contact-info">
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Nombre:</span>
                                                <span class="info-value">${data.beneficiado.nombre}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Puesto:</span>
                                                <span class="info-value">${data.beneficiado.puesto}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Dependencia:</span>
                                                <span class="info-value">${data.beneficiado.dependencia}</span>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Correo:</span>
                                                <a href="mailto:${data.beneficiado.correo}" class="info-value text-decoration-none">
                                                    ${data.beneficiado.correo}
                                                </a>
                                            </div>
                                            <div class="info-item">
                                                <span class="info-label fw-bold">Teléfono:</span>
                                                <a href="tel:${data.beneficiado.telefono}" class="info-value text-decoration-none">
                                                    ${data.beneficiado.telefono}
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Sección 4: Soluciones Registradas -->
                        <div class="card border-0 shadow-sm mb-4">
                            <div class="card-body">
                                <div class="d-flex align-items-center mb-3">
                                    <i class="bi bi-clipboard-check text-primary me-2"></i>
                                    <h6 class="card-title mb-0 title-secondary">Soluciones Registradas</h6>
                                </div>
                                
                                ${data.todas_las_soluciones && data.todas_las_soluciones.length > 0 
                                    ? `
                                        <div class="solutions-list">
                                            ${data.todas_las_soluciones.map((s, index) => `
                                                <div class="solution-item ${index !== data.todas_las_soluciones.length - 1 ? 'mb-4 pb-4 border-bottom' : ''}">
                                                    <div class="d-flex justify-content-between align-items-start mb-3">
                                                        <div class="d-flex align-items-center">
                                                            <div class="user-avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                                                ${s.usuario.charAt(0).toUpperCase()}
                                                            </div>
                                                            <div>
                                                                <div class="fw-semibold">${s.usuario}</div>
                                                            </div>
                                                        </div>
                                                        <span class="badge ${s.estatus === 'T' ? 'bg-success' : 'bg-warning text-dark'} status-badge">
                                                            <i class="bi ${s.estatus === 'T' ? 'bi-check-circle' : 'bi-clock'} me-1"></i>
                                                            ${s.estatus === 'T' ? 'Terminado' : 'En proceso'}
                                                        </span>
                                                    </div>

                                                    <!-- Comentarios -->
                                                    <div class="mb-3">
                                                        <div class="d-flex align-items-center mb-2">
                                                            <i class="bi bi-chat-left-text text-muted me-2"></i>
                                                            <small class="text-muted fw-medium">Comentarios</small>
                                                        </div>
                                                        <div class="ps-3 border-start border-2">
                                                            ${s.comentarie
                                                                ? `<div class="comment-text">${s.comentarie.replace(/\n/g, '<br>')}</div>`
                                                                : '<em class="text-muted">Sin comentario</em>'
                                                            }
                                                        </div>
                                                    </div>

                                                    <!-- Solución -->
                                                    <div>
                                                        <div class="d-flex align-items-center mb-2">
                                                            <i class="bi bi-wrench text-muted me-2"></i>
                                                            <small class="text-muted fw-medium">Solución</small>
                                                        </div>
                                                        <div class="ps-3 border-start border-2">
                                                            ${s.solucion
                                                                ? `<div class="solution-text">${s.solucion}</div>`
                                                                : '<em class="text-muted">Aún pendiente de terminar</em>'
                                                            }
                                                        </div>
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    `
                                    : `
                                        <div class="text-center py-5">
                                            <i class="bi bi-inbox display-6 text-muted mb-3"></i>
                                            <p class="text-muted mb-0">No hay técnicos asignados con reporte aún.</p>
                                        </div>
                                    `
                                }
                            </div>
                        </div>

                        <!-- Sección 5: Calificación (condicional) -->
                        ${data.estatus === 'Terminada' ? `
                            <div class="card border-0 shadow-sm mb-4">
                                <div class="card-body">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="bi bi-star-fill text-warning me-2"></i>
                                        <h6 class="card-title mb-0 title-secondary">Calificación del Usuario</h6>
                                    </div>
                                    ${data.comentario?.comentario
                                        ? `
                                            <div class="rating-section">
                                                <div class="mb-3">
                                                    <div class="info-label mb-1">Comentario:</div>
                                                    <div class="user-comment p-3 rounded bg-light">
                                                        ${data.comentario.comentario}
                                                    </div>
                                                </div>
                                                <div>
                                                    <div class="info-label mb-2">Calificación:</div>
                                                    <div class="stars-display">
                                                        ${renderStars(data.comentario.calificacion)}
                                                    </div>
                                                </div>
                                            </div>
                                        `
                                        : `
                                            <div class="text-center py-4">
                                                <i class="bi bi-chat-quote display-6 text-muted mb-3"></i>
                                                <p class="text-muted">Aún no hay comentarios.</p>
                                            </div>
                                        `
                                    }
                                </div>
                            </div>
                        ` : ""}

                        <!-- Sección 6: Acciones del Usuario -->
                        <div class="user-actions-section">
                            ${data.estatus_usuario === 'A' ? `
                                <button class="btn btn-primary btn-lg w-100 py-3 d-flex align-items-center justify-content-center"
                                    onclick="cambiarEstatus(${data.orden}, 'E')">
                                    <i class="bi bi-play-circle me-2"></i>
                                    Iniciar Orden
                                </button>
                            ` : data.estatus_usuario === 'E' ? `
                                <div class="card border-0 shadow-sm mb-4">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <i class="bi bi-flag-fill text-success me-2"></i>
                                            <h6 class="card-title mb-0 title-secondary">Finalizar Participación</h6>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label fw-medium">Describe la solución final (opcional)</label>
                                            <textarea id="solucion" 
                                                    class="form-control" 
                                                    rows="4"
                                                    placeholder="Escribe los detalles de la solución implementada..."></textarea>
                                        </div>
                                        <button class="btn btn-success btn-lg w-100 py-3 d-flex align-items-center justify-content-center"
                                            onclick="cambiarEstatus(${data.orden}, 'T')">
                                            <i class="bi bi-check-circle me-2"></i>
                                            Terminar Mi Participación
                                        </button>
                                    </div>
                                </div>
                            ` : data.estatus_usuario === 'T' ? `
                                <div class="alert alert-success d-flex align-items-center" role="alert">
                                    <i class="bi bi-check-circle-fill fs-4 me-3"></i>
                                    <div>
                                        <h6 class="alert-heading mb-1">¡Participación Concluida!</h6>
                                        <p class="mb-0">Has completado tu participación en esta orden.</p>
                                    </div>
                                </div>
                            ` : ""}
                        </div>

                        ${data.estatus_usuario
                            ? `
                            <!-- Sección 7: Agregar Comentario -->
                            <div class="card border-0 shadow-sm mb-4">
                                <div class="card-body">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="bi bi-chat-left-text text-primary me-2"></i>
                                        <h6 class="card-title mb-0 title-secondary">Agregar Comentario</h6>
                                    </div>
                                    <div class="mb-3">
                                        <textarea id="comentario_${data.orden}" 
                                                class="form-control" 
                                                rows="4"
                                                placeholder="Escribe tu comentario o observaciones sobre esta orden..."></textarea>
                                    </div>
                                    <button class="btn btn-secondary w-100 py-3 d-flex align-items-center justify-content-center"
                                        onclick="guardarComentario(${data.orden})">
                                        <i class="bi bi-save me-2"></i>
                                        Guardar Comentario
                                    </button>
                                </div>
                            </div>
                            `
                            : ''
                        }


                        <!-- Sección 8: Acciones Finales -->
                        <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                            <button class="btn btn-outline-secondary d-flex align-items-center"
                                onclick="imprimirOrden(${data.orden})">
                                <i class="bi bi-printer me-2"></i>
                                Imprimir Orden
                            </button>
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">
                                Cerrar
                            </button>
                        </div>
                    </div>

                    <!-- Estilos inline para mejor presentación -->
                    <style>
                        .title-primary {
                            color: #2c3e50;
                            font-weight: 600;
                        }
                        
                        .title-secondary {
                            color: #34495e;
                            font-weight: 600;
                            font-size: 1.1rem;
                        }
                        
                        .info-item {
                            margin-bottom: 0.75rem;
                            display: flex;
                            align-items: flex-start;
                        }
                        
                        .info-label {
                            font-weight: 500;
                            color: #7f8c8d;
                            min-width: 120px;
                        }
                        
                        .info-value {
                            color: #2c3e50;
                            flex: 1;
                        }
                        
                        .description-box {
                            background-color: #f8f9fa;
                            border-left: 4px solid #3498db;
                            font-size: 0.95rem;
                            line-height: 1.5;
                        }
                        
                        .custom-progress {
                            border-radius: 12px;
                            overflow: hidden;
                            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                        }
                        
                        .progress-text {
                            font-size: 0.85rem;
                            font-weight: 600;
                            text-shadow: 0 1px 1px rgba(0,0,0,0.2);
                        }
                        
                        .priority-badge {
                            padding: 0.35em 0.65em;
                            font-size: 0.85em;
                        }
                        
                        .status-badge {
                            padding: 0.5em 1em;
                            font-size: 0.85em;
                        }
                        
                        .contact-info a:hover {
                            text-decoration: underline !important;
                        }
                        
                        .user-avatar {
                            font-weight: 600;
                            font-size: 1rem;
                        }
                        
                        .comment-text, .solution-text {
                            font-size: 0.9rem;
                            line-height: 1.5;
                            color: #2c3e50;
                        }
                        
                        .user-comment {
                            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            line-height: 1.5;
                        }
                        
                        .solution-item {
                            transition: all 0.3s ease;
                        }
                        
                        .solution-item:hover {
                            transform: translateX(5px);
                        }
                        
                        .btn-lg {
                            font-weight: 500;
                            transition: all 0.3s ease;
                        }
                        
                        .btn-lg:hover {
                            transform: translateY(-2px);
                            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        }
                    </style>
                `;
            })
            .catch(err => {
                modalBody.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header border-bottom">
                            <h5 class="modal-title text-danger">Error</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center py-5">
                            <i class="bi bi-exclamation-triangle-fill text-danger display-4 mb-3"></i>
                            <h5 class="text-danger mb-3">Error al cargar los datos</h5>
                            <p class="text-muted">No se pudieron cargar los detalles de la orden.</p>
                            <button class="btn btn-outline-secondary mt-3" data-bs-dismiss="modal">
                                Cerrar
                            </button>
                        </div>
                    </div>
                `;
                console.error('Error al cargar detalles de orden:', err);
            });
    });
    
    const modalReasignar = document.getElementById("reasignarOrdenModal");

    modalReasignar.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const ordenId = button.getAttribute("data-orden-id");
        const modalBody = document.getElementById("modal-reasignar-contenido");

        modalBody.innerHTML = `
            <div class="text-center text-muted py-5">
                <div class="spinner-border text-primary mb-3"></div>
                <p>Cargando información...</p>
            </div>
        `;

        fetch(`/ordenes/cargar_detalles/proceso/${ordenId}/`)
            .then(res => res.json())
            .then(data => {

                modalBody.innerHTML = `
                    <div class="p-3 border rounded mb-3">

                        <!-- Información general -->
                        <div class="row mb-2">
                            <div class="col-md-6 small">
                                <div><strong>Orden:</strong> ${data.orden}</div>
                                <div><strong>Aplicación:</strong> ${data.aplicacion}</div>
                                <div><strong>Clasificación:</strong> ${data.clasificacion}</div>
                            </div>

                            <div class="col-md-6 small">
                                <div>
                                    <strong>Prioridad:</strong>
                                    <span class="badge bg-warning text-dark">${data.prioridad}</span>
                                </div>
                            </div>
                        </div>

                        <hr class="my-2">

                        <!-- Solicitante / Beneficiado -->
                        <div class="row small mb-2">
                            <div class="col-md-6">
                                <div class="fw-semibold mb-1">Solicitante</div>
                                <div>${data.solicitante?.nombre || "N/A"}</div>
                                <div class="text-muted">${data.solicitante?.puesto || "N/A"} · ${data.solicitante?.dependencia || "N/A"}</div>
                                <div>${data.solicitante?.correo || "N/A"} | ${data.solicitante?.telefono || "N/A"}</div>
                            </div>

                            <div class="col-md-6">
                                <div class="fw-semibold mb-1">Beneficiado</div>
                                <div>${data.beneficiado?.nombre || "N/A"}</div>
                                <div class="text-muted">${data.beneficiado?.puesto || "N/A"} · ${data.beneficiado?.dependencia || "N/A"}</div>
                                <div>${data.beneficiado?.correo || "N/A"} | ${data.beneficiado?.telefono || "N/A"}</div>
                            </div>
                        </div>

                        <!-- Descripción -->
                        <div class="small">
                            <strong>Descripción</strong>
                            <div class="border rounded p-2 bg-light mt-1">
                                ${data.descripcion}
                            </div>
                        </div>

                    </div>

                    <div class="small p-3 border rounded mb-3" id="contenedor-usuarios">
                        <div class="text-center text-muted py-4">
                            <div class="spinner-border text-primary mb-2"></div>
                            <p>Cargando usuarios disponibles...</p>
                        </div>
                    </div>
                `;

                cargarUsuariosReasignacion(ordenId);

            })
            .catch(err => {
                console.error(err);
                modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        Error al cargar la información de la orden.
                    </div>
                `;
            });
    });

    /* ==========================================
    FUNCIÓN AISLADA PARA LOS USUARIOS
    ========================================== */
    function cargarUsuariosReasignacion(ordenId) {
        const contenedor = document.getElementById("contenedor-usuarios");

        fetch(`/ordenes/usuarios_disponibles/${ordenId}/`)
            .then(res => res.json())
            .then(data => {

                if (!data.usuarios || data.usuarios.length === 0) {
                    contenedor.innerHTML = `
                        <p class="text-center text-muted">
                            No hay usuarios disponibles para reasignación.
                        </p>`;
                    return;
                }

                let opciones = '';
                data.usuarios.forEach(u => {
                    opciones += `
                        <option value="${u.id}">
                            ${u.nombre} (${u.tipo}) | ${u.ordenes_asignadas} órdenes
                        </option>`;
                });

                contenedor.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label"><strong>Usuarios</strong></label>
                        <select class="form-select" id="usuarioReasignar" multiple>
                            ${opciones}
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label"><strong>Comentario</strong></label>
                        <textarea id="comentarioReasignar" class="form-control" rows="3"></textarea>
                    </div>

                    <button id="btn-confirmar-reasignacion"
                            class="btn btn-primary w-100"
                            data-orden-id="${ordenId}">
                        Confirmar reasignación
                    </button>
                `;

                $('#usuarioReasignar').select2({
                    placeholder: "Selecciona los usuarios...",
                    dropdownParent: $('#reasignarOrdenModal'),
                    width: '100%'
                });
            })
            .catch(err => {
                console.error(err);
                contenedor.innerHTML = `
                    <div class="alert alert-danger">
                        Error al cargar los usuarios.
                    </div>
                `;
            });
    }


    document.addEventListener("click", function (event) {
        const btn = event.target.closest("#btn-confirmar-reasignacion");
        if (!btn) return;

        const ordenId = btn.dataset.ordenId;
        const usuariosIds = $('#usuarioReasignar').val();
        const comentario = document.getElementById("comentarioReasignar").value;

        if (!usuariosIds || usuariosIds.length === 0) {
            showModal("Por favor, selecciona al menos un usuario para reasignar.", "alert", function (){
                return;

            });
        }

        fetch(`/ordenes/reasignar/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                orden_id: ordenId,
                usuarios_ids: usuariosIds,
                comentario: comentario
            })
        })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(data => { throw new Error(data.error || 'Error desconocido del servidor'); });
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    showModal(data.message, "success");
                    const modalInstance = bootstrap.Modal.getInstance(document.getElementById("reasignarOrdenModal"));
                    modalInstance.hide();
                    location.reload();
                } else {
                    showModal("Error al reasignar: " + (data.error || "Fallo desconocido."));
                }
            })
            .catch(err => {
                console.error("Error en la solicitud:", err);
                showModal("Ocurrió un error al intentar reasignar la orden: " + err.message);
            });
    });

});

function renderStars(score) {
    score = parseInt(score);
    let stars = "";

    for (let i = 1; i <= 5; i++) {
        stars += i <= score 
            ? '<span style="color:#f7d106;font-size:1.3rem;">★</span>' 
            : '<span style="color:#ccc;font-size:1.3rem;">☆</span>';
    }

    return stars;
}

function obtenerProgreso(estatus) {
    switch (estatus) {
        case "Asignada":
            return {porcentaje: 25, color: "bg-warning text-dark", texto: "Asignada"};
        case "En proceso":
            return {porcentaje: 50, color: "bg-info text-dark", texto: "En proceso"};
        case "Terminada":
            return {porcentaje: 100, color: "bg-success", texto: "Terminada"};
        case "Cancelada":
            return {porcentaje: 0, color: "bg-danger", texto: "Cancelada"};
        default:
            return {porcentaje: 0, color: "bg-secondary", texto: "Desconocido"};
    }   
}


