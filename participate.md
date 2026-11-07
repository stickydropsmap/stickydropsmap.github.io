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
