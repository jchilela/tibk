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
    path('', sitetibl.views.index, name = 'index'),
    path('tibl/gestao/<gestaoescolhida>/<int:pagina>/', sitetibl.views.mostraGestao),
    path('tibl/<gestaoescolhida>/detalhe/<int:identificador>/', sitetibl.views.mostraDetalhe),
    path('tibl/<gestaoescolhida>/criar/', sitetibl.views.mostraCriacao),
    path('tibl/<gestaoescolhida>/actualizar/<int:id>/', sitetibl.views.mostraActualizacao),
    path('tibl/<gestaoescolhida>/eliminar/<int:id>/', sitetibl.views.mostraEliminacao),
    path('tibl/buscairmao/', sitetibl.views.encontraIrmao),
    path('tibl/buscacontasbancarias/', sitetibl.views.encontraContasbancarias),
    path('tibl/buscaajudas/', sitetibl.views.encontraAjudas),
    path('tibl/buscacestas/', sitetibl.views.encontraCestas),
    path('tibl/buscaactividades/', sitetibl.views.encontraActividades),
    path('tibl/buscadepartamentos/', sitetibl.views.encontraDepartamentos),
    path('tibl/buscadizimosofertas/', sitetibl.views.encontraDizimosofertas),
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
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index1'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
