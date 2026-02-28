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
          label: 'Numero de irmaos cadastrados',
          data: json.data,
          backgroundColor: '#769656'
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
    const baseColors = ['#769656', '#98b37e', '#4d6338', '#b9ccaa', '#5f7d48', '#cfe0bf'];
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

  // 3. Gráfico de Linhas (pedido de saida)
  safeFetch('/dashboard/pedido-saida-semana').then(json => {
    if (!json) return;
    new Chart(document.getElementById('pedidoSaida'), {
      type: 'line',
      data: {
        labels: json.labels,
        datasets: [{
          label: `Pedidos de Saída (${json.ano})`,
          data: json.data,
          borderColor: '#769656',
          tension: 0.3,
          fill: true,
          backgroundColor: 'rgba(118, 150, 86, 0.1)'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: `Pedidos de Saída por Dia da Semana – ${json.ano}`
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  });


  // 4. Conteudos de ensino
  safeFetch('/dashboard/conteudo-ensino-mensal').then(json => {
    if (!json) return;
    const totalEl = document.getElementById('fluxoTotalConteudos');
    if (totalEl) totalEl.innerText = `${json.total} conteúdos`;

    const chartEl = document.getElementById('fluxoCaixaChartConteudos');
    if (chartEl) {
      new Chart(chartEl, {
        type: 'line',
        data: {
          labels: json.labels,
          datasets: [{
            label: `Conteúdos Criados (${json.ano})`,
            data: json.data,
            borderColor: '#769656',
            backgroundColor: 'rgba(118,150,86,0.1)',
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { precision: 0 }
            }
          }
        }
      });
    }
  });

  // 5. dizimo e oferta
  safeFetch('/dashboard/dizimo-oferta').then(json => {
    if (!json || !json.datasets) return;
    const colors = ['#769656', '#98b37e', '#4d6338', '#b9ccaa', '#5f7d48', '#cfe0bf'];

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
            borderColor: '#769656',
            backgroundColor: 'rgba(118,150,86,0.1)',
            tension: 0.3,
            fill: true
          },
          {
            label: `Visitantes (${json.ano})`,
            data: json.visitantes,
            borderColor: '#98b37e',
            backgroundColor: 'rgba(152,179,126,0.1)',
            tension: 0.3,
            fill: true
          },
          {
            label: `Crianças (${json.ano})`,
            data: json.criancas,
            borderColor: '#4d6338',
            backgroundColor: 'rgba(77,99,56,0.1)',
            tension: 0.3,
            fill: true
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