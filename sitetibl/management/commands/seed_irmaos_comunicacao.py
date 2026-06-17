from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from sitetibl.models import Departamento, Irmao, Mandato, Municipio, Provincia, Sitio


class Command(BaseCommand):
    help = (
        'Cria/atualiza irmãos do cadastro interno do Departamento de Comunicação e Imagem '
        '(idempotente, sem importar fotos).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--default-password',
            type=str,
            default='Teste@123',
            help='Palavra-passe para contas criadas sem password definida (padrao: Teste@123).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria criado/atualizado sem gravar na base de dados.',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.default_password = options['default_password']

        provincia_luanda = self._get_or_create_provincia_luanda()

        dados_irmaos = [
            {
                'nome': 'Elizabeth Chaves',
                'apelido': 'Sapalalo',
                'outrosnomes': 'Beta',
                'sexo': 'Feminino',
                'estadocivil': 'Casado(a)',
                'datanascimento': '25/12/1977',
                'telefone': '923306249',
                'telefonewhatsapp': '923306249',
                'email': 'Cambinja@hotmail.com',
                'ruaenumero': 'FIlda',
                'bairro': 'Filda',
                'provincia': 'Luanda',
                'municipio': 'Cazenga',
                'localcongregacao': 'TIBL',
                'celula': 'Gamek',
                'culto': 'Português',
                'batizado': 'Sim',
                'dizimista': 'Sim',
                'profissao': 'Jornalist',
                'grauescolaridade': 'Superior',
                'especialidade': 'Comunicação',
                'observacao': '',
            },
            {
                'nome': 'Rosalina',
                'apelido': 'Carvalho',
                'outrosnomes': 'Rosa',
                'sexo': 'Feminino',
                'estadocivil': 'Solteiro(a)',
                'datanascimento': '24/10/2006',
                'telefone': '938327696',
                'telefonewhatsapp': '938327696',
                'email': 'Alexasilvacar@icloud.com',
                'ruaenumero': 'Rua 100',
                'bairro': 'Urbanização Nova Vida',
                'provincia': 'Luanda',
                'municipio': 'Kilamba Kiaxi',
                'localcongregacao': '3ª Igreja Baptista de Luanda',
                'celula': 'Nova Vida',
                'culto': 'Português',
                'batizado': 'Sim',
                'dizimista': 'Sim',
                'profissao': 'Estudante',
                'grauescolaridade': 'Superior',
                'especialidade': '',
                'observacao': '',
            },
            {
                'nome': 'Jovane António Ribeiro',
                'apelido': 'Ribeiro',
                'outrosnomes': '',
                'sexo': 'Mascullino',
                'estadocivil': 'Solteiro(a)',
                'datanascimento': '',
                'telefone': '926581532',
                'telefonewhatsapp': '926581532',
                'email': 'jovaneribeiro26@gmail.com',
                'ruaenumero': '12 de Julho',
                'bairro': 'Sambizanga',
                'provincia': 'Luanda',
                'municipio': '',
                'localcongregacao': '3 igreja batista de Luanda',
                'celula': '',
                'culto': 'Português',
                'batizado': 'Sim',
                'dizimista': 'Não',
                'profissao': '',
                'grauescolaridade': 'Superior',
                'especialidade': '',
                'observacao': '',
            },
            {
                'nome': 'Welwitchia',
                'apelido': 'Da Silva',
                'outrosnomes': 'Solene Fernandes',
                'sexo': 'Feminino',
                'estadocivil': 'Solteiro(a)',
                'datanascimento': '18/08/2007',
                'telefone': '940728096',
                'telefonewhatsapp': '940728096',
                'email': 'welwitchiadasilva@gmail.com',
                'ruaenumero': '8',
                'bairro': 'Mártires do Kifangondo',
                'provincia': 'Luanda',
                'municipio': 'Rangel',
                'localcongregacao': '3 igreja Baptista de Luanda',
                'celula': '',
                'culto': 'Português',
                'batizado': 'Sim',
                'dizimista': 'Não',
                'profissao': 'Estudante',
                'grauescolaridade': 'Superior',
                'especialidade': '',
                'observacao': '',
            },
            {
                'nome': 'Adélia',
                'apelido': 'Cristina',
                'outrosnomes': '',
                'sexo': 'Feminino',
                'estadocivil': 'Solteiro(a)',
                'datanascimento': '22/03/2006',
                'telefone': '926502848',
                'telefonewhatsapp': '926502848',
                'email': 'cristinaadelia24@gmail.com',
                'ruaenumero': 'Avenida Comandante Valódia',
                'bairro': '',
                'provincia': 'Luanda',
                'municipio': 'Sambizanga',
                'localcongregacao': 'Terceira Igreja Baptista de Luanda',
                'celula': '',
                'culto': 'Português',
                'batizado': 'Não',
                'dizimista': 'Não',
                'profissao': 'Estudante',
                'grauescolaridade': 'Superior',
                'especialidade': '',
                'observacao': '',
            },
            {
                'nome': 'Biluca',
                'apelido': 'Quimuanga',
                'outrosnomes': '',
                'sexo': 'Mascullino',
                'estadocivil': 'Solteiro(a)',
                'datanascimento': '07/10/1993',
                'telefone': '924383829',
                'telefonewhatsapp': '924383829',
                'email': 'bilucamorais@gmail.com',
                'ruaenumero': '',
                'bairro': 'Rocha Pinto, Paviterra',
                'provincia': 'Luanda',
                'municipio': 'Maianga',
                'localcongregacao': '3 TIBL',
                'celula': '',
                'culto': 'Inglês',
                'batizado': 'Sim',
                'dizimista': '',
                'profissao': 'Profissional de audiovisual',
                'grauescolaridade': 'Superior',
                'especialidade': 'Cinema e Televisão',
                'observacao': '',
            },
            {
                'nome': 'Hernany Martins',
                'apelido': 'Fernando',
                'outrosnomes': '',
                'sexo': 'Mascullino',
                'estadocivil': 'Solteiro(a)',
                'datanascimento': '27/06/2005',
                'telefone': '+244938747504',
                'telefonewhatsapp': '+244938747504',
                'email': 'hernanymartins59@gmail.com',
                'ruaenumero': 'Luanda sul,692',
                'bairro': 'Luanda Sul',
                'provincia': 'Luanda',
                'municipio': 'Viana',
                'localcongregacao': 'TIBL',
                'celula': '',
                'culto': 'Português, Inglês, Manancial',
                'batizado': 'Sim',
                'dizimista': 'Não',
                'profissao': 'Telecomunicações',
                'grauescolaridade': 'Médio',
                'especialidade': 'Telecomunicações',
                'observacao': '',
            },
        ]

        emails_processados = []

        created_users = 0
        updated_users = 0
        created_irmaos = 0
        updated_irmaos = 0

        for row in dados_irmaos:
            municipio_obj = self._get_or_create_municipio(row.get('municipio', ''), provincia_luanda)
            local_congregacao = self._get_or_create_sitio_igreja(row.get('localcongregacao', ''))
            celula = self._get_or_create_sitio_celula(row.get('celula', ''))

            username = self._build_username(row['nome'], row['apelido'], row['email'])
            email = row['email'].strip().lower()
            first_name = row['nome'].strip().split(' ')[0]
            last_name = row['apelido'].strip()

            user_created = False
            if self.dry_run:
                user = User.objects.filter(username=username).first() or User.objects.filter(email=email).first()
                user_created = user is None
            else:
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                    },
                )

                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                if user_created:
                    user.set_password(self.default_password)
                user.save()

            if user_created:
                created_users += 1
            else:
                updated_users += 1

            irmao_defaults = {
                'nome': row['nome'].strip(),
                'apelido': row['apelido'].strip(),
                'outrosnomes': row.get('outrosnomes', '').strip(),
                'sexo': self._map_sexo(row.get('sexo', '')),
                'estadocivil': self._map_estado_civil(row.get('estadocivil', '')),
                'datanascimento': self._parse_date(row.get('datanascimento', '')),
                'telefone': row.get('telefone', '').strip(),
                'telefonewhatsapp': row.get('telefonewhatsapp', '').strip(),
                'ruaenumero': row.get('ruaenumero', '').strip(),
                'bairro': row.get('bairro', '').strip(),
                'provincia': provincia_luanda,
                'municipio': municipio_obj,
                'localcongregacao': local_congregacao,
                'celula': celula,
                'culto': self._map_culto(row.get('culto', '')),
                'categoria': 'membro_batizado' if self._to_bool(row.get('batizado', '')) else 'assistente',
                'dizimista': self._map_dizimista(row.get('dizimista', '')),
                'profissao': row.get('profissao', '').strip(),
                'grauescolaridade': self._map_escolaridade(row.get('grauescolaridade', '')),
                'especialidade': row.get('especialidade', '').strip(),
                'observacao': row.get('observacao', '').strip(),
                'user': user if not self.dry_run else None,
            }

            if self.dry_run:
                exists = Irmao.objects.filter(email=email).exists()
                if exists:
                    updated_irmaos += 1
                else:
                    created_irmaos += 1
            else:
                _, created = Irmao.objects.update_or_create(
                    email=email,
                    defaults=irmao_defaults,
                )
                if created:
                    created_irmaos += 1
                else:
                    updated_irmaos += 1

            emails_processados.append(email)

            self.stdout.write(
                f"Irmao {row['nome']} {row['apelido']}: "
                f"{'criaria' if self.dry_run and not Irmao.objects.filter(email=email).exists() else 'atualizaria' if self.dry_run else 'criado' if created else 'atualizado'}"
            )

        mandatos_criados, mandatos_existentes = self._vincular_departamento_comunicacao(
            emails_processados
        )
        if self.dry_run:
            self.stdout.write(
                f'[DRY-RUN] Vínculos ao departamento Comunicação e imagem: '
                f'criaria={mandatos_criados}, existentes={mandatos_existentes}'
            )
        else:
            self.stdout.write(
                f'Vínculos ao departamento Comunicação e imagem: '
                f'criados={mandatos_criados}, existentes={mandatos_existentes}'
            )

        modo = 'DRY-RUN' if self.dry_run else 'APLICADO'
        self.stdout.write(
            self.style.SUCCESS(
                f'[{modo}] Utilizadores criados={created_users}, atualizados={updated_users} | '
                f'Irmaos criados={created_irmaos}, atualizados={updated_irmaos}'
            )
        )

    def _vincular_departamento_comunicacao(self, emails_processados):
        if self.dry_run:
            departamento = Departamento.objects.filter(designacao='Comunicação e imagem').first()
            if departamento is None:
                mandatos_existentes = 0
                mandatos_criados = len(emails_processados)
                return mandatos_criados, mandatos_existentes

            mandatos_criados = 0
            mandatos_existentes = 0
            for email in emails_processados:
                irmao = Irmao.objects.filter(email=email).first()
                if irmao and Mandato.objects.filter(irmao=irmao, departamento=departamento).exists():
                    mandatos_existentes += 1
                else:
                    mandatos_criados += 1
            return mandatos_criados, mandatos_existentes

        departamento, _ = Departamento.objects.get_or_create(
            designacao='Comunicação e imagem',
            defaults={
                'abreviacao': 'DCI',
                'descricao': 'Departamento de comunicação e imagem',
            },
        )

        mandatos_criados = 0
        mandatos_existentes = 0
        for email in emails_processados:
            irmao = Irmao.objects.filter(email=email).first()
            if irmao is None:
                continue
            _, created = Mandato.objects.get_or_create(
                irmao=irmao,
                departamento=departamento,
                defaults={
                    'funcao': 'membro',
                    'inicio': date.today(),
                },
            )
            if created:
                mandatos_criados += 1
            else:
                mandatos_existentes += 1

        return mandatos_criados, mandatos_existentes

    def _get_or_create_provincia_luanda(self):
        if self.dry_run:
            return Provincia.objects.filter(nome='Luanda').first() or Provincia(
                nome='Luanda', codigo='LDA'
            )

        provincia, _ = Provincia.objects.get_or_create(
            nome='Luanda',
            defaults={'codigo': 'LDA'},
        )
        return provincia

    def _get_or_create_municipio(self, nome, provincia):
        nome_limpo = nome.strip()
        if not nome_limpo:
            return None

        if self.dry_run:
            return Municipio.objects.filter(nome=nome_limpo, provincia__nome='Luanda').first() or Municipio(
                nome=nome_limpo, provincia=provincia
            )

        municipio, _ = Municipio.objects.get_or_create(
            nome=nome_limpo,
            provincia=provincia,
        )
        return municipio

    def _canonical_igreja(self, nome):
        nome_limpo = (nome or '').strip().lower()
        mapa = {
            'tibl': 'Terceira Igreja Baptista de Luanda',
            '3 tibl': 'Terceira Igreja Baptista de Luanda',
            '3 igreja batista de luanda': 'Terceira Igreja Baptista de Luanda',
            '3 igreja baptista de luanda': 'Terceira Igreja Baptista de Luanda',
            '3ª igreja baptista de luanda': 'Terceira Igreja Baptista de Luanda',
            'terceira igreja baptista de luanda': 'Terceira Igreja Baptista de Luanda',
        }
        return mapa.get(nome_limpo, nome.strip())

    def _get_or_create_sitio_igreja(self, designacao):
        designacao = self._canonical_igreja(designacao)
        if not designacao:
            return None

        if self.dry_run:
            return Sitio.objects.filter(designacao=designacao).first() or Sitio(designacao=designacao, tipo='1')

        sitio, _ = Sitio.objects.get_or_create(
            designacao=designacao,
            defaults={'tipo': '1'},
        )
        return sitio

    def _get_or_create_sitio_celula(self, designacao):
        designacao = (designacao or '').strip()
        if not designacao:
            return None

        if self.dry_run:
            return Sitio.objects.filter(designacao=designacao).first() or Sitio(designacao=designacao, tipo='2')

        sitio, _ = Sitio.objects.get_or_create(
            designacao=designacao,
            defaults={'tipo': '2'},
        )
        return sitio

    def _parse_date(self, value):
        value = (value or '').strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, '%d/%m/%Y').date()
        except ValueError:
            return None

    def _map_sexo(self, value):
        valor = (value or '').strip().lower()
        return 'F' if 'fem' in valor else 'M'

    def _map_estado_civil(self, value):
        valor = (value or '').strip().lower()
        if 'casado' in valor:
            return 'C'
        if 'viuv' in valor:
            return 'V'
        if 'amar' in valor:
            return 'A'
        if 'divorc' in valor:
            return 'D'
        return 'S'

    def _map_culto(self, value):
        valor = (value or '').strip().lower()
        if valor and 'ingl' in valor and 'portugu' not in valor:
            return 'I'
        return 'P'

    def _to_bool(self, value):
        return (value or '').strip().lower() == 'sim'

    def _map_dizimista(self, value):
        return 'sim' if self._to_bool(value) else 'nao'

    def _map_escolaridade(self, value):
        valor = (value or '').strip().lower()
        if valor in {'basico', 'básico'}:
            return 'basico'
        if valor == 'medio' or valor == 'médio':
            return 'medio'
        if valor == 'superior':
            return 'superior'
        return ''

    def _slugify(self, text):
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        ascii_text = re.sub(r'[^a-zA-Z0-9]+', '.', ascii_text).strip('.')
        return ascii_text.lower()

    def _build_username(self, nome, apelido, email):
        base = self._slugify(f'{nome} {apelido}') or self._slugify(email.split('@')[0])
        username = base[:150]
        email = (email or '').strip().lower()

        if self.dry_run:
            return username

        existing = User.objects.filter(username=username).first()
        if existing is None:
            return username
        if email and existing.email.strip().lower() == email:
            return username

        index = 2
        while True:
            suffix = f'.{index}'
            candidate = f"{username[:150 - len(suffix)]}{suffix}"
            candidate_user = User.objects.filter(username=candidate).first()
            if candidate_user is None:
                return candidate
            if email and candidate_user.email.strip().lower() == email:
                return candidate
            index += 1
