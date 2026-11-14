"""Cache das páginas públicas do boletim.

Todas as chaves incluem uma «versão» global. Gravar um boletim, um anúncio,
a configuração, etc. muda a versão (ver ``signals.py``), o que torna
inválidas de uma só vez todas as entradas antigas, com qualquer backend de
cache (LocMem, Redis, ...), sem ser preciso apagar chaves por padrão.
"""
import time

from django.core.cache import cache

TTL = 300  # 5 minutos
CHAVE_VERSAO = 'boletim:versao'


def versao():
    v = cache.get(CHAVE_VERSAO)
    if v is None:
        v = time.time_ns()
        if not cache.add(CHAVE_VERSAO, v, None):
            v = cache.get(CHAVE_VERSAO) or v
    return v


def invalidar():
    # Valor sempre novo (e não reutilizável), mesmo que a chave tenha
    # sido despejada da cache entretanto.
    cache.set(CHAVE_VERSAO, time.time_ns(), None)


def chave(*partes):
    return 'boletim:{}:{}'.format(versao(), ':'.join(str(p) for p in partes))


def obter(*partes):
    return cache.get(chave(*partes))


def guardar(valor, *partes):
    cache.set(chave(*partes), valor, TTL)
