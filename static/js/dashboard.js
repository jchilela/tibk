document.addEventListener("DOMContentLoaded", function () {

  // Helper: Safe Fetch with Error Handling and Toast integration
  async function safeFetch(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Fetch error on ${url}:`, error);
      if (window.TIBL && window.TIBL.toast) {
        window.TIBL.toast(`Erro ao carregar dados do gráfico: ${url.split('/').pop()}`, 'error');
      }
      return null;
    }
  }

  // 1. Gráfico de Barras (irmaos cadastrados)
  safeFetch('/dashboard/numero-irmaos-cadastrados-mensalmente').then(json => {
    if (!json) return;
    new Chart(document.getElementById('irmaos'), {
      type: 'bar',
      data: {
        labels: json.labels,
        datasets: [{
          label: 'Irmãos Cadastrados',
          data: json.data,
          backgroundColor: '#2e7d32', /* Premium Emerald */
          borderRadius: 6
        }]
      },
      options: {
        responsive: true
      }
    });
  });

  // 2. Gráfico de Pizza (Orçamento)
  safeFetch('/dashboard/orcamento-departamento').then(json => {
    if (!json) return;
    const canvas = document.getElementById('pizzaOrcamento');
    const baseColors = ['#1b5e20', '#2e7d32', '#4caf50', '#81c784', '#a5d6a7', '#c8e6c9'];
    const colors = json.labels.map((_, i) => baseColors[i % baseColors.length]);

    new Chart(canvas, {
      type: 'pie',
      data: {
        labels: json.labels,
        datasets: [{
          data: json.data,
          backgroundColor: colors
        }]
      },
      options: {
        responsive: true,
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                let valor = context.parsed;
                let percent = ((valor / total) * 100).toFixed(1);
                return `${context.label}: ${valor.toLocaleString()} (${percent}%)`;
              }
            }
          }
        }
      }
    });
  });

  /* 3. Gráfico de Linhas (pedido de saida) - Comentado por falta de canvas no HTML
  safeFetch('/dashboard/pedido-saida-semana').then(json => {
    ...
  });
  */


  /* 4. Conteudos de ensino - Update stat only
  safeFetch('/dashboard/conteudo-ensino-mensal').then(json => {
    if (!json) return;
    const totalEl = document.getElementById('fluxoTotalConteudos');
    if (totalEl) totalEl.innerText = `${json.total} conteúdos`;
  });
  */

  // 5. dizimo e oferta
  safeFetch('/dashboard/dizimo-oferta').then(json => {
    if (!json || !json.datasets) return;
    const colors = ['#1b5e20', '#2e7d32', '#ff6f00', '#0288d1', '#7b1fa2', '#c2185b'];

    json.datasets.forEach((ds, i) => {
      ds.borderColor = colors[i % colors.length];
      ds.backgroundColor = colors[i % colors.length] + '33';
      ds.tension = 0.3;
      ds.fill = true;
    });

    new Chart(document.getElementById('ofertasChart'), {
      type: 'line',
      data: {
        labels: json.labels,
        datasets: json.datasets
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        },
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
  });

  // 6. membros
  safeFetch('/dashboard/crescimento-membros').then(json => {
    if (!json) return;
    new Chart(document.getElementById('membrosChart'), {
      type: 'line',
      data: {
        labels: json.labels,
        datasets: [
          {
            label: `Membros (${json.ano})`,
            data: json.membros,
            borderColor: '#1b5e20',
            backgroundColor: 'rgba(27,94,32,0.1)',
            tension: 0.3,
            fill: true,
            pointRadius: 4
          },
          {
            label: `Visitantes (${json.ano})`,
            data: json.visitantes,
            borderColor: '#2e7d32',
            backgroundColor: 'rgba(46,125,50,0.1)',
            tension: 0.3,
            fill: true,
            pointRadius: 4
          },
          {
            label: `Crianças (${json.ano})`,
            data: json.criancas,
            borderColor: '#ff6f00',
            backgroundColor: 'rgba(255,111,0,0.1)',
            tension: 0.3,
            fill: true,
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.dataset.label + ": " + ctx.parsed.y;
              }
            }
          }
        }
      }
    });
  });

});