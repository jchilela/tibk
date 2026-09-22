"""Notificações do Portal de Ocorrências.

- `notificar_lideres_nova_ocorrencia`: email + SMS à liderança do
  Departamento de Segurança (e Administradores) quando uma ocorrência
  é registada publicamente.
- `notificar_reportante_resposta`: email + SMS ao reportante quando a
  liderança actualiza o estado / adiciona nota de resolução.

Os envios nunca devem quebrar o fluxo principal: todos os erros são
registados em log e ignorados.
"""
import logging
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .sms import enviar_sms

logger = logging.getLogger(__name__)

FROM_EMAIL = getattr(settings, 'EMAIL_HOST_USER', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tibl.ao')


def _telefones_de(texto):
    """Divide um campo de telefone (pode conter vários números separados
    por vírgula, ponto-e-vírgula ou barra) numa lista de números."""
    if not texto:
        return []
    return [t.strip() for t in re.split(r'[,;/]', str(texto)) if t.strip()]


def _lideres_seguranca():
    """Devolve os Irmãos que compõem a liderança do Departamento de
    Segurança (Líder, Vice-Líder e Secretário) mais os utilizadores do
    grupo Administrador que tenham ficha de Irmão."""
    from .models import Departamento, Irmao, Mandato

    lideres = {}

    dept = Departamento.objects.filter(designacao__icontains='segurança').first()
    if dept:
        for irmao in (dept.lider_departamento, dept.vice_lider_departamento):
            if irmao:
                lideres[irmao.id] = irmao
        for mandato in Mandato.objects.filter(
            departamento=dept, funcao='secretario',
        ).select_related('irmao'):
            lideres[mandato.irmao_id] = mandato.irmao

    # Administradores com ficha de Irmão também recebem
    admin_users = User.objects.filter(groups__name='Administrador')
    for irmao in Irmao.objects.filter(user__in=admin_users):
        lideres[irmao.id] = irmao

    return list(lideres.values())


def _emails_lideres(lideres):
    emails = set()
    for irmao in lideres:
        if irmao.email:
            emails.add(irmao.email.strip())
        elif irmao.user_id and irmao.user.email:
            emails.add(irmao.user.email.strip())
    # Fallback: admins sem ficha de Irmão mas com email no User
    for user in User.objects.filter(groups__name='Administrador').exclude(email=''):
        emails.add(user.email.strip())
    return sorted(e for e in emails if e)


def _telefones_lideres(lideres):
    telefones = []
    for irmao in lideres:
        telefones.extend(_telefones_de(irmao.telefone))
    return list(dict.fromkeys(telefones))


def notificar_lideres_nova_ocorrencia(ocorrencia):
    """Envia email + SMS à liderança do Dept. de Segurança sobre uma
    nova ocorrência registada."""
    try:
        lideres = _lideres_seguranca()
        if not lideres:
            logger.warning('Nova ocorrência %s sem líderes para notificar.', ocorrencia.protocolo)
            return

        local = ocorrencia.local.designacao if ocorrencia.local else 'Não indicado'
        reportante = ocorrencia.nome_reportante or 'Anónimo'

        emails = _emails_lideres(lideres)
        if emails:
            html = render_to_string('emails/nova_ocorrencia.html', {
                'ocorrencia': ocorrencia,
                'local': local,
                'reportante': reportante,
            })
            send_mail(
                subject=f'[TIBL] Nova Ocorrência {ocorrencia.protocolo} — {ocorrencia.get_categoria_display()}',
                message=strip_tags(html),
                from_email=FROM_EMAIL,
                recipient_list=emails,
                html_message=html,
                fail_silently=True,
            )

        telefones = _telefones_lideres(lideres)
        if telefones:
            sms_texto = (
                f'TIBL: Nova ocorrencia {ocorrencia.protocolo} '
                f'({ocorrencia.get_categoria_display()}) em {local}. '
                f'Titulo: {ocorrencia.titulo[:80]}. Aceda ao portal de gestao.'
            )
            enviar_sms(telefones, sms_texto)
    except Exception:
        logger.exception('Falha ao notificar líderes sobre ocorrência %s', ocorrencia.protocolo)


def notificar_reportante_resposta(ocorrencia):
    """Envia email + SMS ao reportante quando a liderança responde
    (mudança de estado ou nota de resolução)."""
    try:
        estado = ocorrencia.get_estado_display()
        nome = ocorrencia.nome_reportante or 'Irmão(ã)/Visitante'

        if ocorrencia.email_reportante:
            html = render_to_string('emails/resposta_ocorrencia.html', {
                'ocorrencia': ocorrencia,
                'nome': nome,
                'estado': estado,
            })
            send_mail(
                subject=f'[TIBL] Actualização da Ocorrência {ocorrencia.protocolo} — {estado}',
                message=strip_tags(html),
                from_email=FROM_EMAIL,
                recipient_list=[ocorrencia.email_reportante],
                html_message=html,
                fail_silently=True,
            )

        if ocorrencia.telefone_reportante:
            sms_texto = (
                f'TIBL: A sua ocorrencia {ocorrencia.protocolo} foi actualizada para '
                f'"{estado}". Consulte o portal com o numero de protocolo.'
            )
            enviar_sms([ocorrencia.telefone_reportante], sms_texto)
    except Exception:
        logger.exception('Falha ao notificar reportante da ocorrência %s', ocorrencia.protocolo)
