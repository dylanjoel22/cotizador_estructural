/**
 * Dashboard de Cotizaciones - JavaScript Module
 * 
 * Maneja búsqueda en tiempo real con debounce, navegación por carpetas,
 * y renderizado dinámico de la tabla de cotizaciones.
 */

// ========================================================================
// CONFIGURATION & STATE
// ========================================================================

const CONFIG = {
    DEBOUNCE_DELAY: 300, // ms
    API_SEARCH_URL: '/cotizaciones/api/search/',
    API_CARPETAS_URL: '/cotizaciones/api/carpetas/',
};

const state = {
    currentFolder: '',
    currentSearch: '',
    isLoading: false,
};

// ========================================================================
// UTILITY FUNCTIONS
// ========================================================================

/**
 * Debounce function - Retrasa la ejecución hasta que pase un tiempo sin llamadas
 * @param {Function} func - Función a ejecutar
 * @param {number} delay - Delay en ms
 * @returns {Function} - Función debounced
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Muestra u oculta el spinner de carga
 * @param {boolean} show - true para mostrar, false para ocultar
 */
function toggleLoadingSpinner(show) {
    const spinner = document.getElementById('search-spinner');
    if (spinner) {
        spinner.classList.toggle('hidden', !show);
    }
}

/**
 * Muestra notificación toast (error handling)
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - 'success' | 'error' | 'info'
 */
