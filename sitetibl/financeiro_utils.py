# sitetibl/financeiro_utils.py
"""
Utilitários para o Balanço Financeiro: cálculo de saldos por período
(semanal, mensal, trimestral, anual) do movimento geral de entradas/saídas
(banco e caixa). Inclui também a geração do relatório em Excel (.xlsx).
"""

from datetime import date
from decimal import Decimal
from io import BytesIO

from django.db.models import Sum
from django.db.models.functions import TruncWeek, TruncMonth, TruncQuarter, TruncYear

from .models import MOEDA, Entrada, Saida

PERIODO_TRUNC = {
    'semanal': TruncWeek,
    'mensal': TruncMonth,
    'trimestral': TruncQuarter,
    'anual': TruncYear,
}

PERIODOS_VALIDOS = list(PERIODO_TRUNC.keys())

MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]


def _label_periodo(periodo, dt):
    """Devolve um rótulo legível (pt) para o início do período `dt`."""
    if dt is None:
        return '-'
    if periodo == 'semanal':
        return f"Semana de {dt.strftime('%d/%m/%Y')}"
    if periodo == 'mensal':
        return f"{MESES_PT[dt.month]}/{dt.year}"
    if periodo == 'trimestral':
        trimestre = (dt.month - 1) // 3 + 1
        return f"{trimestre}º Trimestre/{dt.year}"
    if periodo == 'anual':
        return f"{dt.year}"
    return dt.strftime('%d/%m/%Y')


def _resolver_intervalo(params):
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


def _calcular_saldo_inicial(datainicio, moeda):
    """
    Calcula o saldo acumulado de todo o histórico ANTERIOR a `datainicio`
    (entradas gerais - saídas gerais), para que o saldo transite
    correctamente de um ano/período para o outro em vez de reiniciar em 0.
    """
    if not datainicio:
        return Decimal('0')

    filtro = {'data__lt': datainicio}
    if moeda:
        filtro['moeda'] = moeda

    total_entradas = (
        Entrada.objects.filter(**filtro).aggregate(total=Sum('valor'))['total']
        or Decimal('0')
    )
    total_saidas = (
        Saida.objects.filter(**filtro).aggregate(total=Sum('valor'))['total']
        or Decimal('0')
    )
    return total_entradas - total_saidas


def build_balanco_financeiro(params):
    """
    Constrói o contexto completo do Balanço Financeiro:
    - Entradas e Saídas gerais (banco + caixa) por período
    - Saldo do período e saldo acumulado (transitado entre períodos/anos)
    - Totais gerais
    """
    periodo = params.get('periodo', 'mensal').strip()
    if periodo not in PERIODOS_VALIDOS:
        periodo = 'mensal'
    trunc_class = PERIODO_TRUNC[periodo]

    moeda = params.get('moeda', '').strip()

    datainicio, datafim, ano = _resolver_intervalo(params)

    # ---- Filtros base -----------------------------------------------------
    filtro_movimento = {}
    if datainicio and datafim:
        filtro_movimento['data__range'] = [datainicio, datafim]
    if moeda:
        filtro_movimento['moeda'] = moeda

    # ---- Entradas gerais (banco + caixa) por período -----------------------
    entradas = (
        Entrada.objects
        .filter(**filtro_movimento)
        .annotate(periodo_dt=trunc_class('data'))
        .values('periodo_dt')
        .annotate(total=Sum('valor'))
    )

    # ---- Saídas gerais (banco + caixa) por período --------------------------
    saidas = (
        Saida.objects
        .filter(**filtro_movimento)
        .annotate(periodo_dt=trunc_class('data'))
        .values('periodo_dt')
        .annotate(total=Sum('valor'))
    )

    # ---- Consolidação por período -------------------------------------------
    periodos = {}

    def _get_bucket(periodo_dt):
        return periodos.setdefault(periodo_dt, {
            'entradas_gerais': Decimal('0'),
            'saidas_gerais': Decimal('0'),
        })

    for row in entradas:
        _get_bucket(row['periodo_dt'])['entradas_gerais'] += row['total'] or Decimal('0')
    for row in saidas:
        _get_bucket(row['periodo_dt'])['saidas_gerais'] += row['total'] or Decimal('0')

    # Saldo transitado de todo o histórico anterior ao início do período
    # filtrado — garante que o saldo acumulado nunca reinicia de um ano
    # para o outro.
    saldo_inicial = _calcular_saldo_inicial(datainicio, moeda)

    linhas = []
    saldo_acumulado = saldo_inicial
    for periodo_dt in sorted((p for p in periodos.keys() if p is not None)):
        bucket = periodos[periodo_dt]
        saldo_periodo = bucket['entradas_gerais'] - bucket['saidas_gerais']
        saldo_acumulado += saldo_periodo
        linhas.append({
            'periodo_dt': periodo_dt,
            'label': _label_periodo(periodo, periodo_dt),
            'entradas_gerais': bucket['entradas_gerais'],
            'saidas_gerais': bucket['saidas_gerais'],
            'saldo_periodo': saldo_periodo,
            'saldo_acumulado': saldo_acumulado,
        })

    # Mostrar do período mais recente para o mais antigo
    linhas_desc = list(reversed(linhas))

    total_entradas_gerais = sum((l['entradas_gerais'] for l in linhas), Decimal('0'))
    total_saidas_gerais = sum((l['saidas_gerais'] for l in linhas), Decimal('0'))
    saldo_geral = total_entradas_gerais - total_saidas_gerais
    # Saldo final = saldo transitado do histórico anterior + movimento do período filtrado.
    saldo_final = linhas[-1]['saldo_acumulado'] if linhas else saldo_inicial

    return {
        'periodo': periodo,
        'moeda': moeda,
        'moeda_choices': MOEDA,
        'ano': ano,
        'datainicio': str(datainicio) if datainicio else '',
        'datafim': str(datafim) if datafim else '',
        'linhas': linhas_desc,
        'total_entradas_gerais': total_entradas_gerais,
        'total_saidas_gerais': total_saidas_gerais,
        'saldo_geral': saldo_geral,
        'saldo_inicial': saldo_inicial,
        'saldo_final': saldo_final,
    }


