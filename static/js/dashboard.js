document.addEventListener("DOMContentLoaded", function () {

  // Helper: Safe Fetch with Error Handling and Toast integration
  async function safeFetch(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("HTTP error! status: " + response.status);
      return await response.json();
    } catch (error) {
      console.error("Fetch error on " + url + ":", error);
      if (window.TIBL && window.TIBL.toast) {
        window.TIBL.toast("Erro ao carregar dados do gráfico: " + url.split('/').pop(), 'error');
      }
      return null;
    }
  }

  // 1. Gráfico de Barras — Irmãos cadastrados mensalmente
  if (document.getElementById('irmaos')) {
    safeFetch('/dashboard/numero-irmaos-cadastrados-mensalmente').then(function (json) {
      if (!json) return;
      new Chart(document.getElementById('irmaos'), {
        type: 'bar',
        data: {
          labels: json.labels,
          datasets: [{
            label: 'Irmãos Cadastrados',
            data: json.data,
            backgroundColor: '#2e7d32',
            borderRadius: 6
          }]
        },
        options: { responsive: true }
      });
    });
  }

  // 2. Gráfico de Pizza — Orçamento por Departamento
  if (document.getElementById('pizzaOrcamento')) {
    safeFetch('/dashboard/orcamento-departamento').then(function (json) {
      if (!json) return;
      var baseColors = ['#1b5e20', '#2e7d32', '#4caf50', '#81c784', '#a5d6a7', '#c8e6c9'];
      var colors = json.labels.map(function (_, i) { return baseColors[i % baseColors.length]; });

      new Chart(document.getElementById('pizzaOrcamento'), {
        type: 'pie',
        data: {
          labels: json.labels,
          datasets: [{ data: json.data, backgroundColor: colors }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  var total = context.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                  var valor = context.parsed;
                  var percent = ((valor / total) * 100).toFixed(1);
                  return context.label + ": " + valor.toLocaleString() + " (" + percent + "%)";
                }
              }
            }
          }
        }
      });
    });
  }

  // 3. Gráfico de Linhas — Dízimos e Ofertas
  if (document.getElementById('ofertasChart')) {
    safeFetch('/dashboard/dizimo-oferta').then(function (json) {
      if (!json || !json.datasets) return;
      var colors = ['#1b5e20', '#2e7d32', '#ff6f00', '#0288d1', '#7b1fa2', '#c2185b'];

      json.datasets.forEach(function (ds, i) {
        ds.borderColor = colors[i % colors.length];
        ds.backgroundColor = colors[i % colors.length] + '33';
        ds.tension = 0.3;
        ds.fill = true;
      });

      new Chart(document.getElementById('ofertasChart'), {
        type: 'line',
        data: { labels: json.labels, datasets: json.datasets },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true } },
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  return context.dataset.label + ": " + context.parsed.y.toLocaleString() + " Kz";
                }
              }
            }
          }
        }
      });

      // Actualizar stat card de dízimos, se existir
      var dizimoEl = document.getElementById('totalDizimos');
      if (dizimoEl && json.datasets[0]) {
        var last = json.datasets[0].data.filter(function (v) { return v > 0; }).pop() || 0;
        dizimoEl.innerText = last.toLocaleString('pt-PT') + ' Kz';
      }
    });
  }

  // 4. Gráfico de Linhas — Crescimento Células
  if (document.getElementById('membrosChart')) {
    safeFetch('/dashboard/crescimento-membros').then(function (json) {
      if (!json) return;
      new Chart(document.getElementById('membrosChart'), {
        type: 'line',
        data: {
          labels: json.labels,
          datasets: [
            {
              label: "Membros (" + json.ano + ")",
              data: json.membros,
              borderColor: '#1b5e20',
              backgroundColor: 'rgba(27,94,32,0.1)',
              tension: 0.3, fill: true, pointRadius: 4
            },
            {
              label: "Visitantes (" + json.ano + ")",
              data: json.visitantes,
              borderColor: '#2e7d32',
              backgroundColor: 'rgba(46,125,50,0.1)',
              tension: 0.3, fill: true, pointRadius: 4
            },
            {
              label: "Crianças (" + json.ano + ")",
              data: json.criancas,
              borderColor: '#ff6f00',
              backgroundColor: 'rgba(255,111,0,0.1)',
              tension: 0.3, fill: true, pointRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
          plugins: {
            tooltip: {
              callbacks: {
                label: function (ctx) { return ctx.dataset.label + ": " + ctx.parsed.y; }
              }
            }
          }
        }
      });
    });
  }

  // 5. Gráfico de Barras Horizontais — Membros por Departamento
  if (document.getElementById('deptMembrosChart')) {
    safeFetch('/dashboard/departamentos-membros').then(function (json) {
      if (!json) return;
      var baseColors = ['#1b5e20', '#2e7d32', '#4caf50', '#81c784', '#a5d6a7', '#c8e6c9', '#388e3c', '#66bb6a'];
      var colors = json.labels.map(function (_, i) { return baseColors[i % baseColors.length]; });

      new Chart(document.getElementById('deptMembrosChart'), {
        type: 'bar',
        data: {
          labels: json.labels,
          datasets: [{
            label: 'Membros',
            data: json.data,
            backgroundColor: colors,
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
          plugins: { legend: { display: false } }
        }
      });
    });
  }

});