(function () {
  "use strict";

  var canvas = document.getElementById("revenueChart");
  if (!canvas) return;

  var labels = window.CHART_LABELS || [];
  var values = window.CHART_VALUES || [];

  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Revenue (₦)",
          data: values,
          backgroundColor: "rgba(197, 154, 61, 0.3)",
          borderColor: "rgba(197, 154, 61, 0.8)",
          borderWidth: 1.5,
          borderRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function (ctx) {
              return "₦" + ctx.raw.toLocaleString();
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: { color: "#6B6560", font: { size: 11 } },
        },
        y: {
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: {
            color: "#6B6560",
            font: { size: 11 },
            callback: function (v) {
              return "₦" + v.toLocaleString();
            },
          },
        },
      },
    },
  });
})();
