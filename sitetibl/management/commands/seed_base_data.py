from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from sitetibl.models import (
    Actividade,
    Banco,
    Centro_Custo,
    Contabancaria,
    Departamento,
    Dizimooferta,
    Entradabanco,
    Entradacaixa,
    Irmao,
    Listaactividades,
    Mandato,
    Municipio,
    Provincia,
    Rubricaentrada,
    Status_Aprovacao,
    Sitio,
    Tipo_Celula,
    Tipo_Moeda,
    TipoOferta,
    Tipificacao_Custo,
    Gruporubrica,
)


class Command(BaseCommand):
    help = (
        'Popula dados base (grupos, tabelas de referencia e superutilizador opcional). '
        'Dados demo de irmaos so sao criados com --with-demo.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Nome de utilizador para criar/atualizar superutilizador (padrao: admin).',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@tibl.local',
            help='Email do superutilizador (padrao: admin@tibl.local).',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Palavra-passe do superutilizador (padrao: admin123).',
        )
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Nao cria/atualiza o superutilizador.',
        )
        parser.add_argument(
            '--with-demo',
            action='store_true',
            help='Cria/atualiza dados operacionais de demonstracao (inclui irmaos demo).',
        )

    def handle(self, *args, **options):
        self.seed_groups()
        self.seed_reference_tables()

        if not options['skip_admin']:
            self.seed_admin(
                username=options['admin_username'],
                email=options['admin_email'],
                password=options['admin_password'],
            )

        if options['with_demo']:
            self.seed_demo_data()

        self.stdout.write(self.style.SUCCESS('Seed concluido com sucesso.'))

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

        self.stdout.write(f'Grupos criados: {created_count} | totais verificados: {len(group_names)}')

        self._assign_group_permissions()

    def _assign_group_permissions(self):
        """Atribui permissoes Django por modelo a cada grupo."""
        app = 'sitetibl'
        crud = ['add', 'change', 'delete', 'view']

        # --- Administrador: tudo em sitetibl ---
        admin_grp = Group.objects.get(name='Administrador')
        all_perms = Permission.objects.filter(content_type__app_label=app)
        admin_grp.permissions.set(all_perms)
        self.stdout.write(f'Administrador: {all_perms.count()} permissoes atribuidas')

        # --- Pastor: supervisao pastoral — ve tudo, CRUD actividades/membros, aprova pedidos ---
        pastor_grp = Group.objects.get(name='Pastor')
        pastor_perms = self._perms_for(app, [
            'pessoa', 'irmao', 'mandato', 'actividade', 'escala',
            'relatoriosemanalcelula', 'conteudoensino', 'enviomensagem',
            'anuncio', 'ajuda', 'pedidosaida',
        ], crud)
        pastor_perms |= self._perms_for(app, [
            'departamento',
        ], ['view', 'change'])
        pastor_perms |= self._perms_for(app, [
            'sitio', 'dizimooferta', 'entradabanco', 'saidabanco',
            'entradacaixa', 'saidacaixa', 'banco', 'contabancaria',
            'orcamentodepartamento', 'inventariopatrimonio',
            'cestabasica', 'pagamentoservico',
        ], ['view'])
        pastor_grp.permissions.set(pastor_perms)
        self.stdout.write(f'Pastor: {pastor_perms.count()} permissoes atribuidas')

        # --- Financeiro: CRUD financeiro + view membros/actividades ---
        fin_grp = Group.objects.get(name='Financeiro')
        fin_perms = self._perms_for(app, [
            'dizimooferta', 'entradabanco', 'saidabanco',
            'entradacaixa', 'saidacaixa', 'contabancaria', 'banco',
            'pedidosaida', 'orcamentodepartamento', 'pagamentoservico',
        ], crud)
        fin_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'actividade', 'departamento',
            'inventariopatrimonio',
        ], ['view'])
        fin_grp.permissions.set(fin_perms)
        self.stdout.write(f'Financeiro: {fin_perms.count()} permissoes atribuidas')

        # --- Secretaria: CRUD membros/actividades/comunicacao + pedido de saida (sem acesso financeiro) ---
        sec_grp = Group.objects.get(name='Secretaria')
        sec_perms = self._perms_for(app, [
            'irmao', 'pessoa', 'actividade', 'escala', 'mandato',
            'departamento', 'sitio', 'relatoriosemanalcelula',
            'conteudoensino', 'enviomensagem', 'anuncio',
            'inventariopatrimonio', 'cestabasica', 'ajuda',
        ], crud)
        sec_perms |= self._perms_for(app, [
            'pedidosaida',
        ], ['view'])
        sec_grp.permissions.set(sec_perms)
        self.stdout.write(f'Secretaria: {sec_perms.count()} permissoes atribuidas')

        # --- Líder de Departamento: gere o seu dept, escalas, cria pedidos ---
        ld_grp = Group.objects.get(name='Líder de Departamento')
        ld_perms = self._perms_for(app, [
            'actividade', 'escala', 'anuncio', 'enviomensagem',
        ], crud)
        # Mandatos: só pode criar e ver, não editar/eliminar
        ld_perms |= self._perms_for(app, ['mandato'], ['add', 'view'])
        ld_perms |= self._perms_for(app, ['departamento'], ['view'])
        ld_perms |= self._perms_for(app, ['funcao'], crud)
        ld_perms |= self._perms_for(app, ['pedidosaida'], ['add', 'view'])
        ld_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'sitio', 'conteudoensino',
        ], ['view'])
        ld_grp.permissions.set(ld_perms)
        self.stdout.write(f'Líder de Departamento: {ld_perms.count()} permissoes atribuidas')

        # --- Vice-Líder de Departamento: apoia líder, escalas, cria pedidos ---
        vld_grp = Group.objects.get(name='Vice-Líder de Departamento')
        vld_perms = self._perms_for(app, [
            'actividade', 'escala', 'anuncio',
        ], crud)
        # Mandatos: só pode criar e ver, não editar/eliminar
        vld_perms |= self._perms_for(app, ['mandato'], ['add', 'view'])
        vld_perms |= self._perms_for(app, ['pedidosaida'], ['add', 'view'])
        vld_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'sitio', 'departamento', 'conteudoensino',
            'enviomensagem',
        ], ['view'])
        vld_perms |= self._perms_for(app, ['funcao'], ['add', 'view'])
        vld_grp.permissions.set(vld_perms)
        self.stdout.write(f'Vice-Líder de Departamento: {vld_perms.count()} permissoes atribuidas')

        # --- Líder de Célula: relatorios + view membros da celula ---
        lc_grp = Group.objects.get(name='Líder de Célula')
        lc_perms = self._perms_for(app, [
            'relatoriosemanalcelula',
        ], ['add', 'change', 'view'])
        lc_perms |= self._perms_for(app, [
            'irmao', 'pessoa', 'sitio', 'actividade', 'departamento',
            'conteudoensino',
        ], ['view'])
        lc_grp.permissions.set(lc_perms)
        self.stdout.write(f'Líder de Célula: {lc_perms.count()} permissoes atribuidas')

        # --- Membros Baptizados: view maioria + add relatorio ---
        mb_grp = Group.objects.get(name='Membros Baptizados')
        mb_perms = self._perms_for(app, [
            'irmao', 'pessoa', 'actividade', 'escala', 'departamento',
            'mandato', 'sitio', 'anuncio',
        ], ['view'])
        mb_perms |= self._perms_for(app, ['relatoriosemanalcelula'], ['add'])
        mb_grp.permissions.set(mb_perms)
        self.stdout.write(f'Membros Baptizados: {mb_perms.count()} permissoes atribuidas')

        # --- Membro Geral: view minima ---
        mg_grp = Group.objects.get(name='Membro Geral')
        mg_perms = self._perms_for(app, [
            'actividade', 'departamento', 'anuncio',
        ], ['view'])
        mg_grp.permissions.set(mg_perms)
        self.stdout.write(f'Membro Geral: {mg_perms.count()} permissoes atribuidas')

    def _perms_for(self, app, models, actions):
        """Devolve QuerySet de permissoes para combinacao app/modelos/accoes."""
        codenames = [
            f'{action}_{model}' for model in models for action in actions
        ]
        return Permission.objects.filter(
            content_type__app_label=app,
            codename__in=codenames,
        )

    def seed_reference_tables(self):
        moedas = [
            ('Kwanza', 'AKZ'),
            ('Dolar Americano', 'USD'),
            ('Euro', 'EUR'),
        ]
        status_aprovacao = [
            'Em analise',
            'Aprovado',
            'Rejeitado',
        ]
        tipo_celula = [
            'Celula Familiar',
            'Celula de Jovens',
            'Celula de Oracao',
        ]
        centro_custo = [
            'Administracao',
            'Missoes',
            'Acao Social',
        ]
        tipificacao_custo = [
            'Operacional',
            'Investimento',
            'Emergencial',
        ]
        tipo_oferta = [
            'Dizimo',
            'Oferta',
            'Oferta Especial',
        ]

        self._seed_designacao_abreviatura(Tipo_Moeda, moedas)
        self._seed_designacao(Status_Aprovacao, status_aprovacao)
        self._seed_designacao(Tipo_Celula, tipo_celula)
        self._seed_designacao(Centro_Custo, centro_custo)
        self._seed_designacao(Tipificacao_Custo, tipificacao_custo)
        self._seed_designacao(TipoOferta, tipo_oferta)

    def seed_admin(self, username, email, password):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )

        if not created:
            user.email = email
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        user.groups.add(admin_group)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Superutilizador criado: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superutilizador atualizado: {username}'))

    def _seed_designacao(self, model, designacoes):
        created_count = 0
        for designacao in designacoes:
            _, created = model.objects.get_or_create(designacao=designacao)
            if created:
                created_count += 1

        self.stdout.write(
            f'{model.__name__}: criados {created_count} | totais verificados {len(designacoes)}'
        )

    def _seed_designacao_abreviatura(self, model, pares):
        created_count = 0
        for designacao, abreviatura in pares:
            _, created = model.objects.get_or_create(
                designacao=designacao,
                defaults={'abreviatura': abreviatura},
            )
            if created:
                created_count += 1

        self.stdout.write(
            f'{model.__name__}: criados {created_count} | totais verificados {len(pares)}'
        )

    def seed_demo_data(self):
        hoje = date.today()

        # Província e Municípios (precisam existir - seed_provincias)
        luanda = Provincia.objects.filter(codigo='LDA').first()
        mun_luanda = Municipio.objects.filter(nome='Luanda', provincia=luanda).first() if luanda else None
        mun_talatona = Municipio.objects.filter(nome='Talatona', provincia=luanda).first() if luanda else None

        # Locais
        sede, _ = Sitio.objects.get_or_create(
            designacao='Templo Sede Maculusso',
            defaults={
                'ruaenumero': 'Rua Comandante Gika, 145',
                'bairro': 'Maculusso',
                'municipio': mun_luanda,
                'provincia': luanda,
                'dataFundacao': date(1987, 5, 17),
                'tipo': '1',
                'descricao': 'Templo principal da igreja',
            },
        )
        celula_camama, _ = Sitio.objects.get_or_create(
            designacao='Celula Camama',
            defaults={
                'bairro': 'Camama',
                'municipio': mun_talatona,
                'provincia': luanda,
                'tipo': '2',
                'descricao': 'Celula de bairro com reuniao semanal',
            },
        )
        celula_pat, _ = Sitio.objects.get_or_create(
            designacao='Celula Patriota',
            defaults={
                'bairro': 'Patriota',
                'municipio': mun_talatona,
                'provincia': luanda,
                'tipo': '2',
                'descricao': 'Celula de crescimento familiar',
            },
        )

        # Membros
        membros = [
            {
                'username': 'joao.silva',
                'email': 'joao.silva@tibl.local',
                'nome': 'Joao',
                'apelido': 'Silva',
                'sexo': 'M',
                'telefone': '+244923111111',
                'dizimista': 'sim',
                'celula': celula_camama,
            },
            {
                'username': 'maria.costa',
                'email': 'maria.costa@tibl.local',
                'nome': 'Maria',
                'apelido': 'Costa',
                'sexo': 'F',
                'telefone': '+244923222222',
                'dizimista': 'sim',
                'celula': celula_pat,
            },
            {
                'username': 'paulo.mendes',
                'email': 'paulo.mendes@tibl.local',
                'nome': 'Paulo',
                'apelido': 'Mendes',
                'sexo': 'M',
                'telefone': '+244923333333',
                'dizimista': 'nao',
                'celula': celula_camama,
            },
            {
                'username': 'ana.pedro',
                'email': 'ana.pedro@tibl.local',
                'nome': 'Ana',
                'apelido': 'Pedro',
                'sexo': 'F',
                'telefone': '+244923444444',
                'dizimista': 'sim',
                'celula': celula_pat,
            },
        ]

        irmaos = {}
        for membro in membros:
            user, _ = User.objects.get_or_create(
                username=membro['username'],
                defaults={
                    'email': membro['email'],
                    'first_name': membro['nome'],
                    'last_name': membro['apelido'],
                },
            )
            user.email = membro['email']
            user.first_name = membro['nome']
            user.last_name = membro['apelido']
            user.set_password('Teste@123')
            user.save()

            irmao, _ = Irmao.objects.update_or_create(
                email=membro['email'],
                defaults={
                    'nome': membro['nome'],
                    'apelido': membro['apelido'],
                    'sexo': membro['sexo'],
                    'telefone': membro['telefone'],
                    'municipio': mun_luanda,
                    'provincia': luanda,
                    'celula': membro['celula'],
                    'localcongregacao': sede,
                    'dizimista': membro['dizimista'],
                    'batizado': True,
                    'user': user,
                },
            )
            irmaos[membro['username']] = irmao

        # Departamentos e mandatos
        dep_louvor, _ = Departamento.objects.get_or_create(
            designacao='Departamento de Louvor',
            defaults={'abreviacao': 'DLO', 'descricao': 'Ministerio de louvor e adoracao'},
        )
        dep_fin, _ = Departamento.objects.get_or_create(
            designacao='Departamento Financeiro',
            defaults={'abreviacao': 'DFI', 'descricao': 'Gestao financeira e controlo interno'},
        )

        dep_louvor.lider_departamento = irmaos['joao.silva']
        dep_louvor.vice_lider_departamento = irmaos['ana.pedro']
        dep_louvor.save()

        dep_fin.lider_departamento = irmaos['maria.costa']
        dep_fin.vice_lider_departamento = irmaos['paulo.mendes']
        dep_fin.save()

        Mandato.objects.get_or_create(
            irmao=irmaos['joao.silva'],
            departamento=dep_louvor,
            defaults={
                'funcao': 'lider',
                'inicio': date(2025, 1, 1),
            },
        )
        Mandato.objects.get_or_create(
            irmao=irmaos['maria.costa'],
            departamento=dep_fin,
            defaults={
                'funcao': 'tesoureiro',
                'inicio': date(2025, 1, 1),
            },
        )

        # Actividades
        culto, _ = Listaactividades.objects.get_or_create(
            designacao='Culto Dominical',
            defaults={'descricao': 'Culto principal de domingo'},
        )
        celula, _ = Listaactividades.objects.get_or_create(
            designacao='Reuniao de Celula',
            defaults={'descricao': 'Reuniao semanal de celula'},
        )

        act_culto, _ = Actividade.objects.update_or_create(
            designacao=culto,
            data=hoje - timedelta(days=7),
            defaults={
                'inicio': time(9, 0),
                'fim': time(11, 30),
                'tema': 'Fidelidade e compromisso no servico',
                'localactividade': sede,
                'versosbiblicos': 'Malaquias 3:10',
                'hinos': 'Hino 45, Hino 112',
                'totalpresentes': 286,
            },
        )
        Actividade.objects.update_or_create(
            designacao=celula,
            data=hoje - timedelta(days=3),
            defaults={
                'inicio': time(19, 0),
                'fim': time(20, 30),
                'tema': 'Vida de oracao no lar',
                'localactividade': celula_camama,
                'versosbiblicos': 'Lucas 18:1',
                'hinos': 'Hino 12',
                'totalpresentes': 34,
            },
        )

        # Rubricas e contas
        grupo_rubrica, _ = Gruporubrica.objects.get_or_create(designacao='Contribuicoes')
        rubrica_dizimo, _ = Rubricaentrada.objects.get_or_create(
            designacao='Dizimos e Ofertas',
            defaults={'gruporubrica': grupo_rubrica},
        )
        if rubrica_dizimo.gruporubrica_id is None:
            rubrica_dizimo.gruporubrica = grupo_rubrica
            rubrica_dizimo.save(update_fields=['gruporubrica'])

        banco_bai, _ = Banco.objects.get_or_create(
            designacao='Banco BAI',
            defaults={
                'abreviacao': 'BAI',
                'gestor': 'Helena Fernandes',
                'telefone': '+244222111222',
                'email': 'gestor.bai@banco.ao',
            },
        )
        conta_tibl, _ = Contabancaria.objects.get_or_create(
            numeroconta='001234567890',
            defaults={
                'banco': banco_bai,
                'iban': 'AO06004400001234567890123',
                'moeda': 'AKZ',
                'saldo': Decimal('2500000.00'),
            },
        )

        # Entradas financeiras
        entrada_banco, _ = Entradabanco.objects.update_or_create(
            contaaacreditar=conta_tibl,
            data=hoje - timedelta(days=6),
            valor=Decimal('185000.00'),
            defaults={
                'moeda': 'AKZ',
                'hora': time(10, 15),
                'via': '2',
                'rubrica': rubrica_dizimo,
                'contaorigem': None,
                'responsavel': irmaos['maria.costa'],
                'observacao': 'Consolidado de transferencias do culto dominical',
            },
        )

        entrada_caixa, _ = Entradacaixa.objects.update_or_create(
            data=hoje - timedelta(days=2),
            valor=Decimal('42000.00'),
            responsavel=irmaos['joao.silva'],
            rubrica=rubrica_dizimo,
            defaults={
                'moeda': 'AKZ',
                'hora': time(18, 45),
                'observacao': 'Ofertas recolhidas na reuniao de celula',
            },
        )

        tipo_dizimo = TipoOferta.objects.get(designacao='Dizimo')
        tipo_oferta = TipoOferta.objects.get(designacao='Oferta')

        Dizimooferta.objects.update_or_create(
            irmao=irmaos['maria.costa'],
            datacorrespondente=hoje - timedelta(days=6),
            tipooferta=tipo_dizimo,
            defaults={
                'valor': Decimal('120000.00'),
                'moeda': 'AKZ',
                'actividade': act_culto,
                'entradabanco': entrada_banco,
            },
        )
        Dizimooferta.objects.update_or_create(
            irmao=irmaos['joao.silva'],
            datacorrespondente=hoje - timedelta(days=2),
            tipooferta=tipo_oferta,
            defaults={
                'valor': Decimal('42000.00'),
                'moeda': 'AKZ',
                'actividade': None,
                'entradacaixa': entrada_caixa,
            },
        )

        self.stdout.write(self.style.SUCCESS('Dados demo realistas criados/atualizados.'))
