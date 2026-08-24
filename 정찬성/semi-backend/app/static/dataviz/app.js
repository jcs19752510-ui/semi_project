const state = {
  task: "",
  model: "",
};

const el = {
  task: document.getElementById("selTask"),
  model: document.getElementById("selModel"),
  btnQuery: document.getElementById("btnQuery"),
  selectedLabel: document.getElementById("selectedLabel"),
  emptyHint: document.getElementById("emptyHint"),
  boxplot: document.getElementById("boxplot"),
  aucLabel: document.getElementById("aucLabel"),
  loadStatus: document.getElementById("loadStatus"),
};

function showLoadStatus(text, isError) {
  el.loadStatus.textContent = text;
  el.loadStatus.style.display = text ? "block" : "none";
  el.loadStatus.classList.toggle("load-status-error", !!isError);
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(`요청 실패: ${url} (${res.status}) ${detail.detail ?? ""}`);
  }
  return res.json();
}

// ── 업무명 → 모델명 드롭다운 (§0-1-1: 선택만으로는 어떤 조회 API도 호출되지 않는다) ──

async function loadTasks() {
  const tasks = await fetchJson("/dataviz/tasks");
  for (const t of tasks) {
    const opt = document.createElement("option");
    opt.value = t.id;
    // 업무종류.png 기준 4종을 전부 드롭다운에 "표시"하되(§요청), 데이터 파이프라인이
    // 아직 없는 업무(문서 군집화/마켓 가격 예측)는 선택만 못 하도록 disabled 처리한다.
    opt.textContent = t.enabled ? t.label : `${t.label} (준비중)`;
    opt.disabled = !t.enabled;
    el.task.appendChild(opt);
  }
}

function setModelDisabled(disabled) {
  el.model.disabled = disabled;
  if (disabled) {
    // 2026-08-24 변경: "전체" 옵션 제거 요청 — 업무 미선택 시에는 아예 빈 목록으로 둔다.
    el.model.innerHTML = "";
    state.model = "";
  }
}

async function onTaskChanged() {
  state.task = el.task.value;
  state.model = "";
  updateSelectedLabel();

  if (state.task === "") {
    // §0-1-1 [기본값]: 업무명 미선택 시 모델명은 비워두고 비활성화.
    setModelDisabled(true);
    updateQueryButton();
    return;
  }

  const models = await fetchJson(`/dataviz/models?task=${encodeURIComponent(state.task)}`);
  // 2026-08-24 변경: "전체"(model=all) 옵션 제거 — 신용카드처럼 대용량 업무에서
  // 5개 모델을 한꺼번에 학습하면 최초 조회가 1분 가까이 걸려(§작업이력 실측) 사용성이
  // 나쁘다. 이제 모델명은 항상 구체적인 모델 하나만 선택하도록 강제한다.
  el.model.innerHTML = "";
  for (const m of models) {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = m.label;
    el.model.appendChild(opt);
  }
  el.model.disabled = false;
  updateQueryButton();

  if (models.length > 0) {
    // <select>는 옵션 채우면 브라우저가 첫 번째를 자동 선택하지만 change 이벤트는 안 뜬다 —
    // 모델명 선택 시 자동조회 정책과 일관되도록 첫 모델로 명시적 자동조회를 트리거한다.
    el.model.value = models[0].id;
    onModelChanged();
  }
}

function onModelChanged() {
  // 2026-08-24 변경: 모델명 선택 시 [전처리조회] 버튼 클릭 없이 즉시 자동 조회한다
  // (기존 §0-1-1 "선택만으로는 API 호출 안 함" 정책을 사용자 요청으로 대체).
  state.model = el.model.value;
  updateSelectedLabel();
  if (state.task !== "" && !el.btnQuery.disabled) {
    onQueryClick();
  }
}

function updateSelectedLabel() {
  const taskLabel = state.task ? el.task.selectedOptions[0].textContent : "전체";
  const modelLabel = state.model ? el.model.selectedOptions[0].textContent : "전체";
  el.selectedLabel.textContent = `선택된 업무: ${taskLabel} / 선택된 모델: ${modelLabel}`;
}

function updateQueryButton() {
  el.btnQuery.disabled = state.task === "";
}

// ── 차트 렌더링 ────────────────────────────────────────────────────────

let targetChart, ageRatioChart, balanceRatioChart, rocChart;

