/* =========================================================================
   ASTRAL — The Gann Oracle · Frontend logic
   ========================================================================= */

const form = document.getElementById("analyze-form");
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const errorBox = document.getElementById("error-box");
const errorMessage = document.getElementById("error-message");

// Last result kept for export
let lastResult = null;

// Pre-fill today's date
document.getElementById("date").valueAsDate = new Date();

// ---------- Form submit ----------
form.addEventListener("submit", async (ev) => {
  ev.preventDefault();

  const ticker = document.getElementById("ticker").value.trim();
  const analysisDate = document.getElementById("date").value || null;
  const scale = parseFloat(document.getElementById("scale").value) || 1.0;
  const lookback = parseInt(document.getElementById("lookback").value) || 365;

  if (!ticker) return;

  // UI state
  results.classList.add("hidden");
  errorBox.classList.add("hidden");
  loading.classList.remove("hidden");

  try {
    const resp = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticker,
        analysis_date: analysisDate,
        scale,
        lookback,
      }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: "Errore sconosciuto" }));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    const data = await resp.json();
    lastResult = data;
    renderResult(data);
  } catch (e) {
    errorMessage.textContent = e.message || String(e);
    errorBox.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
  }
});

// ---------- Tabs ----------
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ---------- Export ----------
document.getElementById("btn-export").addEventListener("click", () => {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `astral_${lastResult.ticker}_${lastResult.analysis_date}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

// ---------- Helpers ----------
function fmt(n, digits = 2) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString("it-IT", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function dirClass(d) {
  return (d || "").toLowerCase();
}

function stars(n) {
  return "★".repeat(n) + "☆".repeat(Math.max(0, 5 - n));
}

function strengthBadge(v) {
  if (v >= 0.7) return `<span class="signal-strength strength-high">${fmt(v, 2)}</span>`;
  if (v >= 0.4) return `<span class="signal-strength strength-med">${fmt(v, 2)}</span>`;
  return `<span class="signal-strength strength-low">${fmt(v, 2)}</span>`;
}

function empty(msg = "Nessun dato") {
  return `<p class="empty">${msg}</p>`;
}

// ---------- Renderers ----------
function renderResult(r) {
  // Header
  document.getElementById("r-ticker").textContent = r.ticker;
  document.getElementById("r-date").textContent = `Oracolo consultato il ${r.analysis_date}`;
  document.getElementById("r-price").textContent = fmt(r.current_price);

  // Verdict
  document.getElementById("r-stars").textContent = stars(r.score);
  const dirEl = document.getElementById("r-direction");
  dirEl.textContent = (r.direction || "").toUpperCase();
  dirEl.className = "direction " + dirClass(r.direction);

  // Oracle vision
  document.getElementById("r-vision").textContent = r.oracle_vision || "";

  // Tarot
  renderTarot(r.tarot);

  // Plan
  renderPlan(r.operative_plan);

  // Tabs
  renderSignals(r.signals || []);
  renderGann(r.gann_levels || [], r.current_price, r.critical_dates || []);
  renderPlanets(r.planet_positions || [], r.planetary_aspects || [], r.moon_phase, r.eclipses || []);
  renderHistorical(r);
  renderMacro(r.macro);
  renderEsoteric(r);

  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderTarot(t) {
  const el = document.getElementById("r-tarot");
  if (!t) {
    el.innerHTML = empty("Nessun arcano assegnato");
    return;
  }
  el.innerHTML = `
    <div class="tarot-card">
      <div class="tarot-number">${romanize(t.number || 0)}</div>
      <div class="tarot-name">${t.name_it || t.name || ""}</div>
      <div class="tarot-meaning">${t.meaning || ""}</div>
      <div class="tarot-market">${t.market_interpretation || ""}</div>
    </div>
  `;
}

function romanize(n) {
  const map = ["0","I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"];
  return map[n] || String(n);
}

function renderPlan(p) {
  const el = document.getElementById("r-plan");
  if (!p) {
    el.innerHTML = empty();
    return;
  }
  const rows = [];
  rows.push(`<div class="plan-row"><span class="plan-label">Direzione</span><span class="plan-value ${dirClass(p.direction)}">${(p.direction || "").toUpperCase()}</span></div>`);
  if (p.entry_level != null) rows.push(`<div class="plan-row"><span class="plan-label">Entrata</span><span class="plan-value entry">${fmt(p.entry_level)}</span></div>`);
  if (p.stop_loss != null) rows.push(`<div class="plan-row"><span class="plan-label">Stop Loss</span><span class="plan-value stop">${fmt(p.stop_loss)}</span></div>`);
  if (p.target_1 != null) rows.push(`<div class="plan-row"><span class="plan-label">Target 1</span><span class="plan-value target">${fmt(p.target_1)}</span></div>`);
  if (p.target_2 != null) rows.push(`<div class="plan-row"><span class="plan-label">Target 2</span><span class="plan-value target">${fmt(p.target_2)}</span></div>`);
  if (p.timeframe) rows.push(`<div class="plan-row"><span class="plan-label">Timeframe</span><span class="plan-value">${p.timeframe}</span></div>`);
  let html = rows.join("");
  if (p.notes) html += `<p class="plan-notes">${p.notes}</p>`;
  el.innerHTML = html;
}

function renderSignals(signals) {
  const el = document.getElementById("tab-signals");
  if (!signals.length) {
    el.innerHTML = empty("Nessun segnale rilevato");
    return;
  }
  const sorted = [...signals].sort((a, b) => (b.strength || 0) - (a.strength || 0));
  el.innerHTML = sorted.map((s) => `
    <div class="signal-row">
      <span class="signal-source">${(s.source || "").replace(/_/g, " ")}</span>
      <span class="signal-desc">${s.description || ""}</span>
      ${strengthBadge(s.strength || 0)}
    </div>
  `).join("");
}

function renderGann(levels, currentPrice, criticalDates) {
  const el = document.getElementById("tab-gann");
  if (!levels.length && !criticalDates.length) {
    el.innerHTML = empty();
    return;
  }
  let html = "";
  if (levels.length) {
    const sorted = [...levels].sort((a, b) => a.price - b.price);
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin-bottom:10px">LIVELLI DI PREZZO</h4>`;
    html += `<table><thead><tr><th>Tipo</th><th>Descrizione</th><th class="num">Prezzo</th><th class="num">Δ%</th></tr></thead><tbody>`;
    sorted.forEach((lv) => {
      const delta = ((lv.price - currentPrice) / currentPrice) * 100;
      const cls = lv.price > currentPrice ? "bullish" : "bearish";
      html += `<tr>
        <td>${lv.level_type || ""}</td>
        <td>${lv.description || ""}</td>
        <td class="num ${cls}">${fmt(lv.price)}</td>
        <td class="num ${cls}">${delta >= 0 ? "+" : ""}${fmt(delta, 2)}%</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }
  if (criticalDates.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin:24px 0 10px">DATE CRITICHE IN ARRIVO</h4>`;
    html += `<table><thead><tr><th>Data</th><th>Ciclo</th><th class="num">Giorni dal pivot</th><th>Note</th></tr></thead><tbody>`;
    criticalDates.forEach((d) => {
      html += `<tr>
        <td>${d.date || ""}</td>
        <td>${d.cycle_name || ""}</td>
        <td class="num">${d.days_from_pivot || ""}</td>
        <td>${d.description || ""}</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }
  el.innerHTML = html;
}

function renderPlanets(positions, aspects, moonPhase, eclipses) {
  const el = document.getElementById("tab-planets");
  let html = "";

  if (positions.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin-bottom:10px">POSIZIONI PLANETARIE</h4>`;
    html += `<table><thead><tr><th>Pianeta</th><th class="num">Longitudine</th><th>Segno</th><th>Stato</th></tr></thead><tbody>`;
    positions.forEach((p) => {
      const planet = p.planet || {};
      const symbol = planet.symbol || "";
      const name = planet.label_it || "";
      const rx = p.is_retrograde || p.speed < 0 ? "℞ Retrogrado" : "→";
      html += `<tr>
        <td>${symbol} ${name}</td>
        <td class="num">${fmt(p.longitude, 2)}°</td>
        <td>${p.sign || ""} ${fmt(p.degree_in_sign || 0, 1)}°</td>
        <td>${rx}</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }

  if (aspects.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin:24px 0 10px">ASPETTI ATTIVI</h4>`;
    html += `<table><thead><tr><th>P1</th><th>Aspetto</th><th>P2</th><th class="num">Orbe</th><th>Stato</th></tr></thead><tbody>`;
    aspects.forEach((a) => {
      const p1 = a.planet1 || {};
      const p2 = a.planet2 || {};
      const asp = a.aspect || {};
      html += `<tr>
        <td>${p1.symbol || ""} ${p1.label_it || ""}</td>
        <td>${asp.label || asp[0] || ""}</td>
        <td>${p2.symbol || ""} ${p2.label_it || ""}</td>
        <td class="num">${fmt(a.orb, 2)}°</td>
        <td>${a.applying ? "Applicante" : "Separante"}</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }

  if (moonPhase) {
    const phase = moonPhase.phase;
    const phaseName = (phase && (phase.value || phase)) || "";
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin:24px 0 10px">LUNA</h4>`;
    html += `<p>Fase: <strong>${phaseName}</strong> · Illuminazione: ${fmt((moonPhase.illumination || 0) * 100, 1)}%</p>`;
  }

  if (eclipses.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin:24px 0 10px">ECLISSI RECENTI</h4>`;
    html += `<table><thead><tr><th>Tipo</th><th>Data</th><th>Descrizione</th><th>Impatto fino al</th></tr></thead><tbody>`;
    eclipses.forEach((e) => {
      html += `<tr>
        <td>${e.eclipse_type || ""}</td>
        <td>${e.date || ""}</td>
        <td>${e.description || ""}</td>
        <td>${e.impact_window_end || ""}</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }

  el.innerHTML = html || empty();
}

function renderHistorical(r) {
  const el = document.getElementById("tab-historical");
  let html = "";

  if (r.kondratieff_season) {
    const [season, pos] = r.kondratieff_season;
    const seasonLabel = (season && (season.label_it || season[0])) || "";
    const seasonDesc = (season && (season.description || season[1])) || "";
    html += `<div class="panel" style="margin:0 0 16px"><h3>⌬ Kondratieff</h3>
      <p><strong>${seasonLabel}</strong> — ${seasonDesc}</p>
      <p style="color:var(--text-dim)">Posizione nel ciclo: ${fmt((pos || 0) * 100, 1)}%</p>
    </div>`;
  }

  if (r.presidential_cycle) {
    const [yr, desc] = r.presidential_cycle;
    html += `<div class="panel" style="margin:0 0 16px"><h3>🏛 Ciclo Presidenziale</h3>
      <p>Anno ${yr} — ${desc}</p></div>`;
  }

  if (r.decennial_pattern) {
    const [digit, desc] = r.decennial_pattern;
    html += `<div class="panel" style="margin:0 0 16px"><h3>⧖ Pattern Decennale</h3>
      <p>Anno con cifra ${digit} — ${desc}</p></div>`;
  }

  if (r.historical_matches && r.historical_matches.length) {
    html += `<div class="panel" style="margin:0 0 16px"><h3>📜 Anniversari di Crisi</h3>`;
    html += `<table><thead><tr><th>Pattern</th><th>Tipo</th><th class="num">Anni fa</th><th>Data anniv.</th></tr></thead><tbody>`;
    r.historical_matches.forEach((m) => {
      const pat = m.pattern || {};
      html += `<tr>
        <td>${pat.name || ""}</td>
        <td>${m.event_type || ""}</td>
        <td class="num">${m.years_ago || ""}</td>
        <td>${m.anniversary_date || ""}</td>
      </tr>`;
    });
    html += "</tbody></table></div>";
  }

  el.innerHTML = html || empty();
}

function renderMacro(m) {
  const el = document.getElementById("tab-macro");
  if (!m) {
    el.innerHTML = empty("Dati macro non disponibili");
    return;
  }
  const rows = [
    ["Fed Funds Rate", m.fed_funds != null ? `${fmt(m.fed_funds, 2)}%` : "—"],
    ["CPI YoY", m.cpi_yoy != null ? `${fmt(m.cpi_yoy, 2)}%` : "—"],
    ["M2 YoY", m.m2_yoy != null ? `${fmt(m.m2_yoy, 2)}%` : "—"],
    ["Yield Curve 10Y-2Y", m.yield_curve_10y2y != null ? `${fmt(m.yield_curve_10y2y, 2)}%` : "—"],
    ["Curva invertita", m.yield_curve_inverted ? "⚠ SÌ" : "No"],
    ["VIX", m.vix != null ? fmt(m.vix, 2) : "—"],
    ["DXY", m.dxy != null ? fmt(m.dxy, 2) : "—"],
  ];
  let html = `<table><tbody>`;
  rows.forEach(([k, v]) => {
    html += `<tr><th>${k}</th><td class="num">${v}</td></tr>`;
  });
  html += `</tbody></table>`;
  if (m.bias) {
    html += `<p style="margin-top:14px">Bias macro: <strong class="${dirClass(m.bias)}">${(m.bias || "").toUpperCase()}</strong></p>`;
  }
  if (m.notes && m.notes.length) {
    html += `<ul style="margin-top:14px;padding-left:20px;color:var(--text-dim)">`;
    m.notes.forEach((n) => { html += `<li>${n}</li>`; });
    html += `</ul>`;
  }
  el.innerHTML = html;
}

function renderEsoteric(r) {
  const el = document.getElementById("tab-esoteric");
  let html = "";

  if (r.fibonacci_levels) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin-bottom:10px">LIVELLI FIBONACCI</h4>`;
    html += `<table><thead><tr><th>Livello</th><th class="num">Prezzo</th></tr></thead><tbody>`;
    Object.entries(r.fibonacci_levels).forEach(([k, v]) => {
      html += `<tr><td>${k}</td><td class="num">${fmt(v)}</td></tr>`;
    });
    html += "</tbody></table>";
  }

  if (r.numerology) {
    html += `<div class="panel" style="margin:20px 0 0"><h3>🔢 Numerologia</h3>`;
    html += `<pre style="font-family:var(--font-body);white-space:pre-wrap">${r.numerology.interpretation || JSON.stringify(r.numerology, null, 2)}</pre>`;
    html += `</div>`;
  }

  if (r.gematria) {
    html += `<div class="panel" style="margin:20px 0 0"><h3>ℵ Gematria</h3>`;
    html += `<p>Valore: <strong>${r.gematria.value}</strong> · Radice: <strong>${r.gematria.root_number}</strong></p>`;
    if (r.gematria.sephira) html += `<p>Sephira: ${r.gematria.sephira}</p>`;
    if (r.gematria.meaning) html += `<p style="color:var(--text-dim);font-style:italic">${r.gematria.meaning}</p>`;
    html += `</div>`;
  }

  el.innerHTML = html || empty();
}
