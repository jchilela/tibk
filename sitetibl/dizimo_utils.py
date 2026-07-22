# sitetibl/dizimo_utils.py
"""
Utilitários para vinculação automática de dízimos com entradas bancárias e de caixa.
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Q
from .models import Dizimooferta, Entrada

logger = logging.getLogger(__name__)


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
        filtro_dizimos = filtro_dizimos.filter(
            entrada__isnull=True,
        )
    
    if moeda:
        filtro_dizimos = filtro_dizimos.filter(moeda=moeda)
    
    for dizimo in filtro_dizimos:
        stats['total_processados'] += 1
        
        if dizimo.entrada:
            stats['ja_vinculados'] += 1
            continue

        if dizimo.entrada and not force:
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
                dizimo.entrada = entrada
                dizimo.save(update_fields=['entrada'])
                stats['sucesso'] += 1
                logger.info('Dizimo %s vinculado com Entrada %s', dizimo.id, entrada.id)
            else:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            logger.error('Erro ao processar dizimo %s: %s', dizimo.id, str(e))
    
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
    filtro_entradas = Entrada.objects.filter(tipo='banco')
    
    if moeda:
        filtro_entradas = filtro_entradas.filter(moeda=moeda)
    
    for entrada in filtro_entradas:
        stats['total_processados'] += 1
        
        # Verifica se já existe um dízimo vinculado
        dizimos_vinculados = Dizimooferta.objects.filter(entrada=entrada)
        
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
                if not dizimo.entrada or force:
                    dizimo.entrada = entrada
                    dizimo.save(update_fields=['entrada'])
                    stats['sucesso'] += 1
                    logger.info('Entrada %s vinculada com Dizimo %s', entrada.id, dizimo.id)
            
            if not dizimos:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            logger.error('Erro ao processar entrada %s: %s', entrada.id, str(e))
    
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
        Entrada ou None
    """
    
    # Calcula intervalo de datas
    if isinstance(data, str):
        data = datetime.strptime(data, '%d/%m/%Y').date()
    
    data_inicio = data - timedelta(days=dias_tolerancia)
    data_fim = data + timedelta(days=dias_tolerancia)
    
    # Busca entrada
    entrada = Entrada.objects.filter(
        tipo='banco',
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
        entrada__isnull=True,
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
        entrada_id = dizimo.entrada.id if dizimo.entrada else None
        dizimo.entrada = None
        dizimo.save()
        
        if entrada_id:
            logger.info('Dizimo %s desvinculado da Entrada %s', dizimo_id, entrada_id)
        
        return True
    except Dizimooferta.DoesNotExist:
        logger.warning('Dizimo %s nao encontrado', dizimo_id)
        return False


def relatorio_vinculacao():
    """
    Gera um relatório da situação de vinculação de dízimos.
    
    Returns:
        dict com informações do relatório
    """
    
    total_dizimos = Dizimooferta.objects.count()
    dizimos_vinculados = Dizimooferta.objects.filter(entrada__isnull=False).count()
    dizimos_nao_vinculados = total_dizimos - dizimos_vinculados
    
    total_entradas = Entrada.objects.filter(tipo='banco').count()
    entradas_com_dizimo = Entrada.objects.filter(tipo='banco', dizimooferta__isnull=False).distinct().count()
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
        filtro_dizimos = filtro_dizimos.filter(
            entrada__isnull=True,
        )
    
    if moeda:
        filtro_dizimos = filtro_dizimos.filter(moeda=moeda)
    
    for dizimo in filtro_dizimos:
        stats['total_processados'] += 1
        
        if dizimo.entrada:
            stats['ja_vinculados'] += 1
            continue

        if dizimo.entrada and not force:
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
                dizimo.entrada = entrada
                dizimo.save(update_fields=['entrada'])
                stats['sucesso'] += 1
                logger.info('Dizimo %s vinculado com Caixa %s', dizimo.id, entrada.id)
            else:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            logger.error('Erro ao processar dizimo %s: %s', dizimo.id, str(e))
    
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
    filtro_entradas = Entrada.objects.filter(tipo='caixa')
    
    if moeda:
        filtro_entradas = filtro_entradas.filter(moeda=moeda)
    
    for entrada in filtro_entradas:
        stats['total_processados'] += 1
        
        # Verifica se já existe um dízimo vinculado
        dizimos_vinculados = Dizimooferta.objects.filter(entrada=entrada)
        
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
                if not dizimo.entrada or force:
                    dizimo.entrada = entrada
                    dizimo.save(update_fields=['entrada'])
                    stats['sucesso'] += 1
                    logger.info('Caixa %s vinculada com Dizimo %s', entrada.id, dizimo.id)
            
            if not dizimos:
                stats['sem_correspondencia'] += 1
                
        except Exception as e:
            stats['erro'] += 1
            logger.error('Erro ao processar caixa %s: %s', entrada.id, str(e))
    
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
        Entrada ou None
    """
    
    # Calcula intervalo de datas
    if isinstance(data, str):
        data = datetime.strptime(data, '%d/%m/%Y').date()
    
    data_inicio = data - timedelta(days=dias_tolerancia)
    data_fim = data + timedelta(days=dias_tolerancia)
    
    # Busca entrada
    entrada = Entrada.objects.filter(
        tipo='caixa',
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
        entrada__isnull=True,
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
        caixa_id = dizimo.entrada.id if dizimo.entrada else None
        dizimo.entrada = None
        dizimo.save()
        
        if caixa_id:
            logger.info('Dizimo %s desvinculado da Caixa %s', dizimo_id, caixa_id)
        
        return True
    except Dizimooferta.DoesNotExist:
        logger.warning('Dizimo %s nao encontrado', dizimo_id)
        return False


def relatorio_vinculacao_completa():
    """
    Gera um relatório completo da situação de vinculação de dízimos 
    (banco + caixa).
    
    Returns:
        dict com informações detalhadas do relatório
    """
    
    total_dizimos = Dizimooferta.objects.count()
    dizimos_vinculados_banco = Dizimooferta.objects.filter(entrada__isnull=False, entrada__tipo='banco').count()
    dizimos_vinculados_caixa = Dizimooferta.objects.filter(entrada__isnull=False, entrada__tipo='caixa').count()
    dizimos_vinculados_total = Dizimooferta.objects.filter(
        entrada__isnull=False
    ).count()
    dizimos_nao_vinculados = total_dizimos - dizimos_vinculados_total
    
    total_entradas_banco = Entrada.objects.filter(tipo='banco').count()
    entradas_banco_com_dizimo = Entrada.objects.filter(
        tipo='banco', dizimooferta__isnull=False
    ).distinct().count()
    entradas_banco_sem_dizimo = total_entradas_banco - entradas_banco_com_dizimo
    
    total_caixas = Entrada.objects.filter(tipo='caixa').count()
    caixas_com_dizimo = Entrada.objects.filter(
        tipo='caixa', dizimooferta__isnull=False
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
