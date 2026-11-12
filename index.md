---
layout: home
#title: StickyDropsMap
#subtitle: Mapa de superficies vegetales con alta captación de agua atmosférica
cover-img: /assets/img/hero.jpg
---

Bienvenido al proyecto de ciencia ciudadana **StickyDropsMap** de la Universidad de Granada.
Ayúdanos a cartografiar las plantas y superficies capaces de capturar agua atmosférica — como
niebla y rocío — para entender mejor los recursos hídricos de nuestros ecosistemas.

<div style="text-align: center; margin: 40px 0;">
  <a href="/participate/" style="background-color: #2ea44f; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-size: 1.2em; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    🙋🏽‍♀️ ¿Cómo puedo participar?
  </a>
</div>

<img src="/assets/img/portada.png" alt="Concepto de StickyDropsMap" style="display: block; margin-top: 15px; max-width: 100%;">

---

## Mapa de especies vegetales singulares

<div style="margin: 3rem 0; width: 100%;">
  <iframe src="https://www.google.com/maps/d/embed?mid=1Ctys8roNKIREFzWwKuwVfj9vsDHdW3A&ehbc=2E312F" width="100%" height="500" style="border:0; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" allowfullscreen="" loading="lazy"></iframe>
</div>

---

## Monitorización Agroclimática de Niebla y Rocío (Red IFAPA)

<style>
  #ifapa-widget-container {
    margin: 2rem 0;
    padding: 20px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e1e4e8;
  }
  #ifapa-widget-container .panel-control {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 20px;
    padding: 15px;
    background: #f6f8fa;
    border-radius: 8px;
    align-items: flex-end;
  }
  #ifapa-widget-container .control-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  #ifapa-widget-container label {
    font-size: 0.85rem;
    font-weight: bold;
    color: #24292e;
  }
  #ifapa-widget-container select,
  #ifapa-widget-container input {
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #d1d5da;
    font-size: 0.9rem;
    background-color: white;
  }
  #ifapa-widget-container button {
    background-color: #2ea44f;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: bold;
    cursor: pointer;
    height: 35px;
    transition: background-color 0.2s;
  }
  #ifapa-widget-container button:hover {
    background-color: #2c974b;
  }
  #ifapa-widget-container .chart-wrapper {
    position: relative;
    width: 100%;
    min-height: 420px;
  }
</style>

<!-- Carga de Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div id="ifapa-widget-container">
  <div class="panel-control">
    <div class="control-group">
      <label for="selProvincia">Provincia:</label>
      <select id="selProvincia">
        <option value="18" selected>Granada</option>
        <option value="29">Málaga</option>
        <option value="4">Almería</option>
        <option value="41">Sevilla</option>
        <option value="14">Córdoba</option>
      </select>
    </div>

    <div class="control-group">
      <label for="selEstacion">Estación:</label>
      <select id="selEstacion"><option value="">Cargando...</option></select>
    </div>

    <div class="control-group">
      <label for="fechaInicio">Fecha Inicio:</label>
      <input type="date" id="fechaInicio">
    </div>

    <div class="control-group">
      <label for="fechaFin">Fecha Fin:</label>
      <input type="date" id="fechaFin">
    </div>

    <button id="btnConsultar">Consultar Datos</button>
  </div>

  <div id="stats" style="margin-bottom: 15px; font-size: 0.95rem; color: #444;"></div>
  
  <div class="chart-wrapper">
    <canvas id="meteorologiaChart"></canvas>
  </div>
</div>

