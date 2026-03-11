# sitetibl/dizimo_utils.py
"""
Utilitários para vinculação automática de dízimos com entradas bancárias e de caixa.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Q
from .models import Dizimooferta, Entradabanco, Entradacaixa


def vincular_dizimos_existentes(dias_tolerancia=0, moeda=None, force=False):
    """
    Tenta vincular dízimos não vinculados com entradas bancárias existentes.
    
    Args:
        dias_tolerancia: Número de dias de tolerância na diferença de datas
        moeda: Se especificado, vincular apenas para uma moeda específica
        force: Se True, re-vincular mesmo registros já vinculados
    
    Returns:
        dict com estatísticas de vinculação
    """
    
    stats = {
        'total_processados': 0,
        'sucesso': 0,
        'erro': 0,
        'ja_vinculados': 0,
        'sem_correspondencia': 0
    }
    
    # Filtro base
    filtro_dizimos = Dizimooferta.objects.all()
    
    if not force:
        filtro_dizimos = filtro_dizimos.filter(entradabanco__isnull=True)
    
    if moeda:
        filtro_dizimos = filtro_dizimos.filter(moeda=moeda)
    
    for dizimo in filtro_dizimos:
        stats['total_processados'] += 1
        
        if dizimo.entradabanco and not force:
            stats['ja_vinculados'] += 1
            continue
        
        try:
            # Busca entrada bancária correspondente
            entrada = buscar_entrada_correspondente(
                dizimo.datacorrespondente,
                dizimo.valor,
                dizimo.moeda,
                dias_tolerancia=dias_tolerancia
            )
            
            if entrada:
                dizimo.entradabanco = entrada
                dizimo.save(update_fields=['entradabanco'])
                stats['sucesso'] += 1
                print(f"✅ Dízimo {dizimo.id} vinculado com Entrada {entrada.id}")
            else:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            print(f"❌ Erro ao processar dízimo {dizimo.id}: {str(e)}")
    
    return stats


def vincular_entradas_bancarias_existentes(dias_tolerancia=0, moeda=None, force=False):
    """
    Tenta vincular entradas bancárias não vinculadas com dízimos existentes.
    
    Args:
        dias_tolerancia: Número de dias de tolerância na diferença de datas
        moeda: Se especificado, vincular apenas para uma moeda específica
        force: Se True, vincular mesmo que já tenha dízimos vinculados
    
    Returns:
        dict com estatísticas de vinculação
    """
    
    stats = {
        'total_processados': 0,
        'sucesso': 0,
        'erro': 0,
        'ja_vinculados': 0,
        'sem_correspondencia': 0
    }
    
    # Filtro base
    filtro_entradas = Entradabanco.objects.all()
    
    if moeda:
        filtro_entradas = filtro_entradas.filter(moeda=moeda)
    
    for entrada in filtro_entradas:
        stats['total_processados'] += 1
        
        # Verifica se já existe um dízimo vinculado
        dizimos_vinculados = Dizimooferta.objects.filter(entradabanco=entrada)
        
        if dizimos_vinculados.exists() and not force:
            stats['ja_vinculados'] += 1
            continue
        
        try:
            # Busca dízimos correspondentes
            dizimos = buscar_dizimos_correspondentes(
                entrada.data,
                entrada.valor,
                entrada.moeda,
                dias_tolerancia=dias_tolerancia
            )
            
            for dizimo in dizimos:
                if not dizimo.entradabanco or force:
                    dizimo.entradabanco = entrada
                    dizimo.save(update_fields=['entradabanco'])
                    stats['sucesso'] += 1
                    print(f"✅ Entrada {entrada.id} vinculada com Dízimo {dizimo.id}")
            
            if not dizimos:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            print(f"❌ Erro ao processar entrada {entrada.id}: {str(e)}")
    
    return stats


def buscar_entrada_correspondente(data, valor, moeda, dias_tolerancia=0):
    """
    Busca uma entrada bancária que corresponda aos critérios especificados.
    
    Args:
        data: Data da entrada (DD/MM/YYYY ou datetime.date)
        valor: Valor da entrada (Decimal)
        moeda: Moeda da entrada
        dias_tolerancia: Tolerância de dias na data
    
    Returns:
        Entradabanco ou None
    """
    
    # Calcula intervalo de datas
    if isinstance(data, str):
        data = datetime.strptime(data, '%d/%m/%Y').date()
    
    data_inicio = data - timedelta(days=dias_tolerancia)
    data_fim = data + timedelta(days=dias_tolerancia)
    
    # Busca entrada
    entrada = Entradabanco.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim,
        valor=Decimal(str(valor)),
        moeda=moeda
    ).exclude(
        dizimooferta__isnull=False  # Exclui se já tem dízimo vinculado
    ).first()
    
    return entrada


def buscar_dizimos_correspondentes(data, valor, moeda, dias_tolerancia=0):
    """
    Busca dízimos que correspondam aos critérios especificados.
    
    Args:
        data: Data do dízimo (DD/MM/YYYY ou datetime.date)
        valor: Valor do dízimo (Decimal)
        moeda: Moeda do dízimo
        dias_tolerancia: Tolerância de dias na data
    
    Returns:
        QuerySet de Dizimooferta
    """
    
    # Calcula intervalo de datas
    if isinstance(data, str):
        data = datetime.strptime(data, '%d/%m/%Y').date()
    
    data_inicio = data - timedelta(days=dias_tolerancia)
    data_fim = data + timedelta(days=dias_tolerancia)
    
    # Busca dízimos
    dizimos = Dizimooferta.objects.filter(
        datacorrespondente__gte=data_inicio,
        datacorrespondente__lte=data_fim,
        valor=Decimal(str(valor)),
        moeda=moeda,
        entradabanco__isnull=True  # Apenas não vinculados
    )
    
    return dizimos


def desvincular_dizimo(dizimo_id):
    """
    Remove a vinculação de um dízimo com uma entrada bancária.
    
    Args:
        dizimo_id: ID do dízimo
    
    Returns:
        bool: True se bem-sucedido
    """
    
    try:
        dizimo = Dizimooferta.objects.get(pk=dizimo_id)
        entrada_id = dizimo.entradabanco.id if dizimo.entradabanco else None
        dizimo.entradabanco = None
        dizimo.save()
        
        if entrada_id:
            print(f"✅ Dízimo {dizimo_id} desvinculado da Entrada {entrada_id}")
        
        return True
    except Dizimooferta.DoesNotExist:
        print(f"❌ Dízimo {dizimo_id} não encontrado")
        return False


def relatorio_vinculacao():
    """
    Gera um relatório da situação de vinculação de dízimos.
    
    Returns:
        dict com informações do relatório
    """
    
    total_dizimos = Dizimooferta.objects.count()
    dizimos_vinculados = Dizimooferta.objects.filter(entradabanco__isnull=False).count()
    dizimos_nao_vinculados = total_dizimos - dizimos_vinculados
    
    total_entradas = Entradabanco.objects.count()
    entradas_com_dizimo = Entradabanco.objects.filter(dizimooferta__isnull=False).distinct().count()
    entradas_sem_dizimo = total_entradas - entradas_com_dizimo
    
    return {
        'dizimos_total': total_dizimos,
        'dizimos_vinculados': dizimos_vinculados,
        'dizimos_nao_vinculados': dizimos_nao_vinculados,
        'taxa_vinculacao_dizimos': f"{(dizimos_vinculados/total_dizimos*100):.2f}%" if total_dizimos > 0 else "0%",
        'entradas_total': total_entradas,
        'entradas_com_dizimo': entradas_com_dizimo,
        'entradas_sem_dizimo': entradas_sem_dizimo,
        'taxa_vinculacao_entradas': f"{(entradas_com_dizimo/total_entradas*100):.2f}%" if total_entradas > 0 else "0%",
    }


# ============================================
# 🏪 FUNÇÕES PARA ENTRADAS DE CAIXA
# ============================================

def vincular_dizimos_com_caixa(dias_tolerancia=0, moeda=None, force=False):
    """
    Tenta vincular dízimos não vinculados com entradas de caixa existentes.
    
    Args:
        dias_tolerancia: Número de dias de tolerância na diferença de datas
        moeda: Se especificado, vincular apenas para uma moeda específica
        force: Se True, re-vincular mesmo registros já vinculados
    
    Returns:
        dict com estatísticas de vinculação
    """
    
    stats = {
        'total_processados': 0,
        'sucesso': 0,
        'erro': 0,
        'ja_vinculados': 0,
        'sem_correspondencia': 0
    }
    
    # Filtro base
    filtro_dizimos = Dizimooferta.objects.all()
    
    if not force:
        filtro_dizimos = filtro_dizimos.filter(entradacaixa__isnull=True)
    
    if moeda:
        filtro_dizimos = filtro_dizimos.filter(moeda=moeda)
    
    for dizimo in filtro_dizimos:
        stats['total_processados'] += 1
        
        if dizimo.entradacaixa and not force:
            stats['ja_vinculados'] += 1
            continue
        
        try:
            # Busca entrada de caixa correspondente
            entrada = buscar_entrada_caixa_correspondente(
                dizimo.datacorrespondente,
                dizimo.valor,
                dizimo.moeda,
                dias_tolerancia=dias_tolerancia
            )
            
            if entrada:
                dizimo.entradacaixa = entrada
                dizimo.save(update_fields=['entradacaixa'])
                stats['sucesso'] += 1
                print(f"✅ Dízimo {dizimo.id} vinculado com Caixa {entrada.id}")
            else:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            print(f"❌ Erro ao processar dízimo {dizimo.id}: {str(e)}")
    
    return stats


def vincular_caixas_existentes(dias_tolerancia=0, moeda=None, force=False):
    """
    Tenta vincular entradas de caixa não vinculadas com dízimos existentes.
    
    Args:
        dias_tolerancia: Número de dias de tolerância na diferença de datas
        moeda: Se especificado, vincular apenas para uma moeda específica
        force: Se True, vincular mesmo que já tenha dízimos vinculados
    
    Returns:
        dict com estatísticas de vinculação
    """
    
    stats = {
        'total_processados': 0,
        'sucesso': 0,
        'erro': 0,
        'ja_vinculados': 0,
        'sem_correspondencia': 0
    }
    
    # Filtro base
    filtro_entradas = Entradacaixa.objects.all()
    
    if moeda:
        filtro_entradas = filtro_entradas.filter(moeda=moeda)
    
    for entrada in filtro_entradas:
        stats['total_processados'] += 1
        
        # Verifica se já existe um dízimo vinculado
        dizimos_vinculados = Dizimooferta.objects.filter(entradacaixa=entrada)
        
        if dizimos_vinculados.exists() and not force:
            stats['ja_vinculados'] += 1
            continue
        
        try:
            # Busca dízimos correspondentes
            dizimos = buscar_dizimos_para_caixa(
                entrada.data,
                entrada.valor,
                entrada.moeda,
                dias_tolerancia=dias_tolerancia
            )
            
            for dizimo in dizimos:
                if not dizimo.entradacaixa or force:
                    dizimo.entradacaixa = entrada
                    dizimo.save(update_fields=['entradacaixa'])
                    stats['sucesso'] += 1
                    print(f"✅ Caixa {entrada.id} vinculada com Dízimo {dizimo.id}")
            
            if not dizimos:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            print(f"❌ Erro ao processar caixa {entrada.id}: {str(e)}")
    
    return stats


def buscar_entrada_caixa_correspondente(data, valor, moeda, dias_tolerancia=0):
    """
    Busca uma entrada de caixa que corresponda aos critérios especificados.
    
    Args:
        data: Data da entrada (DD/MM/YYYY ou datetime.date)
        valor: Valor da entrada (Decimal)
        moeda: Moeda da entrada
        dias_tolerancia: Tolerância de dias na data
    
    Returns:
        Entradacaixa ou None
    """
    
    # Calcula intervalo de datas
    if isinstance(data, str):
        data = datetime.strptime(data, '%d/%m/%Y').date()
    
    data_inicio = data - timedelta(days=dias_tolerancia)
    data_fim = data + timedelta(days=dias_tolerancia)
    
    # Busca entrada
    entrada = Entradacaixa.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim,
        valor=Decimal(str(valor)),
        moeda=moeda
    ).exclude(
        dizimooferta__isnull=False  # Exclui se já tem dízimo vinculado
    ).first()
    
    return entrada


def buscar_dizimos_para_caixa(data, valor, moeda, dias_tolerancia=0):
    """
    Busca dízimos que correspondam aos critérios especificados para caixa.
    
    Args:
        data: Data do dízimo (DD/MM/YYYY ou datetime.date)
        valor: Valor do dízimo (Decimal)
        moeda: Moeda do dízimo
        dias_tolerancia: Tolerância de dias na data
    
    Returns:
        QuerySet de Dizimooferta
    """
    
    # Calcula intervalo de datas
    if isinstance(data, str):
        data = datetime.strptime(data, '%d/%m/%Y').date()
    
    data_inicio = data - timedelta(days=dias_tolerancia)
    data_fim = data + timedelta(days=dias_tolerancia)
    
    # Busca dízimos
    dizimos = Dizimooferta.objects.filter(
        datacorrespondente__gte=data_inicio,
        datacorrespondente__lte=data_fim,
        valor=Decimal(str(valor)),
        moeda=moeda,
        entradacaixa__isnull=True  # Apenas não vinculados
    )
    
    return dizimos


def desvincular_dizimo_caixa(dizimo_id):
    """
    Remove a vinculação de um dízimo com uma entrada de caixa.
    
    Args:
        dizimo_id: ID do dízimo
    
    Returns:
        bool: True se bem-sucedido
    """
    
    try:
        dizimo = Dizimooferta.objects.get(pk=dizimo_id)
        caixa_id = dizimo.entradacaixa.id if dizimo.entradacaixa else None
        dizimo.entradacaixa = None
        dizimo.save()
        
        if caixa_id:
            print(f"✅ Dízimo {dizimo_id} desvinculado da Caixa {caixa_id}")
        
        return True
    except Dizimooferta.DoesNotExist:
        print(f"❌ Dízimo {dizimo_id} não encontrado")
        return False


def relatorio_vinculacao_completa():
    """
    Gera um relatório completo da situação de vinculação de dízimos 
    (banco + caixa).
    
    Returns:
        dict com informações detalhadas do relatório
    """
    
    total_dizimos = Dizimooferta.objects.count()
    dizimos_vinculados_banco = Dizimooferta.objects.filter(entradabanco__isnull=False).count()
    dizimos_vinculados_caixa = Dizimooferta.objects.filter(entradacaixa__isnull=False).count()
    dizimos_vinculados_total = Dizimooferta.objects.filter(
        Q(entradabanco__isnull=False) | Q(entradacaixa__isnull=False)
    ).count()
    dizimos_nao_vinculados = total_dizimos - dizimos_vinculados_total
    
    total_entradas_banco = Entradabanco.objects.count()
    entradas_banco_com_dizimo = Entradabanco.objects.filter(
        dizimooferta__isnull=False
    ).distinct().count()
    entradas_banco_sem_dizimo = total_entradas_banco - entradas_banco_com_dizimo
    
    total_caixas = Entradacaixa.objects.count()
    caixas_com_dizimo = Entradacaixa.objects.filter(
        dizimooferta__isnull=False
    ).distinct().count()
    caixas_sem_dizimo = total_caixas - caixas_com_dizimo
    
    return {
        'dizimos_total': total_dizimos,
        'dizimos_vinculados_banco': dizimos_vinculados_banco,
        'dizimos_vinculados_caixa': dizimos_vinculados_caixa,
        'dizimos_vinculados_total': dizimos_vinculados_total,
        'dizimos_nao_vinculados': dizimos_nao_vinculados,
        'taxa_vinculacao_dizimos': f"{(dizimos_vinculados_total/total_dizimos*100):.2f}%" if total_dizimos > 0 else "0%",
        
        'entradas_banco_total': total_entradas_banco,
        'entradas_banco_com_dizimo': entradas_banco_com_dizimo,
        'entradas_banco_sem_dizimo': entradas_banco_sem_dizimo,
        'taxa_banco': f"{(entradas_banco_com_dizimo/total_entradas_banco*100):.2f}%" if total_entradas_banco > 0 else "0%",
        
        'caixas_total': total_caixas,
        'caixas_com_dizimo': caixas_com_dizimo,
        'caixas_sem_dizimo': caixas_sem_dizimo,
        'taxa_caixa': f"{(caixas_com_dizimo/total_caixas*100):.2f}%" if total_caixas > 0 else "0%",
    }
