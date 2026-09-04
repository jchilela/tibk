from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Verifica checklists recorrentes e gera notificações para responsáveis.'

    def handle(self, *args, **options):
        from sitetibl.models import ChecklistActividade, NotificacaoChecklist

        hoje = timezone.now().date()
        agora = timezone.now()
        amanha = hoje + timedelta(days=1)
        notificacoes_criadas = 0

        checklists = ChecklistActividade.objects.filter(
            notificar_responsaveis=True
        ).select_related('departamento', 'actividade').prefetch_related('items__responsavel')

        for ckl in checklists:
            # 1. Checklist disponível (recorrência)
            if ckl.recorrencia != 'unica' and ckl.deve_gerar_hoje():
                # Evita duplicar no mesmo dia
                ja_notificou_hoje = NotificacaoChecklist.objects.filter(
                    checklist=ckl,
                    tipo='disponivel',
                    data_criacao__date=hoje,
                ).exists()

                if not ja_notificou_hoje:
                    pendentes = ckl.items.filter(concluido=False).count()
                    total = ckl.total_items

                    responsaveis = set()
                    for item in ckl.items.all():
                        if item.responsavel:
                            responsaveis.add(item.responsavel)
                    # Se não há responsáveis específicos, notificar líderes do departamento
                    if not responsaveis and ckl.departamento:
                        if ckl.departamento.lider_departamento:
                            responsaveis.add(ckl.departamento.lider_departamento)
                        if ckl.departamento.vice_lider_departamento:
                            responsaveis.add(ckl.departamento.vice_lider_departamento)

                    for resp in responsaveis:
                        NotificacaoChecklist.objects.create(
                            destinatario=resp,
                            checklist=ckl,
                            tipo='disponivel',
                            titulo=f'Checklist de preparação — {ckl.departamento}',
                            mensagem=(
                                f'A checklist de {ckl.departamento} para '
                                f'{ckl.actividade} está disponível.\n'
                                f'{pendentes} de {total} tarefas pendentes.'
                            ),
                        )
                        notificacoes_criadas += 1

                    ckl.ultima_geracao = agora
                    ckl.save(update_fields=['ultima_geracao'])

            # 2. Tarefas atrasadas (concluído=False e data da actividade já passou)
            data_actividade = ckl.actividade.data
            if data_actividade < hoje:
                for item in ckl.items.filter(concluido=False, responsavel__isnull=False):
                    ja_notificado = NotificacaoChecklist.objects.filter(
                        item=item,
                        tipo='atrasada',
                        data_criacao__date=hoje,
                    ).exists()
                    if not ja_notificado:
                        NotificacaoChecklist.objects.create(
                            destinatario=item.responsavel,
                            checklist=ckl,
                            item=item,
                            tipo='atrasada',
                            titulo=f'Tarefa atrasada: {item.descricao}',
                            mensagem=(
                                f'A tarefa "{item.descricao}" na checklist de '
                                f'{ckl.departamento} para {ckl.actividade} '
                                f'está atrasada. A actividade era em '
                                f'{data_actividade.strftime("%d/%m/%Y")}.'
                            ),
                        )
                        notificacoes_criadas += 1

            # 3. Tarefas próximas do prazo (actividade é amanhã)
            if data_actividade == amanha:
                for item in ckl.items.filter(concluido=False, responsavel__isnull=False):
                    ja_notificado = NotificacaoChecklist.objects.filter(
                        item=item,
                        tipo='proxima_prazo',
                        data_criacao__date=hoje,
                    ).exists()
                    if not ja_notificado:
                        NotificacaoChecklist.objects.create(
                            destinatario=item.responsavel,
                            checklist=ckl,
                            item=item,
                            tipo='proxima_prazo',
                            titulo=f'Tarefa próxima do prazo: {item.descricao}',
                            mensagem=(
                                f'A tarefa "{item.descricao}" na checklist de '
                                f'{ckl.departamento} deve ser concluída até amanhã '
                                f'({data_actividade.strftime("%d/%m/%Y")}).'
                            ),
                        )
                        notificacoes_criadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Notificações processadas: {notificacoes_criadas} criadas.'
            )
        )
