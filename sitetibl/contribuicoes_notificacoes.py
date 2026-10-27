"""Notificações do Portal de Contribuições.

`notificar_membro_contribuicao`: email + SMS ao membro quando a área
financeira confirma ou rejeita uma contribuição por ele registada.

Os envios nunca devem quebrar o fluxo principal: todos os erros são
registados em log e ignorados.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from sitetibl.sms import enviar_sms

logger = logging.getLogger(__name__)

FROM_EMAIL = getattr(settings, 'EMAIL_HOST_USER', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tibl.ao')


def notificar_membro_contribuicao(contribuicao):
    """Envia email + SMS ao membro informando que a sua contribuição foi
    confirmada ou rejeitada pela área financeira."""
    try:
        irmao = contribuicao.irmao
        estado_display = contribuicao.get_estado_display()

        if irmao.email:
            html = render_to_string('emails/contribuicao_validada.html', {
                'contribuicao': contribuicao,
                'irmao': irmao,
                'estado_display': estado_display,
            })
            send_mail(
                subject=f'[TIBL] A sua contribuição foi {estado_display.lower()}',
                message=strip_tags(html),
                from_email=FROM_EMAIL,
                recipient_list=[irmao.email],
                html_message=html,
                fail_silently=True,
            )

        if irmao.telefone:
            sms_texto = (
                f'TIBL: A sua contribuicao de {contribuicao.valor_formatado} '
                f'({contribuicao.get_tipo_display()}) foi {estado_display.lower()}. '
                f'Consulte o portal para mais detalhes.'
            )
            enviar_sms([irmao.telefone], sms_texto)
    except Exception:
        logger.exception('Falha ao notificar membro sobre contribuição #%s', contribuicao.id)
