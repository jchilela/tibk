from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from sitetibl.models import (
    Actividade,
    Banco,
    Cargo,
    Centro_Custo,
    Contabancaria,
    Departamento,
    Dizimooferta,
    Entradabanco,
    Entradacaixa,
    Irmao,
    Listaactividades,
    Mandato,
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
    help = 'Popula dados base (grupos, tabelas de referencia e superutilizador opcional).'

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
            '--skip-demo',
            action='store_true',
            help='Nao cria dados operacionais de demonstracao.',
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

        if not options['skip_demo']:
            self.seed_demo_data()

        self.stdout.write(self.style.SUCCESS('Seed concluido com sucesso.'))

    def seed_groups(self):
        group_names = [
            'Administrador',
            'Financeiro',
            'Secretaria',
            'Membros Baptizados',
            'Membro Geral',
        ]

        created_count = 0
        for name in group_names:
            _, created = Group.objects.get_or_create(name=name)
            if created:
                created_count += 1

        self.stdout.write(f'Grupos criados: {created_count} | totais verificados: {len(group_names)}')

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

        # Locais
        sede, _ = Sitio.objects.get_or_create(
            designacao='Templo Sede Maculusso',
            defaults={
                'ruaenumero': 'Rua Comandante Gika, 145',
                'bairro': 'Maculusso',
                'municipio': 'Luanda',
                'provincia': 'LDA',
                'dataFundacao': date(1987, 5, 17),
                'tipo': '1',
                'descricao': 'Templo principal da igreja',
            },
        )
        celula_camama, _ = Sitio.objects.get_or_create(
            designacao='Celula Camama',
            defaults={
                'bairro': 'Camama',
                'municipio': 'Talatona',
                'provincia': 'LDA',
                'tipo': '2',
                'descricao': 'Celula de bairro com reuniao semanal',
            },
        )
        celula_pat, _ = Sitio.objects.get_or_create(
            designacao='Celula Patriota',
            defaults={
                'bairro': 'Patriota',
                'municipio': 'Talatona',
                'provincia': 'LDA',
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
                    'municipio': 'LU',
                    'provincia': 'LDA',
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

        cargo_lider, _ = Cargo.objects.get_or_create(designacao='Lider', defaults={'descricao': 'Responsavel do departamento'})
        cargo_tes, _ = Cargo.objects.get_or_create(designacao='Tesoureiro', defaults={'descricao': 'Responsavel financeiro'})

        Mandato.objects.get_or_create(
            irmao=irmaos['joao.silva'],
            departamento=dep_louvor,
            cargo=cargo_lider,
            inicio=date(2025, 1, 1),
        )
        Mandato.objects.get_or_create(
            irmao=irmaos['maria.costa'],
            departamento=dep_fin,
            cargo=cargo_tes,
            inicio=date(2025, 1, 1),
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
