from django.core.management.base import BaseCommand

from sitetibl.models import SolicitacaoInterdepartamental
from sitetibl.views import _notificar_solicitacao


class Command(BaseCommand):
    help = 'Reenvia email e SMS de solicitações pendentes (sem duplicar notificações in-app).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--estado',
            default='pendente',
            help='Estado das solicitações a reenviar (default: pendente)',
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Reenviar apenas uma solicitação específica',
        )

    def handle(self, *args, **options):
        qs = SolicitacaoInterdepartamental.objects.select_related(
            'departamento_solicitante',
            'departamento_destinatario',
            'solicitante',
        )
        if options['id']:
            qs = qs.filter(pk=options['id'])
        else:
            qs = qs.filter(estado=options['estado'])

        total = qs.count()
        if not total:
            self.stdout.write(self.style.WARNING('Nenhuma solicitação encontrada.'))
            return

        for solicitacao in qs:
            self.stdout.write(
                f'Reenviando #{solicitacao.id} — {solicitacao.assunto} ({solicitacao.estado})'
            )
            _notificar_solicitacao(
                solicitacao,
                estado_anterior='',
                estado_novo=solicitacao.estado,
                responsavel=solicitacao.solicitante,
                apenas_externo=True,
            )

        self.stdout.write(self.style.SUCCESS(f'Concluído: {total} solicitação(ões) processada(s).'))
