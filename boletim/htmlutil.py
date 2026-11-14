"""HTML limitado para os textos do boletim (leitura, hino, notas, anúncios).

O editor grava etiquetas simples. Tudo o que não está na lista é descartado
antes de gravar, de mostrar e de ir para o PDF.
"""
import re
from html.parser import HTMLParser
from xml.sax.saxutils import escape

_ETIQUETA = re.compile(
    r'<\s*(p|br|strong|b|em|i|u|ul|ol|li|blockquote|h2|h3|a)\b',
    re.IGNORECASE,
)
_PERMITIDAS = {'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'ul', 'ol', 'li', 'blockquote', 'h2', 'h3', 'a'}
_VAZIAS = {'br'}
_BRUTAS = {'script', 'style'}
_QUEBRA = re.compile(r'(?:<br/>)+')


def parece_html(valor):
    return bool(valor and _ETIQUETA.search(valor))


def _href_ok(href):
    href = (href or '').strip()
    baixo = href.lower()
    if baixo.startswith(('javascript:', 'data:', 'vbscript:')):
        return ''
    if baixo.startswith(('http://', 'https://', 'mailto:')):
        return href
    return ''


def _visivel(html):
    texto = re.sub(r'<[^>]+>', '', html or '')
    return bool(texto.replace('\xa0', ' ').strip())


class _Limpador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []
        self.pilha = []
        self.saltar = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in _BRUTAS:
            self.saltar += 1
            return
        if self.saltar or tag not in _PERMITIDAS:
            return
        if tag == 'a':
            href = ''
            for nome, valor in attrs:
                if nome.lower() == 'href':
                    href = _href_ok(valor)
            if not href:
                self.pilha.append('')
                return
            self.partes.append(
                f'<a href="{escape(href, {"\"": "&quot;"})}" rel="noopener noreferrer" target="_blank">'
            )
            self.pilha.append('a')
            return
        if tag == 'br':
            self.partes.append('<br>')
            return
        self.partes.append(f'<{tag}>')
        self.pilha.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _BRUTAS:
            if self.saltar:
                self.saltar -= 1
            return
        if self.saltar or tag in _VAZIAS or tag not in _PERMITIDAS:
            return
        if tag == 'a':
            self._fechar('a')
            return
        self._fechar(tag)

    def handle_data(self, data):
        if self.saltar or not data:
            return
        self.partes.append(escape(data))

    def handle_entityref(self, name):
        return

    def handle_charref(self, name):
        return

    def _fechar(self, tag):
        if tag not in self.pilha:
            return
        while self.pilha:
            aberto = self.pilha.pop()
            if aberto:
                self.partes.append(f'</{aberto}>')
            if aberto == tag:
                break

    def fechar_resto(self):
        while self.pilha:
            aberto = self.pilha.pop()
            if aberto:
                self.partes.append(f'</{aberto}>')

    def resultado(self):
        self.fechar_resto()
        return ''.join(self.partes).strip()


def sanitizar_campo(valor):
    """Devolve texto simples intacto, ou HTML já limpo."""
    if valor is None:
        return ''
    texto = str(valor).replace('\r\n', '\n').replace('\r', '\n').strip()
    if not texto or not parece_html(texto):
        return texto
    parser = _Limpador()
    parser.feed(texto)
    parser.close()
    limpo = parser.resultado()
    if not _visivel(limpo):
        return ''
    return limpo


class _ParaPdf(HTMLParser):
    """Converte o HTML permitido em marcações que o ReportLab aceita."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []
        self.pilha = []

    def _quebra(self):
        if self.partes and not ''.join(self.partes).endswith('<br/>'):
            self.partes.append('<br/>')

    def _abrir(self, marca, token):
        self.partes.append(marca)
        self.pilha.append(token)

    def _fechar(self, token):
        if token not in self.pilha:
            return
        while self.pilha:
            aberto = self.pilha.pop()
            if aberto == 'b':
                self.partes.append('</b>')
            elif aberto == 'i':
                self.partes.append('</i>')
            elif aberto == 'u':
                self.partes.append('</u>')
            elif aberto == 'a':
                self.partes.append('</a>')
            if aberto == token:
                break

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ('p', 'div', 'ul', 'ol', 'blockquote'):
            self._quebra()
            if tag == 'blockquote':
                self._abrir('<i>', 'i')
            else:
                self.pilha.append('')
        elif tag in ('h2', 'h3'):
            self._quebra()
            self._abrir('<b>', 'b')
        elif tag == 'br':
            self.partes.append('<br/>')
        elif tag == 'li':
            self._quebra()
            self.partes.append('- ')
            self.pilha.append('')
        elif tag in ('strong', 'b'):
            self._abrir('<b>', 'b')
        elif tag in ('em', 'i'):
            self._abrir('<i>', 'i')
        elif tag == 'u':
            self._abrir('<u>', 'u')
        elif tag == 'a':
            href = ''
            for nome, valor in attrs:
                if nome.lower() == 'href':
                    href = valor or ''
            self._abrir(f'<a href="{escape(href, {"\"": "&quot;"})}">', 'a')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ('strong', 'b', 'h2', 'h3'):
            self._fechar('b')
        elif tag in ('em', 'i', 'blockquote'):
            self._fechar('i')
        elif tag == 'u':
            self._fechar('u')
        elif tag == 'a':
            self._fechar('a')
        elif tag in ('p', 'div', 'li', 'ul', 'ol'):
            if self.pilha and self.pilha[-1] == '':
                self.pilha.pop()
            self._quebra()

    def handle_data(self, data):
        if data:
            self.partes.append(escape(data))

    def resultado(self):
        vistos = 0
        while self.pilha and vistos < 40:
            vistos += 1
            antes = len(self.pilha)
            self._fechar(self.pilha[-1] or '')
            if self.pilha and self.pilha[-1] == '':
                self.pilha.pop()
            if len(self.pilha) >= antes:
                self.pilha.pop()
        texto = ''.join(self.partes)
        texto = _QUEBRA.sub(lambda m: '<br/><br/>' if len(m.group(0)) > len('<br/>') else '<br/>', texto)
        texto = re.sub(r'^(?:<br/>)+', '', texto)
        texto = re.sub(r'(?:<br/>)+$', '', texto)
        return texto


def para_pdf(valor):
    if not valor:
        return ''
    if not parece_html(valor):
        return escape(str(valor)).replace('\n', '<br/>')
    parser = _ParaPdf()
    parser.feed(sanitizar_campo(valor))
    parser.close()
    return parser.resultado()
