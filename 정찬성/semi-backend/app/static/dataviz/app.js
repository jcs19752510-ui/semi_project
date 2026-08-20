const state = {
  target: "",
  ageMin: "",
  ageMax: "",
  region: "",
  logScale: true,
  page: 1,
  size: 20,
};

const el = {
  target: document.getElementById("filterTarget"),
  ageMin: document.getElementById("filterAgeMin"),
  ageMax: document.getElementById("filterAgeMax"),
  region: document.getElementById("filterRegion"),
  logScale: document.getElementById("filterLogScale"),
  reset: document.getElementById("btnReset"),
  prev: document.getElementById("btnPrev"),
  next: document.getElementById("btnNext"),
  pageInfo: document.getElementById("pageInfo"),
  tableInfo: document.getElementById("tableInfo"),
  tbody: document.querySelector("#recordsTable tbody"),
};

let debounceTimer = null;
function debounce(fn, delay) {
  return (...args) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fn(...args), delay);
  };
}

function baseParams() {
  const params = new URLSearchParams();
  if (state.target !== "") params.set("target", state.target);
  if (state.ageMin !== "") params.set("age_min", state.ageMin);
  if (state.ageMax !== "") params.set("age_max", state.ageMax);
  if (state.region !== "") params.set("region", state.region);
  return params;
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`요청 실패: ${url} (${res.status})`);
  return res.json();
}

async function loadSummary() {
  const data = await fetchJson("/dataviz/summary");
  document.getElementById("sumTotal").textContent = data.total_rows.toLocaleString() + "건";
  document.getElementById("sumColumns").textContent = data.total_columns + "개";
  document.getElementById("sumRatio").textContent = (data.unsatisfied_ratio * 100).toFixed(2) + "%";
  document.getElementById("sumAge").textContent = `${data.var15_min} ~ ${data.var15_max}세`;
  document.getElementById("sumVar38").textContent = data.var38_mean.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

async function loadRegions() {
  const data = await fetchJson("/dataviz/regions");
  for (const item of data) {
    const opt = document.createElement("option");
    opt.value = item.var3;
    opt.textContent = `${item.var3} (${item.count.toLocaleString()}건)`;
    el.region.appendChild(opt);
  }
}

let targetChart, var38Chart, ageChart;

function initCharts() {
  targetChart = new Chart(document.getElementById("targetChart"), {
    type: "bar",
    data: { labels: [], datasets: [{ label: "고객 수", data: [], backgroundColor: ["#2e6de5", "#e5572e"] }] },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });

  var38Chart = new Chart(document.getElementById("var38Chart"), {
    type: "bar",
    data: { labels: [], datasets: [{ label: "빈도", data: [], backgroundColor: "#2e6de5" }] },
    options: {
      responsive: true,
      scales: { x: { ticks: { maxTicksLimit: 10 } } },
      plugins: { legend: { display: false } },
    },
  });

  ageChart = new Chart(document.getElementById("ageChart"), {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        { label: "만족(0)", data: [], backgroundColor: "#2e6de5" },
        { label: "불만족(1)", data: [], backgroundColor: "#e5572e" },
      ],
    },
    options: { responsive: true, scales: { x: { stacked: false } } },
  });
}

function binLabels(edges) {
  const labels = [];
  for (let i = 0; i < edges.length - 1; i++) {
    labels.push(`${edges[i].toFixed(1)}~${edges[i + 1].toFixed(1)}`);
  }
  return labels;
}

async function refreshTargetChart() {
  const data = await fetchJson(`/dataviz/chart/target-distribution?${baseParams().toString()}`);
  targetChart.data.labels = data.labels;
  targetChart.data.datasets[0].data = data.counts;
  targetChart.update();
}

async function refreshVar38Chart() {
  const params = baseParams();
  params.set("log_scale", state.logScale);
  const data = await fetchJson(`/dataviz/chart/var38-histogram?${params.toString()}`);
  var38Chart.data.labels = binLabels(data.bin_edges);
  var38Chart.data.datasets[0].data = data.counts;
  var38Chart.data.datasets[0].label = state.logScale ? "빈도 (log1p 변환)" : "빈도";
  var38Chart.update();
}

async function refreshAgeChart() {
  const params = new URLSearchParams();
  if (state.region !== "") params.set("region", state.region);
  const data = await fetchJson(`/dataviz/chart/age-distribution?${params.toString()}`);
  ageChart.data.labels = binLabels(data.bin_edges);
  ageChart.data.datasets[0].data = data.satisfied_counts;
  ageChart.data.datasets[1].data = data.unsatisfied_counts;
  ageChart.update();
}

async function refreshTable() {
  const params = baseParams();
  params.set("page", state.page);
  params.set("size", state.size);
  const data = await fetchJson(`/dataviz/records?${params.toString()}`);

  el.tbody.innerHTML = "";
  for (const row of data.rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.id}</td><td>${row.var3}</td><td>${row.var15}</td><td>${row.var38.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td><td>${row.target}</td>`;
    el.tbody.appendChild(tr);
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.size));
  el.pageInfo.textContent = `${data.page} / ${totalPages} 페이지`;
  el.tableInfo.textContent = `전체 ${data.total.toLocaleString()}건 (필터 적용됨)`;
  el.prev.disabled = data.page <= 1;
  el.next.disabled = data.page >= totalPages;
}

async function refreshAll() {
  await Promise.all([refreshTargetChart(), refreshVar38Chart(), refreshAgeChart(), refreshTable()]);
}

function onFilterChanged() {
  state.page = 1;
  refreshAll().catch((err) => console.error(err));
}

el.target.addEventListener("change", () => {
  state.target = el.target.value;
  onFilterChanged();
});

el.region.addEventListener("change", () => {
  state.region = el.region.value;
  onFilterChanged();
});

el.logScale.addEventListener("change", () => {
  state.logScale = el.logScale.checked;
  refreshVar38Chart().catch((err) => console.error(err));
});

const onAgeInput = debounce(() => {
  state.ageMin = el.ageMin.value;
  state.ageMax = el.ageMax.value;
  onFilterChanged();
}, 400);

el.ageMin.addEventListener("input", onAgeInput);
el.ageMax.addEventListener("input", onAgeInput);

el.reset.addEventListener("click", () => {
  state.target = "";
  state.ageMin = "";
  state.ageMax = "";
  state.region = "";
  state.logScale = true;
  state.page = 1;
  el.target.value = "";
  el.ageMin.value = "";
  el.ageMax.value = "";
  el.region.value = "";
  el.logScale.checked = true;
  refreshAll().catch((err) => console.error(err));
});

el.prev.addEventListener("click", () => {
  if (state.page > 1) {
    state.page -= 1;
    refreshTable().catch((err) => console.error(err));
  }
});

el.next.addEventListener("click", () => {
  state.page += 1;
  refreshTable().catch((err) => console.error(err));
});

(async function main() {
  initCharts();
  await Promise.all([loadSummary(), loadRegions()]);
  await refreshAll();
})().catch((err) => console.error(err));