<script>
(function() {
  const BASE_URL = "https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaws";
  let miChart = null;

  function formatDateLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function calcularPuntoRocio(temp, humedad) {
    const a = 17.27, b = 237.7;
    const h = Math.max(humedad, 0.1);
    const alpha = ((a * temp) / (b + temp)) + Math.log(h / 100.0);
    return (b * alpha) / (a - alpha);
  }

  async function cargarEstaciones(codProvincia) {
    const selEstacion = document.getElementById("selEstacion");
    selEstacion.innerHTML = "<option>Cargando estaciones...</option>";
    
    try {
      const res = await fetch(`${BASE_URL}/estaciones/${codProvincia}`);
      const estaciones = await res.json();
      const activas = estaciones.filter(e => e.activa !== false);
      
      selEstacion.innerHTML = "";
      activas.forEach(e => {
        const opt = document.createElement("option");
        opt.value = e.codigoEstacion;
        opt.textContent = `${e.nombre} (${e.codigoEstacion})`;
        selEstacion.appendChild(opt);
      });
    } catch (err) {
      selEstacion.innerHTML = "<option>Error al cargar</option>";
    }
  }

  async function ejecutarConsulta() {
    const codProvincia = document.getElementById("selProvincia").value;
    const codEstacion = document.getElementById("selEstacion").value;
    const fhInicio = document.getElementById("fechaInicio").value;
    const fhFin = document.getElementById("fechaFin").value;
    const statsDiv = document.getElementById("stats");

    if (!codEstacion || !fhInicio || !fhFin) {
      alert("Por favor completa todos los campos.");
      return;
    }

    statsDiv.innerHTML = "⏳ Consultando servicio agroclimático de IFAPA...";

    try {
      const url = `${BASE_URL}/datosdiarios/forceEt0/${codProvincia}/${codEstacion}/${fhInicio}/${fhFin}`;
      const res = await fetch(url);
      const datos = await res.json();

      if (!datos || datos.length === 0) {
        statsDiv.innerHTML = "<b style='color:#d9534f;'>No hay registros disponibles para el período y estación seleccionados.</b>";
        return;
      }

      let nNiebla = 0, nRocio = 0;
      const procesados = datos.map(d => {
        const fecha = d.fecha.split('T')[0];
        const pRocio = calcularPuntoRocio(d.tempMedia, d.humedadMedia);
        const depRocio = d.tempMin - pRocio;

        const niebla = (d.humedadMax >= 95.0) && (d.velViento <= 2.0) && (depRocio <= 1.5);
        const rocio = (d.humedadMax >= 98.0) && (d.velViento <= 1.5) && (depRocio <= 0.5);

        let ev = "Sin evento";
        if (niebla && rocio) { ev = "Niebla + Rocío"; nNiebla++; nRocio++; }
        else if (niebla) { ev = "Niebla"; nNiebla++; }
        else if (rocio) { ev = "Rocío"; nRocio++; }

        return { fecha, humedadMax: d.humedadMax, radiacion: d.radiacion, evento: ev };
      });

      const totalEv = procesados.filter(d => d.evento !== "Sin evento").length;
      statsDiv.innerHTML = `
        <strong>Días analizados:</strong> ${procesados.length} | 
        <strong>Eventos detectados:</strong> ${totalEv} (Niebla: <strong>${nNiebla}</strong> días | Rocío: <strong>${nRocio}</strong> días)
      `;

      renderizarGrafica(procesados);
    } catch (e) {
      statsDiv.innerHTML = `<b style='color:#d9534f;'>Error en la consulta: ${e.message}</b>`;
    }
  }

  function renderizarGrafica(datos) {
    const ctx = document.getElementById('meteorologiaChart').getContext('2d');
    
    if (miChart) miChart.destroy();

    miChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: datos.map(d => d.fecha),
        datasets: [
          { label: 'Humedad Máx (%)', data: datos.map(d => d.humedadMax), borderColor: '#36a2eb', borderWidth: 2, pointRadius: 0 },
          { label: 'Radiación (MJ/m²)', data: datos.map(d => d.radiacion), borderColor: '#ff9f40', borderWidth: 2, pointRadius: 0 },
          { label: 'Solo Niebla', data: datos.map(d => d.evento === "Niebla" ? d.humedadMax : null), backgroundColor: '#ff6384', showLine: false, pointRadius: 6 },
          { label: 'Solo Rocío', data: datos.map(d => d.evento === "Rocío" ? d.humedadMax : null), backgroundColor: '#4bc0c0', showLine: false, pointRadius: 7, pointStyle: 'triangle' },
          { label: 'Niebla + Rocío', data: datos.map(d => d.evento === "Niebla + Rocío" ? d.humedadMax : null), backgroundColor: '#9966ff', showLine: false, pointRadius: 9, pointStyle: 'rectRot' }
        ]
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false,
        scales: { 
          x: { ticks: { maxRotation: 45 } }, 
          y: { beginAtZero: true } 
        } 
      }
    });
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const hoy = new Date();
    
    // Configuración temporal: Fecha Fin = Ayer | Fecha Inicio = 356 días antes de Ayer
    const fechaFinDt = new Date(hoy);
    fechaFinDt.setDate(hoy.getDate() - 1);

    const fechaInicioDt = new Date(fechaFinDt);
    fechaInicioDt.setDate(fechaFinDt.getDate() - 356);

    document.getElementById("fechaFin").value = formatDateLocal(fechaFinDt);
    document.getElementById("fechaInicio").value = formatDateLocal(fechaInicioDt);

    const selProvincia = document.getElementById("selProvincia");
    await cargarEstaciones(selProvincia.value);
    
    selProvincia.addEventListener("change", (e) => cargarEstaciones(e.target.value));
    document.getElementById("btnConsultar").addEventListener("click", ejecutarConsulta);
    
    ejecutarConsulta();
  });
})();
</script>

