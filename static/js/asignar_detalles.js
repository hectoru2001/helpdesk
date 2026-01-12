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
                    <div class="p-3 border rounded mb-4">

                        <h5 class="title-secondary mb-3">Información general</h5>

                        <!-- Datos principales -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <p class="mb-1"><strong>Orden:</strong> ${data.orden}</p>
                                <p class="mb-1"><strong>Oficio:</strong> ${data.oficio}</p>
                                <p class="mb-1"><strong>Aplicación:</strong> ${data.aplicacion}</p>
                            </div>

                            <div class="col-md-6">
                                <p class="mb-1"><strong>Clasificación:</strong> ${data.clasificacion}</p>
                                <p class="mb-1">
                                    <strong>Prioridad:</strong>
                                    <span class="badge bg-warning text-dark">
                                        ${data.prioridad}
                                    </span>
                                </p>
                            </div>
                        </div>

                        <!-- Descripción -->
                        <div class="mb-3">
                            <strong>Descripción</strong>
                            <div class="border rounded p-2 bg-light">
                                ${data.descripcion}
                            </div>
                        </div>

                        <!-- Estatus + progreso -->
                        <div class="mt-3">
                            <div class="d-flex justify-content-between mb-1">
                                <strong>Estatus:</strong>
                                <span class="fw-semibold">${progreso.texto}</span>
                            </div>

                            <div class="progress" style="height: 22px;">
                                <div class="progress-bar ${progreso.color} ${progreso.porcentaje < 100 ? 'progress-bar-striped progress-bar-animated' : ''}"
                                    role="progressbar"
                                    style="width: ${progreso.porcentaje}%;">
                                    ${progreso.porcentaje}%
                                </div>
                            </div>
                        </div>

                    </div>


                    ${data.equipo === "true" ? `
                        <div class="p-3 border rounded mb-4">
                            <h6 class="title-secondary">Equipo asignado</h6>
                            <p><strong>Equipo:</strong> ${data.detalle_equipo?.equipo || "N/A"}</p>
                            <p><strong>Marca:</strong> ${data.detalle_equipo?.marca || "N/A"}</p>
                            <p><strong>Color:</strong> ${data.detalle_equipo?.color || "N/A"}</p>
                            <p><strong>Número de serie:</strong> ${data.detalle_equipo?.serie || "N/A"}</p>
                            <p><strong>Patrimonio:</strong> ${data.detalle_equipo?.patrimonio || "N/A"}</p>
                            <p><strong>Descripción:</strong> ${data.detalle_equipo?.descripcion || "N/A"}</p>
                        </div>` : ""}

                    <div class="p-3 border rounded mb-4">
                        <h6 class="title-secondary">Solicitante</h6>
                        <p><strong>Nombre:</strong> ${data.solicitante.nombre}</p>
                        <p><strong>Puesto:</strong> ${data.solicitante.puesto}</p>
                        <p><strong>Dependencia:</strong> ${data.solicitante.dependencia}</p>
                        <p><strong>Correo:</strong> ${data.solicitante.correo}</p>
                        <p><strong>Teléfono:</strong> ${data.solicitante.telefono}</p>
                    </div>

                    <div class="p-3 border rounded mb-4">
                        <h6 class="title-secondary">Beneficiado</h6>
                        <p><strong>Nombre:</strong> ${data.beneficiado.nombre}</p>
                        <p><strong>Puesto:</strong> ${data.beneficiado.puesto}</p>
                        <p><strong>Dependencia:</strong> ${data.beneficiado.dependencia}</p>
                        <p><strong>Correo:</strong> ${data.beneficiado.correo}</p>
                        <p><strong>Teléfono:</strong> ${data.beneficiado.telefono}</p>
                    </div>

                    <div class="p-3 border rounded mb-4">
                        <h6 class="title-secondary">Soluciones registradas</h6>
                        <div class="list-group list-group-flush">
                            ${data.todas_las_soluciones && data.todas_las_soluciones.length > 0 
                                ? data.todas_las_soluciones.map(s => `
                                    <div class="list-group-item px-0">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <strong>${s.usuario}</strong>
                                            <span class="badge ${s.estatus === 'T' ? 'bg-success' : 'bg-warning text-dark'}">
                                                ${s.estatus === 'T' ? 'Terminado' : 'En proceso'}
                                            </span>
                                        </div>
                                        <p class="mb-0 text-secondary" style="font-size: 0.9rem;">
                                            ${s.solucion ? s.solucion : '<em class="text-muted">Sin comentarios registrados</em>'}
                                        </p>
                                    </div>
                                `).join('')
                                : '<p class="text-muted">No hay técnicos asignados con reporte aún.</p>'
                            }
                        </div>
                    </div>
                    
                    ${data.estatus === 'Terminada' ? `
                        <div class="p-3 border rounded mb-4 bg-light">
                            <h6 class="title-secondary">Solución General</h6>
                            ${data.solucion_general
                                ? `<p>${data.solucion_general}</p>`
                                : `<p class="text-muted">No se registró una solución global.</p>`
                            }
                        </div>

                        <div class="p-3 border rounded mb-4">
                            <h6 class="title-secondary">Calificación del usuario</h6>
                            ${data.comentario?.comentario
                                ? `
                                    <p><strong>Comentario:</strong> ${data.comentario.comentario}</p>
                                    <p><strong>Calificación:</strong> ${renderStars(data.comentario.calificacion)}</p>
                                `
                                : `<p class="text-muted">Aún no hay comentarios.</p>`
                            }
                        </div>
                    ` : ""}

                    ${data.estatus_usuario === 'A' ? `
                        <button class="btn btn-primary w-100"
                            onclick="cambiarEstatus(${data.orden}, 'E')">
                            Iniciar orden
                        </button>
                    ` : data.estatus_usuario === 'E' ? `
                        <div class="mb-2">
                            <label class="form-label"><strong>Escribir mi Solución / Observación</strong></label>
                            <textarea id="solucion" class="form-control" rows="3"
                                placeholder="Describe tu avance o solución..."></textarea>
                        </div>
                        <button class="btn btn-success w-100"
                            onclick="cambiarEstatus(${data.orden}, 'T')">
                            Terminar mi participación
                        </button>
                    `: data.estatus_usuario === 'T' ? `
                        <div class="alert alert-success mb-2">
                            <i class="bi bi-check-circle me-1"></i>
                            Has concluido tu participación en esta orden.
                        </div>
                    ` : ""}

                    <div class="text-end mt-3">
                        <button class="btn btn-secondary" onclick="imprimirOrden(${data.orden})">Imprimir orden</button>
                    </div>
                `;
            })
            .catch(err => {
                modalBody.innerHTML = `<div class="alert alert-danger">Error al cargar los datos de la orden.</div>`;
                console.error(err);
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