function showNotification(message, type = 'info') {
    // TODO: Implementar sistema de notificaciones toast
    // Por ahora solo console
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ========================================================================
// API CALLS
// ========================================================================

/**
 * Realiza búsqueda de cotizaciones en el servidor
 * @param {string} query - Término de búsqueda
 * @param {string} carpeta - Filtro de carpeta (opcional)
 * @returns {Promise<Object>} - Datos de cotizaciones
 */
async function searchCotizaciones(query = '', carpeta = '') {
    try {
        toggleLoadingSpinner(true);

        const params = new URLSearchParams();
        if (query) params.append('q', query);
        if (carpeta) params.append('carpeta', carpeta);

        const url = `${CONFIG.API_SEARCH_URL}?${params.toString()}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error al buscar cotizaciones:', error);
        showNotification('Error al cargar cotizaciones. Por favor, intente nuevamente.', 'error');
        return { cotizaciones: [], count: 0 };
    } finally {
        toggleLoadingSpinner(false);
    }
}

/**
 * Obtiene lista de carpetas del servidor
 * @returns {Promise<Object>} - Lista de carpetas con conteos
 */
async function fetchCarpetas() {
    try {
        const response = await fetch(CONFIG.API_CARPETAS_URL, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error('Error al obtener carpetas:', error);
        return { carpetas: [], sin_carpeta_count: 0, total_count: 0 };
    }
}

// ========================================================================
// RENDERING FUNCTIONS
// ========================================================================

/**
 * Genera HTML de badge de estado
 * @param {string} estado - Código de estado
 * @param {string} estadoDisplay - Texto a mostrar
 * @returns {string} - HTML del badge
 */
function getEstadoBadgeHTML(estado, estadoDisplay) {
    const badgeConfig = {
        'TERMINADO': {
            bgColor: 'bg-green-100',
            textColor: 'text-green-800',
            dotColor: 'bg-green-500',
        },
        'CANCELADO': {
            bgColor: 'bg-red-100',
            textColor: 'text-red-800',
            dotColor: 'bg-red-500',
        },
        'POR_REVISAR': {
            bgColor: 'bg-orange-100',
            textColor: 'text-orange-800',
            dotColor: 'bg-orange-500',
        },
        'BORRADOR': {
            bgColor: 'bg-gray-100',
            textColor: 'text-gray-800',
            dotColor: 'bg-gray-400',
        },
    };

    const config = badgeConfig[estado] || badgeConfig['BORRADOR'];

    return `
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor}">
            <span class="w-2 h-2 rounded-full ${config.dotColor} mr-1.5"></span>
            ${estadoDisplay}
        </span>
    `;
}

/**
 * Renderiza la tabla de cotizaciones
 * @param {Array} cotizaciones - Array de objetos cotizacion
 */
function renderTable(cotizaciones) {
    const tbody = document.getElementById('cotizaciones-tbody');

    if (!tbody) {
        console.error('No se encontró el tbody de la tabla');
        return;
    }

    // Caso: sin resultados
    if (cotizaciones.length === 0) {
        tbody.innerHTML = `
            <tr id="empty-state">
                <td colspan="6" class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2 text-gray-300"></i>
                    <p class="text-sm">No se encontraron cotizaciones.</p>
                </td>
            </tr>
        `;
        return;
    }

    // Construir filas
    const rowsHTML = cotizaciones.map(cot => {
        const clienteHTML = `
            <div class="font-medium">${cot.proyecto_nombre}</div>
            <div class="text-xs text-gray-500">${cot.cliente_nombre}</div>
        `;

        return `
            <tr class="hover:bg-blue-50/50 transition duration-100">
                <td class="px-3 py-3 text-sm font-bold text-[#002B5B]">${cot.id}</td>
                <td class="px-3 py-3 text-sm">
                    ${getEstadoBadgeHTML(cot.estado, cot.estado_display)}
                </td>
                <td class="px-3 py-3 text-sm text-gray-900">
                    ${clienteHTML}
                </td>
                <td class="px-3 py-3 text-sm text-center text-gray-600">${cot.fecha_creacion}</td>
                <td class="px-3 py-3 text-sm font-semibold text-red-600 text-right">$ ${parseFloat(cot.total_costo).toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td class="px-3 py-3 text-center text-sm font-medium">
                    <div class="flex items-center justify-center space-x-2">
                        <a href="${cot.url_detalle}" 
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Ver detalles">
                            <i class="fas fa-eye text-sm"></i>
                        </a>
                        <a href="${cot.url_pdf}" 
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Descargar PDF">
                            <i class="fa-solid fa-download"></i>
                        </a>
                        <a href="${cot.url_eliminar}"
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Eliminar">
                            <i class="fa-solid fa-trash"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    // Single DOM update (performance)
    tbody.innerHTML = rowsHTML;
}

/**
 * Renderiza la lista de carpetas en el sidebar
 * @param {Object} data - Datos de carpetas del API
 */
function renderCarpetasList(data) {
    const carpetasList = document.getElementById('carpetas-list');
    if (!carpetasList) return;

    const { carpetas, sin_carpeta_count, total_count } = data;

    const carpetasHTML = carpetas.map(carpeta => `
        <li>
            <button data-carpeta="${carpeta.nombre}" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between">
                <span class="flex items-center">
                    <i class="fas fa-folder mr-2 text-yellow-600"></i>
                    ${carpeta.nombre}
                </span>
                <span class="carpeta-count bg-gray-400 text-white text-xs px-2 py-0.5 rounded-full">${carpeta.count}</span>
            </button>
        </li>
    `).join('');

    // Construir HTML completo
    const fullHTML = `
        <!-- Opción "Todas" -->
        <li>
            <button data-carpeta="" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between active bg-blue-200 font-medium">
                <span class="flex items-center">
                    <i class="fas fa-list-ul mr-2 text-gray-600"></i>
                    Todas
                </span>
                <span class="carpeta-count bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">${total_count}</span>
            </button>
        </li>
        ${carpetasHTML}
        <!-- Opción "Sin Carpeta" -->
        <li>
            <button data-carpeta="sin_carpeta" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between">
                <span class="flex items-center">
                    <i class="fas fa-inbox mr-2 text-gray-500"></i>
                    Sin Carpeta
                </span>
                <span class="carpeta-count bg-gray-400 text-white text-xs px-2 py-0.5 rounded-full">${sin_carpeta_count}</span>
            </button>
        </li>
    `;

    carpetasList.innerHTML = fullHTML;

    // Reattach event listeners
    attachCarpetaListeners();
}

// ========================================================================
// EVENT HANDLERS
// ========================================================================

/**
 * Handler para búsqueda (con debounce)
 */
const handleSearch = debounce(async function (event) {
    const query = event.target.value.trim();
    state.currentSearch = query;

    // Realizar búsqueda
    const data = await searchCotizaciones(query, state.currentFolder);
    renderTable(data.cotizaciones);
}, CONFIG.DEBOUNCE_DELAY);

/**
 * Handler para click en carpeta
 * @param {Event} event - Evento de click
 */
async function handleCarpetaClick(event) {
    const button = event.currentTarget;
    const carpeta = button.dataset.carpeta;

    // Update UI state (resaltar carpeta activa)
    document.querySelectorAll('.carpeta-item').forEach(item => {
        item.classList.remove('active', 'bg-blue-200', 'font-medium');
    });
    button.classList.add('active', 'bg-blue-200', 'font-medium');

    // Update state
    state.currentFolder = carpeta;

    // Realizar búsqueda con filtro de carpeta
    const data = await searchCotizaciones(state.currentSearch, carpeta);
    renderTable(data.cotizaciones);
}

/**
 * Attach event listeners a botones de carpeta
 */
function attachCarpetaListeners() {
    const carpetaButtons = document.querySelectorAll('.carpeta-item');
    carpetaButtons.forEach(button => {
        button.addEventListener('click', handleCarpetaClick);
    });
}

// ========================================================================
// INITIALIZATION
// ========================================================================

/**
 * Inicializa el dashboard
 */
async function initDashboard() {
    console.log('Inicializando Dashboard de Cotizaciones...');

    // Attach search listener
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }

    // Attach carpeta listeners
    attachCarpetaListeners();

    // Cargar lista de carpetas actualizada
    const carpetasData = await fetchCarpetas();
    renderCarpetasList(carpetasData);

    console.log('Dashboard inicializado correctamente');
}

// ========================================================================
// MODAL MANAGEMENT
// ========================================================================

/**
 * Abre el modal de nueva carpeta
 */
function openNewFolderModal() {
    const modal = document.getElementById('nueva-carpeta-modal');
    const input = document.getElementById('carpeta-nombre-input');
    const errorDiv = document.getElementById('modal-error-message');

    if (modal && input) {
        modal.classList.remove('hidden');
        input.value = '';
        input.focus();
        errorDiv.classList.add('hidden');
    }
}

/**
 * Cierra el modal de nueva carpeta
 */
function closeNewFolderModal() {
    const modal = document.getElementById('nueva-carpeta-modal');
    const input = document.getElementById('carpeta-nombre-input');
    const errorDiv = document.getElementById('modal-error-message');

    if (modal) {
        modal.classList.add('hidden');
        input.value = '';
        errorDiv.classList.add('hidden');
    }
}

/**
 * Muestra mensaje de error en el modal
 */
function showModalError(message) {
    const errorDiv = document.getElementById('modal-error-message');
    const errorText = document.getElementById('modal-error-text');

    if (errorDiv && errorText) {
        errorText.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

/**
 * Crea una nueva carpeta
 */
async function createNewFolder() {
    const input = document.getElementById('carpeta-nombre-input');
    const carpetaNombre = input.value.trim();

    // Validación básica
    if (!carpetaNombre) {
        showModalError('Por favor, ingresa un nombre para la carpeta');
        return;
    }

    if (carpetaNombre.length > 100) {
        showModalError('El nombre de la carpeta es muy largo (máximo 100 caracteres)');
        return;
    }

    try {
        // Obtener CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            getCookie('csrftoken');

        // Hacer POST request
        const response = await fetch('/cotizaciones/api/carpetas/crear/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ nombre: carpetaNombre })
        });

        const data = await response.json();

        if (!response.ok) {
            showModalError(data.error || 'Error al crear la carpeta');
            return;
        }

        console.log(`Carpeta "${carpetaNombre}" creada exitosamente`);

        // Cerrar modal
        closeNewFolderModal();

        // Recargar lista de carpetas
        const updatedCarpetas = await fetchCarpetas();
        renderCarpetasList(updatedCarpetas);

        // Mostrar notificación
        showNotification(`Carpeta "${carpetaNombre}" creada exitosamente`, 'success');

    } catch (error) {
        console.error('Error al crear carpeta:', error);
        showModalError('Error de conexión. Intenta nuevamente.');
    }
}

/**
 * Obtiene el CSRF token de las cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Inicializa event listeners del modal
 */
function initModalListeners() {
    const openBtn = document.getElementById('nueva-carpeta-btn');
    const closeBtn = document.getElementById('modal-close-btn');
    const cancelBtn = document.getElementById('modal-cancel-btn');
    const confirmBtn = document.getElementById('modal-confirm-btn');
    const input = document.getElementById('carpeta-nombre-input');
    const modal = document.getElementById('nueva-carpeta-modal');

    // Abrir modal
    if (openBtn) {
        openBtn.addEventListener('click', openNewFolderModal);
    }

    // Cerrar modal
    if (closeBtn) {
        closeBtn.addEventListener('click', closeNewFolderModal);
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeNewFolderModal);
    }

    // Confirmar creación
    if (confirmBtn) {
        confirmBtn.addEventListener('click', createNewFolder);
    }

    // Enter key en input
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                createNewFolder();
            }
        });
    }

    // Cerrar al hacer click fuera del modal
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeNewFolderModal();
            }
        });
    }
}

/**
 * Actualiza la carpeta de una cotización
 */
async function updateCotizacionCarpeta(cotizacionId, carpetaId) {
    try {
        const csrfToken = getCookie('csrftoken');

        const response = await fetch(`/cotizaciones/api/cotizaciones/${cotizacionId}/carpeta/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ carpeta_id: carpetaId || '' })
        });

        const data = await response.json();

        if (!response.ok) {
            console.error('Error al actualizar carpeta:', data.error);
            showNotification(data.error || 'Error al actualizar carpeta', 'error');
            return false;
        }

        // Recargar datos para actualizar contadores
        await loadInitialData();

        showNotification('Carpeta actualizada correctamente', 'success');
        return true;

    } catch (error) {
        console.error('Error al actualizar carpeta:', error);
        showNotification('Error de conexión', 'error');
        return false;
    }
}

// Hace la función global accesible
window.updateCotizacionCarpeta = updateCotizacionCarpeta;

// ========================================================================
// ENTRY POINT
// ========================================================================

// Esperar a que el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard();
        initModalListeners();
    });
} else {
    initDashboard();
    initModalListeners();
}
