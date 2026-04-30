"""
Cria/actualiza os utilizadores de teste para o ambiente QA (idempotente).
Apenas deve ser executado em QA — nunca em produção.
"""
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


TEST_USERS = [
    {'username': 'pastor',          'group': 'Pastor'},
    {'username': 'financeiro',      'group': 'Financeiro'},
    {'username': 'secretaria',      'group': 'Secretaria'},
    {'username': 'lider_dept',      'group': 'Líder de Departamento'},
    {'username': 'vice_lider',      'group': 'Vice-Líder de Departamento'},
    {'username': 'lider_celula',    'group': 'Líder de Célula'},
    {'username': 'membro_batizado', 'group': 'Membros Baptizados'},
    {'username': 'membro_geral',    'group': 'Membro Geral'},
]

DEFAULT_PASSWORD = 'Teste@123'


class Command(BaseCommand):
    help = 'Cria/actualiza utilizadores de teste para QA (idempotente). NAO usar em producao.'

    def handle(self, *args, **options):
        for entry in TEST_USERS:
            user, created = User.objects.get_or_create(
                username=entry['username'],
                defaults={
                    'email': f"{entry['username']}@qa.tibl.local",
                    'first_name': entry['username'].replace('_', ' ').title(),
                },
            )
            user.set_password(DEFAULT_PASSWORD)
            user.save()

            try:
                group = Group.objects.get(name=entry['group'])
                user.groups.set([group])
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Grupo '{entry['group']}' nao encontrado — execute seed_base_data primeiro."
                    )
                )

            status = 'criado' if created else 'actualizado'
            self.stdout.write(f"  {entry['username']} ({entry['group']}): {status}")

        self.stdout.write(self.style.SUCCESS(
            f'seed_qa_users concluido. Password: {DEFAULT_PASSWORD}'
        ))
