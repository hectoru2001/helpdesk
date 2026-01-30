document.addEventListener("DOMContentLoaded", function() {
    const selectUsuarios = document.querySelector("[name='usuarios_asignados']");
    const tablaBody = document.querySelector("#tablaUsuariosSeleccionados tbody");

    if (!selectUsuarios || !tablaBody) return;

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

    const chk = document.getElementById("usar_oficio");
    const input = document.getElementById("oficio");

    function toggle() {
        if (chk.checked) {
            input.disabled = false;
            input.value = "";
            input.focus();
        } else {
            input.disabled = true;
            input.value = "S/N";
        }
    }

    chk.addEventListener("change", toggle);
    toggle(); // inicializar estado
});

function formularioEquipo() {
    const selectEquipo = document.getElementById("tiene_equipo");
    const formEquipo = document.getElementById("formularioEquipo");

    if (!selectEquipo || !formEquipo) return;

    const campos = formEquipo.querySelectorAll("input, select, textarea");

    const mostrar = selectEquipo.value === "si";

    formEquipo.style.display = mostrar ? "block" : "none";

    campos.forEach(campo => {
        campo.disabled = !mostrar;
        if (!mostrar) campo.value = "";
    });
}

document.getElementById("tiene_equipo").addEventListener("change", formularioEquipo);

let timer = null;

function buscarEmpleado(inputTextId, inputHiddenId, resultsId, prefix) {
    clearTimeout(timer);

    const inputTexto = document.getElementById(inputTextId);
    const inputAnterior = document.getElementById(inputHiddenId);

    const q = inputTexto.value.trim().toUpperCase();
    if (q.length < 3) return;

    const valorAnterior = Number(inputAnterior?.value || 0);

    // 🔁 Elegir endpoint según el valor anterior
    const endpoint = valorAnterior === 0
        ? "/ordenes/funcionarios/buscar/"
        : "/ordenes/empleados/buscar/";

    timer = setTimeout(() => {
        fetch(`${endpoint}?q=${encodeURIComponent(q)}`)
            .then(res => res.json())
            .then(data => {
                if (!data.resultados) return;
                cargarResultados(
                    data.resultados,
                    inputTextId,
                    inputHiddenId,
                    resultsId,
                    prefix
                );
            })
            .catch(console.error);
    }, 400);
}

function buscarPorID(inputId, inputTextId, resultsId, prefix) {
    buscarEmpleado(inputId, inputTextId, resultsId, prefix);
}

function cargarResultados(lista, inputTextId, inputHiddenId, resultsId, prefix) {
    const cont = document.getElementById(resultsId);
    cont.dataset.input = inputTextId;
    cont.innerHTML = "";

    if (!lista || lista.length === 0) {
        cont.style.display = "none";
        return;
    }

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

    campos.forEach(campo => {
        const input = document.getElementById(campo.id);
        if (input) input.value = campo.value || "";
    });

    document.getElementById(resultsId).style.display = "none";

    const correoId = `${prefix}_correo`;
    const correoInput = document.getElementById(correoId);
    if (correoInput) {
        correoInput.focus();
    }
}

function buscarYSeleccionar(inputId, inputTextId, resultsId, prefix) {
    event.preventDefault();

    const input = document.getElementById(inputId);
    const valor = input.value.trim();

    // Si el valor es 0 → pasar al siguiente textbox
    if (Number(valor) === 0) {
        const inputs = Array.from(
            document.querySelectorAll("input, select, textarea")
        );

        const index = inputs.indexOf(input);
        if (index !== -1 && inputs[index + 1]) {
            inputs[index + 1].focus();
        }
        return;
    }

    fetch(`/ordenes/empleados/buscar/?q=${encodeURIComponent(valor)}`)
        .then(res => res.json())
        .then(data => {
            if (!data.resultados || data.resultados.length === 0) {
                alert("Usuario no encontrado");
                return;
            }

            const emp = data.resultados[0];
            seleccionarEmpleado(emp, inputTextId, inputId, resultsId, prefix);
        })
        .catch(console.error);
}

