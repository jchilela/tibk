"""Ficheiro iCalendar (.ics) para um anúncio ligado a uma actividade."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from django.conf import settings


def _escapar(texto):
    return (texto or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,') \
        .replace('\r\n', '\\n').replace('\n', '\\n')


def _dobrar(linha):
    """Divide linhas com mais de 75 octetos (RFC 5545, 3.1)."""
    dados = linha.encode('utf-8')
    if len(dados) <= 75:
        return linha
    partes, actual = [], b''
    for ch in linha:
        b = ch.encode('utf-8')
        limite = 75 if not partes else 74
        if len(actual) + len(b) > limite:
            partes.append(actual.decode('utf-8'))
            actual = b''
        actual += b
    partes.append(actual.decode('utf-8'))
    return '\r\n '.join(partes)


def _utc(d, h):
    local = datetime.combine(d, h).replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
    return local.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def gerar_ics(anuncio, titulo, descricao, dominio):
    act = anuncio.actividade
    inicio = _utc(act.data, act.inicio)
    if act.fim and act.fim > act.inicio:
        fim = _utc(act.data, act.fim)
    else:
        fim = _utc(act.data, (datetime.combine(act.data, act.inicio) + timedelta(hours=1)).time())
    local = act.localactividade.designacao if act.localactividade_id else ''
    linhas = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//TIBL//Boletim Digital//PT',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        f'UID:anuncio-{anuncio.pk}@{dominio}',
        'DTSTAMP:' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
        f'DTSTART:{inicio}',
        f'DTEND:{fim}',
        'SUMMARY:' + _escapar(titulo or str(act.designacao)),
    ]
    if descricao:
        linhas.append('DESCRIPTION:' + _escapar(descricao))
    if local:
        linhas.append('LOCATION:' + _escapar(local))
    linhas += ['END:VEVENT', 'END:VCALENDAR']
    return '\r\n'.join(_dobrar(l) for l in linhas) + '\r\n'
