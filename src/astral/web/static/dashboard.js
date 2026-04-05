/* =========================================================================
   ASTRAL — Dashboard logic with TradingView Lightweight Charts
   ========================================================================= */

const form = document.getElementById("analyze-form");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("error-box");
const errorMessage = document.getElementById("error-message");
const opPlaceholder = document.getElementById("op-placeholder");
const opBody = document.getElementById("op-body");
const visionPanel = document.getElementById("vision-panel");
const tabsSection = document.getElementById("tabs-section");
const chartInfo = document.getElementById("chart-info");

let lastResult = null;
let chart = null;
let candleSeries = null;

// Default date = today
document.getElementById("date").valueAsDate = new Date();

// ---------- Chart init ----------
function initChart() {
  if (chart) return;
  const container = document.getElementById("chart");
  chart = LightweightCharts.createChart(container, {
    layout: {
      background: { color: "#0a0612" },
      textColor: "#9a8fae",
      fontFamily: "JetBrains Mono, monospace",
    },
    grid: {
      vertLines: { color: "rgba(58, 42, 92, 0.3)" },
      horzLines: { color: "rgba(58, 42, 92, 0.3)" },
    },
    timeScale: {
      borderColor: "#3a2a5c",
      timeVisible: false,
      secondsVisible: false,
    },
    rightPriceScale: { borderColor: "#3a2a5c" },
    crosshair: {
      vertLine: { color: "#d4af37", width: 1, style: 2 },
      horzLine: { color: "#d4af37", width: 1, style: 2 },
    },
    autoSize: true,
  });
  candleSeries = chart.addCandlestickSeries({
    upColor: "#4ade80",
    downColor: "#f87171",
    borderUpColor: "#4ade80",
    borderDownColor: "#f87171",
    wickUpColor: "#4ade80",
    wickDownColor: "#f87171",
  });
  window.addEventListener("resize", () => chart.timeScale().fitContent());
}

async function loadChart(ticker, lookback) {
  initChart();
  try {
    const resp = await fetch(`/api/ohlcv?ticker=${encodeURIComponent(ticker)}&lookback=${lookback}`);
    if (!resp.ok) return;
    const data = await resp.json();
    candleSeries.setData(data.candles || []);
    chart.timeScale().fitContent();
    if (data.candles && data.candles.length) {
      const last = data.candles[data.candles.length - 1];
      chartInfo.textContent = `${data.ticker} · ${data.candles.length} barre · Ultimo: ${fmt(last.close)}`;
    }
    // Add Gann level price lines if we have a lastResult
    if (lastResult && lastResult.gann_levels) {
      // Clear previous lines — v4 API: create series, call removePriceLine
      // For simplicity, we recreate series
    }
  } catch (e) {
    console.warn("Chart load failed:", e);
  }
}

// ---------- Form submit ----------
form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  await runAnalysis();
});

async function runAnalysis() {
  const ticker = document.getElementById("ticker").value.trim();
  const analysisDate = document.getElementById("date").value || null;
  const scale = parseFloat(document.getElementById("scale").value) || 1.0;
  const lookback = parseInt(document.getElementById("lookback").value) || 365;
  if (!ticker) return;

  errorBox.classList.add("hidden");
  opBody.classList.add("hidden");
  opPlaceholder.classList.remove("hidden");
  loading.classList.remove("hidden");
  visionPanel.classList.add("hidden");
  tabsSection.classList.add("hidden");

  // Load chart in parallel
  loadChart(ticker, lookback);

  try {
    const resp = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, analysis_date: analysisDate, scale, lookback }),
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
}

