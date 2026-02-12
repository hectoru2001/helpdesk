// Esperar a que el DOM esté cargado para poder encontrar el input
document.addEventListener("DOMContentLoaded", function() {
    const patrimonioInput = document.getElementById("id_patrimonio");

    if (patrimonioInput) {
        patrimonioInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter") {
                llenarPatrimonio(e);
            }
        });
    }
});

function llenarPatrimonio(e) {
    e.preventDefault(); // Evita que el formulario se envíe al dar Enter
    
    const patrimonioInput = document.getElementById("id_patrimonio");
    const query = patrimonioInput.value.trim();

    if (!query) return;

    fetch(`/ordenes/patrimonio/buscar/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            if (!data.resultados || data.resultados.length === 0) {
                alert("Patrimonio no encontrado");
                return;
            }

            const patrimonio = data.resultados[0];

            // Rellenamos los campos adicionales
            document.getElementById("id_serie").value = patrimonio.serie;
            document.getElementById("id_equipo").value = patrimonio.descripcion;

            // Selectores de marca y color
            seleccionarSelectPorTexto("id_marca", patrimonio.marca);
            seleccionarSelectPorTexto("id_color", patrimonio.color);
        })
        .catch(error => {
            console.error("Error en la búsqueda:", error);
        });
}

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