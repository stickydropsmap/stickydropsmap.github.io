---
layout: home
title: StickyDropsMap
subtitle: Mapa de superficies vegetales"<br>"con alta captación de agua atmosférica
cover-img: /assets/img/hero.jpg
---

Bienvenido al proyecto de ciencia ciudadana **Sticky Drops Map** de la Universidad de Granada.
Ayúdanos a cartografiar las plantas y superficies capaces de capturar agua atmosférica — como
niebla, rocío y lluvia horizontal — para entender mejor los recursos hídricos de nuestros ecosistemas.

<a class="btn-participate" href="/participate/">¿Cómo puedo participar?</a>

---

## Últimas observaciones de iNaturalist

<div id="inaturalist-section">
  <div id="obs-loading">⏳ Cargando observaciones…</div>
  <div id="obs-error">
    No se pudieron cargar las observaciones. Por favor,
    <a href="https://www.inaturalist.org/projects/mapa-de-superficies-vegetales-con-alta-captacion-de-agua-atmosferica" target="_blank" rel="noopener">
      visita el proyecto en iNaturalist
    </a>.
    <!-- ↑ Reemplaza YOUR_PROJECT_ID con tu slug de proyecto iNaturalist -->
  </div>
  <div id="obs-grid"></div>
</div>

<script>
(function () {
  // ══════════════════════════════════════════════════════════════
  // ⚙️  CONFIGURACIÓN — edita sólo esta sección
  //   Reemplaza YOUR_PROJECT_ID con el slug o ID numérico de tu
  //   proyecto en iNaturalist (p. ej. "sticky-drops-map" o 12345).
  // ══════════════════════════════════════════════════════════════
  var PROJECT_ID = "mapa-de-superficies-vegetales-con-alta-captacion-de-agua-atmosferica"; // ← CAMBIAR AQUÍ
  var MAX_OBS   = 5;
  // ────────────────────────────────────────────────────────────

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

    // Photo
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

    // Body
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

