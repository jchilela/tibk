from sitetibl.models import NotificacaoSistema, Irmao, Departamento, Mandato


def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        count = NotificacaoSistema.objects.filter(
            destinatario=request.user, lida=False
        ).count()
        return {'notificacoes_nao_lidas': count}
    return {'notificacoes_nao_lidas': 0}


def pode_gerir_ocorrencias(user):
    """A gestão de ocorrências é restrita à liderança do Departamento de Segurança
    (Líder, Vice-Líder ou Secretário), além do grupo Administrador/superusers."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.groups.filter(name='Administrador').exists():
        return True

    irmao = Irmao.objects.filter(user=user).first()
    if not irmao:
        return False

    dept_seguranca = Departamento.objects.filter(designacao__icontains='segurança').first()
    if not dept_seguranca:
        return False

    if dept_seguranca.lider_departamento_id == irmao.id or dept_seguranca.vice_lider_departamento_id == irmao.id:
        return True

    return Mandato.objects.filter(
        irmao=irmao, departamento=dept_seguranca, funcao='secretario',
    ).exists()


def acesso_ocorrencias(request):
    return {'pode_gerir_ocorrencias': pode_gerir_ocorrencias(request.user)}
