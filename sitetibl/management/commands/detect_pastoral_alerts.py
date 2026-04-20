"""
Management command: detect_pastoral_alerts
Detecta sinais de risco pastoral e gera alertas automaticamente.
Idempotente — safe to run N vezes sem duplicar alertas.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Max, Avg, Q
from sitetibl.models import (
    Irmao, Escala, Actividade, AlertaPastoral, CasoPastoral,
    RelatorioSemanalCelula, Dizimooferta, Sitio, VisitanteRecorrente,
)


class Command(BaseCommand):
    help = 'Detecta sinais de risco pastoral e gera alertas automaticamente'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Mostra alertas sem gravar')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        total = 0

        total += self._detectar_inactividade(now, dry_run)
        total += self._detectar_novos_sem_acompanhamento(now, dry_run)
        total += self._detectar_sem_celula(dry_run)
        total += self._detectar_ausencia_dizimo(now, dry_run)
        total += self._detectar_aniversarios(now, dry_run)
        total += self._detectar_visitantes_recorrentes(dry_run)
        total += self._detectar_queda_celula(now, dry_run)

        self.stdout.write(self.style.SUCCESS(f'Total alertas gerados: {total}'))

    def _alerta_existe(self, tipo, membro=None, celula=None):
        """Verifica se já existe alerta activo do mesmo tipo."""
        qs = AlertaPastoral.objects.filter(
            tipo=tipo,
        ).exclude(estado__in=['resolvido', 'ignorado'])
        if membro:
            qs = qs.filter(membro=membro)
        if celula:
            qs = qs.filter(celula=celula)
        return qs.exists()

    def _criar_alerta(self, dry_run, **kwargs):
        if dry_run:
            self.stdout.write(f'  [DRY-RUN] {kwargs.get("titulo", "?")}')
            return 1
        AlertaPastoral.objects.create(**kwargs)
        self.stdout.write(f'  ✓ {kwargs.get("titulo", "?")}')
        return 1

    def _detectar_inactividade(self, now, dry_run):
        """Membros sem participação em escalas nos últimos 60 dias."""
        self.stdout.write('── Verificando inactividade...')
        limite = now - timedelta(days=60)
        count = 0

        irmaos = Irmao.objects.filter(activo='activo')
        for irmao in irmaos:
            ultima = Escala.objects.filter(
                irmao=irmao,
                actividade__data__gte=limite,
            ).exists()
            if not ultima and not self._alerta_existe('inactividade', membro=irmao):
                # Calcular dias de inactividade
                ultima_data = Escala.objects.filter(irmao=irmao).aggregate(
                    ultima=Max('actividade__data')
                )['ultima']
                dias = (now.date() - ultima_data).days if ultima_data else 999

                prioridade = 'alta' if dias > 90 else 'normal'
                count += self._criar_alerta(dry_run,
                    membro=irmao,
                    tipo='inactividade',
                    titulo=f'{irmao.nome} {irmao.apelido} — Inactivo há {dias} dias',
                    descricao=f'Membro sem participação em actividades há {dias} dias.',
                    dados_json={'dias_inactivo': dias, 'ultima_actividade': str(ultima_data) if ultima_data else None},
                    gerado_automaticamente=True,
                )
        self.stdout.write(f'  Inactividade: {count} alertas')
        return count

    def _detectar_novos_sem_acompanhamento(self, now, dry_run):
        """Novos membros (>30 dias, não baptizados) sem caso de integração."""
        self.stdout.write('── Verificando novos sem acompanhamento...')
        limite = now - timedelta(days=30)
        count = 0

        novos = Irmao.objects.filter(
            activo='activo',
            data_criacao__lt=limite,
            batizado='nao',
        )
        for irmao in novos:
            tem_caso = CasoPastoral.objects.filter(
                membro=irmao,
                tipo='integracao',
            ).exclude(estado='encerrado').exists()
            if not tem_caso and not self._alerta_existe('novo_sem_acompanhamento', membro=irmao):
                dias = (now.date() - irmao.data_criacao.date()).days if irmao.data_criacao else 0
                count += self._criar_alerta(dry_run,
                    membro=irmao,
                    tipo='novo_sem_acompanhamento',
                    titulo=f'{irmao.nome} {irmao.apelido} — Novo convertido sem acompanhamento',
                    descricao=f'Registado há {dias} dias, não baptizado, sem caso de integração.',
                    dados_json={'dias_desde_registo': dias},
                    gerado_automaticamente=True,
                )
        self.stdout.write(f'  Novos sem acompanhamento: {count} alertas')
        return count

    def _detectar_sem_celula(self, dry_run):
        """Membros baptizados sem célula atribuída."""
        self.stdout.write('── Verificando membros sem célula...')
        count = 0

        sem_celula = Irmao.objects.filter(
            activo='activo',
            batizado='sim',
            celula__isnull=True,
        )
        for irmao in sem_celula:
            if not self._alerta_existe('sem_celula', membro=irmao):
                count += self._criar_alerta(dry_run,
                    membro=irmao,
                    tipo='sem_celula',
                    titulo=f'{irmao.nome} {irmao.apelido} — Sem célula atribuída',
                    descricao='Membro baptizado sem célula atribuída.',
                    gerado_automaticamente=True,
                )
        self.stdout.write(f'  Sem célula: {count} alertas')
        return count

    def _detectar_ausencia_dizimo(self, now, dry_run):
        """Membros dizimistas sem dízimo há mais de 90 dias."""
        self.stdout.write('── Verificando ausência de dízimo...')
        limite = now - timedelta(days=90)
        count = 0

        dizimistas = Irmao.objects.filter(
            activo='activo',
            dizimista='sim',
        )
        for irmao in dizimistas:
            tem_dizimo = Dizimooferta.objects.filter(
                irmao=irmao,
                data__gte=limite.date(),
            ).exists()
            if not tem_dizimo and not self._alerta_existe('ausencia_dizimo', membro=irmao):
                ultimo = Dizimooferta.objects.filter(irmao=irmao).aggregate(
                    ultimo=Max('data')
                )['ultimo']
                dias = (now.date() - ultimo).days if ultimo else 999
                count += self._criar_alerta(dry_run,
                    membro=irmao,
                    tipo='ausencia_dizimo',
                    titulo=f'{irmao.nome} {irmao.apelido} — Sem dízimo há {dias} dias',
                    descricao=f'Membro marcado como dizimista mas sem registo de dízimo há {dias} dias.',
                    dados_json={'dias_sem_dizimo': dias, 'ultimo_dizimo': str(ultimo) if ultimo else None},
                    gerado_automaticamente=True,
                )
        self.stdout.write(f'  Ausência dízimo: {count} alertas')
        return count

    def _detectar_aniversarios(self, now, dry_run):
        """Aniversariantes nos próximos 7 dias."""
        self.stdout.write('── Verificando aniversários...')
        count = 0
        hoje = now.date()

        irmaos = Irmao.objects.filter(activo='activo').exclude(datanascimento__isnull=True)
        for irmao in irmaos:
            try:
                aniv = irmao.datanascimento.replace(year=hoje.year)
            except ValueError:
                continue
            if aniv < hoje:
                aniv = aniv.replace(year=hoje.year + 1)
            diff = (aniv - hoje).days
            if 0 <= diff <= 7:
                if not self._alerta_existe('aniversario', membro=irmao):
                    idade = hoje.year - irmao.datanascimento.year
                    if aniv.month < irmao.datanascimento.month or (aniv.month == irmao.datanascimento.month and aniv.day < irmao.datanascimento.day):
                        idade -= 1
                    count += self._criar_alerta(dry_run,
                        membro=irmao,
                        tipo='aniversario',
                        titulo=f'{irmao.nome} {irmao.apelido} — Aniversário em {diff} dias ({idade} anos)',
                        descricao=f'Aniversário a {aniv.strftime("%d/%m")}. Contactar para felicitação pastoral.',
                        dados_json={'data_aniversario': str(aniv), 'idade': idade, 'dias_faltam': diff},
                        gerado_automaticamente=True,
                    )
        self.stdout.write(f'  Aniversários: {count} alertas')
        return count

    def _detectar_visitantes_recorrentes(self, dry_run):
        """Visitantes com >=3 visitas ainda em estado 'visitante'."""
        self.stdout.write('── Verificando visitantes recorrentes...')
        count = 0

        visitantes = VisitanteRecorrente.objects.filter(
            estado='visitante',
            numero_visitas__gte=3,
        )
        for v in visitantes:
            if not self._alerta_existe('visitante_recorrente', celula=v.celula):
                count += self._criar_alerta(dry_run,
                    celula=v.celula,
                    tipo='visitante_recorrente',
                    titulo=f'Visitante recorrente: {v.nome} — {v.numero_visitas} visitas',
                    descricao=f'{v.nome} visitou a célula {v.celula} {v.numero_visitas} vezes e ainda não foi integrado.',
                    dados_json={'visitante_nome': v.nome, 'visitas': v.numero_visitas},
                    gerado_automaticamente=True,
                )
        self.stdout.write(f'  Visitantes recorrentes: {count} alertas')
        return count

    def _detectar_queda_celula(self, now, dry_run):
        """Células com queda >30% na participação (4 semanas recentes vs 4 semanas anteriores)."""
        self.stdout.write('── Verificando queda de participação em células...')
        count = 0
        hoje = now.date()
        fim_recente = hoje
        inicio_recente = hoje - timedelta(weeks=4)
        fim_anterior = inicio_recente
        inicio_anterior = inicio_recente - timedelta(weeks=4)

        celulas = Sitio.objects.filter(tipo=2)
        for celula in celulas:
            recente = RelatorioSemanalCelula.objects.filter(
                celula=celula,
                data__range=(inicio_recente, fim_recente),
            ).aggregate(media=Avg('numero_participantes'))['media']

            anterior = RelatorioSemanalCelula.objects.filter(
                celula=celula,
                data__range=(inicio_anterior, fim_anterior),
            ).aggregate(media=Avg('numero_participantes'))['media']

            if anterior and recente and anterior > 0:
                queda = ((anterior - recente) / anterior) * 100
                if queda >= 30 and not self._alerta_existe('queda_celula', celula=celula):
                    count += self._criar_alerta(dry_run,
                        celula=celula,
                        tipo='queda_celula',
                        titulo=f'Célula {celula} — Queda de {queda:.0f}% na participação',
                        descricao=f'Média de participantes caiu de {anterior:.1f} para {recente:.1f} (queda de {queda:.0f}%).',
                        dados_json={'media_anterior': round(anterior, 1), 'media_recente': round(recente, 1), 'queda_percentual': round(queda, 1)},
                        gerado_automaticamente=True,
                    )
        self.stdout.write(f'  Queda células: {count} alertas')
        return count
