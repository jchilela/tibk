from django.urls import path
from sitetibl import views

app_name = 'sitetibl'

urlpatterns = [
    # Página inicial
    path('', views.comeco, name='comeco'),

    # CRUD genérico
    path('gestao/<gestaoescolhida>/<int:pagina>/', views.mostraGestao, name='mostra_gestao'),
    path('<gestaoescolhida>/detalhe/<int:identificador>/', views.mostraDetalhe, name='mostra_detalhe'),
    path('<gestaoescolhida>/detalhe/<int:identificador>', views.mostraDetalhe, name='mostra_detalhe_legacy'),
    path('actividades/recorrentes/', views.criar_actividades_recorrentes, name='criar_actividades_recorrentes'),
    path('<gestaoescolhida>/criar/', views.mostraCriacao, name='mostra_criacao'),
    path('<gestaoescolhida>/actualizar/<int:id>/', views.mostraActualizacao, name='mostra_actualizacao'),
    path('<gestaoescolhida>/eliminar/<int:id>/', views.mostraEliminacao, name='mostra_eliminacao'),

    # Buscas (filtros)
    path('buscairmao/', views.encontraIrmao, name='busca_irmao'),
    path('buscacontasbancarias/', views.encontraContasbancarias, name='busca_contasbancarias'),
    path('buscaajudas/', views.encontraAjudas, name='busca_ajudas'),
    path('buscacestas/', views.encontraCestas, name='busca_cestas'),
    path('buscaactividades/', views.encontraActividades, name='busca_actividades'),
    path('buscadepartamentos/', views.encontraDepartamentos, name='busca_departamentos'),
    path('buscadizimosofertas/', views.encontraDizimosofertas, name='busca_dizimosofertas'),
    path('buscasaidascaixa/', views.encontraSaidascaixa, name='busca_saidascaixa'),
    path('buscaentradascaixa/', views.encontraEntradascaixa, name='busca_entradascaixa'),
    path('buscasaidasbanco/', views.encontraSaidasbanco, name='busca_saidasbanco'),
    path('buscaentradasbanco/', views.encontraEntradasbanco, name='busca_entradasbanco'),
    path('buscarelatoriosemanalcelula/', views.encontraRelatorioSemanalCelula, name='busca_relatoriosemanalcelula'),
    path('buscacelulas/', views.encontraCelulas, name='busca_celulas'),
    path('buscapedidosaida/', views.encontraPedidoSaida, name='busca_pedidosaida'),
    path('buscaorcamentodepartamento/', views.encontraOrcamentoDepartamento, name='busca_orcamentodepartamento'),
    path('buscainventariopatrimonio/', views.encontraInventarioPatrimonio, name='busca_inventariopatrimonio'),
    path('buscaconteudoensino/', views.encontraConteudoEnsino, name='busca_conteudoensino'),
    path('buscaenviomensagem/', views.encontraEnvioMensagem, name='busca_enviomensagem'),
    path('enviomensagem/nova/', views.criarEnvioMensagem, name='criar_enviomensagem'),
    path('buscabancos/', views.encontraBancos, name='busca_bancos'),
    path('buscaescalas/', views.encontraEscalas, name='busca_escalas'),

    # Escalas por actividade (API)
    path('actividade/<int:actividade_id>/escalas/', views.EscalasPorActividadeView.as_view(), name='escalas_por_actividade'),
    path('actividade/<int:actividade_id>/escalar-massa/', views.escalar_em_massa, name='escalar_em_massa'),

    # API: municípios por província (cascading dropdown)
    path('api/municipios/<int:provincia_id>/', views.api_municipios, name='api_municipios'),
    path('api/funcoes-actividade/<int:actividade_id>/', views.api_funcoes_por_actividade, name='api_funcoes_actividade'),
    path('api/actividades/feed/', views.actividades_feed, name='actividades_feed'),

    # Calendário de actividades
    path('actividades/calendario/', views.actividades_calendario, name='actividades_calendario'),

    # Rotas legadas preservadas para compatibilidade entre branches
    path('contasbancarias/inativar/<int:id>/', views.inativaContabancaria, name='inativaContabancaria'),
    path('contasbancarias/reativar/<int:id>/', views.reativaContabancaria, name='reativaContabancaria'),
    path('contasbancarias/inativas/', views.contasbancariasinativas, name='contasbancariasinativas'),
    path('relatorioofertasportipo/', views.relatorioofertasportipo, name='relatorioofertasportipo'),
    path('relatorioofertasportipo/pdf/', views.relatorioofertasportipo_pdf, name='relatorioofertasportipo_pdf'),
    path('insights/dizimosofertas/', views.insightsdizimosofertas, name='insights_dizimosofertas'),
    path('dizimos/recibo/<int:dizimo_id>/visualizar/', views.visualizar_recibo_dizimo, name='visualizar_recibo_dizimo'),
    path('dizimos/recibo/<int:dizimo_id>/', views.gerar_recibo_dizimo, name='gerar_recibo_dizimo'),

    # Perfil pessoal
    path('meu-perfil/', views.meu_perfil, name='meu_perfil'),
]
