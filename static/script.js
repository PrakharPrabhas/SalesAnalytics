const $ = (id) => document.getElementById(id);
const charts = {};
const currency = (n) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(n || 0));
const number = (n) => new Intl.NumberFormat("en-IN").format(Number(n || 0));
const palette = [
  "#5278e8",
  "#36b58a",
  "#f2a65a",
  "#9b7be7",
  "#e47791",
  "#54b6c8",
  "#8996a8",
  "#c3a45c",
];

function commonOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          usePointStyle: true,
          boxWidth: 7,
          padding: 17,
          font: { family: "Inter", size: 10 },
        },
      },
    },
  };
}
function makeChart(id, type, data, options = {}) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart($(id), {
    type,
    data,
    options: { ...commonOptions(), ...options },
  });
}
function buildCharts(d) {
  makeChart(
    "trendChart",
    "line",
    {
      labels: d.monthly.labels,
      datasets: [
        {
          label: "Sales",
          data: d.monthly.sales,
          borderColor: "#5278e8",
          backgroundColor: "rgba(82,120,232,.10)",
          fill: true,
          tension: 0.35,
          pointRadius: 2,
          borderWidth: 2,
        },
        {
          label: "Profit",
          data: d.monthly.profit,
          borderColor: "#36b58a",
          backgroundColor: "transparent",
          tension: 0.35,
          pointRadius: 2,
          borderWidth: 2,
        },
      ],
    },
    {
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 9 } } },
        y: {
          grid: { color: "#f0f2f6" },
          ticks: {
            font: { size: 9 },
            callback: (v) => "₹" + (v / 1000).toFixed(0) + "k",
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
          align: "end",
          labels: { usePointStyle: true, boxWidth: 7, font: { size: 10 } },
        },
      },
    },
  );
  makeChart(
    "categoryChart",
    "doughnut",
    {
      labels: d.category.labels,
      datasets: [
        {
          data: d.category.values,
          backgroundColor: palette,
          borderWidth: 0,
          hoverOffset: 5,
        },
      ],
    },
    {
      cutout: "68%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,
            boxWidth: 7,
            padding: 13,
            font: { size: 9 },
          },
        },
      },
    },
  );
  makeChart(
    "regionChart",
    "bar",
    {
      labels: d.region.labels,
      datasets: [
        {
          label: "Sales",
          data: d.region.values,
          backgroundColor: palette,
          borderRadius: 5,
          maxBarThickness: 35,
        },
      ],
    },
    {
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 9 } } },
        y: {
          grid: { color: "#f0f2f6" },
          ticks: {
            font: { size: 9 },
            callback: (v) => "₹" + (v / 1000).toFixed(0) + "k",
          },
        },
      },
    },
  );
  makeChart(
    "productChart",
    "bar",
    {
      labels: d.products.labels,
      datasets: [
        {
          label: "Sales",
          data: d.products.sales,
          backgroundColor: "#7895ee",
          borderRadius: 5,
          maxBarThickness: 24,
        },
      ],
    },
    {
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { color: "#f0f2f6" },
          ticks: {
            font: { size: 9 },
            callback: (v) => "₹" + (v / 1000).toFixed(0) + "k",
          },
        },
        y: { grid: { display: false }, ticks: { font: { size: 10 } } },
      },
    },
  );
  makeChart(
    "paymentChart",
    "doughnut",
    {
      labels: d.payment.labels,
      datasets: [
        {
          data: d.payment.values,
          backgroundColor: palette,
          borderWidth: 0,
          hoverOffset: 5,
        },
      ],
    },
    {
      cutout: "68%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,
            boxWidth: 7,
            padding: 12,
            font: { size: 9 },
          },
        },
      },
    },
  );
}
function renderTable(rows) {
  const body = $("ordersBody");
  $("tableCount").textContent = `${rows.length} recent orders`;
  if (!rows.length) {
    body.innerHTML =
      '<tr><td colspan="8" class="empty">No sales records match these filters.</td></tr>';
    return;
  }
  body.innerHTML = rows
    .map(
      (r) => `<tr>
    <td>${escapeHtml(r.Order_ID)}</td><td>${escapeHtml(r.Order_Date)}</td>
    <td>${escapeHtml(r.Customer)}</td><td>${escapeHtml(r.Product)}</td>
    <td>${escapeHtml(r.Category)}</td><td>${escapeHtml(r.Region)}</td>
    <td>${currency(r.Sales)}</td><td class="positive">${currency(r.Profit)}</td>
  </tr>`,
    )
    .join("");
}
function escapeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
}
async function loadDashboard() {
  const params = new URLSearchParams({
    start: $("startDate").value,
    end: $("endDate").value,
    category: $("category").value,
    region: $("region").value,
    search: $("search").value,
  });
  try {
    const response = await fetch(`/api/dashboard?${params}`);
    if (!response.ok) throw new Error("Could not load dashboard data");
    const d = await response.json(),
      k = d.kpis;
    $("salesKpi").textContent = currency(k.sales);
    $("profitKpi").textContent = currency(k.profit);
    $("ordersKpi").textContent = number(k.orders);
    $("customersKpi").textContent = number(k.customers);
    $("quantityKpi").textContent = number(k.quantity);
    $("averageKpi").textContent = currency(k.average_order);
    $("recordsKpi").textContent = number(d.row_count);
    buildCharts(d);
    renderTable(d.recent);
  } catch (err) {
    console.error(err);
    $("ordersBody").innerHTML =
      '<tr><td colspan="8" class="empty">Unable to load data. Check that the Flask server is running.</td></tr>';
  }
}
let searchTimer;
["startDate", "endDate", "category", "region"].forEach((id) =>
  $(id).addEventListener("change", loadDashboard),
);
$("search").addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadDashboard, 300);
});
$("resetBtn").addEventListener("click", () => {
  $("startDate").value = document.body.dataset.minDate;
  $("endDate").value = document.body.dataset.maxDate;
  $("category").value = "All";
  $("region").value = "All";
  $("search").value = "";
  loadDashboard();
});
$("exportBtn").addEventListener("click", () => {
  const params = new URLSearchParams({
    start: $("startDate").value,
    end: $("endDate").value,
    category: $("category").value,
    region: $("region").value,
    search: $("search").value,
  });
  window.location.href = `/api/export?${params}`;
});
loadDashboard();
