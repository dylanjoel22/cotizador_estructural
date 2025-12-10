(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))a(n);new MutationObserver(n=>{for(const o of n)if(o.type==="childList")for(const s of o.addedNodes)s.tagName==="LINK"&&s.rel==="modulepreload"&&a(s)}).observe(document,{childList:!0,subtree:!0});function r(n){const o={};return n.integrity&&(o.integrity=n.integrity),n.referrerPolicy&&(o.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?o.credentials="include":n.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function a(n){if(n.ep)return;n.ep=!0;const o=r(n);fetch(n.href,o)}})();const p={DEBOUNCE_DELAY:300,API_SEARCH_URL:"/cotizaciones/api/search/",API_CARPETAS_URL:"/cotizaciones/api/carpetas/"},d={currentFolder:"",currentSearch:""};function v(t,e){let r;return function(...a){clearTimeout(r),r=setTimeout(()=>t.apply(this,a),e)}}function m(t){const e=document.getElementById("search-spinner");e&&e.classList.toggle("hidden",!t)}function c(t,e="info"){console.log(`[${e.toUpperCase()}] ${t}`)}async function x(t="",e=""){try{m(!0);const r=new URLSearchParams;t&&r.append("q",t),e&&r.append("carpeta",e);const a=`${p.API_SEARCH_URL}?${r.toString()}`,n=await fetch(a,{method:"GET",headers:{"X-Requested-With":"XMLHttpRequest"}});if(!n.ok)throw new Error(`HTTP error! status: ${n.status}`);return await n.json()}catch(r){return console.error("Error al buscar cotizaciones:",r),c("Error al cargar cotizaciones. Por favor, intente nuevamente.","error"),{cotizaciones:[],count:0}}finally{m(!1)}}async function b(){try{const t=await fetch(p.API_CARPETAS_URL,{method:"GET",headers:{"X-Requested-With":"XMLHttpRequest"}});if(!t.ok)throw new Error(`HTTP error! status: ${t.status}`);return await t.json()}catch(t){return console.error("Error al obtener carpetas:",t),{carpetas:[],sin_carpeta_count:0,total_count:0}}}function w(t,e){const r={TERMINADO:{bgColor:"bg-green-100",textColor:"text-green-800",dotColor:"bg-green-500"},CANCELADO:{bgColor:"bg-red-100",textColor:"text-red-800",dotColor:"bg-red-500"},POR_REVISAR:{bgColor:"bg-orange-100",textColor:"text-orange-800",dotColor:"bg-orange-500"},BORRADOR:{bgColor:"bg-gray-100",textColor:"text-gray-800",dotColor:"bg-gray-400"}},a=r[t]||r.BORRADOR;return`
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${a.bgColor} ${a.textColor}">
            <span class="w-2 h-2 rounded-full ${a.dotColor} mr-1.5"></span>
            ${e}
        </span>
    `}function h(t){const e=document.getElementById("cotizaciones-tbody");if(!e){console.error("No se encontró el tbody de la tabla");return}if(t.length===0){e.innerHTML=`
            <tr id="empty-state">
                <td colspan="6" class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2 text-gray-300"></i>
                    <p class="text-sm">No se encontraron cotizaciones.</p>
                </td>
            </tr>
        `;return}const r=t.map(a=>{const n=`
            <div class="font-medium">${a.proyecto_nombre}</div>
            <div class="text-xs text-gray-500">${a.cliente_nombre}</div>
        `;return`
            <tr class="hover:bg-blue-50/50 transition duration-100">
                <td class="px-3 py-3 text-sm font-bold text-[#002B5B]">${a.id}</td>
                <td class="px-3 py-3 text-sm">
                    ${w(a.estado,a.estado_display)}
                </td>
                <td class="px-3 py-3 text-sm text-gray-900">
                    ${n}
                </td>
                <td class="px-3 py-3 text-sm text-center text-gray-600">${a.fecha_creacion}</td>
                <td class="px-3 py-3 text-sm font-semibold text-red-600 text-right">$ ${parseFloat(a.total_costo).toLocaleString("es-CL",{minimumFractionDigits:2,maximumFractionDigits:2})}</td>
                <td class="px-3 py-3 text-center text-sm font-medium">
                    <div class="flex items-center justify-center space-x-2">
                        <a href="${a.url_detalle}" 
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Ver detalles">
                            <i class="fas fa-eye text-sm"></i>
                        </a>
                        <a href="${a.url_pdf}" 
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Descargar PDF">
                            <i class="fa-solid fa-download"></i>
                        </a>
                        <a href="${a.url_eliminar}"
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Eliminar">
                            <i class="fa-solid fa-trash"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `}).join("");e.innerHTML=r}function E(t){const e=document.getElementById("carpetas-list");if(!e)return;const{carpetas:r,sin_carpeta_count:a,total_count:n}=t,o=r.map(u=>`
        <li>
            <button data-carpeta="${u.nombre}" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between">
                <span class="flex items-center">
                    <i class="fas fa-folder mr-2 text-yellow-600"></i>
                    ${u.nombre}
                </span>
                <span class="carpeta-count bg-gray-400 text-white text-xs px-2 py-0.5 rounded-full">${u.count}</span>
            </button>
        </li>
    `).join(""),s=`
        <!-- Opción "Todas" -->
        <li>
            <button data-carpeta="" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between active bg-blue-200 font-medium">
                <span class="flex items-center">
                    <i class="fas fa-list-ul mr-2 text-gray-600"></i>
                    Todas
                </span>
                <span class="carpeta-count bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">${n}</span>
            </button>
        </li>
        ${o}
        <!-- Opción "Sin Carpeta" -->
        <li>
            <button data-carpeta="sin_carpeta" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between">
                <span class="flex items-center">
                    <i class="fas fa-inbox mr-2 text-gray-500"></i>
                    Sin Carpeta
                </span>
                <span class="carpeta-count bg-gray-400 text-white text-xs px-2 py-0.5 rounded-full">${a}</span>
            </button>
        </li>
    `;e.innerHTML=s,C()}const B=v(async function(t){const e=t.target.value.trim();d.currentSearch=e;const r=await x(e,d.currentFolder);h(r.cotizaciones)},p.DEBOUNCE_DELAY);async function I(t){const e=t.currentTarget,r=e.dataset.carpeta;document.querySelectorAll(".carpeta-item").forEach(n=>{n.classList.remove("active","bg-blue-200","font-medium")}),e.classList.add("active","bg-blue-200","font-medium"),d.currentFolder=r;const a=await x(d.currentSearch,r);h(a.cotizaciones)}function C(){document.querySelectorAll(".carpeta-item").forEach(e=>{e.addEventListener("click",I)})}async function f(){console.log("Inicializando Dashboard de Cotizaciones...");const t=document.getElementById("search-input");t&&t.addEventListener("input",B),C();const e=await b();E(e),console.log("Dashboard inicializado correctamente")}function T(){const t=document.getElementById("nueva-carpeta-modal"),e=document.getElementById("carpeta-nombre-input"),r=document.getElementById("modal-error-message");t&&e&&(t.classList.remove("hidden"),e.value="",e.focus(),r.classList.add("hidden"))}function l(){const t=document.getElementById("nueva-carpeta-modal"),e=document.getElementById("carpeta-nombre-input"),r=document.getElementById("modal-error-message");t&&(t.classList.add("hidden"),e.value="",r.classList.add("hidden"))}function i(t){const e=document.getElementById("modal-error-message"),r=document.getElementById("modal-error-text");e&&r&&(r.textContent=t,e.classList.remove("hidden"))}async function g(){const e=document.getElementById("carpeta-nombre-input").value.trim();if(!e){i("Por favor, ingresa un nombre para la carpeta");return}if(e.length>100){i("El nombre de la carpeta es muy largo (máximo 100 caracteres)");return}try{const r=document.querySelector("[name=csrfmiddlewaretoken]")?.value||L("csrftoken"),a=await fetch("/cotizaciones/api/carpetas/crear/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":r,"X-Requested-With":"XMLHttpRequest"},body:JSON.stringify({nombre:e})}),n=await a.json();if(!a.ok){i(n.error||"Error al crear la carpeta");return}console.log(`Carpeta "${e}" creada exitosamente`),l();const o=await b();E(o),c(`Carpeta "${e}" creada exitosamente`,"success")}catch(r){console.error("Error al crear carpeta:",r),i("Error de conexión. Intenta nuevamente.")}}function L(t){let e=null;if(document.cookie&&document.cookie!==""){const r=document.cookie.split(";");for(let a=0;a<r.length;a++){const n=r[a].trim();if(n.substring(0,t.length+1)===t+"="){e=decodeURIComponent(n.substring(t.length+1));break}}}return e}function y(){const t=document.getElementById("nueva-carpeta-btn"),e=document.getElementById("modal-close-btn"),r=document.getElementById("modal-cancel-btn"),a=document.getElementById("modal-confirm-btn"),n=document.getElementById("carpeta-nombre-input"),o=document.getElementById("nueva-carpeta-modal");t&&t.addEventListener("click",T),e&&e.addEventListener("click",l),r&&r.addEventListener("click",l),a&&a.addEventListener("click",g),n&&n.addEventListener("keypress",s=>{s.key==="Enter"&&g()}),o&&o.addEventListener("click",s=>{s.target===o&&l()})}async function R(t,e){try{const r=L("csrftoken"),a=await fetch(`/cotizaciones/api/cotizaciones/${t}/carpeta/`,{method:"PATCH",headers:{"Content-Type":"application/json","X-CSRFToken":r,"X-Requested-With":"XMLHttpRequest"},body:JSON.stringify({carpeta_id:e||""})}),n=await a.json();return a.ok?(await loadInitialData(),c("Carpeta actualizada correctamente","success"),!0):(console.error("Error al actualizar carpeta:",n.error),c(n.error||"Error al actualizar carpeta","error"),!1)}catch(r){return console.error("Error al actualizar carpeta:",r),c("Error de conexión","error"),!1}}window.updateCotizacionCarpeta=R;document.readyState==="loading"?document.addEventListener("DOMContentLoaded",()=>{f(),y()}):(f(),y());document.body.classList.remove("fouc-hidden");console.log("Hola desde Vite y Django!");
