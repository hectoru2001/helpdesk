/**
 * Script para el reporte de órdenes con gráficas
 */

// Variables globales
let statusChart = null;

/**
 * Inicializa la gráfica de distribución de estados
 */
function initializeChart() {
    // Verificar si hay datos disponibles
    if (!window.reporteOrdenesData || window.reporteOrdenesData.length === 0) {
        const chartContainer = document.getElementById('chartContainer');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="alert alert-info text-center">
                    No hay datos disponibles para mostrar la gráfica
                </div>
            `;
        }
        return;
    }

    const reportData = window.reporteOrdenesData;
    const usuarios = reportData.map(r => r.usuario);
    const ctx = document.getElementById('statusDistributionChart');
    
    if (!ctx) {
        console.error('No se encontró el elemento canvas para la gráfica');
        return;
    }
    
    // Destruir gráfica anterior si existe
    if (statusChart) {
        statusChart.destroy();
    }
    
    // Crear nueva gráfica
    statusChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: usuarios,
            datasets: [
                {
                    label: 'Asignadas',
                    data: reportData.map(r => r.asignadas),
                    backgroundColor: 'rgba(255, 206, 86, 0.7)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                },
                {
                    label: 'En Proceso',
                    data: reportData.map(r => r.enProceso),
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Terminadas',
                    data: reportData.map(r => r.terminadas),
                    backgroundColor: 'rgba(75, 192, 75, 0.7)',
                    borderColor: 'rgba(75, 192, 75, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Canceladas',
                    data: reportData.map(r => r.canceladas),
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y}`;
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cantidad de órdenes',
                        font: {
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        stepSize: 1,
                        precision: 0
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Configura el switch para cambiar entre tabla y gráfica
 */
function setupViewToggle() {
    const viewToggle = document.getElementById('viewToggle');
    const printGraphButton = document.getElementById('printGraphButton');

    if (!viewToggle) return;
    
    viewToggle.addEventListener('change', function() {
        const isTableMode = this.checked;
        const tableContainer = document.getElementById('tableContainer');
        const chartContainer = document.getElementById('chartContainer');
        const viewModeLabel = document.getElementById('viewModeLabel');
        const printGraphButton = document.getElementById('printGraphButton');

        if (tableContainer && chartContainer && viewModeLabel) {
            if (isTableMode) {
                tableContainer.classList.remove('d-none');
                chartContainer.classList.add('d-none');
                viewModeLabel.textContent = 'Tabla';

                // 🔒 Ocultar botón de imprimir gráfica
                if (printGraphButton) {
                    printGraphButton.classList.add('d-none');
                }

            } else {
                tableContainer.classList.add('d-none');
                chartContainer.classList.remove('d-none');
                viewModeLabel.textContent = 'Gráfica';

                // 🖨️ Mostrar botón de imprimir gráfica
                if (printGraphButton) {
                    printGraphButton.classList.remove('d-none');
                }

                setTimeout(() => {
                    if (statusChart) {
                        statusChart.resize();
                    } else if (window.reporteOrdenesData && window.reporteOrdenesData.length > 0) {
                        initializeChart();
                    }
                }, 100);
            }
        }
    });

}

/**
 * Configura el redimensionamiento de la gráfica
 */
function setupResizeHandler() {
    window.addEventListener('resize', function() {
        if (statusChart && document.getElementById('viewToggle') && 
            !document.getElementById('viewToggle').checked) {
            statusChart.resize();
        }
    });
}

/**
 * Inicializa todas las funcionalidades
 */
function initializeReporteOrdenes() {
    // Esperar a que Chart.js esté cargado
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no está cargado');
        return;
    }
    
    // Configurar las funcionalidades
    setupPrintGraphButton();
    setupViewToggle();
    setupResizeHandler();
    
    // Inicializar gráfica si hay datos
    if (window.reporteOrdenesData && window.reporteOrdenesData.length > 0) {
        initializeChart();
    }
    
    // También inicializar si los datos se cargan más tarde
    const checkDataInterval = setInterval(() => {
        if (window.reporteOrdenesData && window.reporteOrdenesData.length > 0 && !statusChart) {
            initializeChart();
            clearInterval(checkDataInterval);
        }
    }, 500);
    
    // Limpiar el intervalo después de 5 segundos
    setTimeout(() => clearInterval(checkDataInterval), 5000);
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeReporteOrdenes);
} else {
    initializeReporteOrdenes();
}

// Exportar funciones para uso externo si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeChart,
        setupViewToggle,
        initializeReporteOrdenes
    };
}

function setupPrintGraphButton() {
    const printButton = document.getElementById('printGraphButton');

    if (!printButton) return;

    printButton.addEventListener('click', function () {

        if (!statusChart) {
            alert('La gráfica no está disponible para imprimir');
            return;
        }

        // 🔓 Activar leyenda temporalmente
        statusChart.options.plugins.legend.display = true;
        statusChart.update();

        setTimeout(() => {
            const imageUrl = statusChart.toBase64Image();

            // 🔒 Volver a ocultar leyenda
            statusChart.options.plugins.legend.display = false;
            statusChart.update();

            const printWindow = window.open('', '_blank');

            printWindow.document.write(`
                <html>
                    <head>
                        <title>Reporte</title>
                        <style>
                            @page {
                                margin: 10mm;
                            }
                            body {
                                margin: 0;
                                padding: 0;
                                text-align: center;
                            }
                            img {
                                max-width: 100%;
                            }
                        </style>
                    </head>
                    <body>
                    <h3>Distribución de estados de órdenes por usuario</h3>
                        <img src="${imageUrl}">
                    </body>
                </html>
            `);

            printWindow.document.close();
            printWindow.focus();

            setTimeout(() => {
                printWindow.print();
                printWindow.close();
            }, 500);

        }, 200);
    });

}