---

## Visibilidad Real en Pista y Detección de Niebla (Visibilímetros AEMET)

<style>
  #aemet-real-widget { font-family: Arial, sans-serif; margin: 2rem 0; padding: 20px; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e1e4e8; }
  #aemet-real-widget .panel { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; padding: 15px; background: #f6f8fa; border-radius: 8px; align-items: flex-end; }
  #aemet-real-widget .grupo { display: flex; flex-direction: column; gap: 4px; }
  #aemet-real-widget label { font-size: 0.85rem; font-weight: bold; color: #24292e; }
  #aemet-real-widget select { padding: 6px 10px; border-radius: 6px; border: 1px solid #d1d5da; font-size: 0.9rem; background: #fff; }
  #aemet-real-widget button { background-color: #2ea44f; color: white; border: none; padding: 8px 15px; border-radius: 6px; font-size: 0.9rem; font-weight: bold; cursor: pointer; height: 35px; transition: background-color 0.2s; }
  #aemet-real-widget button:hover { background-color: #2c974b; }
  #aemet-real-widget .chart-box { position: relative; width: 100%; height: 420px; }
  #aemet-real-widget table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9rem; }
  #aemet-real-widget th, #aemet-real-widget td { padding: 9px 12px; border-bottom: 1px solid #e1e4e8; text-align: left; }
  #aemet-real-widget th { background-color: #f6f8fa; color: #24292e; }
  #aemet-real-widget tr.fila-estacion { cursor: pointer; }
  #aemet-real-widget tr.fila-estacion:hover { background-color: #f1f8ff; }
</style>
<div id="aemet-real-widget">
  <div class="panel">
    <div class="grupo">
      <label for="selAeropuertoReal">Aeropuerto (Visibilímetro AEMET):</label>
      <select id="selAeropuertoReal"></select>
    </div>
    <div class="grupo">
      <label for="selModoVista">Resolución temporal:</label>
      <select id="selModoVista">
        <option value="horario" selected>Horaria (Lectura directa sensor)</option>
        <option value="diario">Diaria (Visibilidad mínima por día)</option>
      </select>
    </div>
    <button id="btnRefrescarReal">Actualizar vista</button>
  </div>
  <div id="statsReal" style="margin-bottom: 14px; font-size: 0.95rem; color: #333;">⏳ Cargando lecturas reales de visibilímetros...</div>
  <div class="chart-box">
    <canvas id="chartVisibilidadReal"></canvas>
  </div>
  <div id="tablaComparativaReal" style="overflow-x: auto;"></div>