function initCharts() {
  targetChart = new Chart(document.getElementById("targetChart"), {
    type: "bar",
    data: {
      labels: ["만족(0)", "불만족(1)"],
      datasets: [{ label: "고객 수", data: [], backgroundColor: ["#2e6de5", "#e5572e"] }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });

  ageRatioChart = new Chart(document.getElementById("ageRatioChart"), {
    type: "bar",
    data: { labels: [], datasets: [{ label: "불만족 비율(%)", data: [], backgroundColor: "#e5572e" }] },
    options: {
      responsive: true,
      scales: { x: { ticks: { maxTicksLimit: 10 } }, y: { title: { display: true, text: "%" } } },
      plugins: { legend: { display: false } },
    },
  });

  balanceRatioChart = new Chart(document.getElementById("balanceRatioChart"), {
    type: "bar",
    data: { labels: [], datasets: [{ label: "불만족 비율(%)", data: [], backgroundColor: "#e5572e" }] },
    options: {
      responsive: true,
      scales: { x: { ticks: { maxTicksLimit: 10 } }, y: { title: { display: true, text: "%" } } },
      plugins: { legend: { display: false } },
    },
  });

  rocChart = new Chart(document.getElementById("rocChart"), {
    type: "line",
    data: {
      datasets: [
        {
          label: "ROC",
          data: [],
          borderColor: "#2e6de5",
          pointRadius: 0,
          borderWidth: 2,
          showLine: true,
        },
        {
          label: "무작위 기준선",
          data: [
            { x: 0, y: 0 },
            { x: 1, y: 1 },
          ],
          borderColor: "#c7cbd1",
          borderDash: [4, 4],
          pointRadius: 0,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      parsing: false,
      scales: {
        x: { type: "linear", min: 0, max: 1, title: { display: true, text: "FPR" } },
        y: { min: 0, max: 1, title: { display: true, text: "TPR" } },
      },
    },
  });
}

function binLabel(range) {
  // pandas Interval 문자열 "(4.999, 23.0]" → "5.0~23.0"로 축약 표시(§0-1-6: 소수점 1자리).
  const m = range.match(/\(([-\d.]+),\s*([-\d.]+)]/);
  if (!m) return range;
  return `${Number(m[1]).toFixed(1)}~${Number(m[2]).toFixed(1)}`;
}

function renderPreprocessCheck(body) {
  const labels = body.labels;
  // 업무마다 축·문구 의미가 달라(산탄데르=만족/불만족, 신용카드=정상/사기) 차트 제목과
  // 타깃분포 라벨을 응답의 labels로 매번 갱신한다.
  document.getElementById("targetChartTitle").textContent = "타깃 클래스 불균형 분포";
  document.getElementById("bin1ChartTitle").textContent = labels.bin1_title;
  document.getElementById("bin2ChartTitle").textContent = labels.bin2_title;
  document.getElementById("boxplotTitle").textContent = labels.box_title;

  targetChart.data.labels = [labels.negative, labels.positive];
  targetChart.data.datasets[0].data = [body.target_distribution.satisfied, body.target_distribution.unsatisfied];
  targetChart.update();

  ageRatioChart.data.labels = body.bin1_ratio.map((b) => binLabel(b.range));
  ageRatioChart.data.datasets[0].data = body.bin1_ratio.map((b) => b.ratio);
  ageRatioChart.update();

  balanceRatioChart.data.labels = body.bin2_ratio.map((b) => binLabel(b.range));
  balanceRatioChart.data.datasets[0].data = body.bin2_ratio.map((b) => b.ratio);
  balanceRatioChart.update();

  renderBoxplot(body.value_boxplot, labels);
}

function renderBoxplot(box, labels) {
  // whisker_low/high(1.5×IQR 표준 수염) 기준으로 축을 잡는다 — saldo_var30처럼 꼬리가
  // 아주 긴 컬럼을 진짜 min/max로 스케일링하면 박스가 실선처럼 눌려 안 보이게 된다.
  const groups = [
    { key: "satisfied", label: labels.negative, color: "#2e6de5" },
    { key: "unsatisfied", label: labels.positive, color: "#e5572e" },
  ];
  const allValues = groups.flatMap((g) => [box[g.key].whisker_low, box[g.key].whisker_high]);
  const lo = Math.min(...allValues);
  const hi = Math.max(...allValues);
  const span = hi - lo || 1;
  const pct = (v) => ((Math.min(Math.max(v, lo), hi) - lo) / span) * 100;

  el.boxplot.innerHTML = "";
  for (const g of groups) {
    const s = box[g.key];
    const col = document.createElement("div");
    col.className = "boxplot-col";

    const track = document.createElement("div");
    track.className = "boxplot-track";

    const whisker = document.createElement("div");
    whisker.className = "boxplot-whisker";
    whisker.style.bottom = `${pct(s.whisker_low)}%`;
    whisker.style.height = `${pct(s.whisker_high) - pct(s.whisker_low)}%`;
    whisker.style.borderColor = g.color;

    const boxEl = document.createElement("div");
    boxEl.className = "boxplot-box";
    boxEl.style.bottom = `${pct(s.q1)}%`;
    boxEl.style.height = `${Math.max(pct(s.q3) - pct(s.q1), 0.5)}%`;
    boxEl.style.background = g.color;

    const median = document.createElement("div");
    median.className = "boxplot-median";
    median.style.bottom = `${pct(s.median)}%`;

    track.append(whisker, boxEl, median);
    const caption = document.createElement("span");
    caption.className = "boxplot-caption";
    const outlierNote = s.outlier_count > 0 ? `, 이상치 ${s.outlier_count.toLocaleString()}건 생략` : "";
    caption.textContent = `${g.label} (중앙값 ${s.median.toLocaleString()}${outlierNote})`;

    col.append(track, caption);
    el.boxplot.appendChild(col);
  }
}

function renderModelResult(body) {
  // §0-1-2 [기본값]: 백엔드는 다중 곡선을 반환할 수 있으나, 프론트는 curves[0]만 렌더링한다.
  const curve = body.curves[0];
  if (!curve) return;
  rocChart.data.datasets[0].data = curve.fpr.map((x, i) => ({ x, y: curve.tpr[i] }));
  rocChart.data.datasets[0].label = `${curve.label} ROC`;
  rocChart.update();
  el.aucLabel.textContent = `AUC = ${curve.auc.toFixed(4)} (${curve.label})`;
}

// ── 전처리조회 버튼: 유일하게 결과 API를 호출하는 트리거 ──────────────────

async function onQueryClick() {
  el.btnQuery.disabled = true;
  el.btnQuery.textContent = "조회 중...";
  el.emptyHint.style.display = "none";

  const task = state.task;
  const model = state.model || "all";
  const params = `task=${encodeURIComponent(task)}&model=${encodeURIComponent(model)}`;
  // §3 리스크 2: preprocess-check와 model-result는 반드시 병렬로 호출한다.
  // allSettled를 쓰는 이유: 하나가 실패해도(예: 모델 학습 라이브러리 문제) 나머지
  // 정상 응답까지 함께 안 그려지는 일이 없도록, 성공한 쪽은 반드시 렌더링한다.
  const [preprocessResult, modelResultResult] = await Promise.allSettled([
    fetchJson(`/dataviz/preprocess-check?${params}`),
    fetchJson(`/dataviz/model-result?${params}`),
  ]);

  const errors = [];
  if (preprocessResult.status === "fulfilled") {
    renderPreprocessCheck(preprocessResult.value);
  } else {
    console.error(preprocessResult.reason);
    errors.push(`전처리검증: ${preprocessResult.reason.message}`);
  }
  if (modelResultResult.status === "fulfilled") {
    renderModelResult(modelResultResult.value);
  } else {
    console.error(modelResultResult.reason);
    errors.push(`모델결과: ${modelResultResult.reason.message}`);
  }
  if (errors.length > 0) {
    alert(errors.join("\n"));
  }

  // §0-1-5 [기본값]: 두 API 모두 완료된 시점(성공/실패 무관)에 버튼 재활성화.
  el.btnQuery.disabled = false;
  el.btnQuery.textContent = "전처리조회";
}

el.task.addEventListener("change", () => onTaskChanged().catch((err) => console.error(err)));
el.model.addEventListener("change", onModelChanged);
el.btnQuery.addEventListener("click", () => onQueryClick());

// Render 무료 티어처럼 서버가 비활성 상태에서 깨어나는 데 50초 이상 걸릴 수 있는
// 배포 환경을 고려해, 최초 진입 시 업무 목록 로딩을 재시도한다. 이게 없으면
// 콜드스타트 중 첫 요청만 실패하고도 화면엔 아무 표시가 없어 "고장난 것처럼" 보인다.
async function loadTasksWithRetry() {
  const maxAttempts = 8;
  const delaysMs = [1000, 2000, 3000, 5000, 8000, 8000, 8000, 8000]; // 총 최대 약 45초
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      if (attempt > 1) showLoadStatus(`서버를 깨우는 중입니다... (${attempt}/${maxAttempts})`, false);
      await loadTasks();
      showLoadStatus("", false);
      return;
    } catch (err) {
      console.error(err);
      if (attempt === maxAttempts) {
        showLoadStatus("업무 목록을 불러오지 못했습니다. 새로고침(F5)해서 다시 시도해 주세요.", true);
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, delaysMs[attempt - 1]));
    }
  }
}

(async function main() {
  initCharts();
  updateSelectedLabel();
  await loadTasksWithRetry();
})().catch((err) => console.error(err));
