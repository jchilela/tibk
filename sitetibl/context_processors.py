from sitetibl.models import NotificacaoSistema


def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        count = NotificacaoSistema.objects.filter(
            destinatario=request.user, lida=False
        ).count()
        return {'notificacoes_nao_lidas': count}
    return {'notificacoes_nao_lidas': 0}