</div>
<script>
(function() {
  const DATA_URL = "/assets/data/aemet_visibilidad.json";
  let datosGlobales = null;
  let chartInstancia = null;
  async function iniciarWidgetAemetReal() {
    const statsDiv = document.getElementById("statsReal");
    try {
      const res = await fetch(`${DATA_URL}?t=${Math.floor(Date.now() / 600000)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      datosGlobales = await res.json();
      const sel = document.getElementById("selAeropuertoReal");
      sel.innerHTML = "";
      Object.entries(datosGlobales.estaciones).forEach(([idema, info]) => {
        const opt = document.createElement("option");
        opt.value = idema;
        opt.textContent = `${info.nombre} [${idema}]`;
        sel.appendChild(opt);
      });
      renderizarTablaComparativa();
      actualizarGrafica();
    } catch (err) {
      statsDiv.innerHTML = `<b style="color:#d9534f;">No se pudo cargar el archivo de datos (${err.message}).</b>`;
    }
  }
  function agregarPorDia(registros) {
    const porDia = {};
    registros.forEach(r => {
      const dia = r.fint.split("T")[0];
      if (!porDia[dia]) {
        porDia[dia] = { dia, minVis: r.vis_m, horasNiebla: 0 };
      } else if (r.vis_m < porDia[dia].minVis) {
        porDia[dia].minVis = r.vis_m;
      }
      if (r.vis_m < 1000) porDia[dia].horasNiebla++;
    });
    return Object.values(porDia).sort((a, b) => a.dia.localeCompare(b.dia));
  }
  function actualizarGrafica() {
    if (!datosGlobales) return;
    const idema = document.getElementById("selAeropuertoReal").value;
    const modo = document.getElementById("selModoVista").value;
    const est = datosGlobales.estaciones[idema];
    const statsDiv = document.getElementById("statsReal");
    if (!est || est.registros.length === 0) {
      statsDiv.innerHTML = `<b>No hay lecturas de visibilímetro registradas aún para ${idema}.</b>`;
      return;
    }
    let etiquetas = [];
    let valoresVis = [];
    let extraTooltip = [];
    if (modo === "horario") {
      etiquetas = est.registros.map(r => r.fint.replace("T", " "));
      valoresVis = est.registros.map(r => r.vis_m);
      extraTooltip = est.registros.map(r => `Temp: ${r.ta ?? "-"} °C | HR: ${r.hr ?? "-"} % | Viento: ${r.vv ?? "-"} m/s`);
    } else {
      const diarios = agregarPorDia(est.registros);
      etiquetas = diarios.map(d => d.dia);
      valoresVis = diarios.map(d => d.minVis);
      extraTooltip = diarios.map(d => `Horas con niebla (<1000 m): ${d.horasNiebla} h`);
    }
    const horasNieblaTotal = est.registros.filter(r => r.vis_m < 1000).length;
    const horasDensaTotal = est.registros.filter(r => r.vis_m < 500).length;
    const visMinima = Math.min(...valoresVis);
    statsDiv.innerHTML = `
      <strong>Estación:</strong> ${est.nombre} (IDEMA ${idema}) | 
      <strong>Última actualización:</strong> ${datosGlobales.ultima_actualizacion.replace("T", " ").replace("Z", " UTC")}<br>
      <strong>Registros horarios acumulados:</strong> ${est.registros.length} h | 
      <strong>Visibilidad mínima medida:</strong> ${visMinima} m | 
      <strong>Niebla (&lt;1000 m):</strong> ${horasNieblaTotal} h | 
      <strong>Niebla densa (&lt;500 m):</strong> ${horasDensaTotal} h
    `;
    const ctx = document.getElementById("chartVisibilidadReal").getContext("2d");
    if (chartInstancia) chartInstancia.destroy();
    const puntosNiebla = valoresVis.map(v => (v < 1000 ? v : null));
    const umbral1000 = new Array(etiquetas.length).fill(1000);
    const umbral500 = new Array(etiquetas.length).fill(500);
    chartInstancia = new Chart(ctx, {
      type: "line",
      data: {
        labels: etiquetas,
        datasets: [
          { label: "Visibilidad láser medida (m)", data: valoresVis, borderColor: "#1b4965", backgroundColor: "rgba(27, 73, 101, 0.12)", borderWidth: 2, fill: true, pointRadius: modo === "horario" ? 2 : 3 },
          { label: "Umbral Niebla (1000 m)", data: umbral1000, borderColor: "#ff9f40", borderWidth: 1.5, borderDash: [6, 6], pointRadius: 0 },
          { label: "Niebla Densa (500 m)", data: umbral500, borderColor: "#e63946", borderWidth: 1.5, borderDash: [4, 4], pointRadius: 0 },
          { label: "Evento de Niebla Real (< 1000 m)", data: puntosNiebla, backgroundColor: "#e63946", borderColor: "#e63946", showLine: false, pointRadius: 6 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          title: { display: true, text: `Visibilímetro Real AEMET - ${est.nombre}`, font: { size: 14 } },
          tooltip: {
            callbacks: {
              afterBody: function(context) {
                const idx = context[0].dataIndex;
                return extraTooltip[idx] || "";
              }
            }
          }
        },
        scales: {
          x: { ticks: { maxRotation: 45 } },
          y: { beginAtZero: true, title: { display: true, text: "Visibilidad Horizontal en Pista (metros)" } }
        }
      }
    });
  }
  function renderizarTablaComparativa() {
    const contenedor = document.getElementById("tablaComparativaReal");
    const filas = Object.entries(datosGlobales.estaciones).map(([idema, info]) => {
      const regs = info.registros || [];
      const hNiebla = regs.filter(r => r.vis_m < 1000).length;
      const hDensa = regs.filter(r => r.vis_m < 500).length;
      const minV = regs.length > 0 ? Math.min(...regs.map(r => r.vis_m)) : null;
      return { idema, nombre: info.nombre, totalH: regs.length, hNiebla, hDensa, minV };
    });
    filas.sort((a, b) => b.hNiebla - a.hNiebla || b.hDensa - a.hDensa);
    let html = `
      <h4 style="margin-top: 20px; margin-bottom: 6px;">Comparativa de Visibilímetros Reales (Sur de España)</h4>
      <p style="font-size: 0.85rem; color: #586069; margin-top: 0;">Haz clic en una fila para ver su gráfica.</p>
      <table>
        <thead>
          <tr><th>Aeropuerto</th><th>IDEMA</th><th>Visibilidad Mínima</th><th>Horas Niebla (&lt;1000 m)</th><th>Horas Densa (&lt;500 m)</th><th>Muestra acumulada</th></tr>
        </thead>
        <tbody>
    `;
    filas.forEach(f => {
      html += `
        <tr class="fila-estacion" data-idema="${f.idema}">
          <td><strong>${f.nombre}</strong></td>
          <td><code>${f.idema}</code></td>
          <td>${f.minV !== null ? f.minV + " m" : "Sin datos"}</td>
          <td><strong>${f.hNiebla} h</strong></td>
          <td>${f.hDensa} h</td>
          <td>${f.totalH} h</td>
        </tr>
      `;
    });
    html += "</tbody></table>";
    contenedor.innerHTML = html;
    contenedor.querySelectorAll("tr.fila-estacion").forEach(tr => {
      tr.addEventListener("click", () => {
        document.getElementById("selAeropuertoReal").value = tr.getAttribute("data-idema");
        actualizarGrafica();
      });
    });
  }
  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("selAeropuertoReal").addEventListener("change", actualizarGrafica);
    document.getElementById("selModoVista").addEventListener("change", actualizarGrafica);
    document.getElementById("btnRefrescarReal").addEventListener("click", actualizarGrafica);
    iniciarWidgetAemetReal();
  });
})();
</script>

---

## Últimas observaciones de iNaturalist

<div id="inaturalist-section">
  <div id="obs-loading">⏳ Cargando observaciones…</div>
  <div id="obs-error" style="display: none;">
    No se pudieron cargar las observaciones. Por favor,
    <a href="https://www.inaturalist.org/projects/mapa-de-superficies-vegetales-con-alta-captacion-de-agua-atmosferica" target="_blank" rel="noopener">
      visita el proyecto en iNaturalist
    </a>.
  </div>
  <div id="obs-grid"></div>
</div>

<script>
(function () {
  var PROJECT_ID = "mapa-de-superficies-vegetales-con-alta-captacion-de-agua-atmosferica";
  var MAX_OBS    = 5;

  var apiUrl =
    "https://api.inaturalist.org/v1/observations" +
    "?project_id=" + encodeURIComponent(PROJECT_ID) +
    "&per_page=" + MAX_OBS +
    "&order=desc&order_by=created_at";

  var grid    = document.getElementById("obs-grid");
  var loading = document.getElementById("obs-loading");
  var errBox  = document.getElementById("obs-error");

  function formatDate(dateStr) {
    if (!dateStr) return "";
    var d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
  }

  function renderObservation(obs) {
    var card = document.createElement("a");
    card.className = "obs-card";
    card.href      = "https://www.inaturalist.org/observations/" + obs.id;
    card.target    = "_blank";
    card.rel       = "noopener noreferrer";

    var photoEl;
    var photoUrl =
      obs.photos && obs.photos.length > 0
        ? obs.photos[0].url.replace("square", "medium")
        : null;

    if (photoUrl) {
      photoEl = document.createElement("img");
      photoEl.src   = photoUrl;
      photoEl.alt   = obs.species_guess || "Observación";
      photoEl.loading = "lazy";
    } else {
      photoEl = document.createElement("div");
      photoEl.className = "obs-card-placeholder";
      photoEl.textContent = "🌿";
    }

    var body     = document.createElement("div");
    body.className = "obs-card-body";

    var species  = document.createElement("p");
    species.className = "obs-species";
    species.textContent =
      (obs.taxon && obs.taxon.preferred_common_name) ||
      obs.species_guess ||
      "Especie desconocida";

    var date = document.createElement("p");
    date.className = "obs-date";
    date.textContent = formatDate(obs.observed_on);

    body.appendChild(species);
    body.appendChild(date);
    card.appendChild(photoEl);
    card.appendChild(body);
    return card;
  }

  fetch(apiUrl)
    .then(function (response) {
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }
      return response.json();
    })
    .then(function (data) {
      loading.style.display = "none";
      errBox.style.display = "none";
      
      var results = data.results || [];
      if (results.length === 0) {
        errBox.style.display = "block";
        return;
      }
      results.forEach(function (obs) {
        grid.appendChild(renderObservation(obs));
      });
    })
    .catch(function () {
      loading.style.display = "none";
      errBox.style.display  = "block";
    });
})();
</script>
