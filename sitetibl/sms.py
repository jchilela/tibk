import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SMS_URL = 'https://api.strongx.it.ao/v1/sms/send'


def _normalizar_telefones(telefones):
    if isinstance(telefones, str):
        candidatos = [telefones]
    else:
        candidatos = telefones or []
    return list(dict.fromkeys(str(t).strip() for t in candidatos if t and str(t).strip()))


def enviar_sms(telefones, mensagem):
    """
    Envia SMS via StrongX.
    Se STRONGX_TEST_PHONE estiver definido, redirecciona todos os SMS para esse número.
    Retorna True se pelo menos um envio foi bem-sucedido.
    """
    originais = _normalizar_telefones(telefones)
    if not originais:
        return False

    api_key = getattr(settings, 'STRONGX_API_KEY', '')
    if not api_key:
        logger.error('STRONGX_API_KEY não configurada — SMS não enviado.')
        return False

    app_id = getattr(settings, 'STRONGX_APP_ID', '')
    if not app_id:
        logger.error('STRONGX_APP_ID não configurado — SMS não enviado.')
        return False

    test_phone = (getattr(settings, 'STRONGX_TEST_PHONE', '') or '').strip()
    if test_phone:
        if len(originais) == 1:
            prefix = f'[TESTE p/ {originais[0]}] '
        else:
            amostra = ', '.join(originais[:5])
            if len(originais) > 5:
                amostra += f'...+{len(originais) - 5}'
            prefix = f'[TESTE ({len(originais)} dest.) p/ {amostra}] '
        destinos = [test_phone]
        corpo = prefix + mensagem
        logger.info('SMS em modo teste — redireccionado para %s', test_phone)
    else:
        destinos = originais
        corpo = mensagem

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    ok = False
    for telefone in destinos:
        payload = {
            'to': telefone,
            'message': corpo,
            'applicationId': app_id,
        }
        try:
            response = requests.post(SMS_URL, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info('SMS enviado para %s', telefone)
                ok = True
            else:
                try:
                    erro = response.json()
                    codigo = erro.get('error', 'erro_desconhecido')
                    detalhe = erro.get('message', response.text)
                except Exception:
                    codigo = 'erro_desconhecido'
                    detalhe = response.text
                logger.error(
                    'Falha SMS para %s — status %s [%s]: %s',
                    telefone, response.status_code, codigo, detalhe,
                )
        except requests.exceptions.RequestException as e:
            logger.error('Erro de ligação SMS para %s: %s', telefone, e)
    return ok
