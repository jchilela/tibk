from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        'Popula configuracao essencial: grupos, permissoes e provincias/municipios '
        '(idempotente).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-groups',
            action='store_true',
            help='Nao cria/atualiza grupos e permissoes.',
        )
        parser.add_argument(
            '--skip-provincias',
            action='store_true',
            help='Nao executa seed_provincias.',
        )

    def handle(self, *args, **options):
        if not options['skip_groups']:
            self.seed_groups()

        if not options['skip_provincias']:
            call_command('seed_provincias')

        self.stdout.write(self.style.SUCCESS('Seed de configuracao essencial concluido.'))

    def seed_groups(self):
        group_names = [
            'Administrador',
            'Pastor',
            'Financeiro',
            'Secretaria',
            'Líder de Departamento',
            'Vice-Líder de Departamento',
            'Líder de Célula',
            'Membros Baptizados',
            'Membro Geral',
        ]

        created_count = 0
        for name in group_names:
            _, created = Group.objects.get_or_create(name=name)
            if created:
                created_count += 1

        self.stdout.write(
            f'Grupos criados: {created_count} | totais verificados: {len(group_names)}'
        )

        self._assign_group_permissions()

    def _assign_group_permissions(self):
        app = 'sitetibl'
        crud = ['add', 'change', 'delete', 'view']

        admin_grp = Group.objects.get(name='Administrador')
        all_perms = Permission.objects.filter(content_type__app_label=app)
        admin_grp.permissions.set(all_perms)
        self.stdout.write(f'Administrador: {all_perms.count()} permissoes atribuidas')

        pastor_grp = Group.objects.get(name='Pastor')
        pastor_perms = self._perms_for(app, [
            'pessoa', 'irmao', 'mandato', 'actividade', 'escala',
            'relatoriosemanalcelula', 'conteudoensino', 'enviomensagem',
            'anuncio', 'ajuda', 'pedidosaida',
        ], crud)
        pastor_perms |= self._perms_for(app, ['departamento'], ['view', 'change'])
        pastor_perms |= self._perms_for(app, [
            'sitio', 'dizimooferta', 'entrada', 'saida',
            'banco', 'contabancaria',
            'orcamentodepartamento', 'inventariopatrimonio',
            'cestabasica', 'pagamentoservico',
        ], ['view'])
        pastor_grp.permissions.set(pastor_perms)
        self.stdout.write(f'Pastor: {pastor_perms.count()} permissoes atribuidas')

        fin_grp = Group.objects.get(name='Financeiro')
        fin_perms = self._perms_for(app, [
            'dizimooferta', 'entrada', 'saida',
            'contabancaria', 'banco',
            'pedidosaida', 'orcamentodepartamento', 'pagamentoservico',
        ], crud)
        fin_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'actividade', 'departamento',
            'inventariopatrimonio',
        ], ['view'])
        fin_grp.permissions.set(fin_perms)
        self.stdout.write(f'Financeiro: {fin_perms.count()} permissoes atribuidas')

        sec_grp = Group.objects.get(name='Secretaria')
        sec_perms = self._perms_for(app, [
            'irmao', 'pessoa', 'actividade', 'escala', 'mandato',
            'departamento', 'sitio', 'relatoriosemanalcelula',
            'conteudoensino', 'enviomensagem', 'anuncio',
            'inventariopatrimonio', 'cestabasica', 'ajuda',
        ], crud)
        sec_perms |= self._perms_for(app, [
            'dizimooferta', 'entrada', 'pedidosaida',
        ], ['view'])
        sec_grp.permissions.set(sec_perms)
        self.stdout.write(f'Secretaria: {sec_perms.count()} permissoes atribuidas')

        ld_grp = Group.objects.get(name='Líder de Departamento')
        ld_perms = self._perms_for(app, ['actividade', 'escala', 'anuncio', 'enviomensagem'], crud)
        ld_perms |= self._perms_for(app, ['mandato'], ['add', 'view'])
        ld_perms |= self._perms_for(app, ['departamento'], ['view'])
        ld_perms |= self._perms_for(app, ['funcao'], crud)
        ld_perms |= self._perms_for(app, ['pedidosaida'], ['add', 'view'])
        ld_perms |= self._perms_for(app, ['irmao', 'pessoa', 'sitio', 'conteudoensino'], ['view'])
        ld_grp.permissions.set(ld_perms)
        self.stdout.write(f'Líder de Departamento: {ld_perms.count()} permissoes atribuidas')

        vld_grp = Group.objects.get(name='Vice-Líder de Departamento')
        vld_perms = self._perms_for(app, ['actividade', 'escala', 'anuncio'], crud)
        vld_perms |= self._perms_for(app, ['mandato'], ['add', 'view'])
        vld_perms |= self._perms_for(app, ['pedidosaida'], ['add', 'view'])
        vld_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'sitio', 'departamento', 'conteudoensino', 'enviomensagem',
        ], ['view'])
        vld_perms |= self._perms_for(app, ['funcao'], ['add', 'view'])
        vld_grp.permissions.set(vld_perms)
        self.stdout.write(f'Vice-Líder de Departamento: {vld_perms.count()} permissoes atribuidas')

        lc_grp = Group.objects.get(name='Líder de Célula')
        lc_perms = self._perms_for(app, ['relatoriosemanalcelula'], ['add', 'change', 'view'])
        lc_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'sitio', 'actividade', 'departamento', 'conteudoensino',
        ], ['view'])
        lc_grp.permissions.set(lc_perms)
        self.stdout.write(f'Líder de Célula: {lc_perms.count()} permissoes atribuidas')

        mb_grp = Group.objects.get(name='Membros Baptizados')
        mb_perms = self._perms_for(app, [
            'irmao', 'pessoa', 'actividade', 'escala', 'departamento',
            'mandato', 'sitio', 'anuncio',
        ], ['view'])
        mb_perms |= self._perms_for(app, ['relatoriosemanalcelula'], ['add'])
        mb_grp.permissions.set(mb_perms)
        self.stdout.write(f'Membros Baptizados: {mb_perms.count()} permissoes atribuidas')

        mg_grp = Group.objects.get(name='Membro Geral')
        mg_perms = self._perms_for(app, ['actividade', 'departamento', 'anuncio'], ['view'])
        mg_grp.permissions.set(mg_perms)
        self.stdout.write(f'Membro Geral: {mg_perms.count()} permissoes atribuidas')

    def _perms_for(self, app, models, actions):
        codenames = [f'{action}_{model}' for model in models for action in actions]
        return Permission.objects.filter(content_type__app_label=app, codename__in=codenames)