// ---------- Watchlist click ----------
document.querySelectorAll(".watchlist li").forEach((el) => {
  el.addEventListener("click", () => {
    document.getElementById("ticker").value = el.dataset.ticker;
    runAnalysis();
  });
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
function dirClass(d) { return (d || "").toLowerCase(); }
function stars(n) { return "★".repeat(n) + "☆".repeat(Math.max(0, 5 - n)); }
function strengthBadge(v) {
  if (v >= 0.7) return `<span class="signal-strength strength-high">${fmt(v, 2)}</span>`;
  if (v >= 0.4) return `<span class="signal-strength strength-med">${fmt(v, 2)}</span>`;
  return `<span class="signal-strength strength-low">${fmt(v, 2)}</span>`;
}
function empty(msg = "Nessun dato") { return `<p class="empty">${msg}</p>`; }
function romanize(n) {
  const map = ["0","I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"];
  return map[n] || String(n);
}

// ---------- Renderers ----------
function renderResult(r) {
  opPlaceholder.classList.add("hidden");
  opBody.classList.remove("hidden");
  visionPanel.classList.remove("hidden");
  tabsSection.classList.remove("hidden");

  document.getElementById("r-price").textContent = fmt(r.current_price);
  document.getElementById("r-date").textContent = r.analysis_date;
  document.getElementById("r-stars").textContent = stars(r.score);

  const dirEl = document.getElementById("r-direction");
  dirEl.textContent = (r.direction || "").toUpperCase();
  dirEl.className = "op-direction " + dirClass(r.direction);

  document.getElementById("r-vision").textContent = r.oracle_vision || "";

  renderTarot(r.tarot);
  renderPlan(r.operative_plan);

  renderSignals(r.signals || []);
  renderGann(r.gann_levels || [], r.current_price, r.critical_dates || []);
  renderPlanets(r.planet_positions || [], r.planetary_aspects || [], r.moon_phase, r.eclipses || []);
  renderHistorical(r);
  renderMacro(r.macro);
  renderEsoteric(r);

  // Add Gann horizontal lines on chart
  if (candleSeries && r.gann_levels && r.gann_levels.length) {
    const topLevels = [...r.gann_levels]
      .sort((a, b) => Math.abs(a.price - r.current_price) - Math.abs(b.price - r.current_price))
      .slice(0, 6);
    topLevels.forEach((lv) => {
      candleSeries.createPriceLine({
        price: lv.price,
        color: lv.price > r.current_price ? "rgba(74, 222, 128, 0.6)" : "rgba(248, 113, 113, 0.6)",
        lineWidth: 1,
        lineStyle: 2,
        axisLabelVisible: true,
        title: lv.level_type || "",
      });
    });
  }
}

function renderTarot(t) {
  const el = document.getElementById("r-tarot");
  if (!t) { el.innerHTML = empty(); return; }
  el.innerHTML = `
    <div style="text-align:center">
      <div style="font-family:var(--font-display);font-size:40px;color:var(--gold);line-height:1">${romanize(t.number || 0)}</div>
      <div style="font-family:var(--font-head);font-size:13px;letter-spacing:2px;color:var(--gold-bright);margin-top:6px">${t.name_it || t.name || ""}</div>
      <div style="font-size:12px;color:var(--text-dim);font-style:italic;margin-top:6px">${t.meaning || ""}</div>
      <div style="font-size:12px;color:var(--text);margin-top:4px">${t.market_interpretation || ""}</div>
    </div>
  `;
}

function renderPlan(p) {
  const el = document.getElementById("r-plan");
  if (!p) { el.innerHTML = empty(); return; }
  const rows = [];
  const row = (lbl, val, cls = "") => `<div class="plan-row"><span class="plan-label">${lbl}</span><span class="plan-value ${cls}">${val}</span></div>`;
  rows.push(row("Direzione", (p.direction || "").toUpperCase(), dirClass(p.direction)));
  if (p.entry_level != null) rows.push(row("Entrata", fmt(p.entry_level), "entry"));
  if (p.stop_loss != null) rows.push(row("Stop", fmt(p.stop_loss), "stop"));
  if (p.target_1 != null) rows.push(row("Target 1", fmt(p.target_1), "target"));
  if (p.target_2 != null) rows.push(row("Target 2", fmt(p.target_2), "target"));
  let html = rows.join("");
  if (p.notes) html += `<p class="plan-notes">${p.notes}</p>`;
  el.innerHTML = html;
}

function renderSignals(signals) {
  const el = document.getElementById("tab-signals");
  if (!signals.length) { el.innerHTML = empty("Nessun segnale rilevato"); return; }
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
    html += `<table><thead><tr><th>Data</th><th>Ciclo</th><th class="num">Giorni</th><th>Note</th></tr></thead><tbody>`;
    criticalDates.forEach((d) => {
      html += `<tr><td>${d.date || ""}</td><td>${d.cycle_name || ""}</td><td class="num">${d.days_from_pivot || ""}</td><td>${d.description || ""}</td></tr>`;
    });
    html += "</tbody></table>";
  }
  el.innerHTML = html || empty();
}

function renderPlanets(positions, aspects, moonPhase, eclipses) {
  const el = document.getElementById("tab-planets");
  let html = "";
  if (positions.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin-bottom:10px">POSIZIONI PLANETARIE</h4>`;
    html += `<table><thead><tr><th>Pianeta</th><th class="num">Longitudine</th><th>Segno</th><th>Stato</th></tr></thead><tbody>`;
    positions.forEach((p) => {
      const planet = p.planet || {};
      html += `<tr>
        <td>${planet.symbol || ""} ${planet.label_it || ""}</td>
        <td class="num">${fmt(p.longitude, 2)}°</td>
        <td>${p.sign || ""} ${fmt(p.degree_in_sign || 0, 1)}°</td>
        <td>${p.is_retrograde || p.speed < 0 ? "℞ Retrogrado" : "→"}</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }
  if (aspects.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin:24px 0 10px">ASPETTI ATTIVI</h4>`;
    html += `<table><thead><tr><th>P1</th><th>Aspetto</th><th>P2</th><th class="num">Orbe</th></tr></thead><tbody>`;
    aspects.forEach((a) => {
      const p1 = a.planet1 || {};
      const p2 = a.planet2 || {};
      const asp = a.aspect || {};
      html += `<tr>
        <td>${p1.symbol || ""} ${p1.label_it || ""}</td>
        <td>${asp.label || ""}</td>
        <td>${p2.symbol || ""} ${p2.label_it || ""}</td>
        <td class="num">${fmt(a.orb, 2)}°</td>
      </tr>`;
    });
    html += "</tbody></table>";
  }
  if (moonPhase) {
    const phase = moonPhase.phase;
    const phaseName = (phase && (phase.value || phase)) || "";
    html += `<p style="margin-top:20px">Luna: <strong>${phaseName}</strong> · Illuminazione: ${fmt((moonPhase.illumination || 0) * 100, 1)}%</p>`;
  }
  if (eclipses.length) {
    html += `<h4 style="color:var(--gold-soft);font-family:var(--font-head);letter-spacing:2px;font-size:12px;margin:24px 0 10px">ECLISSI</h4>`;
    html += `<table><thead><tr><th>Tipo</th><th>Data</th><th>Descrizione</th></tr></thead><tbody>`;
    eclipses.forEach((e) => {
      html += `<tr><td>${e.eclipse_type || ""}</td><td>${e.date || ""}</td><td>${e.description || ""}</td></tr>`;
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
      <p style="color:var(--text-dim)">Posizione nel ciclo: ${fmt((pos || 0) * 100, 1)}%</p></div>`;
  }
  if (r.presidential_cycle) {
    const [yr, desc] = r.presidential_cycle;
    html += `<div class="panel" style="margin:0 0 16px"><h3>🏛 Ciclo Presidenziale</h3><p>Anno ${yr} — ${desc}</p></div>`;
  }
  if (r.decennial_pattern) {
    const [digit, desc] = r.decennial_pattern;
    html += `<div class="panel" style="margin:0 0 16px"><h3>⧖ Pattern Decennale</h3><p>Anno con cifra ${digit} — ${desc}</p></div>`;
  }
  if (r.historical_matches && r.historical_matches.length) {
    html += `<div class="panel" style="margin:0 0 16px"><h3>📜 Anniversari di Crisi</h3>`;
    html += `<table><thead><tr><th>Pattern</th><th>Tipo</th><th class="num">Anni fa</th><th>Data</th></tr></thead><tbody>`;
    r.historical_matches.forEach((m) => {
      const pat = m.pattern || {};
      html += `<tr><td>${pat.name || ""}</td><td>${m.event_type || ""}</td><td class="num">${m.years_ago || ""}</td><td>${m.anniversary_date || ""}</td></tr>`;
    });
    html += "</tbody></table></div>";
  }
  el.innerHTML = html || empty();
}

function renderMacro(m) {
  const el = document.getElementById("tab-macro");
  if (!m) { el.innerHTML = empty("Dati macro non disponibili (serve FRED API key)"); return; }
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
  rows.forEach(([k, v]) => { html += `<tr><th>${k}</th><td class="num">${v}</td></tr>`; });
  html += `</tbody></table>`;
  if (m.bias) html += `<p style="margin-top:14px">Bias macro: <strong class="${dirClass(m.bias)}">${(m.bias || "").toUpperCase()}</strong></p>`;
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
    html += `<pre style="font-family:var(--font-body);white-space:pre-wrap">${r.numerology.interpretation || JSON.stringify(r.numerology, null, 2)}</pre></div>`;
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

// Init empty chart on load
initChart();