def gerar_excel_balanco_financeiro(context):
    """Gera o Balanço Financeiro em formato .xlsx (openpyxl) e devolve um BytesIO."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    header_fill = PatternFill(start_color='1F3D1F', end_color='1F3D1F', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True)
    title_font = Font(bold=True, size=14)
    subtitle_font = Font(italic=True, size=10, color='555555')
    total_fill = PatternFill(start_color='D9EAD3', end_color='D9EAD3', fill_type='solid')
    total_font = Font(bold=True)
    thin = Side(style='thin', color='CCCCCC')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ---- Sheet: Resumo -------------------------------------------------
    ws = wb.active
    ws.title = 'Resumo'
    ws['A1'] = 'Balanço Financeiro'
    ws['A1'].font = title_font
    ws.merge_cells('A1:B1')

    periodo_label = {
        'semanal': 'Semanal', 'mensal': 'Mensal',
        'trimestral': 'Trimestral', 'anual': 'Anual',
    }.get(context['periodo'], context['periodo'])
    intervalo = (
        f"{context['datainicio']} a {context['datafim']}"
        if context['datainicio'] else 'Todos os registos'
    )
    ws['A2'] = f"Periodicidade: {periodo_label}  |  Intervalo: {intervalo}"
    ws['A2'].font = subtitle_font
    ws.merge_cells('A2:B2')

    resumo_rows = [
        ('Saldo Transitado (Anos/Períodos Anteriores)', context['saldo_inicial']),
        ('Total Entradas Gerais (Banco + Caixa)', context['total_entradas_gerais']),
        ('Total Saídas Gerais (Banco + Caixa)', context['total_saidas_gerais']),
        ('Movimento Líquido do Período', context['saldo_geral']),
        ('Saldo Final Transitado (Acumulado)', context['saldo_final']),
    ]

    row_idx = 4
    ws.cell(row=row_idx, column=1, value='Indicador').font = header_font
    ws.cell(row=row_idx, column=1).fill = header_fill
    ws.cell(row=row_idx, column=2, value='Valor').font = header_font
    ws.cell(row=row_idx, column=2).fill = header_fill
    row_idx += 1
    for label, valor in resumo_rows:
        ws.cell(row=row_idx, column=1, value=label).border = border
        cell = ws.cell(row=row_idx, column=2, value=float(valor))
        cell.number_format = '#,##0.00'
        cell.border = border
        if 'Saldo Final' in label:
            ws.cell(row=row_idx, column=1).font = total_font
            ws.cell(row=row_idx, column=1).fill = total_fill
            cell.font = total_font
            cell.fill = total_fill
        row_idx += 1

    ws.column_dimensions['A'].width = 42
    ws.column_dimensions['B'].width = 20

    # ---- Sheet: Detalhe por Período --------------------------------------
    ws2 = wb.create_sheet('Detalhe por Período')
    colunas = [
        'Período', 'Entradas Gerais', 'Saídas Gerais',
        'Saldo do Período', 'Saldo Acumulado',
    ]
    for col_idx, titulo in enumerate(colunas, start=1):
        cell = ws2.cell(row=1, column=col_idx, value=titulo)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = border

    # Escrever em ordem cronológica (mais antigo primeiro) no Excel
    linhas_cronologicas = list(reversed(context['linhas']))
    for row_offset, linha in enumerate(linhas_cronologicas, start=2):
        valores = [
            linha['label'], float(linha['entradas_gerais']), float(linha['saidas_gerais']),
            float(linha['saldo_periodo']), float(linha['saldo_acumulado']),
        ]
        for col_idx, valor in enumerate(valores, start=1):
            cell = ws2.cell(row=row_offset, column=col_idx, value=valor)
            cell.border = border
            if col_idx > 1:
                cell.number_format = '#,##0.00'

    for col_idx, titulo in enumerate(colunas, start=1):
        largura = 22 if col_idx == 1 else 18
        ws2.column_dimensions[get_column_letter(col_idx)].width = largura

    ws2.freeze_panes = 'A2'

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
