// Carpetas data global
window.carpetasData = {{ carpetas_disponibles | safe }};

// Enhanced renderTable with dropdown
(function () {
    const originalRenderTable = window.renderTable || function () { };

    window.renderTable = function (cotizaciones) {
        const tbody = document.getElementById('cotizaciones-tbody');
        if (!tbody) return;

        if (!cotizaciones || cotizaciones.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                        <div class="flex flex-col items-center">
                            <i class="fas fa-inbox text-5xl text-gray-300 mb-3"></i>
                            <p class="font-medium">No se encontraron cotizaciones</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        // Build dropdown options HTML
        const carpetasOptions = window.carpetasData ? window.carpetasData.map(c =>
            `<option value="${c.id}">${c.nombre}</option>`
        ).join('') : '';

        const rowsHTML = cotizaciones.map(cot => {
            const statusBadge = getStatusBadge ? getStatusBadge(cot.estado, cot.estado_display) : cot.estado_display;

            return `
                <tr class="hover:bg-gray-50 transition duration-150">
                    <td class="px-4 py-3 text-sm font-medium text-gray-900">${cot.id}</td>
                    <td class="px-4 py-3">${statusBadge}</td>
                    <td class="px-4 py-3">
                        <div class="text-sm font-semibold text-gray-900">${cot.proyecto_nombre}</div>
                        <div class="text-xs text-gray-500">${cot.cliente_nombre}</div>
                    </td>
                    <td class="px-4 py-3">
                        <select 
                            data-cotizacion-id="${cot.id}" 
                            class="carpeta-dropdown text-xs bg-white border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                            onchange="window.updateCotizacionCarpeta(${cot.id}, this.value)">
                            <option value="">Sin Carpeta</option>
                            ${carpetasOptions}
                        </select>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-500">${cot.fecha_creacion}</td>
                    <td class="px-4 py-3 text-right">
                        <span class="text-sm font-bold text-red-600">$ ${formatNumber ? formatNumber(cot.total_costo) : cot.total_costo}</span>
                    </td>
                    <td class="px-4 py-3 text-center">
                        <div class="flex items-center justify-center space-x-2">
                            <a href="${cot.url_detalle}" class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1" title="Ver detalles">
                                <i class="fas fa-eye text-sm"></i>
                            </a>
                            <a href="${cot.url_pdf}" class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1" title="Descargar PDF">
                                <i class="fa-solid fa-download"></i>
                            </a>
                            <a href="${cot.url_eliminar}" class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1" title="Eliminar">
                                <i class="fa-solid fa-trash"></i>
                            </a>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = rowsHTML;

        // Set selected values for dropdowns
        cotizaciones.forEach(cot => {
            const dropdown = tbody.querySelector(`select[data-cotizacion-id="${cot.id}"]`);
            if (dropdown && cot.carpeta_id) {
                dropdown.value = cot.carpeta_id;
            }
        });
    };
})();
