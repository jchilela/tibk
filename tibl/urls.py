"""gestao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
import sitetibl.views
from django.conf.urls import include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/clearcache/', include('clearcache.urls')),
    path('tibl/', sitetibl.views.comeco),
    path('tibl/gestao/<gestaoescolhida>/<int:pagina>/', sitetibl.views.mostraGestao),
    path('tibl/<gestaoescolhida>/detalhe/<int:identificador>/', sitetibl.views.mostraDetalhe),
    path('tibl/<gestaoescolhida>/criar/', sitetibl.views.mostraCriacao),
    path('tibl/<gestaoescolhida>/actualizar/<int:id>/', sitetibl.views.mostraActualizacao),
    path('tibl/<gestaoescolhida>/eliminar/<int:id>/', sitetibl.views.mostraEliminacao),
    path('tibl/contasbancarias/inativar/<int:id>/', sitetibl.views.inativaContabancaria, name='inativaContabancaria'),
    path('tibl/contasbancarias/reativar/<int:id>/', sitetibl.views.reativaContabancaria, name='reativaContabancaria'),
    path('tibl/contasbancarias/inativas/', sitetibl.views.contasbancariasinativas, name='contasbancariasinativas'),
    # contas bancárias: filtro avançado (banco/moeda)
    path('tibl/filtrarcontasbancarias/', sitetibl.views.ContaBancariaFilterListView.as_view(), name='contasFiltradas'),
    # contas bancárias: busca por campos soltos (proprietário/banco)
    path('tibl/buscacontasbancarias/', sitetibl.views.encontraContasbancarias),
    path('tibl/buscaajudas/', sitetibl.views.encontraAjudas),
    path('tibl/buscacestas/', sitetibl.views.encontraCestas),
    path('tibl/buscaactividades/', sitetibl.views.encontraActividades),
    path('tibl/buscadepartamentos/', sitetibl.views.encontraDepartamentos),
    path('tibl/buscadizimosofertas/', sitetibl.views.encontraDizimosofertas),
    path('tibl/relatoriodizimosmembro/', sitetibl.views.relatoriodizimosmembro),
    path('tibl/relatorioofertasportipo/', sitetibl.views.relatorioofertasportipo),
    path('tibl/buscasaidascaixa/', sitetibl.views.encontraSaidascaixa),
    path('tibl/buscaentradascaixa/', sitetibl.views.encontraEntradascaixa),
    path('tibl/buscasaidasbanco/', sitetibl.views.encontraSaidasbanco),
    path('tibl/buscaentradasbanco/', sitetibl.views.encontraEntradasbanco),
    path('tibl/buscarelatoriosemanalcelula/', sitetibl.views.encontraRelatorioSemanalCelula),
    path('tibl/buscapedidosaida/', sitetibl.views.encontraPedidoSaida),
    path('tibl/buscaorcamentodepartamento/', sitetibl.views.encontraOrcamentoDepartamento),
    path('tibl/buscainventariopatrimonio/', sitetibl.views.encontraInventarioPatrimonio),
    path('tibl/buscaconteudoensino/', sitetibl.views.encontraConteudoEnsino),
    path('tibl/buscaenviomensagem/', sitetibl.views.encontraEnvioMensagem),
    path('tibl/buscabancos/', sitetibl.views.encontraBancos),
    path('tibl/buscaescalas/', sitetibl.views.encontraEscalas),
    path('tibl/actividade/<int:actividade_id>/escalas/',sitetibl.views.EscalasPorActividadeView.as_view()),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', sitetibl.views.root_redirect, name='index'), # redireciona para o menu de dashboards

    #endpoints para dashboard
    path('dashboard/', sitetibl.views.dashboard, name='dashboard'),
    path('dashboard/numero-irmaos-cadastrados-mensalmente', sitetibl.views.dashboardIrmaos),
    path('dashboard/orcamento-departamento', sitetibl.views.dashboardOrcamentoDepartamento),
    path('dashboard/pedido-saida-semana', sitetibl.views.dashboardPedidosSaidaSemana),
    path('dashboard/conteudo-ensino-mensal', sitetibl.views.dashboardConteudoEnsinoMensal),
    path('dashboard/dizimo-oferta', sitetibl.views.dashboardDizimoOferta),
    path('dashboard/crescimento-membros', sitetibl.views.dashboardCrescimentoMembros),

    #endpoints para baixar relatórios
    path('relatorios/', sitetibl.views.pagina_relatorios, name='pagina_relatorios'),
    path('relatorios/irmaos/pdf/', sitetibl.views.relatorio_irmaos_pdf, name="relatorio_irmaos_pdf"),
    path('relatorios/dizimos/pdf/', sitetibl.views.relatorio_dizimos_pdf, name='relatorio_dizimos_pdf'),
    path('relatorios/departamentos/pdf/', sitetibl.views.relatorio_departamentos_pdf, name='relatorio_departamentos_pdf'),
    path('relatorios/escalas/pdf/', sitetibl.views.relatorio_escalas_pdf, name='relatorio_escalas_pdf'),
    path('relatorios/actividades/pdf/', sitetibl.views.relatorio_actividades_pdf, name='relatorio_actividades_pdf'),
    path('relatorios/inventario_patrimonio/pdf/', sitetibl.views.relatorio_inventario_patrimonio_pdf, name='relatorio_inventario_patrimonio_pdf'),
    path('relatorios/saida_caixa/pdf/', sitetibl.views.relatorio_saida_caixa_pdf, name='relatorio_saida_caixa_pdf'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
