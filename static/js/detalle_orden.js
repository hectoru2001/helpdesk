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
                console.log(err);
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
