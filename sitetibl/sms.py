import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SMS_URL = 'https://telcosms.co.ao/send_message'


def _normalizar_telefones(telefones):
    if isinstance(telefones, str):
        candidatos = [telefones]
    else:
        candidatos = telefones or []
    return list(dict.fromkeys(str(t).strip() for t in candidatos if t and str(t).strip()))


def enviar_sms(telefones, mensagem):
    """
    Envia SMS via TelcoSMS.
    Se TELCOSMS_TEST_PHONE estiver definido, redirecciona todos os SMS para esse número.
    Retorna True se pelo menos um envio foi bem-sucedido.
    """
    originais = _normalizar_telefones(telefones)
    if not originais:
        return False

    api_key = getattr(settings, 'TELCOSMS_API_KEY', '')
    if not api_key:
        logger.error('TELCOSMS_API_KEY não configurada — SMS não enviado.')
        return False

    test_phone = (getattr(settings, 'TELCOSMS_TEST_PHONE', '') or '').strip()
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

    ok = False
    for telefone in destinos:
        sms_data = {
            'message': {
                'api_key_app': api_key,
                'phone_number': telefone,
                'message_body': corpo,
            }
        }
        try:
            response = requests.post(SMS_URL, json=sms_data, timeout=10)
            if response.status_code == 200:
                logger.info('SMS enviado para %s', telefone)
                ok = True
            else:
                logger.error(
                    'Falha SMS para %s — status %s: %s',
                    telefone, response.status_code, response.text,
                )
        except requests.exceptions.RequestException as e:
            logger.error('Erro SMS para %s: %s', telefone, e)
    return ok
