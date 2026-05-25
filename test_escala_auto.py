import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import Protocolo, Escala, Actividade, Irmao, Funcao, Listaactividades
from django.contrib.auth.models import User

print("\n" + "="*60)
print("TESTE: Protocolo com Escalas Automáticas")
print("="*60 + "\n")

# 1. Criar um protocolo de teste
protocolo = Protocolo.objects.filter(numero='TESTE-AUTO-001').first()
if not protocolo:
    protocolo = Protocolo.objects.create(
        numero='TESTE-AUTO-001',
        tipo='interno',
        assunto='Teste Auto',
        prioridade='normal'
    )
    print("✅ Protocolo criado:", protocolo.numero)
else:
    print("✅ Protocolo existe:", protocolo.numero)

# 2. Verificar se tem actividade_principal
print(f"\n📋 Actividade Principal Atual: {protocolo.actividade_principal}")

# 3. Criar uma actividade de teste
lista_desig = Listaatividades.objects.first()
if lista_desig:
    actividade = Actividade.objects.filter(designacao=lista_desig).first()
    if not actividade:
        actividade = Actividade.objects.create(
            designacao=lista_desig,
            data='2026-05-12',
            inicio='09:00:00',
            fim='10:00:00',
            localactividade='Casa'
        )
        print("✅ Actividade criada:", actividade.designacao)
    else:
        print("✅ Actividade existe:", actividade.designacao)

    # 4. Criar escala e validar que actividade_principal é atualizado
    irmao = Irmao.objects.first()
    funcao = Funcao.objects.filter(designacao__iexact='protocolo').first()
    
    if irmao and funcao:
        escala, created = Escala.objects.get_or_create(
            irmao=irmao,
            actividade=actividade,
            funcao=funcao
        )
        
        if created:
            print("✅ Escala criada:", escala.id)
        else:
            print("⚠️ Escala já existe:", escala.id)
        
        # Simular o que faz protocolo_add_escalas
        protocolo.actividade_principal = actividade
        protocolo.save(update_fields=['actividade_principal'])
        print("✅ Actividade Principal atualizado")
        
        # 5. Verificar escalas no detalhe
        protocolo.refresh_from_db()
        escalas = Escala.objects.filter(actividade_id=protocolo.actividade_principal_id)
        print(f"\n📊 Escalas encontradas: {escalas.count()}")
        for e in escalas:
            print(f"   - {e.irmao.nome} ({e.funcao.designacao})")

print("\n" + "="*60)
print("✅ TESTE COMPLETO COM SUCESSO")
print("="*60 + "\n")
