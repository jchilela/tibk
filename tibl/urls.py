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
from django.urls import path, include
import sitetibl.views

urlpatterns = [
    path('admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # App sitetibl
    path('tibl/', include('sitetibl.urls')),

    # Root redirect
    path('', sitetibl.views.root_redirect, name='index'),

    # Dashboards
    path('dashboard/', sitetibl.views.dashboard, name='dashboard'),
    path('dashboard/as-minhas-escalas/', sitetibl.views.minhas_escalas, name='minhas_escalas'),
    path('dashboard/numero-irmaos-cadastrados-mensalmente', sitetibl.views.dashboardIrmaos, name='dashboard_irmaos'),
    path('dashboard/orcamento-departamento', sitetibl.views.dashboardOrcamentoDepartamento, name='dashboard_orcamento_departamento'),
    path('dashboard/pedido-saida-semana', sitetibl.views.dashboardPedidosSaidaSemana, name='dashboard_pedidos_saida_semana'),
    path('dashboard/conteudo-ensino-mensal', sitetibl.views.dashboardConteudoEnsinoMensal, name='dashboard_conteudo_ensino_mensal'),
    path('dashboard/dizimo-oferta', sitetibl.views.dashboardDizimoOferta, name='dashboard_dizimo_oferta'),
    path('dashboard/crescimento-membros', sitetibl.views.dashboardCrescimentoMembros, name='dashboard_crescimento_membros'),
    path('dashboard/departamentos-membros', sitetibl.views.dashboardDepartamentosMembros, name='dashboard_departamentos_membros'),

    # Relatórios
    path('relatorios/', sitetibl.views.pagina_relatorios, name='pagina_relatorios'),
    path('relatorios/irmaos/pdf/', sitetibl.views.relatorio_irmaos_pdf, name='relatorio_irmaos_pdf'),
    path('relatorios/dizimos/pdf/', sitetibl.views.relatorio_dizimos_pdf, name='relatorio_dizimos_pdf'),
    path('relatorios/departamentos/pdf/', sitetibl.views.relatorio_departamentos_pdf, name='relatorio_departamentos_pdf'),
    path('relatorios/escalas/pdf/', sitetibl.views.relatorio_escalas_pdf, name='relatorio_escalas_pdf'),
    path('relatorios/actividades/pdf/', sitetibl.views.relatorio_actividades_pdf, name='relatorio_actividades_pdf'),
    path('relatorios/inventario_patrimonio/pdf/', sitetibl.views.relatorio_inventario_patrimonio_pdf, name='relatorio_inventario_patrimonio_pdf'),
    path('relatorios/saida_caixa/pdf/', sitetibl.views.relatorio_saida_caixa_pdf, name='relatorio_saida_caixa_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
