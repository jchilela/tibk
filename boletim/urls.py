from datetime import date

from django.urls import path, register_converter

from boletim import views_gestao, views_publicas


class DataISOConverter:
    regex = r'\d{4}-\d{2}-\d{2}'

    def to_python(self, valor):
        return date.fromisoformat(valor)  # ValueError → rota não corresponde (404)

    def to_url(self, valor):
        return valor.isoformat() if isinstance(valor, date) else str(valor)


register_converter(DataISOConverter, 'dataiso')

app_name = 'boletim'

urlpatterns = [
    # ── Público (sem login) ──
    path('', views_publicas.boletim_actual, name='actual'),
    path('arquivo/', views_publicas.arquivo, name='arquivo'),
    path('visitante/', views_publicas.visitante, name='visitante'),
    path('oracao/', views_publicas.oracao, name='oracao'),
    path('anuncio/<int:pk>.ics', views_publicas.anuncio_ics, name='anuncio_ics'),
    path('<dataiso:data>/', views_publicas.boletim_por_data, name='data'),
    path('<dataiso:data>/pdf/', views_publicas.boletim_pdf, name='pdf'),

    # ── Gestão (com login e permissões) ──
    path('gestao/', views_gestao.lista, name='gestao_lista'),
    path('gestao/novo/', views_gestao.novo, name='gestao_novo'),
    path('gestao/<int:pk>/editar/', views_gestao.editar, name='gestao_editar'),
    path('gestao/<int:pk>/pre-visualizar/', views_gestao.pre_visualizar, name='gestao_preview'),
    path('gestao/<int:pk>/publicar/', views_gestao.publicar, name='gestao_publicar'),
    path('gestao/anuncios/novo/', views_gestao.anuncio_novo, name='gestao_anuncio_novo'),
    path('gestao/anuncios/<int:pk>/editar/', views_gestao.anuncio_editar, name='gestao_anuncio_editar'),
    path('gestao/oracao/', views_gestao.oracao_lista, name='gestao_oracao_lista'),
    path('gestao/oracao/<int:pk>/', views_gestao.oracao_detalhe, name='gestao_oracao_detalhe'),
]