document.addEventListener("DOMContentLoaded", () => {
    const switchIgualSolicitante = document.getElementById("igual_solicitante");

    if (switchIgualSolicitante) {
        switchIgualSolicitante.addEventListener("change", function() {
            if (this.checked) {
                // Copiar datos de solicitante a beneficiado
                document.getElementById("usuario_beneficiado").value = document.getElementById("usuario_solicita").value;
                document.getElementById("usuario_beneficiado_text").value = document.getElementById("usuario_solicita_text").value;
                document.getElementById("beneficiado_dependencia").value = document.getElementById("solicitante_dependencia").value;
                document.getElementById("beneficiado_departamento").value = document.getElementById("solicitante_departamento").value;
                document.getElementById("beneficiado_correo").value = document.getElementById("solicitante_correo").value;
                document.getElementById("beneficiado_telefono").value = document.getElementById("solicitante_telefono").value;
                document.getElementById("beneficiado_puesto").value = document.getElementById("solicitante_puesto").value;
            } else {
                // Limpiar campos de beneficiado
                document.getElementById("usuario_beneficiado").value = "";
                document.getElementById("usuario_beneficiado_text").value = "";
                document.getElementById("beneficiado_dependencia").value = "";
                document.getElementById("beneficiado_departamento").value = "";
                document.getElementById("beneficiado_correo").value = "";
                document.getElementById("beneficiado_telefono").value = "";
                document.getElementById("beneficiado_puesto").value = "";
            }
        });
    }
    const form = document.getElementById("nuevaOrden");

    function validarCorreoMunicipal(correo) {
        return correo.endsWith("@juarez.gob.mx");
    }

    form.addEventListener("submit", function (e) {

        let valido = true;

        const camposRequeridos = [
            "prioridad",
            "usuario_solicita",
            "usuario_solicita_text",
            "usuario_beneficiado",
            "usuario_beneficiado_text",
            "beneficiado_dependencia",
            "beneficiado_correo",
            "beneficiado_departamento",
            "beneficiado_telefono",
            "beneficiado_puesto",
            "aplicacion",
            "clasificacion",
            "problema",
            "descripcion"
        ];

        camposRequeridos.forEach(id => {
            const input = document.getElementById(id);
            if (!input) return;

            if (input.value.trim() === "") {
                input.classList.add("is-invalid");
                valido = false;
            } else {
                input.classList.remove("is-invalid");
            }
        });

        const usuarios = document.getElementById("id_usuarios_asignados");

        if (usuarios && usuarios.selectedOptions.length === 0) {
            usuarios.classList.add("is-invalid");
            valido = false;
            alert("Debes asignar al menos 1 usuario a la orden.");
        } else {
            usuarios.classList.remove("is-invalid");
        }


        const usarOficio = document.getElementById("usar_oficio");
        const oficio = document.getElementById("oficio");

        if (usarOficio.checked) {
            if (oficio.value.trim() === "") {
                oficio.classList.add("is-invalid");
                valido = false;
            } else {
                oficio.classList.remove("is-invalid");
            }
        }


        const correoSolicitante = document.getElementById("solicitante_correo");
        const correoBeneficiado = document.getElementById("beneficiado_correo");

        if (correoSolicitante && !validarCorreoMunicipal(correoSolicitante.value.trim())) {
            correoSolicitante.classList.add("is-invalid");
            valido = false;
            alert("El correo del solicitante debe terminar en @juarez.gob.mx");
        } else {
            correoSolicitante.classList.remove("is-invalid");
        }

        if (correoBeneficiado && !validarCorreoMunicipal(correoBeneficiado.value.trim())) {
            correoBeneficiado.classList.add("is-invalid");
            valido = false;
            alert("El correo del beneficiado debe terminar en @juarez.gob.mx");
        } else {
            correoBeneficiado.classList.remove("is-invalid");
        }


        if (!valido) {
            e.preventDefault();
            e.stopPropagation();
        }
    });
});

document.addEventListener("click", (e) => {

    const listas = document.querySelectorAll("[id^='resultados_']");

    listas.forEach(lista => {

        const inputId = lista.dataset.input; 
        const input = document.getElementById(inputId);

        const clicDentro = lista.contains(e.target) || (input && input.contains(e.target));

        if (!clicDentro) {
            lista.style.display = "none";
        }
    });
});

function seleccionarSelectPorTexto(selectId, texto) {
    if (!texto) return;

    const select = document.getElementById(selectId);
    if (!select) return;

    const buscado = texto.trim().toLowerCase();

    for (let opt of select.options) {
        if (opt.text.trim().toLowerCase() === buscado) {
            select.value = opt.value;
            return;
        }
    }

    console.warn(`No se encontró opción "${texto}" en ${selectId}`);
}


function llenarPatrimonio(e) {
    e.preventDefault(); 
    const patrimonioInput = document.getElementById("patrimonio");

    fetch(`/ordenes/patrimonio/buscar/?q=${encodeURIComponent(patrimonioInput.value.trim())}`)
        .then(res => res.json())
        .then(data => {
            if (!data.resultados || data.resultados.length === 0) {
                alert("Patrimonio no encontrado");
                return;
            }

            const patrimonio = data.resultados[0];
            patrimonioInput.value = patrimonio.codigo;
            document.getElementById("serie").value = patrimonio.serie;
            document.getElementById("equipo").value = patrimonio.descripcion;

            seleccionarSelectPorTexto("id_marca", patrimonio.marca);
            seleccionarSelectPorTexto("id_color", patrimonio.color);
        })
        .catch(console.error);
}

