# sitetibl/ocorrencias_utils.py
"""
Utilitários para os Relatórios de Ocorrências: agregação por período
(semanal, mensal, trimestral, anual), contagens por categoria/estado,
e construção do contexto usado tanto na página HTML como no PDF.
"""

from datetime import date

from django.db.models import Count

from .financeiro_utils import PERIODO_TRUNC, PERIODOS_VALIDOS, _label_periodo
from .models import Ocorrencia, CATEGORIA_OCORRENCIA, ESTADO_OCORRENCIA


def _resolver_intervalo_ocorrencias(params):
    """Resolve (datainicio, datafim, ano_label) a partir dos parâmetros GET."""
    datainicio = params.get('datainicio', '').strip()
    datafim = params.get('datafim', '').strip()
    ano = params.get('ano', '').strip()

    if datainicio and datafim:
        return datainicio, datafim, ''

    if ano and ano != 'todos':
        try:
            ano_int = int(ano)
            return date(ano_int, 1, 1), date(ano_int, 12, 31), ano
        except ValueError:
            pass

    if ano == 'todos':
        return None, None, 'todos'

    hoje = date.today()
    return date(hoje.year, 1, 1), date(hoje.year, 12, 31), str(hoje.year)


def build_relatorio_ocorrencias(params):
    """
    Constrói o contexto completo do Relatório de Ocorrências:
    - Agregação por período (semanal/mensal/trimestral/anual)
    - Totais por categoria e por estado
    - Listagem detalhada das ocorrências no intervalo seleccionado
    """
    periodo = params.get('periodo', 'mensal').strip()
    if periodo not in PERIODOS_VALIDOS:
        periodo = 'mensal'

    datainicio, datafim, ano_label = _resolver_intervalo_ocorrencias(params)

    qs = Ocorrencia.objects.select_related('local', 'resolvido_por').all()
    if datainicio:
        qs = qs.filter(data_ocorrencia__gte=datainicio)
    if datafim:
        qs = qs.filter(data_ocorrencia__lte=datafim)

    trunc_fn = PERIODO_TRUNC[periodo]
    agregados_qs = (
        qs.exclude(data_ocorrencia__isnull=True)
          .annotate(periodo_dt=trunc_fn('data_ocorrencia'))
          .values('periodo_dt')
          .annotate(total=Count('id'))
          .order_by('periodo_dt')
    )
    agregados_periodo = [
        {'label': _label_periodo(periodo, item['periodo_dt']), 'total': item['total']}
        for item in agregados_qs
    ]

    por_categoria = list(
        qs.values('categoria').annotate(total=Count('id')).order_by('-total')
    )
    categoria_labels = dict(CATEGORIA_OCORRENCIA)
    for item in por_categoria:
        item['label'] = categoria_labels.get(item['categoria'], item['categoria'])

    por_estado = list(
        qs.values('estado').annotate(total=Count('id')).order_by('estado')
    )
    estado_labels = dict(ESTADO_OCORRENCIA)
    for item in por_estado:
        item['label'] = estado_labels.get(item['estado'], item['estado'])

    anos_disponiveis = sorted({
        d.year for d in Ocorrencia.objects
            .exclude(data_ocorrencia__isnull=True)
            .values_list('data_ocorrencia', flat=True)
    }, reverse=True)

    return {
        'periodo': periodo,
        'periodos_validos': PERIODOS_VALIDOS,
        'datainicio': datainicio,
        'datafim': datafim,
        'ano_label': ano_label,
        'anos_disponiveis': anos_disponiveis,
        'ocorrencias': qs.order_by('-data_ocorrencia', '-data_registo'),
        'total_geral': qs.count(),
        'total_pendentes': qs.filter(estado='pendente').count(),
        'total_em_analise': qs.filter(estado='em_analise').count(),
        'total_resolvidas': qs.filter(estado='resolvida').count(),
        'agregados_periodo': agregados_periodo,
        'por_categoria': por_categoria,
        'por_estado': por_estado,
    }
