(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const a of document.querySelectorAll('link[rel="modulepreload"]'))r(a);new MutationObserver(a=>{for(const n of a)if(n.type==="childList")for(const s of n.addedNodes)s.tagName==="LINK"&&s.rel==="modulepreload"&&r(s)}).observe(document,{childList:!0,subtree:!0});function o(a){const n={};return a.integrity&&(n.integrity=a.integrity),a.referrerPolicy&&(n.referrerPolicy=a.referrerPolicy),a.crossOrigin==="use-credentials"?n.credentials="include":a.crossOrigin==="anonymous"?n.credentials="omit":n.credentials="same-origin",n}function r(a){if(a.ep)return;a.ep=!0;const n=o(a);fetch(a.href,n)}})();const l={DEBOUNCE_DELAY:300,API_SEARCH_URL:"/cotizador/api/search/",API_CARPETAS_URL:"/cotizador/api/carpetas/"},i={currentFolder:"",currentSearch:""};function x(e,t){let o;return function(...r){clearTimeout(o),o=setTimeout(()=>e.apply(this,r),t)}}function d(e){const t=document.getElementById("search-spinner");t&&t.classList.toggle("hidden",!e)}function g(e,t="info"){console.log(`[${t.toUpperCase()}] ${e}`)}async function p(e="",t=""){try{d(!0);const o=new URLSearchParams;e&&o.append("q",e),t&&o.append("carpeta",t);const r=`${l.API_SEARCH_URL}?${o.toString()}`,a=await fetch(r,{method:"GET",headers:{"X-Requested-With":"XMLHttpRequest"}});if(!a.ok)throw new Error(`HTTP error! status: ${a.status}`);return await a.json()}catch(o){return console.error("Error al buscar cotizaciones:",o),g("Error al cargar cotizaciones. Por favor, intente nuevamente.","error"),{cotizaciones:[],count:0}}finally{d(!1)}}async function b(){try{const e=await fetch(l.API_CARPETAS_URL,{method:"GET",headers:{"X-Requested-With":"XMLHttpRequest"}});if(!e.ok)throw new Error(`HTTP error! status: ${e.status}`);return await e.json()}catch(e){return console.error("Error al obtener carpetas:",e),{carpetas:[],sin_carpeta_count:0,total_count:0}}}function y(e,t){const o={TERMINADO:{bgColor:"bg-green-100",textColor:"text-green-800",dotColor:"bg-green-500"},CANCELADO:{bgColor:"bg-red-100",textColor:"text-red-800",dotColor:"bg-red-500"},POR_REVISAR:{bgColor:"bg-orange-100",textColor:"text-orange-800",dotColor:"bg-orange-500"},BORRADOR:{bgColor:"bg-gray-100",textColor:"text-gray-800",dotColor:"bg-gray-400"}},r=o[e]||o.BORRADOR;return`
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${r.bgColor} ${r.textColor}">
            <span class="w-2 h-2 rounded-full ${r.dotColor} mr-1.5"></span>
            ${t}
        </span>
    `}function f(e){const t=document.getElementById("cotizaciones-tbody");if(!t){console.error("No se encontró el tbody de la tabla");return}if(e.length===0){t.innerHTML=`
            <tr id="empty-state">
                <td colspan="6" class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2 text-gray-300"></i>
                    <p class="text-sm">No se encontraron cotizaciones.</p>
                </td>
            </tr>
        `;return}const o=e.map(r=>{const a=`
            <div class="font-medium">${r.proyecto_nombre}</div>
            <div class="text-xs text-gray-500">${r.cliente_nombre}</div>
        `;return`
            <tr class="hover:bg-blue-50/50 transition duration-100">
                <td class="px-3 py-3 text-sm font-bold text-[#002B5B]">${r.id}</td>
                <td class="px-3 py-3 text-sm">
                    ${y(r.estado,r.estado_display)}
                </td>
                <td class="px-3 py-3 text-sm text-gray-900">
                    ${a}
                </td>
                <td class="px-3 py-3 text-sm text-center text-gray-600">${r.fecha_creacion}</td>
                <td class="px-3 py-3 text-sm font-semibold text-red-600 text-right">$ ${parseFloat(r.total_costo).toLocaleString("es-CL",{minimumFractionDigits:2,maximumFractionDigits:2})}</td>
                <td class="px-3 py-3 text-center text-sm font-medium">
                    <div class="flex items-center justify-center space-x-2">
                        <a href="${r.url_detalle}" 
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Ver detalles">
                            <i class="fas fa-eye text-sm"></i>
                        </a>
                        <a href="${r.url_pdf}" 
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Descargar PDF">
                            <i class="fa-solid fa-download"></i>
                        </a>
                        <a href="${r.url_eliminar}"
                           class="text-[#7CA8D5] hover:text-[#002B5B] transition duration-150 p-1"
                           title="Eliminar">
                            <i class="fa-solid fa-trash"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `}).join("");t.innerHTML=o}function h(e){const t=document.getElementById("carpetas-list");if(!t)return;const{carpetas:o,sin_carpeta_count:r,total_count:a}=e,n=o.map(c=>`
        <li>
            <button data-carpeta="${c.nombre}" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between">
                <span class="flex items-center">
                    <i class="fas fa-folder mr-2 text-yellow-600"></i>
                    ${c.nombre}
                </span>
                <span class="carpeta-count bg-gray-400 text-white text-xs px-2 py-0.5 rounded-full">${c.count}</span>
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
                <span class="carpeta-count bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">${a}</span>
            </button>
        </li>
        ${n}
        <!-- Opción "Sin Carpeta" -->
        <li>
            <button data-carpeta="sin_carpeta" 
                    class="carpeta-item w-full text-left px-3 py-2 rounded-md text-sm hover:bg-blue-100 transition duration-150 flex items-center justify-between">
                <span class="flex items-center">
                    <i class="fas fa-inbox mr-2 text-gray-500"></i>
                    Sin Carpeta
                </span>
                <span class="carpeta-count bg-gray-400 text-white text-xs px-2 py-0.5 rounded-full">${r}</span>
            </button>
        </li>
    `;t.innerHTML=s,m()}const C=x(async function(e){const t=e.target.value.trim();i.currentSearch=t;const o=await p(t,i.currentFolder);f(o.cotizaciones)},l.DEBOUNCE_DELAY);async function L(e){const t=e.currentTarget,o=t.dataset.carpeta;document.querySelectorAll(".carpeta-item").forEach(a=>{a.classList.remove("active","bg-blue-200","font-medium")}),t.classList.add("active","bg-blue-200","font-medium"),i.currentFolder=o;const r=await p(i.currentSearch,o);f(r.cotizaciones)}function m(){document.querySelectorAll(".carpeta-item").forEach(t=>{t.addEventListener("click",L)})}async function u(){console.log("Inicializando Dashboard de Cotizaciones...");const e=document.getElementById("search-input");e&&e.addEventListener("input",C),m();const t=await b();h(t),console.log("Dashboard inicializado correctamente")}document.readyState==="loading"?document.addEventListener("DOMContentLoaded",u):u();document.body.classList.remove("fouc-hidden");console.log("Hola desde Vite y Django!");
