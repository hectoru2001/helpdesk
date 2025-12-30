let empleados = [];
let empleadosOriginales = []; // Para mantener una copia de todos los empleados
let paginaActual = 1;
const porPagina = 10;

// -------------------------------
// Cargar datos desde la API
// -------------------------------
function cargarEmpleados() {
    fetch("/ordenes/empleados/buscar/")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            empleados = data.resultados || [];
            empleadosOriginales = [...empleados]; // Guardar copia completa
            paginaActual = 1;
            renderTabla();
            renderPaginacion();
        })
        .catch(error => {
            console.error("Error cargando empleados:", error);
            // Aquí podrías mostrar un mensaje al usuario
        });
}

// -------------------------------
// Pintar tabla con paginación
// -------------------------------
function renderTabla() {
    const tbody = document.getElementById("tablaEmpleados");
    if (!tbody) {
        console.error("No se encontró el elemento tablaEmpleados");
        return;
    }
    
    tbody.innerHTML = "";

    const inicio = (paginaActual - 1) * porPagina;
    const fin = inicio + porPagina;
    const paginaDatos = empleados.slice(inicio, fin);

    if (paginaDatos.length === 0) {
        const row = `
            <tr>
                <td colspan="6" class="text-center">No se encontraron empleados</td>
            </tr>
        `;
        tbody.insertAdjacentHTML("beforeend", row);
        return;
    }

    paginaDatos.forEach(emp => {
        const numero = emp.Numero_Empleado || "N/A";
        const nombre = emp.Nombre_Empleado || "N/A";
        const depto = emp.Dependencia || "N/A";
        const correo = emp.Correo_Electronico || "N/A";
        const telef = emp.Telefono || "N/A";
        const depar = emp.Id_Departamento || "N/A";

        const row = `
            <tr>
                <td>${numero}</td>
                <td>${nombre}</td>
                <td>${depto}</td>
                <td>${correo}</td>
                <td>${telef}</td>
                <td>${depar}</td>
            </tr>
        `;
        tbody.insertAdjacentHTML("beforeend", row);
    });
}

// -------------------------------
// Crear paginación dinámica
// -------------------------------
function renderPaginacion() {
    const pagNav = document.getElementById("paginacion");
    if (!pagNav) {
        console.error("No se encontró el elemento paginacion");
        return;
    }
    
    pagNav.innerHTML = "";

    const totalPaginas = Math.ceil(empleados.length / porPagina);
    
    if (totalPaginas <= 1) return;

    const maxVisibles = 5;
    let inicio = Math.max(1, paginaActual - Math.floor(maxVisibles / 2));
    let fin = Math.min(totalPaginas, inicio + maxVisibles - 1);

    // Ajustar inicio si estamos cerca del final
    if (fin - inicio < maxVisibles - 1) {
        inicio = Math.max(1, fin - maxVisibles + 1);
    }

    // Botón Primera página
    if (paginaActual > 1) {
        pagNav.innerHTML += `
            <li class="page-item">
                <button class="page-link" onclick="cambiarPagina(1)">«</button>
            </li>`;
    }

    // Botón anterior
    if (paginaActual > 1) {
        pagNav.innerHTML += `
            <li class="page-item">
                <button class="page-link" onclick="cambiarPagina(${paginaActual - 1})">‹</button>
            </li>`;
    }

    // Números de página visibles
    for (let i = inicio; i <= fin; i++) {
        pagNav.innerHTML += `
            <li class="page-item ${i === paginaActual ? "active" : ""}">
                <button class="page-link" onclick="cambiarPagina(${i})">${i}</button>
            </li>`;
    }

    // Botón siguiente
    if (paginaActual < totalPaginas) {
        pagNav.innerHTML += `
            <li class="page-item">
                <button class="page-link" onclick="cambiarPagina(${paginaActual + 1})">›</button>
            </li>`;
    }

    // Botón última página
    if (paginaActual < totalPaginas) {
        pagNav.innerHTML += `
            <li class="page-item">
                <button class="page-link" onclick="cambiarPagina(${totalPaginas})">»</button>
            </li>`;
    }
}

function cambiarPagina(num) {
    paginaActual = num;
    renderTabla();
    renderPaginacion();
}

// -------------------------------
// Buscador en tiempo real MEJORADO
// -------------------------------
function inicializarBuscador() {
    const buscarInput = document.getElementById("buscarInput");
    if (!buscarInput) {
        console.error("No se encontró el elemento buscarInput");
        return;
    }

    // Limpiar evento anterior y agregar nuevo
    buscarInput.removeEventListener("input", buscarEmpleados);
    buscarInput.addEventListener("input", buscarEmpleados);
}

function buscarEmpleados() {
    const q = this.value.toLowerCase().trim();
    
    if (q === "") {
        // Si no hay búsqueda, restaurar todos los empleados
        empleados = [...empleadosOriginales];
    } else {
        // Filtrar desde la copia original
        empleados = empleadosOriginales.filter(emp =>
            (emp.Nombre_Empleado?.toLowerCase().includes(q) || false) ||
            (emp.Numero_Empleado?.toString().includes(q) || false) ||
            (emp.Dependencia?.toLowerCase().includes(q) || false) ||
            (emp.Correo_Electronico?.toLowerCase().includes(q) || false)
        );
    }
    
    paginaActual = 1;
    renderTabla();
    renderPaginacion();
}

// -------------------------------
// Función para limpiar búsqueda
// -------------------------------
function limpiarBusqueda() {
    const buscarInput = document.getElementById("buscarInput");
    if (buscarInput) {
        buscarInput.value = "";
        empleados = [...empleadosOriginales];
        paginaActual = 1;
        renderTabla();
        renderPaginacion();
    }
}

// -------------------------------
// Inicialización
// -------------------------------
document.addEventListener("DOMContentLoaded", function() {
    cargarEmpleados();
    inicializarBuscador();
});