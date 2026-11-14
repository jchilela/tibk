"""PDF A4 do boletim (ReportLab)."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from boletim.textos import TEXTOS

VERDE = colors.HexColor('#1f5130')


def _p(texto):
    """Escapa o texto para o Paragraph e mantém as quebras de linha."""
    return escape(texto or '').replace('\n', '<br/>')


def gerar_pdf(ctx, cfg, lingua):
    t = TEXTOS[lingua]
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title=f"{ctx['titulo']} — {ctx['data_extenso']}", author=cfg['nome_igreja'],
    )
    base = getSampleStyleSheet()
    s_igreja = ParagraphStyle('igreja', parent=base['Title'], fontSize=15, leading=18, textColor=VERDE, spaceAfter=2)
    s_sub = ParagraphStyle('sub', parent=base['Normal'], alignment=TA_CENTER, fontSize=10, textColor=colors.grey)
    s_titulo = ParagraphStyle('titulo', parent=base['Heading2'], alignment=TA_CENTER, spaceBefore=6, spaceAfter=2)
    s_sec = ParagraphStyle('sec', parent=base['Heading3'], textColor=VERDE, spaceBefore=10, spaceAfter=4)
    s_txt = ParagraphStyle('txt', parent=base['Normal'], fontSize=10, leading=13)
    s_peq = ParagraphStyle('peq', parent=s_txt, fontSize=9, textColor=colors.HexColor('#444444'))

    h = []
    h.append(Paragraph(_p(cfg['nome_igreja']), s_igreja))
    if cfg['congregacao']:
        h.append(Paragraph(_p(cfg['congregacao']), s_sub))
    h.append(Paragraph(_p(ctx['titulo']), s_titulo))
    data = ctx['data_extenso'] + (f" · {ctx['hora_inicio']}" if ctx['hora_inicio'] else '')
    h.append(Paragraph(_p(data), s_sub))
    if ctx['tema']:
        h.append(Paragraph(f"<b>{_p(t['tema'])}:</b> {_p(ctx['tema'])}", s_sub))

    def tabela(linhas, larguras):
        tb = Table(linhas, colWidths=larguras)
        tb.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor('#dddddd')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return tb

    largura = A4[0] - 3.6 * cm

    if ctx['itens']:
        h.append(Paragraph(_p(t['ordem_culto']), s_sec))
        linhas = [[Paragraph(_p(i['titulo']), s_txt), Paragraph(_p(i['detalhe']), s_peq)] for i in ctx['itens']]
        h.append(tabela(linhas, [largura * 0.6, largura * 0.4]))

    if ctx['leitura_referencia'] or ctx['leitura_texto']:
        h.append(Paragraph(_p(t['leitura']), s_sec))
        if ctx['leitura_referencia']:
            h.append(Paragraph(f"<b>{_p(ctx['leitura_referencia'])}</b>", s_txt))
        if ctx['leitura_texto']:
            h.append(Paragraph(_p(ctx['leitura_texto']), s_txt))

    if ctx['hino_referencia'] or ctx['hino_letra']:
        h.append(Paragraph(_p(t['hino']), s_sec))
        if ctx['hino_referencia']:
            h.append(Paragraph(f"<b>{_p(ctx['hino_referencia'])}</b>", s_txt))
        if ctx['hino_letra']:
            h.append(Paragraph(_p(ctx['hino_letra']), s_txt))

    if ctx['escalas']:
        h.append(Paragraph(_p(t['escalas']), s_sec))
        linhas = [[Paragraph(_p(e['rotulo']), s_peq), Paragraph(_p(', '.join(e['nomes'])), s_txt)]
                  for e in ctx['escalas']]
        h.append(tabela(linhas, [largura * 0.4, largura * 0.6]))

    if ctx['anuncios']:
        h.append(Paragraph(_p(t['anuncios']), s_sec))
        for a in ctx['anuncios']:
            if a['titulo']:
                h.append(Paragraph(f"<b>{_p(a['titulo'])}</b>", s_txt))
            h.append(Paragraph(_p(a['texto']), s_txt))
            h.append(Spacer(1, 4))

    if ctx['programas']:
        h.append(Paragraph(_p(t['programas']), s_sec))
        linhas = [[Paragraph(_p(p['dia']), s_txt), Paragraph(_p(p['horario']), s_peq), Paragraph(_p(p['titulo']), s_txt)]
                  for p in ctx['programas']]
        h.append(tabela(linhas, [largura * 0.25, largura * 0.2, largura * 0.55]))

    if cfg['lideranca']:
        h.append(Paragraph(_p(t['lideranca']), s_sec))
        h.append(Paragraph(_p('\n'.join(cfg['lideranca'])), s_peq))

    if cfg['redes']:
        h.append(Spacer(1, 8))
        h.append(Paragraph(' · '.join(f"{_p(r['nome'])}: {_p(r['url'])}" for r in cfg['redes']), s_peq))

    doc.build(h)
    return buf.getvalue()
