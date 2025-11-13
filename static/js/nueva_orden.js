document.addEventListener("DOMContentLoaded", function() {
    const selectUsuarios = document.querySelector("[name='usuarios_asignados']");
    const tablaBody = document.querySelector("#tablaUsuariosSeleccionados tbody");

    if (!selectUsuarios || !tablaBody) return; // evita errores si no existen

    function actualizarTabla() {
        const seleccionados = Array.from(selectUsuarios.selectedOptions);
        tablaBody.innerHTML = "";

        if (seleccionados.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="2" class="text-center text-muted">Sin usuarios seleccionados</td>
                </tr>`;
            return;
        }

        seleccionados.forEach((option, index) => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${index + 1}</td>
                <td>${option.textContent}</td>
            `;
            tablaBody.appendChild(fila);
        });
    }

    selectUsuarios.addEventListener("change", actualizarTabla);
    formularioEquipo();
});

function formularioEquipo() {
    const selectEquipo = document.getElementById("tiene_equipo");
    const formEquipo = document.getElementById("formularioEquipo");

    if (!selectEquipo || !formEquipo) return;

    const campos = formEquipo.querySelectorAll("input, select, textarea");

    function toggleEquipoForm() {
        const mostrar = selectEquipo.value === "si";
        formEquipo.style.display = mostrar ? "block" : "none";
        campos.forEach(campo => {
            campo.disabled = !mostrar;
            if (!mostrar) campo.value = "";
        });
    }

    selectEquipo.addEventListener("change", toggleEquipoForm);
}