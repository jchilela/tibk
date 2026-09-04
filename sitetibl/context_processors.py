from sitetibl.models import NotificacaoSistema


def notificacoes_nao_lidas(request):
    if hasattr(request, '_notificacoes_cache'):
        return request._notificacoes_cache

    if request.user.is_authenticated:
        count = NotificacaoSistema.objects.filter(
            destinatario=request.user, lida=False
        ).count()

        checklist_count = 0
        try:
            from sitetibl.models import NotificacaoChecklist, Irmao
            irmao = Irmao.objects.filter(user=request.user).first()
            if irmao:
                checklist_count = NotificacaoChecklist.objects.filter(
                    destinatario=irmao, lida=False
                ).count()
        except Exception:
            pass

        result = {
            'notificacoes_nao_lidas': count,
            'notificacoes_checklist_nao_lidas': checklist_count,
        }
    else:
        result = {'notificacoes_nao_lidas': 0, 'notificacoes_checklist_nao_lidas': 0}

    request._notificacoes_cache = result
    return result
