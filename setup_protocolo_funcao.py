import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import Funcao

# Verificar se a função 'Protocolo' existe
funcao = Funcao.objects.filter(designacao__iexact='protocolo').first()

if funcao:
    print(f"✓ Função 'Protocolo' já existe (ID: {funcao.id})")
else:
    # Criar a função 'Protocolo'
    funcao = Funcao.objects.create(designacao='Protocolo')
    print(f"✓ Função 'Protocolo' criada com sucesso (ID: {funcao.id})")
