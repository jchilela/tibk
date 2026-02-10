document.addEventListener("DOMContentLoaded", function () {

// 1. Gráfico de Barras (irmaos cadastrados)
fetch('/dashboard/numero-irmaos-cadastrados-mensalmente')
  .then(response => response.json())
  .then(json => {
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
fetch('/dashboard/orcamento-departamento')
  .then(response => response.json())
  .then(json => {

      const canvas = document.getElementById('pizzaOrcamento');

      // Paleta base de verdes
      const baseColors = ['#769656', '#98b37e', '#4d6338', '#b9ccaa', '#5f7d48', '#cfe0bf'];

      // Gera cores repetindo da paleta se houver mais departamentos do que cores
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
                          label: function(context) {
                              let total = context.dataset.data.reduce((a,b)=>a+b,0);
                              let valor = context.parsed;
                              let percent = ((valor / total) * 100).toFixed(1);
                              return `${context.label}: ${valor.toLocaleString()} (${percent}%)`;
                          }
                      }
                  }
              }
          }
      });
  })
  .catch(err => console.error("Erro ao buscar dados da API:", err));


// 3. Gráfico de Linhas (pedido de saida)
fetch('/dashboard/pedido-saida-semana')
  .then(response => response.json())
  .then(json => {

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
fetch('/dashboard/conteudo-ensino-mensal')
  .then(r => r.json())
  .then(json => {

    // Número grande
    document.getElementById('fluxoTotalConteudos').innerText =
      `${json.total} conteúdos`;

    // Gráfico
    new Chart(document.getElementById('fluxoCaixaChartConteudos'), {
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

  });

//5. dizimo e pferta
fetch('/dashboard/dizimo-oferta')
  .then(r => r.json())
  .then(json => {

    // Gera cores automáticas (tons verdes parecidos)
    const colors = [
      '#769656','#98b37e','#4d6338','#b9ccaa','#5f7d48','#cfe0bf'
    ];

    // Adiciona cor em ordem para cada dataset
    json.datasets.forEach((ds, i) => {
      ds.borderColor = colors[i % colors.length];
      ds.backgroundColor = colors[i % colors.length] + '33'; // alpha 20%
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
          y: {
            beginAtZero: true
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ": " + context.parsed.y.toLocaleString() + " Kz";
              }
            }
          }
        }
      }
    });

  });

//6.mebros
fetch('/dashboard/crescimento-membros')
  .then(r => r.json())
  .then(json => {

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
              label: function(ctx) {
                return ctx.dataset.label + ": " + ctx.parsed.y;
              }
            }
          }
        }
      }
    });

  });

});