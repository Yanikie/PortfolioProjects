(() => {
  const API = '/api/sensor.php';
  const POLL_INTERVAL = 60_000; // refresh every 60 s

  // ── Chart colour palette (matches your CSS vars) ────────────────────────────
  const COLORS = {
    temp:  { line: '#e07b39', fill: 'rgba(224,123,57,0.12)'  },
    hum:   { line: '#4a90a4', fill: 'rgba(74,144,164,0.12)'  },
    press: { line: '#7b6fa0', fill: 'rgba(123,111,160,0.12)' },
  };

  // ── Tiny helpers ─────────────────────────────────────────────────────────────
  const $  = id => document.getElementById(id);
  const fmt = n  => n != null ? n.toFixed(1) : '—';

  function formatTimestamp(unix) {
    return new Date(unix * 1000).toLocaleString('nl-NL', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function minMax(arr) {
    if (!arr.length) return { min: null, max: null };
    return { min: Math.min(...arr), max: Math.max(...arr) };
  }

  // ── Response shape validation ─────────────────────────────────────────────
  // Checks that the API returned the exact structure the dashboard expects.
  // Returns true if everything looks right, false if something is wrong or
  // unexpected (e.g. a DB error leaked into the JSON, a CDN returned its own
  // error page as JSON, or someone tampered with the response in transit).
  function isValidResponse(data) {
    if (typeof data !== 'object' || data === null) return false;
    if (data.ok !== true) return false;

    // No readings yet is fine — the caller handles this separately
    if (data.latest === null) return true;

    // latest must be a well-formed reading object
    const l = data.latest;
    if (typeof l !== 'object' || l === null)             return false;
    if (typeof l.recorded_at  !== 'number')              return false;
    if (typeof l.temperature  !== 'number')              return false;
    if (typeof l.humidity     !== 'number')              return false;
    if (typeof l.pressure     !== 'number')              return false;

    // series must be an object with four arrays of equal length
    const s = data.series;
    if (typeof s !== 'object' || s === null)             return false;

    const arrays = ['timestamps', 'temperatures', 'humidities', 'pressures'];
    for (const key of arrays) {
      if (!Array.isArray(s[key])) return false;
    }

    const len = s.timestamps.length;
    if (
      s.temperatures.length !== len ||
      s.humidities.length   !== len ||
      s.pressures.length    !== len
    ) return false;

    // Every value in every series array must be a number
    for (const key of arrays) {
      if (!s[key].every(v => typeof v === 'number')) return false;
    }

    return true;
  }

  // ── Build / update a Chart.js line chart ────────────────────────────────────
  function makeChart(canvasId, labels, data, color, yLabel) {
    const ctx = $(canvasId).getContext('2d');
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data,
          borderColor:     color.line,
          backgroundColor: color.fill,
          borderWidth: 2,
          pointRadius: data.length > 200 ? 0 : 2,  // hide dots if dense
          tension: 0.3,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: {
              maxTicksLimit: 8,
              color: '#888',
              font: { size: 11 },
            },
            grid: { color: 'rgba(0,0,0,0.05)' },
          },
          y: {
            title: { display: true, text: yLabel, color: '#888', font: { size: 11 } },
            ticks: { color: '#888', font: { size: 11 } },
            grid:  { color: 'rgba(0,0,0,0.05)' },
          },
        },
      },
    });
  }

  // ── State ────────────────────────────────────────────────────────────────────
  let charts = {};

  // ── Main fetch + render ──────────────────────────────────────────────────────
  async function refresh() {
    let data;
    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data = await res.json();
    } catch (err) {
      $('dataSource').textContent = 'Sensor offline';
      console.error('Dashboard fetch failed:', err);
      return;
    }

    // Validate the shape of the response before touching the DOM
    if (!isValidResponse(data)) {
      $('dataSource').textContent = 'Unexpected data from server';
      console.error('Dashboard: invalid API response shape', data);
      return;
    }

    if (!data.latest) {
      $('dataSource').textContent = 'No data yet';
      return;
    }

    const { latest, series } = data;

    // ── Stat cards ──────────────────────────────────────────────────────────
    $('statTemp').textContent  = fmt(latest.temperature);
    $('statHum').textContent   = fmt(latest.humidity);
    $('statPress').textContent = fmt(latest.pressure);

    const mmT = minMax(series.temperatures);
    const mmH = minMax(series.humidities);
    const mmP = minMax(series.pressures);

    $('statTempRange').textContent  = mmT.min != null ? `↓ ${fmt(mmT.min)} · ↑ ${fmt(mmT.max)} (7 d)` : '';
    $('statHumRange').textContent   = mmH.min != null ? `↓ ${fmt(mmH.min)} · ↑ ${fmt(mmH.max)} (7 d)` : '';
    $('statPressRange').textContent = mmP.min != null ? `↓ ${fmt(mmP.min)} · ↑ ${fmt(mmP.max)} (7 d)` : '';

    // ── Meta bar ────────────────────────────────────────────────────────────
    $('dataSource').textContent    = `Sensor · ${data.count} readings`;
    $('dataTimestamp').textContent = `Last update: ${formatTimestamp(latest.recorded_at)}`;

    // ── Labels ──────────────────────────────────────────────────────────────
    const labels = series.timestamps.map(formatTimestamp);

    // ── Charts: create on first load, update afterwards ─────────────────────
    if (!charts.temp) {
      charts.temp  = makeChart('chartTemp',  labels, series.temperatures, COLORS.temp,  '°C');
      charts.hum   = makeChart('chartHum',   labels, series.humidities,   COLORS.hum,   '%');
      charts.press = makeChart('chartPress', labels, series.pressures,    COLORS.press, 'hPa');
    } else {
      for (const [key, , seriesKey] of [
        ['temp',  'temperatures', 'temperatures'],
        ['hum',   'humidities',   'humidities'],
        ['press', 'pressures',    'pressures'],
      ]) {
        charts[key].data.labels            = labels;
        charts[key].data.datasets[0].data  = series[seriesKey];
        charts[key].update('none'); // 'none' = skip animation on refresh
      }
    }
  }

  // ── Boot ─────────────────────────────────────────────────────────────────────
  // Chart.js must already be loaded; if not, load it dynamically
  function boot() {
    refresh();
    setInterval(refresh, POLL_INTERVAL);
  }

  if (typeof Chart === 'undefined') {
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';
    s.onload = boot;
    document.head.appendChild(s);
  } else {
    boot();
  }
})();