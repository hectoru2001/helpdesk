document.addEventListener("DOMContentLoaded", () => {

    // Función que inicializa los formsets
    function inicializarFormset() {
        const formsetRows = document.querySelectorAll(".solicitante-form");

        formsetRows.forEach(row => {
            const inputNumero = row.querySelector("input[name$='usuario_beneficiado']");
            const inputNombre = row.querySelector("input[name$='nombre_beneficiado']");
            const inputNumeroSolicitante = row.querySelector("input[name$='usuario_solicita']");
            const inputNombreSolicitante = row.querySelector("input[name$='nombre_solicitante']");

            if (!inputNumeroSolicitante || !inputNombreSolicitante) return;

            // Crear contenedor de resultados para el nombre del solicitante si no existe
            let resultadosIdSolicitante = inputNombreSolicitante.id + "_resultados";
            let resultadosDivSolicitante = document.getElementById(resultadosIdSolicitante);
            if (!resultadosDivSolicitante) {
                resultadosDivSolicitante = document.createElement("div");
                resultadosDivSolicitante.id = resultadosIdSolicitante;
                resultadosDivSolicitante.className = "autocomplete-results list-group";
                resultadosDivSolicitante.style.cssText = `
                    position: absolute;
                    z-index: 99999;
                    top: 100%;
                    left: 0;
                    width: 100%;
                    min-width: 200px;
                    max-height: 250px;
                    overflow-y: auto;
                    display: none;
                    background-color: #ffffff !important;
                    border: 1px solid #ddd;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                `;
                inputNombreSolicitante.parentNode.style.position = "relative";
                inputNombreSolicitante.parentNode.appendChild(resultadosDivSolicitante);
            }

            // --- EVENTO ENTER EN EL NÚMERO DE EMPLEADO SOLICITANTE ---
            inputNumeroSolicitante.addEventListener("keydown", event => {
                if (event.key === "Enter") {
                    event.preventDefault();
                    const valor = inputNumeroSolicitante.value.trim();
                    if (!valor) return;
                    buscarEmpleadoSolicitante(valor, row, resultadosDivSolicitante, inputNombreSolicitante);
                }
            });

            // --- AUTOCOMPLETADO EN TIEMPO REAL PARA EL NOMBRE DEL SOLICITANTE ---
            inputNombreSolicitante.addEventListener("input", () => {
                const query = inputNombreSolicitante.value.trim();

                if (inputNombreSolicitante.buscarTimer) {
                    clearTimeout(inputNombreSolicitante.buscarTimer);
                    inputNombreSolicitante.buscarTimer = null;
                }

                if (query.length < 2) {
                    resultadosDivSolicitante.style.display = "none";
                    return;
                }

                inputNombreSolicitante.buscarTimer = setTimeout(() => {
                    buscarAutocompletadoSolicitante(query.toUpperCase(), row, resultadosDivSolicitante, inputNombreSolicitante);
                }, 300);
            });

            // Manejar teclas en el campo de nombre del solicitante
            inputNombreSolicitante.addEventListener("keydown", (event) => {
                const resultados = resultadosDivSolicitante.querySelectorAll("button");
                const resultadoActivo = resultadosDivSolicitante.querySelector(".active");
                let index = -1;
                
                if (resultados.length > 0) {
                    if (resultadoActivo) {
                        index = Array.from(resultados).indexOf(resultadoActivo);
                    }
                    
                    switch(event.key) {
                        case "ArrowDown":
                            event.preventDefault();
                            if (index < resultados.length - 1) {
                                if (resultadoActivo) resultadoActivo.classList.remove("active");
                                resultados[index + 1].classList.add("active");
                            } else if (resultados.length > 0) {
                                if (resultadoActivo) resultadoActivo.classList.remove("active");
                                resultados[0].classList.add("active");
                            }
                            break;
                            
                        case "ArrowUp":
                            event.preventDefault();
                            if (index > 0) {
                                if (resultadoActivo) resultadoActivo.classList.remove("active");
                                resultados[index - 1].classList.add("active");
                            }
                            break;
                            
                        case "Enter":
                            if (resultadoActivo && resultadosDivSolicitante.style.display !== "none") {
                                event.preventDefault();
                                resultadoActivo.click();
                            }
                            break;
                            
                        case "Escape":
                            resultadosDivSolicitante.style.display = "none";
                            break;
                    }
                }
            });

            // Cerrar lista si se hace click fuera
            document.addEventListener("click", e => {
                if (!resultadosDivSolicitante.contains(e.target) && e.target !== inputNombreSolicitante) {
                    resultadosDivSolicitante.style.display = "none";
                }
            });

            // Mantener también la funcionalidad original para beneficiado
            if (inputNumero && inputNombre) {
                let resultadosIdBeneficiado = inputNombre.id + "_resultados";
                let resultadosDivBeneficiado = document.getElementById(resultadosIdBeneficiado);
                if (!resultadosDivBeneficiado) {
                    resultadosDivBeneficiado = document.createElement("div");
                    resultadosDivBeneficiado.id = resultadosIdBeneficiado;
                    resultadosDivBeneficiado.className = "autocomplete-results list-group";
                    resultadosDivBeneficiado.style.cssText = `
                        position: absolute;
                        z-index: 99999;
                        top: 100%;
                        left: 0;
                        width: 100%;
                        min-width: 200px;
                        max-height: 250px;
                        overflow-y: auto;
                        display: none;
                        background-color: #ffffff !important;
                        border: 1px solid #ddd;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    `;
                    inputNombre.parentNode.style.position = "relative";
                    inputNombre.parentNode.appendChild(resultadosDivBeneficiado);
                }

                inputNumero.addEventListener("keydown", event => {
                    if (event.key === "Enter") {
                        event.preventDefault();
                        const valor = inputNumero.value.trim();
                        if (!valor) return;
                        buscarEmpleado(valor, row, resultadosDivBeneficiado, inputNombre);
                    }
                });

                inputNombre.addEventListener("input", () => {
                    const query = inputNombre.value.trim();

                    if (inputNombre.buscarTimer) {
                        clearTimeout(inputNombre.buscarTimer);
                        inputNombre.buscarTimer = null;
                    }

                    if (query.length < 2) {
                        resultadosDivBeneficiado.style.display = "none";
                        return;
                    }

                    inputNombre.buscarTimer = setTimeout(() => {
                        buscarAutocompletado(query.toUpperCase(), row, resultadosDivBeneficiado, inputNombre);
                    }, 300);
                });

                inputNombre.addEventListener("keydown", (event) => {
                    const resultados = resultadosDivBeneficiado.querySelectorAll("button");
                    const resultadoActivo = resultadosDivBeneficiado.querySelector(".active");
                    let index = -1;
                    
                    if (resultados.length > 0) {
                        if (resultadoActivo) {
                            index = Array.from(resultados).indexOf(resultadoActivo);
                        }
                        
                        switch(event.key) {
                            case "ArrowDown":
                                event.preventDefault();
                                if (index < resultados.length - 1) {
                                    if (resultadoActivo) resultadoActivo.classList.remove("active");
                                    resultados[index + 1].classList.add("active");
                                } else if (resultados.length > 0) {
                                    if (resultadoActivo) resultadoActivo.classList.remove("active");
                                    resultados[0].classList.add("active");
                                }
                                break;
                                
                            case "ArrowUp":
                                event.preventDefault();
                                if (index > 0) {
                                    if (resultadoActivo) resultadoActivo.classList.remove("active");
                                    resultados[index - 1].classList.add("active");
                                }
                                break;
                                
                            case "Enter":
                                if (resultadoActivo && resultadosDivBeneficiado.style.display !== "none") {
                                    event.preventDefault();
                                    resultadoActivo.click();
                                }
                                break;
                                
                            case "Escape":
                                resultadosDivBeneficiado.style.display = "none";
                                break;
                        }
                    }
                });

                document.addEventListener("click", e => {
                    if (!resultadosDivBeneficiado.contains(e.target) && e.target !== inputNombre) {
                        resultadosDivBeneficiado.style.display = "none";
                    }
                });
            }
        });
    }

    // Función para buscar empleado solicitante (usado por número de empleado)
    function buscarEmpleadoSolicitante(query, row, resultadosDiv, inputNombre) {
        fetch(`/ordenes/empleados/buscar/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                if (!data.resultados || data.resultados.length === 0) {
                    alert("Empleado no encontrado");
                    return;
                }
                const emp = data.resultados[0];
                llenarCamposFormsetSolicitante(row, emp);
                if (inputNombre) inputNombre.value = emp.Nombre_Empleado;
            })
            .catch(console.error);
    }

    // Función para autocompletado por nombre del solicitante
    function buscarAutocompletadoSolicitante(query, row, resultadosDiv, inputNombre) {
        // Obtener el valor anterior del input hidden asociado
        const inputHidden = document.querySelector(`[data-empleado-id]`); // Ajusta el selector según tu HTML
        const valorAnterior = Number(inputHidden?.value || 0);
        
        // 🔁 Elegir endpoint según el valor anterior (misma lógica de buscarEmpleado)
        const endpoint = valorAnterior === 0
            ? "/ordenes/funcionarios/buscar/"
            : "/ordenes/empleados/buscar/";

        fetch(`${endpoint}?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                resultadosDiv.innerHTML = "";
                
                if (!data.resultados || data.resultados.length === 0) {
                    resultadosDiv.style.display = "none";
                    return;
                }
                
                const resultados = data.resultados.slice(0, 10);
                
                resultados.forEach(emp => {
                    const btn = document.createElement("button");
                    btn.type = "button";
                    btn.className = "list-group-item list-group-item-action text-start";
                    btn.tabIndex = -1;
                    btn.style.cssText = "border: none; background: none; width: 100%; text-align: left; padding: 8px 12px; cursor: pointer;";
                    
                    btn.innerHTML = `
                        <div><strong>${emp.Numero_Empleado}</strong></div>
                        <div>${emp.Nombre_Empleado}</div>
                        <small style="color: #6c757d;">${emp.Dependencia} </small>
                    `;
                    
                    btn.onclick = (e) => {
                        e.preventDefault();
                        llenarCamposFormsetSolicitante(row, emp);
                        if (inputNombre) inputNombre.value = emp.Nombre_Empleado;
                        resultadosDiv.style.display = "none";
                    };
                    
                    btn.onmouseenter = () => {
                        resultadosDiv.querySelectorAll("button").forEach(b => {
                            b.classList.remove("active");
                            b.style.backgroundColor = "";
                        });
                        btn.classList.add("active");
                        btn.style.backgroundColor = "#f8f9fa";
                    };
                    
                    btn.onmouseleave = () => {
                        if (!btn.classList.contains("active")) {
                            btn.style.backgroundColor = "";
                        }
                    };
                    
                    resultadosDiv.appendChild(btn);
                });
                
                resultadosDiv.style.display = "block";
                
                if (resultados.length > 5) {
                    resultadosDiv.style.maxHeight = "250px";
                    resultadosDiv.style.overflowY = "scroll";
                }
            })
            .catch(error => {
                console.error("Error en autocompletado:", error);
                resultadosDiv.style.display = "none";
            });
    }

    // Función que llena todos los campos del formset de un row con los datos del empleado para solicitante
    function llenarCamposFormsetSolicitante(row, emp) {
        const campos = [
            { selector: "input[name$='usuario_solicitante']", value: emp.Numero_Empleado },
            { selector: "input[name$='nombre_solicitante']", value: emp.Nombre_Empleado },
            { selector: "input[name$='dependencia_solicitante']", value: emp.Dependencia },
            { selector: "input[name$='correo_solicitante']", value: "" },
            { selector: "input[name$='telefono_solicitante']", value: "" },
            { selector: "select[name$='puesto_solicitante']", value: "" }
        ];

        campos.forEach(c => {
            const input = row.querySelector(c.selector);
            if (!input) return;

            if (input.tagName === "SELECT") {
                const valorEmp = c.value.toUpperCase().trim();

                for (let i = 0; i < input.options.length; i++) {
                    const optionValue = input.options[i].value.toUpperCase().trim();
                    const optionText  = input.options[i].text.toUpperCase().trim();

                    if (optionValue === valorEmp || optionText === valorEmp) {
                        input.value = input.options[i].value;
                        break;
                    }
                }
            } else {
                input.value = c.value;
            }
        });
    }

    // Función para buscar empleado beneficiado
    function buscarEmpleado(query, row, resultadosDiv, inputNombre) {
        fetch(`/ordenes/empleados/buscar/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                if (!data.resultados || data.resultados.length === 0) {
                    alert("Empleado no encontrado");
                    return;
                }
                const emp = data.resultados[0];
                llenarCamposFormsetBeneficiado(row, emp);
                if (inputNombre) inputNombre.value = emp.Nombre_Empleado;
            })
            .catch(console.error);
    }

    // Función para autocompletado por nombre del beneficiado
    function buscarAutocompletado(query, row, resultadosDiv, inputNombre) {
        // Obtener el valor anterior del input hidden asociado
        // Asumiendo que existe un input hidden con id o data-atributo relacionado
        const inputHidden = document.querySelector(`[data-beneficiado-id]`); // Ajusta este selector
        const valorAnterior = Number(inputHidden?.value || 0);
        
        // 🔁 Elegir endpoint según el valor anterior (misma lógica de buscarEmpleado)
        const endpoint = valorAnterior === 0
            ? "/ordenes/funcionarios/buscar/"
            : "/ordenes/empleados/buscar/";

        fetch(`${endpoint}?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                resultadosDiv.innerHTML = "";
                
                if (!data.resultados || data.resultados.length === 0) {
                    resultadosDiv.style.display = "none";
                    return;
                }
                
                const resultados = data.resultados.slice(0, 10);
                
                resultados.forEach(emp => {
                    const btn = document.createElement("button");
                    btn.type = "button";
                    btn.className = "list-group-item list-group-item-action text-start";
                    btn.tabIndex = -1;
                    btn.style.cssText = "border: none; background: none; width: 100%; text-align: left; padding: 8px 12px; cursor: pointer;";
                    
                    btn.innerHTML = `
                        <div><strong>${emp.Numero_Empleado}</strong></div>
                        <div>${emp.Nombre_Empleado}</div>
                        <small style="color: #6c757d;">${emp.Dependencia} </small>
                    `;
                    
                    btn.onclick = (e) => {
                        e.preventDefault();
                        llenarCamposFormsetBeneficiado(row, emp);
                        if (inputNombre) inputNombre.value = emp.Nombre_Empleado;
                        resultadosDiv.style.display = "none";
                    };
                    
                    btn.onmouseenter = () => {
                        resultadosDiv.querySelectorAll("button").forEach(b => {
                            b.classList.remove("active");
                            b.style.backgroundColor = "";
                        });
                        btn.classList.add("active");
                        btn.style.backgroundColor = "#f8f9fa";
                    };
                    
                    btn.onmouseleave = () => {
                        if (!btn.classList.contains("active")) {
                            btn.style.backgroundColor = "";
                        }
                    };
                    
                    resultadosDiv.appendChild(btn);
                });
                
                resultadosDiv.style.display = "block";
                
                if (resultados.length > 5) {
                    resultadosDiv.style.maxHeight = "250px";
                    resultadosDiv.style.overflowY = "scroll";
                }
            })
            .catch(error => {
                console.error("Error en autocompletado:", error);
                resultadosDiv.style.display = "none";
            });
    }
    // Función que llena todos los campos del formset de un row con los datos del empleado para beneficiado
    function llenarCamposFormsetBeneficiado(row, emp) {
        const campos = [
            { selector: "input[name$='usuario_beneficiado']", value: emp.Numero_Empleado },
            { selector: "input[name$='nombre_beneficiado']", value: emp.Nombre_Empleado },
            { selector: "input[name$='dependencia_beneficiado']", value: emp.Dependencia },
            { selector: "input[name$='correo_beneficiado']", value: "" },
            { selector: "input[name$='telefono_beneficiado']", value: "" },
            { selector: "select[name$='puesto_beneficiado']", value: "" }
        ];

        campos.forEach(c => {
            const input = row.querySelector(c.selector);
            if (!input) return;

            if (input.tagName === "SELECT") {
                const valorEmp = c.value.toUpperCase().trim();

                for (let i = 0; i < input.options.length; i++) {
                    const optionValue = input.options[i].value.toUpperCase().trim();
                    const optionText  = input.options[i].text.toUpperCase().trim();

                    if (optionValue === valorEmp || optionText === valorEmp) {
                        input.value = input.options[i].value;
                        break;
                    }
                }
            } else {
                input.value = c.value;
            }
        });
    }

    // Inicializar al cargar la página
    inicializarFormset();

    // Si usas Django formsets dinámicos, necesitas reinicializar cuando se agregue un nuevo form
    const agregarBtn = document.querySelector("[id$='-ADD']");
    if (agregarBtn) {
        agregarBtn.addEventListener("click", () => {
            setTimeout(inicializarFormset, 100);
        });
    }

});

document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("change", function (e) {

        if (!e.target.classList.contains("igualar-puesto")) return;

        const switchInput = e.target;
        const row = switchInput.closest(".solicitante-form");

        if (!row) return;

        // Campos a copiar
        const campos = [
            ["usuario_beneficiado", "usuario_solicita"],
            ["nombre_beneficiado", "nombre_solicitante"],
            ["dependencia_beneficiado", "dependencia_solicitante"],
            ["correo_beneficiado", "correo_solicitante"],
            ["telefono_beneficiado", "telefono_solicitante"],
            ["puesto_beneficiado", "puesto_solicitante"],
        ];

        campos.forEach(([origen, destino]) => {

            const campoOrigen = row.querySelector(`[name$='${origen}']`);
            const campoDestino = row.querySelector(`[name$='${destino}']`);

            if (!campoOrigen || !campoDestino) return;

            if (switchInput.checked) {
                campoDestino.value = campoOrigen.value;

                if (campoDestino.tagName === "SELECT") {
                    campoDestino.dispatchEvent(new Event("change"));
                }

            } else {
                campoDestino.value = "";
            }
        });

    });

});