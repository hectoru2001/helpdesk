let timer; // para búsquedas con delay

// --- Función para obtener CSRF ---
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
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

function cargarUsuariosReasignacion(ordenId) {
    fetch(`/ordenes/usuarios_disponibles/${ordenId}/`)
        .then(res => res.json())
        .then(data => {

            const contenedor = document.getElementById("contenedor-reasignacion");

            if (!data.usuarios || data.usuarios.length === 0) {
                contenedor.innerHTML =
                    `<p class="text-center text-muted">No hay usuarios disponibles.</p>`;
                return;
            }

            let opciones = data.usuarios.map(u =>
                `<option value="${u.id}">
                    ${u.nombre} (${u.tipo}) | ${u.ordenes_asignadas} órdenes
                </option>`
            ).join('');

            contenedor.innerHTML = `
                <div class="mb-3">
                    <label class="form-label">Usuarios</label>
                    <select id="usuarioReasignar" class="form-select" multiple>
                        ${opciones}
                    </select>
                </div>

                <div class="mb-3">
                    <label class="form-label">Comentario</label>
                    <textarea id="comentarioReasignar" class="form-control" rows="3"></textarea>
                </div>

                <button class="btn btn-primary w-100" id="btn-confirmar-reasignacion">
                    Confirmar reasignación
                </button>
            `;

            $('#usuarioReasignar').select2({
                placeholder: "Selecciona los usuarios...",
                dropdownParent: $('#reasignarOrdenModal'),
                width: '100%',
            });

            document.getElementById("btn-confirmar-reasignacion").onclick =
                () => confirmarReasignacionMultiple(ordenId);
        })
        .catch(err => {
            document.getElementById("contenedor-reasignacion").innerHTML =
                `<div class="alert alert-danger">Error al cargar usuarios.</div>`;
            console.error(err);
        });
}

// --- Evento principal cuando carga el DOM ---
document.addEventListener("DOMContentLoaded", function () {
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
