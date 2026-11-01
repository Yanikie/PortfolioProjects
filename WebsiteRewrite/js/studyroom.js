(() => {
  const API = "/api/sensor.php";
  const POLL_INTERVAL = 60000;

  const $ = (id) => document.getElementById(id);
  const fmt = (n) => n.toFixed(1);
  const css = getComputedStyle(document.documentElement);
  const color = (name) => css.getPropertyValue(name).trim();

  // -------- Helpers --------
  function formatTime(unix) {
    return new Date(unix * 1000).toLocaleString("en-GB", {
      day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
    });
  }

  function isValid(data) {
    if (!data || data.ok !== true) return false;
    if (data.latest === null) return true;

    const l = data.latest;
    const s = data.series;
    if (!l || !s) return false;
    if (!["recorded_at", "temperature", "humidity", "pressure"].every((k) => typeof l[k] === "number")) return false;

    const keys = ["timestamps", "temperatures", "humidities", "pressures"];
    if (!keys.every((k) => Array.isArray(s[k]) && s[k].length === s.timestamps.length)) return false;
    return keys.every((k) => s[k].every((v) => typeof v === "number"));
  }

  function showRange(id, values) {
    if (!values.length) return;
    $(id).textContent = `7-day low ${fmt(Math.min(...values))}, high ${fmt(Math.max(...values))}`;
  }

  // -------- Charts --------
  const charts = {};

  function makeChart(canvasId, labels, values) {
    return new Chart($(canvasId), {
      type: "line",
      data: {
        labels,
        datasets: [{
          data: values,
          borderColor: color("--bronze"),
          backgroundColor: "rgba(82, 44, 16, 0.6)",
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 3,
          tension: 0.3,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: {
            ticks: {
              color: color("--soft"),
              maxTicksLimit: 3,
              font: { family: "IBM Plex Serif", size: 12 },
              callback: (value) => Number(value).toLocaleString("en-GB", { maximumFractionDigits: 1, useGrouping: false }),
            },
            grid: { color: "#3a3a3a" },
            border: { display: false },
          },
        },
      },
    });
  }

  function drawChart(key, canvasId, labels, values) {
    if (typeof Chart === "undefined") return;
    if (!charts[key]) {
      charts[key] = makeChart(canvasId, labels, values);
      return;
    }
    charts[key].data.labels = labels;
    charts[key].data.datasets[0].data = values;
    charts[key].update("none");
  }

  // -------- Refresh --------
  async function refresh() {
    let data;
    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data = await res.json();
    } catch (err) {
      $("sensorStatus").textContent = "The sensor can't be reached right now. This page checks again every minute.";
      return;
    }

    if (!isValid(data)) {
      $("sensorStatus").textContent = "The sensor sent data this page can't read. This page checks again every minute.";
      return;
    }

    if (!data.latest) {
      $("sensorStatus").textContent = "No readings in the past 7 days.";
      return;
    }

    const { latest, series } = data;
    const labels = series.timestamps.map(formatTime);

    $("sensorStatus").textContent =
      `Last update ${formatTime(latest.recorded_at)}. ${data.count.toLocaleString("en-GB")} readings in the past 7 days.`;

    $("valueTemp").textContent = fmt(latest.temperature);
    $("valuePress").textContent = fmt(latest.pressure);
    showRange("rangeTemp", series.temperatures);
    showRange("rangePress", series.pressures);
    drawChart("temp", "chartTemp", labels, series.temperatures);
    drawChart("press", "chartPress", labels, series.pressures);

    // The weather station sends 0 until the humidity sensor is installed
    const hasHumidity = latest.humidity !== 0;
    $("chartHumWrap").hidden = !hasHumidity;
    $("noteHum").hidden = hasHumidity;
    $("valueHum").textContent = hasHumidity ? fmt(latest.humidity) : "—";
    if (hasHumidity) {
      showRange("rangeHum", series.humidities);
      drawChart("hum", "chartHum", labels, series.humidities);
    }
  }

  refresh();
  setInterval(refresh, POLL_INTERVAL);
})();
