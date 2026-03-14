# Create your views here.
from django.contrib import admin, messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaulttags import register
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from datetime import date
from django import forms
from django.urls import reverse
from django.template import loader
from django.db.models import Sum, Count, F, Q
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, LongTable
from reportlab.lib import colors
import os
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncMonth
import json
from django.http import JsonResponse
from django.utils.timezone import now
from collections import OrderedDict
from django.db.models.functions import ExtractWeekDay
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#from django.db.models import Count

# Register your models here.
#from gestaoinfra.models import Contacto
from sitetibl.models import Irmao
from sitetibl.models import Municipio
from sitetibl.models import TipoOferta
from sitetibl.models import Ajuda
from sitetibl.models import Cestabasica
from sitetibl.models import Banco
from sitetibl.models import Contabancaria
from sitetibl.models import Actividade
from sitetibl.models import Departamento
from sitetibl.models import ComposicaoCesta
from sitetibl.models import Funcao
from sitetibl.models import Listaactividades
from sitetibl.models import Mandato
from sitetibl.models import Escala
from sitetibl.models import Rubricaentrada
from sitetibl.models import Rubricasaida
from sitetibl.models import Saidacaixa
from sitetibl.models import Saidabanco
from sitetibl.models import Entradacaixa
from sitetibl.models import Entradabanco
from sitetibl.models import Dizimooferta
from sitetibl.models import Pagamentoservico
from sitetibl.models import Gruporubrica
from sitetibl.models import Servico
from sitetibl.models import Tipoajuda
from sitetibl.models import RelatorioSemanalCelula
from sitetibl.models import PedidoSaida
from sitetibl.models import Anuncio
from sitetibl.forms import OrcamentoDepartamento
from sitetibl.forms import InventarioPatrimonio
from sitetibl.forms import ConteudoEnsino
from sitetibl.forms import EnvioMensagem

from sitetibl.serializers import EscalaSerializer

from sitetibl.forms import IrmaoForm
from sitetibl.forms import AjudaForm
from sitetibl.forms import CestabasicaForm
from sitetibl.forms import BancoForm
from sitetibl.forms import ContabancariaForm
from sitetibl.forms import ActividadeForm
from sitetibl.forms import DepartamentoForm
from sitetibl.forms import MandatoForm
from sitetibl.forms import EscalaForm
from sitetibl.forms import SaidacaixaForm
from sitetibl.forms import SaidabancoForm
from sitetibl.forms import EntradacaixaForm
from sitetibl.forms import EntradabancoForm
from sitetibl.forms import DizimoofertaForm
from sitetibl.forms import PagamentoservicoForm
from sitetibl.forms import GruporubricaForm
from sitetibl.forms import ServicoForm
from sitetibl.forms import RelatorioSemanalCelulaForm
from sitetibl.forms import PedidoSaidaForm
from sitetibl.forms import PedidoSaidaUpdateForm
from sitetibl.forms import OrcamentoDepartamentoForm
from sitetibl.forms import InventarioPatrimonioForm
from sitetibl.forms import ConteudoEnsinoForm
from sitetibl.forms import EnvioMensagemForm
from sitetibl.forms import MeuPerfilForm, MeuPerfilPasswordForm
from sitetibl.forms import ActividadesRecorrentesForm
from django.contrib.auth import update_session_auth_hash
from datetime import timedelta

PROVINCIAS = {'BNG':'Bengo','BGL':'Benguela','BIE':'Bié','CAB':'Cabinda','CNE':'Cunene','HMB':'Huambo','HLA':'Huila','KKG':'Kuando kubango','KZN':'Kuanza Norte','KZS':'Kuanza Sul','LDA':'Luanda','LDN':'Lunda Norte','LDS':'Lunda Sul','MLG':'Malange','MXC':'Moxico','NMB':'Namibe','UGE':'Uige','ZAR':'Zaire'}

MOEDA = {'AKZ':'Kwanza','USD':'USA Dólar','EU':'Euro','R':'Reais','RAN':'ZA Rands','NAMD':'Dólar Namibiano', 'LB':'Libra Inglesa'}
MESES = {'1':'Janeiro','2':'Fevereiro','3':'Março','4':'Abril','5':'Maio','6':'Junho','7':'Julho','8':'Agosto','9':'Setembro','10':'Outubro','11':'Novembro','12':'Dezembro'}
TIPO = {'1':'Saude','2':'Falecimento','3':'Propina','4':'Cesta básica','5':'Casamento','6':'Outra'}

def comeco(request):
    return render(request, 'index.html')


@login_required
def api_municipios(request, provincia_id):
    """Retorna municípios de uma província em JSON (para cascading dropdown)."""
    municipios = Municipio.objects.filter(
        provincia_id=provincia_id
    ).order_by('nome').values('id', 'nome')
    return JsonResponse(list(municipios), safe=False)


@login_required
def api_funcoes_por_actividade(request, actividade_id):
    """Retorna funções relevantes para o departamento da actividade + genéricas."""
    actividade = get_object_or_404(Actividade, id=actividade_id)
    if actividade.departamento_id:
        funcoes = Funcao.objects.filter(
            Q(departamento_id=actividade.departamento_id) | Q(departamento__isnull=True)
        ).order_by('designacao')
    else:
        funcoes = Funcao.objects.all().order_by('designacao')
    data = [{'id': f.id, 'designacao': f.designacao} for f in funcoes]
    return JsonResponse(data, safe=False)


def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

@login_required
def mostraGestao(request,gestaoescolhida,pagina):
    lista = {'escalas' : Escala.objects.select_related('irmao', 'actividade', 'funcao'), 
             'mandatos': Mandato.objects.select_related('irmao', 'departamento'), 
             'irmaos': Irmao.objects.select_related('celula', 'localcongregacao', 'provincia', 'municipio'), 
             'ajudas': Ajuda.objects.select_related('ajuda', 'beneficiario', 'patrocinador', 'cesta'), 
             'cestas': Cestabasica.objects.select_related('saiudobanco', 'saiudacaixa'), 
             'bancos': Banco.objects, 
             'contasbancarias' : Contabancaria.objects.select_related('banco', 'proprietario', 'instituicao'), 
             'actividades' : Actividade.objects.select_related('designacao', 'localactividade'), 
             'departamentos' : Departamento.objects.select_related('lider_departamento', 'vice_lider_departamento'),
             'entradabancos' : Entradabanco.objects.select_related('contaaacreditar', 'rubrica', 'responsavel'), 
             'saidabancos' : Saidabanco.objects.select_related('conta', 'rubrica', 'responsavel'), 
             'entradascaixa' : Entradacaixa.objects.select_related('responsavel', 'rubrica'), 
             'saidascaixa' : Saidacaixa.objects.select_related('responsavel', 'rubrica'), 
             'dizimosofertas' : Dizimooferta.objects.select_related('irmao', 'tipooferta', 'actividade'),
             'relatoriosemanalcelula' : RelatorioSemanalCelula.objects.select_related('nome_celula', 'lider_responsavel'), 
             'pedidosaida' : PedidoSaida.objects.select_related('departamento', 'requerente', 'status_de_aprovacao', 'aprovador'),
             'orcamentodepartamento': OrcamentoDepartamento.objects.select_related('departamento', 'moeda'),
             'inventariopatrimonio': InventarioPatrimonio.objects.select_related('categoria_patrimonio', 'responsavel', 'estado'),
             'conteudoensino': ConteudoEnsino.objects.select_related('autor'),
             'enviomensagem': EnvioMensagem.objects.select_related('quemenviou'),
             }
    if gestaoescolhida == 'departamentos':
        resultado = (
            lista[gestaoescolhida]
            .all()
            .annotate(total_integrantes=Count('integrantes', distinct=True))
            .order_by('designacao')
        )
    elif gestaoescolhida == 'contasbancarias':
        nomev = request.GET.get('nomev', '').strip()
        apelidov = request.GET.get('apelidov', '').strip()
        bancov = request.GET.get('bancov', '').strip()
        numerocontav = request.GET.get('numerocontav', '').strip()
        ibanv = request.GET.get('ibanv', '').strip()
        moedav = request.GET.get('moedav', '').strip()

        kwargs = {
            'is_active': True,
            'proprietario__nome__icontains': nomev,
            'proprietario__apelido__icontains': apelidov,
            'banco__designacao__icontains': bancov,
            'numeroconta__icontains': numerocontav,
            'iban__icontains': ibanv,
        }
        if moedav:
            kwargs['moeda'] = moedav

        resultado = lista[gestaoescolhida].filter(**kwargs).order_by('id')
    elif (gestaoescolhida == 'irmaos'):
        resultado = lista[gestaoescolhida].prefetch_related('mandato_set__departamento').all().order_by('nome','outrosnomes')
    else:
        resultado = lista[gestaoescolhida].all().order_by('id') 
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    if (gestaoescolhida == 'ajudas') or (gestaoescolhida == 'cestas') or (gestaoescolhida == 'actividades'):
        context = { 'bb':paginaresultado, 'listameses' : MESES, 'tipoajuda' : Tipoajuda.objects.values('id','designacao'), 'listafuncoes' : Funcao.objects.values('id','designacao'), 'listaactividades' : Listaactividades.objects.values('id','designacao')}
    elif gestaoescolhida == 'departamentos':
        context = { 'bb':paginaresultado, 'listadepartamentos' : Departamento.objects.values('id','designacao'), 'funcao_choices': Mandato.FUNCAO_CHOICES}
    elif gestaoescolhida == 'contasbancarias':
        context = {
            'bb': paginaresultado,
            'listamoedas': MOEDA.items(),
            'filtro_nomev': request.GET.get('nomev', ''),
            'filtro_apelidov': request.GET.get('apelidov', ''),
            'filtro_bancov': request.GET.get('bancov', ''),
            'filtro_numerocontav': request.GET.get('numerocontav', ''),
            'filtro_ibanv': request.GET.get('ibanv', ''),
            'filtro_moedav': request.GET.get('moedav', ''),
        }
    elif (gestaoescolhida == 'entradascaixa') or (gestaoescolhida == 'saidascaixa') or (gestaoescolhida == 'entradabancos') or (gestaoescolhida == 'saidabancos'):
        context = { 'bb':paginaresultado, 'listarubricasentrada' : Rubricaentrada.objects.values('id', 'designacao'), 'listarubricassaida' : Rubricasaida.objects.values('id', 'designacao'), 'listameses' : MESES, 'listacontasigreja' : Contabancaria.objects.values('id','numeroconta','instituicao_id').filter(instituicao_id=1) }
    elif gestaoescolhida == 'irmaos':
        context = { 'bb':paginaresultado, 'listamunicipios': Municipio.objects.select_related('provincia').order_by('provincia__nome', 'nome') }
    else:
        context = { 'bb':paginaresultado, 'listameses' : MESES }

    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, gestaoescolhida + '.html', context)


@login_required
def mostraActualizacao(request, gestaoescolhida, id):
    lista = {'escalas' : Escala, 
             'mandatos': Mandato, 
             'irmaos':Irmao, 
             'ajudas':Ajuda, 
             'cestas': Cestabasica, 
             'bancos': Banco, 
             'contasbancarias' : Contabancaria, 
             'actividades' : Actividade, 
             'departamentos' : Departamento, 
             'entradabancos' : Entradabanco, 
             'saidabancos' : Saidabanco, 
             'entradascaixa' : Entradacaixa, 
             'saidascaixa' : Saidacaixa, 
             'dizimosofertas' : Dizimooferta,
             'relatoriosemanalcelula' : RelatorioSemanalCelula, 
             'pedidosaida' : PedidoSaida,
             'orcamentodepartamento': OrcamentoDepartamento,
             'inventariopatrimonio': InventarioPatrimonio,
             'conteudoensino':ConteudoEnsino,
             'enviomensagem':EnvioMensagem,
             

              }
    listaformularios = {'escalas' : EscalaForm, 
                        'mandatos': MandatoForm, 
                        'irmaos':IrmaoForm, 
                        'ajudas':AjudaForm, 
                        'cestas': CestabasicaForm, 
                        'bancos': BancoForm, 
                        'contasbancarias' : ContabancariaForm, 
                        'actividades' : ActividadeForm, 
                        'departamentos' : DepartamentoForm, 
                        'entradabancos' : EntradabancoForm, 
                        'saidabancos' : SaidabancoForm, 
                        'entradascaixa' : EntradacaixaForm, 
                        'saidascaixa' : SaidacaixaForm, 
                        'dizimosofertas' : DizimoofertaForm, 
                        'relatoriosemanalcelula' : RelatorioSemanalCelulaForm,
                        'pedidosaida' : PedidoSaidaUpdateForm,
                        'orcamentodepartamento' : OrcamentoDepartamentoForm,
                        'inventariopatrimonio': InventarioPatrimonioForm,
                        'conteudoensino':ConteudoEnsinoForm,
                        'enviomensagem':EnvioMensagemForm,
                        }
    
    model = lista[gestaoescolhida]
  
    # 🔐 verificação dinâmica
    perm = f'{model._meta.app_label}.change_{model._meta.model_name}'
    if not request.user.has_perm(perm):
        messages.error(request, 'Acesso negado! Você não tem permissão para actualizar registros.')
        return redirect('index')

    registo = get_object_or_404(model, id=id)

    # 🔐 Verificação de propriedade para actividades
    if gestaoescolhida == 'actividades':
        papel_elevado = request.user.has_perm('sitetibl.change_mandato')
        if not papel_elevado:
            pode_editar = (registo.criado_por is not None and registo.criado_por == request.user)
            if not pode_editar and registo.departamento_id:
                irmao_logado = Irmao.objects.filter(user=request.user).first()
                if irmao_logado:
                    pode_editar = Departamento.objects.filter(
                        Q(lider_departamento=irmao_logado) | Q(vice_lider_departamento=irmao_logado),
                        id=registo.departamento_id,
                    ).exists()
            if not pode_editar:
                messages.error(request, 'Só pode editar actividades que criou ou do seu departamento.')
                return redirect('index')

    if request.method == 'GET':
        form = listaformularios[gestaoescolhida](instance=registo)
        return render(request, 'formulario_actualizacao.html', {
            'formulario': form,
            'id': id
        })

    elif request.method == 'POST':
        formulario = listaformularios[gestaoescolhida](
            request.POST,
            request.FILES,
            instance=registo
        )

        if formulario.is_valid():
            obj = formulario.save(commit=False)

            # ⚠️ Verificação de conflito de horário para actividades
            if gestaoescolhida == 'actividades':
                data = formulario.cleaned_data['data']
                inicio = formulario.cleaned_data['inicio']
                fim = formulario.cleaned_data['fim']
                conflitos = Actividade.objects.filter(
                    data=data, inicio__lt=fim, fim__gt=inicio
                ).exclude(id=registo.id)
                mesma_data_diferente = Actividade.objects.filter(
                    data=data
                ).exclude(id=registo.id).exclude(inicio__lt=fim, fim__gt=inicio)
                if conflitos.exists():
                    primeiro = conflitos.first()
                    messages.error(
                        request,
                        f'Conflito de horário: já existe uma actividade "{primeiro.designacao}" '
                        f'das {primeiro.inicio} às {primeiro.fim} neste dia com horário sobrepóvel.'
                    )
                    return render(request, 'formulario_actualizacao.html', {'formulario': formulario, 'id': id})
                elif mesma_data_diferente.exists():
                    messages.warning(
                        request,
                        'Já existe outra actividade neste dia com horário diferente. '
                        'Se for num local diferente, pode prosseguir normalmente.'
                    )

            if gestaoescolhida == 'pedidosaida':
                # só define aprovador se o estado NÃO for nulo
                if obj.status_de_aprovacao is not None:
                    try:
                        obj.aprovador = Irmao.objects.get(user=request.user)
                    except Irmao.DoesNotExist:
                        messages.error(
                            request,
                            'O utilizador logado não está associado a nenhum Irmão.'
                        )
                        return render(request, 'formulario_actualizacao.html', {
                            'formulario': formulario
                        })
                else:
                    # se o estado for null, garante que o aprovador também fica null
                    obj.aprovador = None

            obj.save()
            messages.success(request, 'Actualização foi bem sucedida')
            return HttpResponseRedirect(reverse('index'))

        else:
            messages.error(request, 'Foram encontrados erros ao preencher o formulário.')
            return render(request, 'formulario_actualizacao.html', {
                'formulario': formulario
            })

@login_required
@login_required
def mostraDetalhe(request, gestaoescolhida, identificador):
    lista_qs = {
        'irmaos': Irmao.objects.select_related('celula', 'localcongregacao', 'provincia', 'municipio'),
        'ajudas': Ajuda.objects.select_related('ajuda', 'beneficiario', 'patrocinador', 'cesta'),
        'cestas': Cestabasica.objects.select_related('saiudobanco', 'saiudacaixa'),
        'bancos': Banco.objects,
        'contasbancarias': Contabancaria.objects.select_related('banco', 'proprietario', 'instituicao'),
        'actividades': Actividade.objects.select_related('designacao', 'localactividade'),
        'departamentos': Departamento.objects.select_related('lider_departamento', 'vice_lider_departamento'),
        'entradabancos': Entradabanco.objects.select_related('contaaacreditar', 'rubrica', 'responsavel'),
        'saidabancos': Saidabanco.objects.select_related('conta', 'rubrica', 'responsavel'),
        'entradascaixa': Entradacaixa.objects.select_related('responsavel', 'rubrica'),
        'saidascaixa': Saidacaixa.objects.select_related('responsavel', 'rubrica'),
        'dizimosofertas': Dizimooferta.objects.select_related('irmao', 'tipooferta', 'actividade'),
        'relatoriosemanalcelula': RelatorioSemanalCelula.objects.select_related('nome_celula', 'lider_responsavel'),
        'pedidosaida': PedidoSaida.objects.select_related('departamento', 'requerente', 'status_de_aprovacao', 'aprovador'),
        'orcamentodepartamento': OrcamentoDepartamento.objects.select_related('departamento', 'moeda'),
        'inventariopatrimonio': InventarioPatrimonio.objects.select_related('categoria_patrimonio', 'responsavel', 'estado'),
        'conteudoensino': ConteudoEnsino.objects.select_related('autor'),
        'enviomensagem': EnvioMensagem.objects.select_related('quemenviou'),
        'escalas': Escala.objects.select_related('irmao', 'actividade', 'funcao'),
    }
    queryset = lista_qs.get(gestaoescolhida)
    if queryset is None:
        return redirect('index')

    # Avoid rendering blank detail pages when an invalid id is requested.
    registo = get_object_or_404(queryset, id=identificador)
    registoachado = [registo]
    ficheirodetalhado = gestaoescolhida + 'detalhado.html'
    if gestaoescolhida == 'cestas':
        detalhecestas = ComposicaoCesta.objects.filter(cesta = identificador)
        context = {}
        while detalhecestas.exists():
            totalcestasajuda = Ajuda.objects.filter(cesta = identificador).count()
            montantedisponibilizado = Cestabasica.objects.values('valordisponibilizado').filter( id = identificador)
            for valor in montantedisponibilizado:
                a = valor['valordisponibilizado']
            subtotal = detalhecestas.all().annotate(subsoma = F('quantidade') * F('precounitario'))
            total = subtotal.aggregate(soma = Sum('subsoma')).get('soma')
            valorgasto = total * totalcestasajuda
            cestasremanescentes = int((a - valorgasto)/total)
            context = {'registoachado' : registoachado, 'gestaoescolhida' : gestaoescolhida, 'detalhecestas' : subtotal, 'total' : total, 'totalcestasajuda' : totalcestasajuda, 'montantedisponibilizado' : a, 'valorgasto' : valorgasto, 'cestasremanescentes' : cestasremanescentes}
    elif gestaoescolhida == 'actividades':
        escalas_da_actividade = Escala.objects.filter(actividade_id=identificador).select_related('irmao', 'funcao').order_by('funcao__designacao')
        todas_funcoes = Funcao.objects.all().order_by('designacao')
        todos_irmaos = Irmao.objects.select_related('celula', 'localcongregacao').order_by('nome', 'apelido')
        context = {
            'registoachado': registoachado, 
            'gestaoescolhida': gestaoescolhida, 
            'escalas_da_actividade': escalas_da_actividade,
            'todas_funcoes': todas_funcoes,
            'todos_irmaos': todos_irmaos
        }
    elif gestaoescolhida == 'departamentos':
        mandatos_departamento = (
            Mandato.objects
            .select_related('irmao')
            .filter(departamento_id=identificador)
            .order_by('funcao', 'irmao__nome', 'irmao__apelido')
        )
        irmao_logado = Irmao.objects.filter(user=request.user).first()
        lidera_departamento = (
            irmao_logado is not None
            and (registo.lider_departamento_id == irmao_logado.id
                 or registo.vice_lider_departamento_id == irmao_logado.id)
        )
        # Papéis elevados (Pastor/Secretaria/Admin) gerem qualquer dept;
        # LD/VLD só gere o departamento onde é líder ou vice-líder.
        papel_elevado_dept = request.user.has_perm('sitetibl.change_mandato')
        pode_gerir_membros = lidera_departamento or papel_elevado_dept

        if request.method == 'POST':
            if not pode_gerir_membros:
                messages.error(request, 'Apenas o lider do departamento ou um administrador pode gerir membros.')
                return HttpResponseRedirect(reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador]))

            action = request.POST.get('action', '').strip()
            if action == 'add_member':
                irmao_id = request.POST.get('irmao_id', '').strip()
                funcao = request.POST.get('funcao', 'membro').strip()
                funcoes_validas = [c[0] for c in Mandato.FUNCAO_CHOICES]
                if funcao not in funcoes_validas:
                    funcao = 'membro'

                if not irmao_id:
                    messages.error(request, 'Seleccione um irmão para adicionar ao departamento.')
                else:
                    mandato_existente = Mandato.objects.filter(
                        departamento_id=identificador,
                        irmao_id=irmao_id,
                    ).first()

                    # Funções exclusivas: só pode haver um por departamento
                    FUNCOES_EXCLUSIVAS = {'lider', 'vice_lider', 'secretario', 'tesoureiro', 'coordenador'}
                    if funcao in FUNCOES_EXCLUSIVAS:
                        ocupante = Mandato.objects.filter(
                            departamento_id=identificador,
                            funcao=funcao,
                        ).select_related('irmao').first()
                        if ocupante and str(ocupante.irmao_id) != irmao_id:
                            nome_anterior = f'{ocupante.irmao.nome} {ocupante.irmao.apelido}'
                            ocupante.funcao = 'membro'
                            ocupante.save(update_fields=['funcao'])
                            funcao_display = dict(Mandato.FUNCAO_CHOICES).get(funcao, funcao)
                            messages.warning(
                                request,
                                f'{nome_anterior} deixou de ser {funcao_display} e voltou a ser Membro.'
                            )

                    if mandato_existente:
                        # Membro já existe — actualizar a função
                        if mandato_existente.funcao != funcao:
                            mandato_existente.funcao = funcao
                            mandato_existente.save(update_fields=['funcao'])
                            messages.success(request, 'Função do membro actualizada com sucesso.')
                        else:
                            messages.warning(request, 'Este membro já pertence a este departamento com essa função.')
                    else:
                        try:
                            Mandato.objects.create(
                                departamento_id=identificador,
                                irmao_id=irmao_id,
                                funcao=funcao,
                            )
                            messages.success(request, 'Membro adicionado ao departamento com sucesso.')
                        except IntegrityError:
                            messages.error(request, 'Não foi possível adicionar o membro. Verifique os dados informados.')

            elif action == 'remove_member':
                mandato_id = request.POST.get('mandato_id', '').strip()
                mandato = Mandato.objects.filter(id=mandato_id, departamento_id=identificador).first()
                if mandato is None:
                    messages.error(request, 'Registo de mandato nao encontrado para este departamento.')
                else:
                    # Limpar FK do Departamento se removendo lider/vice_lider
                    if mandato.funcao == 'lider':
                        Departamento.objects.filter(pk=identificador, lider_departamento=mandato.irmao).update(lider_departamento=None)
                    elif mandato.funcao == 'vice_lider':
                        Departamento.objects.filter(pk=identificador, vice_lider_departamento=mandato.irmao).update(vice_lider_departamento=None)
                    mandato.delete()
                    messages.success(request, 'Membro removido do departamento com sucesso.')

            elif action == 'add_funcao':
                if not (lidera_departamento or request.user.has_perm('sitetibl.add_funcao')):
                    messages.error(request, 'Sem permissão para adicionar funções.')
                else:
                    nome_funcao = request.POST.get('nome_funcao', '').strip()
                    if not nome_funcao:
                        messages.error(request, 'O nome da função não pode estar vazio.')
                    elif Funcao.objects.filter(designacao=nome_funcao, departamento_id=identificador).exists():
                        messages.warning(request, 'Esta função já existe neste departamento.')
                    else:
                        Funcao.objects.create(designacao=nome_funcao, departamento_id=identificador)
                        messages.success(request, f'Função "{nome_funcao}" adicionada ao departamento.')

            elif action == 'remove_funcao':
                if not (lidera_departamento or request.user.has_perm('sitetibl.delete_funcao')):
                    messages.error(request, 'Sem permissão para remover funções.')
                else:
                    funcao_id = request.POST.get('funcao_id', '').strip()
                    func = Funcao.objects.filter(id=funcao_id, departamento_id=identificador).first()
                    if func is None:
                        messages.error(request, 'Função não encontrada neste departamento.')
                    elif Escala.objects.filter(funcao=func).exists():
                        messages.warning(request, f'Não é possível remover "{func.designacao}" porque já está em uso em escalas.')
                    else:
                        func.delete()
                        messages.success(request, 'Função removida do departamento.')

            return HttpResponseRedirect(reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador]))

        funcoes_departamento = Funcao.objects.filter(departamento_id=identificador).order_by('designacao')
        pode_gerir_funcoes = (
            lidera_departamento
            or request.user.has_perm('sitetibl.add_funcao')
        )

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'mandatos_departamento': mandatos_departamento,
            'todos_irmaos': Irmao.objects.order_by('nome', 'apelido'),
            'funcao_choices': Mandato.FUNCAO_CHOICES,
            'pode_gerir_membros': pode_gerir_membros,
            'funcoes_departamento': funcoes_departamento,
            'pode_gerir_funcoes': pode_gerir_funcoes,
        }
    elif gestaoescolhida == 'contasbancarias':
        entradas_conta = (
            Entradabanco.objects
            .select_related('rubrica', 'responsavel', 'contaorigem')
            .filter(contaaacreditar_id=identificador)
            .order_by('-data', '-hora')
        )
        saidas_conta = (
            Saidabanco.objects
            .select_related('rubrica', 'responsavel', 'contaaacreditar')
            .filter(conta_id=identificador)
            .order_by('-data', '-hora')
        )
        total_entradas = entradas_conta.aggregate(total=Sum('valor')).get('total') or 0
        total_saidas = saidas_conta.aggregate(total=Sum('valor')).get('total') or 0

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_conta': entradas_conta[:8],
            'saidas_conta': saidas_conta[:8],
            'total_entradas_conta': total_entradas,
            'total_saidas_conta': total_saidas,
            'saldo_movimento': total_entradas - total_saidas,
        }
    elif gestaoescolhida == 'bancos':
        contas_banco = (
            Contabancaria.objects
            .select_related('proprietario', 'instituicao')
            .filter(banco_id=identificador)
            .order_by('numeroconta')
        )
        entradas_banco = (
            Entradabanco.objects
            .select_related('contaaacreditar', 'rubrica')
            .filter(contaaacreditar__banco_id=identificador)
            .order_by('-data', '-hora')[:6]
        )
        saidas_banco = (
            Saidabanco.objects
            .select_related('conta', 'rubrica')
            .filter(conta__banco_id=identificador)
            .order_by('-data', '-hora')[:6]
        )
        total_contas = contas_banco.count()
        total_saldo_banco = sum(conta.saldo_actual() for conta in contas_banco)

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'contas_banco': contas_banco,
            'entradas_banco': entradas_banco,
            'saidas_banco': saidas_banco,
            'total_contas_banco': total_contas,
            'total_saldo_banco': total_saldo_banco,
        }
    elif gestaoescolhida == 'entradabancos':
        conta_destino_id = registo.contaaacreditar_id
        entradas_relacionadas = Entradabanco.objects.none()
        saidas_relacionadas = Saidabanco.objects.none()
        if conta_destino_id:
            entradas_relacionadas = (
                Entradabanco.objects
                .select_related('rubrica')
                .filter(contaaacreditar_id=conta_destino_id)
                .exclude(id=identificador)
                .order_by('-data', '-hora')[:6]
            )
            saidas_relacionadas = (
                Saidabanco.objects
                .select_related('rubrica')
                .filter(conta_id=conta_destino_id)
                .order_by('-data', '-hora')[:6]
            )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_relacionadas': entradas_relacionadas,
            'saidas_relacionadas': saidas_relacionadas,
        }
    elif gestaoescolhida == 'saidabancos':
        conta_origem_id = registo.conta_id
        entradas_relacionadas = Entradabanco.objects.none()
        saidas_relacionadas = Saidabanco.objects.none()
        if conta_origem_id:
            entradas_relacionadas = (
                Entradabanco.objects
                .select_related('rubrica')
                .filter(contaaacreditar_id=conta_origem_id)
                .order_by('-data', '-hora')[:6]
            )
            saidas_relacionadas = (
                Saidabanco.objects
                .select_related('rubrica')
                .filter(conta_id=conta_origem_id)
                .exclude(id=identificador)
                .order_by('-data', '-hora')[:6]
            )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_relacionadas': entradas_relacionadas,
            'saidas_relacionadas': saidas_relacionadas,
        }
    elif gestaoescolhida == 'entradascaixa':
        entradas_relacionadas = (
            Entradacaixa.objects
            .select_related('rubrica', 'responsavel')
            .filter(rubrica_id=registo.rubrica_id)
            .exclude(id=identificador)
            .order_by('-data', '-hora')[:6]
        )
        saidas_relacionadas = (
            Saidacaixa.objects
            .select_related('rubrica', 'responsavel')
            .filter(responsavel_id=registo.responsavel_id)
            .order_by('-data', '-hora')[:6]
        )
        total_entradas_rubrica = (
            Entradacaixa.objects
            .filter(rubrica_id=registo.rubrica_id)
            .aggregate(total=Sum('valor'))
            .get('total') or 0
        )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_relacionadas': entradas_relacionadas,
            'saidas_relacionadas': saidas_relacionadas,
            'total_entradas_rubrica': total_entradas_rubrica,
        }
    elif gestaoescolhida == 'saidascaixa':
        saidas_relacionadas = (
            Saidacaixa.objects
            .select_related('rubrica', 'responsavel')
            .filter(rubrica_id=registo.rubrica_id)
            .exclude(id=identificador)
            .order_by('-data', '-hora')[:6]
        )
        entradas_relacionadas = (
            Entradacaixa.objects
            .select_related('rubrica', 'responsavel')
            .filter(responsavel_id=registo.responsavel_id)
            .order_by('-data', '-hora')[:6]
        )
        total_saidas_rubrica = (
            Saidacaixa.objects
            .filter(rubrica_id=registo.rubrica_id)
            .aggregate(total=Sum('valor'))
            .get('total') or 0
        )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_relacionadas': entradas_relacionadas,
            'saidas_relacionadas': saidas_relacionadas,
            'total_saidas_rubrica': total_saidas_rubrica,
        }
    elif gestaoescolhida == 'irmaos':
        mandatos_irmao = (
            Mandato.objects
            .select_related('departamento')
            .filter(irmao_id=identificador)
            .order_by('departamento__designacao')
        )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'mandatos_irmao': mandatos_irmao,
        }
    else:
        context = {'registoachado' : registoachado, 'gestaoescolhida' : gestaoescolhida}
    return render(request, ficheirodetalhado, context)

@login_required
def mostraEliminacao(request, gestaoescolhida, id):
    lista = {'irmaos':Irmao, 
             'ajudas':Ajuda, 
             'cestas': Cestabasica, 
             'bancos': Banco, 
             'contasbancarias' : Contabancaria, 
             'actividades' : Actividade, 
             'departamentos' : Departamento, 
             'entradabancos' : Entradabanco, 
             'saidabancos' : Saidabanco, 
             'entradascaixa' : Entradacaixa, 
             'saidascaixa' : Saidacaixa, 
             'dizimosofertas' : Dizimooferta,
             'relatoriosemanalcelula' : RelatorioSemanalCelula, 
             'pedidosaida' : PedidoSaida,
             'orcamentodepartamento': OrcamentoDepartamento,
             'inventariopatrimonio': InventarioPatrimonio,
             'conteudoensino':ConteudoEnsino,
             'enviomensagem':EnvioMensagem,
             'escalas':Escala,
             }
    model = lista.get(gestaoescolhida)

    # 🔐 verificação dinâmica
    perm = f'{model._meta.app_label}.delete_{model._meta.model_name}'
    if not request.user.has_perm(perm):
        messages.error(request, 'Acesso negado! Você não tem permissão para eliminar registros.')
        return redirect('index')

    registo = get_object_or_404(model, id=id)

    # 🔐 Verificação de propriedade para actividades
    if gestaoescolhida == 'actividades':
        papel_elevado = request.user.has_perm('sitetibl.change_mandato')
        if not papel_elevado:
            pode_eliminar = (registo.criado_por is not None and registo.criado_por == request.user)
            if not pode_eliminar and registo.departamento_id:
                irmao_logado = Irmao.objects.filter(user=request.user).first()
                if irmao_logado:
                    pode_eliminar = Departamento.objects.filter(
                        Q(lider_departamento=irmao_logado) | Q(vice_lider_departamento=irmao_logado),
                        id=registo.departamento_id,
                    ).exists()
            if not pode_eliminar:
                messages.error(request, 'Só pode eliminar actividades que criou ou do seu departamento.')
                return redirect('index')

    if request.method == 'POST':
        registo.delete()
        messages.success(request, 'Eliminação foi bem sucedida')
        return redirect('index')

    # GET → mostra confirmação
    return render(request, 'confirmar_eliminacao.html', {
        'registo': registo,
        'gestao': gestaoescolhida
    })

@login_required
def mostraCriacao(request, gestaoescolhida):
    listaformularios = {'escalas' : EscalaForm, 
                        'mandatos': MandatoForm, 
                        'irmaos':IrmaoForm, 
                        'ajudas':AjudaForm, 
                        'cestas': CestabasicaForm, 
                        'bancos': BancoForm, 
                        'contasbancarias' : ContabancariaForm, 
                        'actividades' : ActividadeForm, 
                        'departamentos' : DepartamentoForm, 
                        'entradabancos' : EntradabancoForm, 
                        'saidabancos' : SaidabancoForm, 
                        'entradascaixa' : EntradacaixaForm, 
                        'saidascaixa' : SaidacaixaForm, 
                        'dizimosofertas' : DizimoofertaForm,
                        'relatoriosemanalcelula' : RelatorioSemanalCelulaForm, 
                        'pedidosaida':PedidoSaidaForm,
                        'orcamentodepartamento':OrcamentoDepartamentoForm,
                        'inventariopatrimonio': InventarioPatrimonioForm,
                        'conteudoensino':ConteudoEnsinoForm,
                        'enviomensagem':EnvioMensagemForm,
                        }
    form_class = listaformularios.get(gestaoescolhida)
    if not form_class:
        messages.error(request, 'Tipo de formulário inválido.')
        return redirect('index')

    # 🔐 MODEL CORRETO
    model = form_class._meta.model
    perm = f'{model._meta.app_label}.add_{model._meta.model_name}'

    if not request.user.has_perm(perm):
        messages.error(request, 'Acesso negado! Você não tem permissão criar novos registros.')
        return redirect('index')

    if request.method == 'POST':
        formulario = form_class(request.POST, request.FILES)
        if formulario.is_valid():
            obj = formulario.save(commit=False)

            # ⚠️ Verificação de conflito de horário para actividades
            if gestaoescolhida == 'actividades':
                data = formulario.cleaned_data['data']
                inicio = formulario.cleaned_data['inicio']
                fim = formulario.cleaned_data['fim']
                conflitos = Actividade.objects.filter(
                    data=data, inicio__lt=fim, fim__gt=inicio
                )
                mesma_data_diferente = Actividade.objects.filter(
                    data=data
                ).exclude(inicio__lt=fim, fim__gt=inicio)
                if conflitos.exists():
                    primeiro = conflitos.first()
                    messages.error(
                        request,
                        f'Conflito de horário: já existe uma actividade "{primeiro.designacao}" '
                        f'das {primeiro.inicio} às {primeiro.fim} neste dia com horário sobrepóvel.'
                    )
                    return render(request, 'formulario_criacao.html', {'formulario': formulario})
                elif mesma_data_diferente.exists():
                    messages.warning(
                        request,
                        'Já existe outra actividade neste dia com horário diferente. '
                        'Se for num local diferente, pode prosseguir normalmente.'
                    )

            obj.save()

            # 👤 Regista o criador nas actividades
            if gestaoescolhida == 'actividades':
                obj.criado_por = request.user
                obj.save(update_fields=['criado_por'])

            # Se for Irmão e o utilizador escolheu departamentos, criar Mandatos
            if gestaoescolhida == 'irmaos':
                departamentos = formulario.cleaned_data.get('departamentos')
                if departamentos:
                    for dep in departamentos:
                        Mandato.objects.get_or_create(
                            irmao=obj, departamento=dep,
                            defaults={'funcao': 'membro'},
                        )
            messages.success(request, 'Dados salvos com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Foram encontrados erros ao preencher o formulário')
    else:
        formulario = form_class()

    return render(request, 'formulario_criacao.html', {'formulario': formulario})

@login_required
def encontraIrmao(request):
    nomev = request.GET.get('nomev', '').strip()
    apelidov = request.GET.get('apelidov', '').strip()
    municipiov = request.GET.get('municipiov', '').strip()
    bairrov = request.GET.get('bairrov', '').strip()
    
    profissaov = request.GET.get('profissaov', '').strip()
    
    pagina = request.GET.get('pagina', '1')
    kwargs= {'nome__icontains':nomev, 'apelido__icontains' : apelidov, 'bairro__icontains' : bairrov}
    if profissaov:
        kwargs['profissao__icontains'] = profissaov
    if municipiov and municipiov != '0':
        kwargs['municipio_id'] = municipiov
    resultado = Irmao.objects.select_related('celula', 'localcongregacao', 'provincia', 'municipio').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'irmaosfiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

@login_required
def encontraRelatorioSemanalCelula(request):
    nomev = request.GET['nomev']
    liderv = request.GET['liderv']
    localv = request.GET['localv']
    temav = request.GET['temav']
    kwargs= {'nome_celula__icontains':nomev, 
             'lider_responsavel__icontains' : liderv, 
             'local_reuniao__icontains' : localv, 
             'tema_palavra__icontains' : temav }
    pagina= request.GET['pagina']
    resultado = RelatorioSemanalCelula.objects.select_related('nome_celula', 'lider_responsavel').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'relatoriosemanalcelulafiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

@login_required
def encontraPedidoSaida(request):
    nomev = request.GET['projectov']
    liderv = request.GET['montantev']
    localv = request.GET['ibanv']
    kwargs= {'projecto__icontains':nomev, 
             'montante__icontains' : liderv, 
             'iban__icontains' : localv, 
              }
    pagina= request.GET['pagina']
    resultado = PedidoSaida.objects.select_related('departamento', 'requerente', 'status_de_aprovacao', 'aprovador').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'pedidosaidafiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

@login_required
def encontraContasbancarias(request):
    nomev = request.GET.get('nomev', '').strip()
    apelidov = request.GET.get('apelidov', '').strip()
    bancov = request.GET.get('bancov', '').strip()
    kwargs = {
        'proprietario__nome__icontains': nomev,
        'proprietario__apelido__icontains': apelidov,
        'banco__designacao__icontains': bancov,
        'is_active': True,
    }
    resultado = Contabancaria.objects.filter(**kwargs)
    return render(request,'contasbancariasfiltradas.html', {'bb': resultado })


@login_required
def inativaContabancaria(request, id):
    if not request.user.has_perm('sitetibl.change_contabancaria'):
        messages.error(request, 'Acesso negado para inativar conta bancária.')
        return redirect('index')

    conta = get_object_or_404(Contabancaria, id=id)
    conta.is_active = False
    conta.save(update_fields=['is_active'])
    messages.success(request, f'Conta {conta.numeroconta} inativada com sucesso.')
    return redirect(f'/tibl/contasbancarias/detalhe/{id}/')


@login_required
def reativaContabancaria(request, id):
    if not request.user.has_perm('sitetibl.change_contabancaria'):
        messages.error(request, 'Acesso negado para reativar conta bancária.')
        return redirect('index')

    conta = get_object_or_404(Contabancaria, id=id)
    conta.is_active = True
    conta.save(update_fields=['is_active'])
    messages.success(request, f'Conta {conta.numeroconta} reativada com sucesso.')
    return redirect(f'/tibl/contasbancarias/detalhe/{id}/')


@login_required
def contasbancariasinativas(request):
    pagina = request.GET.get('pagina', 1)
    resultado = Contabancaria.objects.select_related('banco', 'proprietario', 'instituicao').filter(is_active=False).order_by('id')
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, 'contasbancariasinativas.html', {
        'bb': paginaresultado,
        'total_inativas': resultado.count(),
    })


def _get_relatorio_dizimos_membro_context(params):
    q = params.get('q', '').strip()
    mesv = params.get('mesv', '0')
    anov = params.get('anov', '0')
    datainicio = params.get('datainicio', '').strip()
    datafim = params.get('datafim', '').strip()

    filtros = {}
    if mesv != '0':
        filtros['datacorrespondente__month'] = mesv
    if anov != '0':
        filtros['datacorrespondente__year'] = anov
    if datainicio:
        filtros['datacorrespondente__gte'] = datainicio
    if datafim:
        filtros['datacorrespondente__lte'] = datafim

    queryset = Dizimooferta.objects.select_related('irmao').filter(**filtros)
    if q:
        queryset = queryset.filter(
            Q(irmao__nome__icontains=q)
            | Q(irmao__apelido__icontains=q)
            | Q(irmao__outrosnomes__icontains=q)
            | Q(irmao__email__icontains=q)
        )

    agregados = list(
        queryset.values('irmao_id', 'moeda')
        .annotate(total_registos=Count('id'), total_valor=Sum('valor'))
        .order_by('-total_valor')
    )

    irmaos_ids = [item['irmao_id'] for item in agregados]
    irmaos_map = {
        irmao.id: irmao
        for irmao in Irmao.objects.filter(id__in=irmaos_ids)
    }

    relatorio = []
    contribuinte_ids = set()
    for item in agregados:
        irmao = irmaos_map.get(item['irmao_id'])
        if not irmao:
            continue
        contribuinte_ids.add(irmao.id)
        relatorio.append({
            'irmao': irmao,
            'total_registos': item['total_registos'],
            'total_valor': item['total_valor'] or 0,
            'moeda': item['moeda'],
        })

    total_contribuintes = len(contribuinte_ids)
    total_geral = queryset.aggregate(total=Sum('valor'))['total'] or 0
    moedas_distintas = list(queryset.values_list('moeda', flat=True).distinct())
    moeda_resumo = moedas_distintas[0] if len(moedas_distintas) == 1 else 'MULTI'
    media_por_membro = (total_geral / total_contribuintes) if total_contribuintes and len(moedas_distintas) == 1 else None

    return {
        'relatorio': relatorio,
        'q': q,
        'mesv': mesv,
        'anov': anov,
        'datainicio': datainicio,
        'datafim': datafim,
        'listameses': MESES,
        'total_contribuintes': total_contribuintes,
        'total_geral': total_geral,
        'media_por_membro': media_por_membro,
        'moeda_resumo': moeda_resumo,
        'query_string': params.urlencode(),
    }


def _desenhar_rodape_pdf(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 9)
    canvas_obj.setFillColor(colors.HexColor('#666666'))
    canvas_obj.drawRightString(doc.pagesize[0] - 40, 20, f'Pagina {canvas_obj.getPageNumber()}')
    canvas_obj.restoreState()


@login_required
def relatoriodizimosmembro(request):
    return render(request, 'relatoriodizimosmembro.html', _get_relatorio_dizimos_membro_context(request.GET))


@login_required
def relatoriodizimosmembro_pdf(request):
    context = _get_relatorio_dizimos_membro_context(request.GET)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_dizimos_por_membro.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatorio de Dizimos por Membro",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'RelatorioHeaderMembro',
        parent=styles['Heading2'],
        alignment=1,
        textColor=colors.HexColor('#1f3d1f'),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'RelatorioSubtitleMembro',
        parent=styles['Normal'],
        alignment=1,
        textColor=colors.HexColor('#4f4f4f'),
        fontSize=9,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        'RelatorioMetaMembro',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        leading=12,
        spaceAfter=4,
    )
    elements = []

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(Paragraph("<b>Terceira Igreja Baptista de Luanda</b>", header_style))
    elements.append(Paragraph("Sistema TIBL | Relatorio Financeiro", subtitle_style))
    elements.append(Paragraph("<b>Relatorio de Dizimos por Membro</b>", styles['Title']))

    filtros_aplicados = []
    if context['q']:
        filtros_aplicados.append(f"Pesquisa: {context['q']}")
    if context['mesv'] != '0':
        filtros_aplicados.append(f"Mes: {MESES.get(context['mesv'], context['mesv'])}")
    if context['anov'] != '0':
        filtros_aplicados.append(f"Ano: {context['anov']}")
    if context['datainicio']:
        filtros_aplicados.append(f"De: {context['datainicio']}")
    if context['datafim']:
        filtros_aplicados.append(f"Ate: {context['datafim']}")

    periodo = 'Todos os periodos'
    if context['datainicio'] and context['datafim']:
        periodo = f"{context['datainicio']} ate {context['datafim']}"
    elif context['datainicio']:
        periodo = f"A partir de {context['datainicio']}"
    elif context['datafim']:
        periodo = f"Ate {context['datafim']}"
    elif context['mesv'] != '0' and context['anov'] != '0':
        periodo = f"{MESES.get(context['mesv'], context['mesv'])} de {context['anov']}"
    elif context['mesv'] != '0':
        periodo = MESES.get(context['mesv'], context['mesv'])
    elif context['anov'] != '0':
        periodo = f"Ano de {context['anov']}"

    moeda_label = 'Multimoeda' if context['moeda_resumo'] == 'MULTI' else context['moeda_resumo']

    elements.append(Paragraph(f"<b>Periodo:</b> {periodo}", meta_style))
    elements.append(Paragraph(f"<b>Emitido em:</b> {date.today().strftime('%d/%m/%Y')}", meta_style))
    if filtros_aplicados:
        elements.append(Paragraph(f"<b>Filtros:</b> {' | '.join(filtros_aplicados)}", meta_style))
    else:
        elements.append(Paragraph("<b>Filtros:</b> Nenhum filtro adicional aplicado", meta_style))

    resumo = Table([
        ['Contribuintes', 'Total arrecadado', 'Moeda', 'Media por membro'],
        [
            str(context['total_contribuintes']),
            f"{context['total_geral']:,.2f}",
            moeda_label,
            f"{context['media_por_membro']:,.2f}" if context['media_por_membro'] is not None else '--',
        ],
    ], colWidths=[100, 130, 90, 110])
    resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9ead3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f3d1f')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f4fbf1')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a8c79d')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(resumo)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    data = [['Membro', 'Email', 'Moeda', 'Total Contribuido', 'N. Registos']]
    for item in context['relatorio']:
        data.append([
            f"{item['irmao'].nome} {item['irmao'].apelido}",
            item['irmao'].email or '-',
            item['moeda'],
            f"{item['total_valor']:,.2f}",
            str(item['total_registos'])
        ])

    if len(data) == 1:
        data.append(['Nenhum registo encontrado', '-', '-', '-', '-'])

    data.append([
        'Total Geral',
        '',
        moeda_label,
        f"{context['total_geral']:,.2f}",
        ''
    ])

    table = LongTable(data, colWidths=[150, 130, 60, 100, 70], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f3e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements, onFirstPage=_desenhar_rodape_pdf, onLaterPages=_desenhar_rodape_pdf)
    return response


def _get_relatorio_ofertas_por_tipo_context(params):
    q = params.get('q', '').strip()
    mes = params.get('mes', '').strip()
    ano = params.get('ano', '').strip()
    datainicio = params.get('datainicio', '').strip()
    datafim = params.get('datafim', '').strip()

    filtros = {}
    if mes:
        filtros['datacorrespondente__month'] = mes
    if ano:
        filtros['datacorrespondente__year'] = ano
    if datainicio:
        filtros['datacorrespondente__gte'] = datainicio
    if datafim:
        filtros['datacorrespondente__lte'] = datafim

    queryset = Dizimooferta.objects.select_related('tipooferta', 'irmao').filter(**filtros)
    if q:
        queryset = queryset.filter(
            Q(tipooferta__designacao__icontains=q)
            | Q(irmao__nome__icontains=q)
            | Q(irmao__apelido__icontains=q)
            | Q(irmao__email__icontains=q)
        )

    reporte = list(
        queryset.values('tipooferta__designacao', 'moeda')
        .annotate(total=Sum('valor'), count=Count('id'))
        .order_by('-total', 'tipooferta__designacao')
    )

    total_geral = queryset.aggregate(total=Sum('valor'))['total'] or 0
    moedas_distintas = list(queryset.values_list('moeda', flat=True).distinct())
    moeda_resumo = moedas_distintas[0] if len(moedas_distintas) == 1 else 'MULTI'

    return {
        'reporte': reporte,
        'q': q,
        'mes': mes,
        'ano': ano,
        'datainicio': datainicio,
        'datafim': datafim,
        'total_geral': total_geral,
        'moeda_resumo': moeda_resumo,
        'query_string': params.urlencode(),
    }


@login_required
def relatorioofertasportipo(request):
    return render(request, 'relatorioofertasportipo.html', _get_relatorio_ofertas_por_tipo_context(request.GET))


@login_required
def relatorioofertasportipo_pdf(request):
    context = _get_relatorio_ofertas_por_tipo_context(request.GET)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_ofertas_por_tipo.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatorio de Ofertas por Tipo",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'RelatorioHeader',
        parent=styles['Heading2'],
        alignment=1,
        textColor=colors.HexColor('#1f3d1f'),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'RelatorioSubtitle',
        parent=styles['Normal'],
        alignment=1,
        textColor=colors.HexColor('#4f4f4f'),
        fontSize=9,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        'RelatorioMeta',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        leading=12,
        spaceAfter=4,
    )
    elements = []

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(Paragraph("<b>Terceira Igreja Baptista de Luanda</b>", header_style))
    elements.append(Paragraph("Sistema TIBL | Relatorio Financeiro", subtitle_style))
    elements.append(Paragraph("<b>Relatorio de Ofertas por Tipo</b>", styles['Title']))

    filtros_aplicados = []
    if context['q']:
        filtros_aplicados.append(f"Pesquisa: {context['q']}")
    if context['mes']:
        filtros_aplicados.append(f"Mes: {MESES.get(context['mes'], context['mes'])}")
    if context['ano']:
        filtros_aplicados.append(f"Ano: {context['ano']}")
    if context['datainicio']:
        filtros_aplicados.append(f"De: {context['datainicio']}")
    if context['datafim']:
        filtros_aplicados.append(f"Ate: {context['datafim']}")
    periodo = 'Todos os periodos'
    if context['datainicio'] and context['datafim']:
        periodo = f"{context['datainicio']} ate {context['datafim']}"
    elif context['datainicio']:
        periodo = f"A partir de {context['datainicio']}"
    elif context['datafim']:
        periodo = f"Ate {context['datafim']}"
    elif context['mes'] and context['ano']:
        periodo = f"{MESES.get(context['mes'], context['mes'])} de {context['ano']}"
    elif context['mes']:
        periodo = MESES.get(context['mes'], context['mes'])
    elif context['ano']:
        periodo = f"Ano de {context['ano']}"

    total_registos = sum(row['count'] for row in context['reporte'])
    moeda_label = 'Multimoeda' if context['moeda_resumo'] == 'MULTI' else context['moeda_resumo']

    elements.append(Paragraph(f"<b>Periodo:</b> {periodo}", meta_style))
    elements.append(Paragraph(f"<b>Emitido em:</b> {date.today().strftime('%d/%m/%Y')}", meta_style))
    if filtros_aplicados:
        elements.append(Paragraph(f"<b>Filtros:</b> {' | '.join(filtros_aplicados)}", meta_style))
    else:
        elements.append(Paragraph("<b>Filtros:</b> Nenhum filtro adicional aplicado", meta_style))

    resumo = Table([
        ['Tipos de oferta', 'Total arrecadado', 'Moeda', 'Registos'],
        [str(len(context['reporte'])), f"{context['total_geral']:,.2f}", moeda_label, str(total_registos)],
    ], colWidths=[110, 140, 90, 90])
    resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9ead3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f3d1f')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f4fbf1')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a8c79d')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(resumo)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    data = [['Tipo de Oferta', 'Moeda', 'Total Arrecadado', 'N. Registos']]
    for row in context['reporte']:
        data.append([
            row['tipooferta__designacao'] or 'Geral',
            row['moeda'],
            f"{row['total']:,.2f}",
            str(row['count'])
        ])

    if len(data) == 1:
        data.append(['Nenhum registo encontrado', '-', '-', '-'])

    data.append([
        'Total Geral',
        'Multimoeda' if context['moeda_resumo'] == 'MULTI' else context['moeda_resumo'],
        f"{context['total_geral']:,.2f}",
        ''
    ])

    table = LongTable(data, colWidths=[180, 70, 120, 80], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f3e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements, onFirstPage=_desenhar_rodape_pdf, onLaterPages=_desenhar_rodape_pdf)
    return response




@login_required
def visualizar_recibo_dizimo(request, dizimo_id):
    messages.warning(request, f'Recibo de dízimo #{dizimo_id} não está disponível nesta branch.')
    return redirect('index')


@login_required
def gerar_recibo_dizimo(request, dizimo_id):
    messages.warning(request, f'Geração de recibo de dízimo #{dizimo_id} não está disponível nesta branch.')
    return redirect('index')

@login_required
def encontraAjudas(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    tipoajudav = int(request.GET['tipoajudav'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'beneficiario__nome__icontains':nomev, 'beneficiario__apelido__icontains' : apelidov,'ajuda_id' : tipoajudav,'data__month':mesv, 'data__year' : anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (tipoajudav == 0):
        del kwargs['ajuda_id']
    resultado = Ajuda.objects.select_related('ajuda', 'beneficiario', 'patrocinador', 'cesta').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'ajudasfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraCestas(request):
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'codigo__month':mesv, 'codigo__year' : anov}
    if (mesv == '0'):
        del kwargs['codigo__month']
    if (anov == '0'):
        del kwargs['codigo__year']
    resultado = Cestabasica.objects.select_related('saiudobanco', 'saiudacaixa').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'cestasfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraActividades(request):
    nomev = request.GET.get('nomev', '').strip()
    apelidov = request.GET.get('apelidov', '').strip()
    actividadev = request.GET.get('actividadev', '0')
    funcaov = request.GET.get('funcaov', '0')
    mesv = request.GET.get('mesv', '0')
    anov = request.GET.get('anov', '0')
    pagina = request.GET.get('pagina', 1)
    kwargs= {'irmao__nome__icontains' : nomev, 'irmao__apelido__icontains' : apelidov, 'actividade__designacao' : actividadev, 'funcao_id' : funcaov, 'actividade__data__month':mesv, 'actividade__data__year' : anov}
    
    if (
        not nomev and
        not apelidov and
        actividadev == '0' and
        funcaov == '0' and
        mesv == '0' and
        anov == '0'
    ):
        messages.warning(request, "Preencha pelo menos um campo para efectuar a busca.")
        return redirect('/tibl/gestao/actividades/1/')
    
    if (actividadev == '0'):
        del kwargs['actividade__designacao']
    if (funcaov == '0'):
        del kwargs['funcao_id']
    if (mesv == '0'):
        del kwargs['actividade__data__month']
    if (anov == '0'):
        del kwargs['actividade__data__year']
    resultado = Escala.objects.values('actividade_id','actividade__designacao','actividade__designacao__designacao','actividade__data','funcao__designacao','irmao__nome','irmao__apelido','actividade__localactividade__designacao').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'actividadesfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraDepartamentos(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    departamentov = int(request.GET['departamentov'])
    funcaov = request.GET.get('funcaov', '').strip()
    pagina= request.GET['pagina']
    kwargs= {'irmao__nome__icontains':nomev, 'irmao__apelido__icontains' : apelidov, 'departamento_id' : departamentov }
    if (departamentov == 0):
        del kwargs['departamento_id']
    if funcaov:
        kwargs['funcao'] = funcaov
    resultado = Mandato.objects.values('departamento_id', 'departamento__designacao', 'funcao', 'irmao__nome', 'irmao__apelido').filter(**kwargs).order_by('departamento__designacao')
    # Mapear valor bruto do cargo para etiqueta legível
    cargo_map = dict(Mandato.FUNCAO_CHOICES)
    resultado = list(resultado)
    for r in resultado:
        r['cargo_display'] = cargo_map.get(r['funcao'], r['funcao'])
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'departamentosfiltrados.html', {'bb':paginaresultado})


@login_required
def encontraDizimosofertas(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'irmao__nome__icontains' : nomev, 'irmao__apelido__icontains' : apelidov, 'datacorrespondente__month':mesv, 'datacorrespondente__year' : anov}
    if (mesv == '0'):
        del kwargs['datacorrespondente__month']
    if (anov == '0'):
        del kwargs['datacorrespondente__year']
    resultado = Dizimooferta.objects.select_related('irmao', 'tipooferta', 'actividade').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'dizimosofertasfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraSaidascaixa(request):
    rubricav = int(request.GET['rubricav'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'rubrica' : rubricav, 'data__month':mesv, 'data__year' : anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (rubricav == 0):
        del kwargs['rubrica']
    resultado = Saidacaixa.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'saidascaixafiltradas.html', {'bb':paginaresultado})

@login_required
def encontraEntradascaixa(request):
    rubricav = int(request.GET['rubricav'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'rubrica' : rubricav, 'data__month':mesv, 'data__year' : anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (rubricav == 0):
        del kwargs['rubrica']
    resultado = Entradacaixa.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'entradascaixafiltradas.html', {'bb':paginaresultado})

@login_required
def encontraSaidasbanco(request):
    contabancariav = int(request.GET['contabancariav'])
    rubricav = int(request.GET['rubricav'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'conta' : contabancariav, 'aquisicao__rubrica_id' : rubricav, 'data__month' : mesv, 'data__year' : anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (rubricav == 0):
        del kwargs['aquisicao__rubrica_id']
    if (contabancariav == 0):
        del kwargs['conta']
    resultado = Saidabanco.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'saidasbancofiltradas.html', {'bb':paginaresultado})

@login_required
def encontraEntradasbanco(request):
    contabancariav = int(request.GET['contabancariav'])
    rubricav = int(request.GET['rubricav'])
    viav = request.GET.get('viav', '0')
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'contaaacreditar':contabancariav, 'rubrica':rubricav, 'via':viav, 'data__month':mesv, 'data__year':anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (rubricav == 0):
        del kwargs['rubrica']
    if (viav == '0'):
        del kwargs['via']
    if (contabancariav == 0):
        del kwargs['contaaacreditar']
    resultado = Entradabanco.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'entradasbancofiltradas.html', {'bb':paginaresultado})


@login_required
def encontraOrcamentoDepartamento(request):
    departamentov = request.GET['departamentov']
    orcamentov = request.GET['orcamentov']
    anov = request.GET['anov']
    
    kwargs= {'departamento__designacao__icontains':departamentov, 
             'orcamento__icontains' : orcamentov, 
             'ano__icontains' : anov, 
            }
    pagina= request.GET['pagina']
    resultado = OrcamentoDepartamento.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'orcamentodepartamentofiltrados.html', {'bb':paginaresultado})


@login_required
def encontraInventarioPatrimonio(request):
    nomev = request.GET['nomev']
    descricaov = request.GET['descricaov']
    codigov = request.GET['codigov']
    
    kwargs= {'nome__icontains':nomev, 
             'descricao__icontains' : descricaov, 
             'codigo__icontains' : codigov, 
            }
    pagina= request.GET['pagina']
    resultado = InventarioPatrimonio.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'inventariopatrimoniofiltrados.html', {'bb':paginaresultado})

@login_required
def encontraConteudoEnsino(request):
    autorv = request.GET['autorv']
    titulov = request.GET['titulov']
    
    
    kwargs= {'autor__nome__icontains':autorv, 
             'titulo__icontains' : titulov, 
             
            }
    pagina= request.GET['pagina']
    resultado = ConteudoEnsino.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'conteudoensinofiltrados.html', {'bb':paginaresultado})


@login_required
def encontraEnvioMensagem(request):
    mensagemv = request.GET['mensagemv']
    quemenviou = request.GET['quemenviou']
    
    
    kwargs= {'mensagem__icontains':mensagemv, 
             'quemenviou__nome__icontains' : quemenviou, 
             
            }
    pagina= request.GET['pagina']
    resultado = EnvioMensagem.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'enviomensagemfiltrados.html', {'bb':paginaresultado})

@login_required
def encontraBancos(request):
    designacao = request.GET['designacao']
    abreviatura = request.GET['abreviatura']
    
    
    kwargs= {'designacao__icontains':designacao, 
             'abreviacao__icontains' : abreviatura, 
             
            }
    pagina= request.GET['pagina']
    resultado = Banco.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'bancosfiltrados.html', {'bb':paginaresultado})

@login_required
def encontraEscalas(request):
    actividade = request.GET.get('actividade', '')
    funcao = request.GET.get('funcao', '')
    departamentov = request.GET.get('departamentov', '0')

    kwargs = {
        'actividade__designacao__designacao__icontains': actividade,
        'funcao__designacao__icontains': funcao,
    }
    if departamentov and departamentov != '0':
        kwargs['actividade__departamento_id'] = departamentov

    pagina = request.GET.get('pagina', 1)
    resultado = Escala.objects.filter(**kwargs).select_related(
        'irmao', 'actividade', 'actividade__departamento', 'funcao'
    )
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    departamentos = Departamento.objects.all().order_by('designacao')
    return render(request, 'escalasfiltrados.html', {
        'bb': paginaresultado,
        'departamentos': departamentos,
        'departamentov_sel': departamentov,
    })


@login_required
def criar_actividades_recorrentes(request):
    """Cria múltiplas actividades para uma série semanal recorrente."""
    if not request.user.has_perm('sitetibl.add_actividade'):
        messages.error(request, 'Acesso negado! Não tem permissão para criar actividades.')
        return redirect('index')

    if request.method == 'POST':
        form = ActividadesRecorrentesForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo_actividade']
            departamento = form.cleaned_data.get('departamento')
            localactividade = form.cleaned_data.get('localactividade')
            inicio = form.cleaned_data['inicio']
            fim = form.cleaned_data['fim']
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            dias_semana = [int(d) for d in form.cleaned_data['dias_semana']]

            current = data_inicio
            criadas = []
            while current <= data_fim:
                if current.weekday() in dias_semana:
                    a = Actividade.objects.create(
                        designacao=tipo,
                        departamento=departamento,
                        localactividade=localactividade,
                        inicio=inicio,
                        fim=fim,
                        data=current,
                        criado_por=request.user,
                    )
                    criadas.append(a)
                current += timedelta(days=1)

            if criadas:
                messages.success(
                    request,
                    f'{len(criadas)} actividade{"s" if len(criadas) != 1 else ""} criada{"s" if len(criadas) != 1 else ""} com sucesso.'
                )
            else:
                messages.warning(request, 'Nenhuma actividade criada. Verifique o intervalo de datas e os dias seleccionados.')
            return redirect('sitetibl:mostra_gestao', gestaoescolhida='actividades', pagina=1)
    else:
        form = ActividadesRecorrentesForm()

    return render(request, 'actividades_recorrentes.html', {'form': form})


class EscalasPorActividadeView(APIView):

    def get(self, request, actividade_id):

        try:
            actividade = Actividade.objects.get(id=actividade_id)
        except Actividade.DoesNotExist:
            return Response(
                {"erro": "Actividade não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

        escalas = Escala.objects.filter(actividade=actividade)

        serializer = EscalaSerializer(escalas, many=True)

        return Response({
            "actividade": str(actividade),
            "escalas": serializer.data
        })


#VIEWS PARA OS DASHBOARDS

@login_required
def dashboardIrmaos(request):
    ano = now().year

    queryset = (
        Irmao.objects
        .filter(data_criacao__year=ano)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')   # ordem cronológica
    )

    # Cria todos os meses com valor zero
    meses = OrderedDict()
    for i in range(1, 13):
        meses[i] = 0

    # Preenche os meses que têm dados
    for item in queryset:
        meses[item['mes'].month] = item['total']

    # Labels dinâmicos: mês + ano
    labels = [f"{mes} {ano}" for mes in ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']]
    data = list(meses.values())

    return JsonResponse({
        "labels": labels,
        "data": data
    })

@login_required
def dashboardOrcamentoDepartamento(request):
    ano = now().year

    queryset = (
        OrcamentoDepartamento.objects
        .filter(ano=ano)
        .values('departamento__designacao')
        .annotate(total=Sum('orcamento'))
        .order_by('departamento__designacao')
    )

    labels = []
    data = []

    for item in queryset:
        labels.append(item['departamento__designacao'])
        data.append(float(item['total']))

    return JsonResponse({
        "labels": labels,
        "data": data
    })

@login_required
def dashboardPedidosSaidaSemana(request):
    ano = now().year

    queryset = (
        PedidoSaida.objects
        .filter(data_criacao__year=ano)
        .annotate(dia_semana=ExtractWeekDay('data_criacao'))
        .values('dia_semana')
        .annotate(total=Count('id'))
    )

    # Django: 1=Dom, 2=Seg, 3=Ter, ..., 7=Sáb
    dias = {
        1: 'Dom',
        2: 'Seg',
        3: 'Ter',
        4: 'Qua',
        5: 'Qui',
        6: 'Sex',
        7: 'Sáb',
    }

    # Inicializa todos os dias com zero
    dados = {dia: 0 for dia in dias.values()}

    for item in queryset:
        nome_dia = dias[item['dia_semana']]
        dados[nome_dia] = item['total']

    return JsonResponse({
        "ano":ano,
        "labels": list(dados.keys()),
        "data": list(dados.values())
    })


@login_required
def dashboardConteudoEnsinoMensal(request):
    ano = now().year

    queryset = (
        ConteudoEnsino.objects
        .filter(data_criacao__year=ano)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    meses = {
        1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
        7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'
    }

    labels = []
    data = []
    total_geral = 0

    for item in queryset:
        labels.append(meses[item['mes'].month])
        data.append(item['total'])
        total_geral += item['total']

    return JsonResponse({
        "ano": ano,
        "labels": labels,
        "data": data,
        "total": total_geral
    })

@login_required
def dashboardDizimoOferta(request):
    ano = now().year

    # Pega todos os tipos de oferta existentes
    tipos = TipoOferta.objects.all()

    meses = {i: 0 for i in range(1, 13)}
    labels = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

    datasets = []

    for tipo in tipos:
        queryset = (
            Dizimooferta.objects
            .filter(datacorrespondente__year=ano, tipooferta=tipo)
            .annotate(mes=TruncMonth('datacorrespondente'))
            .values('mes')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        # Preenche todos os meses
        data = meses.copy()
        for item in queryset:
            data[item['mes'].month] = float(item['total'] or 0)

        datasets.append({
            "label": tipo.designacao,   # Nome do tipo de oferta
            "data": list(data.values())
        })

    return JsonResponse({
        "ano": ano,
        "labels": labels,
        "datasets": datasets
    })



@login_required
def dashboardCrescimentoMembros(request):
    ano = now().year

    queryset = (
        RelatorioSemanalCelula.objects
        .filter(data_reuniao__year=ano)
        .annotate(mes=TruncMonth('data_reuniao'))
        .values('mes')
        .annotate(
            total_membros=Sum('numero_participantes_membros'),
            total_visitantes=Sum('numero_participantes_visitantes'),
            total_criancas=Sum('numero_participantes_criancas')
        )
        .order_by('mes')
    )

    # Meses padrão
    meses = {i: 0 for i in range(1, 13)}
    labels = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

    data_membros = meses.copy()
    data_visitantes = meses.copy()
    data_criancas = meses.copy()

    for item in queryset:
        m = item['mes'].month
        data_membros[m] = item['total_membros'] or 0
        data_visitantes[m] = item['total_visitantes'] or 0
        data_criancas[m] = item['total_criancas'] or 0

    return JsonResponse({
        "ano": ano,
        "labels": labels,
        "membros": list(data_membros.values()),
        "visitantes": list(data_visitantes.values()),
        "criancas": list(data_criancas.values())
    })


@login_required
def dashboardDepartamentosMembros(request):
    """Número de membros por departamento — gráfico de barras horizontais."""
    dados = (
        Mandato.objects
        .values('departamento__designacao')
        .annotate(total=Count('irmao', distinct=True))
        .order_by('-total')
    )
    labels = [d['departamento__designacao'] for d in dados]
    data = [d['total'] for d in dados]
    return JsonResponse({"labels": labels, "data": data})


#VIEWS QUE GERAM RELATÓRIOS
@login_required
def meu_perfil(request):
    """Página de perfil pessoal: actualiza contactos e senha."""
    try:
        irmao = request.user.irmao
    except Irmao.DoesNotExist:
        irmao = None

    perfil_form = MeuPerfilForm(instance=irmao) if irmao else None
    senha_form = MeuPerfilPasswordForm(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'perfil' and irmao:
            perfil_form = MeuPerfilForm(request.POST, request.FILES, instance=irmao)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Dados de contacto actualizados com sucesso.')
                return redirect('sitetibl:meu_perfil')

        elif action == 'senha':
            senha_form = MeuPerfilPasswordForm(user=request.user, data=request.POST)
            if senha_form.is_valid():
                senha_form.save()
                update_session_auth_hash(request, senha_form.user)
                messages.success(request, 'Senha alterada com sucesso.')
                return redirect('sitetibl:meu_perfil')

    return render(request, 'meu_perfil.html', {
        'perfil_form': perfil_form,
        'senha_form': senha_form,
        'irmao': irmao,
    })


@login_required
def pagina_relatorios(request):
    return render(request, 'relatorios/template_relatorio.html')


@login_required
@permission_required('sitetibl.change_irmao', raise_exception=True)
def relatorio_irmaos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_irmaos.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Irmãos",
        author="Sistema TIBL"
    )

    elements = []
    styles = getSampleStyleSheet()

    # 🔹 LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 TÍTULO
    elements.append(
        Paragraph(
            "<b>Relatório Geral de Irmãos</b>",
            styles['Title']
        )
    )

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # 🔹 CABEÇALHO DA TABELA
    data = [
        ['Nome', 'Telefone', 'Dizimista', 'Batizado']
    ]

    # 🔹 DADOS
    for irmao in Irmao.objects.all():
        data.append([
            irmao.nome,
            irmao.telefone or '-',
            'Sim' if irmao.dizimista else 'Não',
            'Sim' if irmao.batizado else 'Não'
        ])

    # 🔹 TABELA
    table = Table(data, colWidths=[160, 110, 90, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_dizimooferta', raise_exception=True)
def relatorio_dizimos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_dizimos_ofertas.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Dizimos",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # 🔹 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Dízimos e Ofertas</b>", styles['Title'])
    )

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # 🔹 CABEÇALHO DA TABELA
    data = [
        ['Irmão', 'Telefone', 'Tipo de Oferta', 'Valor', 'Moeda', 'Data']
    ]

    # 🔹 DADOS
    queryset = Dizimooferta.objects.select_related(
        'irmao', 'tipooferta'
    ).order_by('-datacorrespondente')

    for d in queryset:
        data.append([
            d.irmao.nome,
            d.irmao.telefone or '-',
            d.tipooferta.designacao if d.tipooferta else '-',
            f"{d.valor:,.2f}",
            d.moeda,
            d.datacorrespondente.strftime('%d/%m/%Y')
        ])

    # 🔹 TABELA
    table = Table(
        data,
        colWidths=[110, 80, 100, 70, 50, 70]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_departamento', raise_exception=True)
def relatorio_departamentos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_departamentos.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        title="Relatório de Departamentos",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # 🔹 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    # 🔹 TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Departamentos</b>", styles['Title'])
    )

   
    elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 TABELA
    data = [['Departamento', 'Líder', 'Vice-Líder']]

    for d in Departamento.objects.all():
        data.append([
            d.designacao,
            str(d.lider_departamento) if d.lider_departamento else '-',
            str(d.vice_lider_departamento) if d.vice_lider_departamento else '-'
        ])

    table = Table(data, colWidths=[180, 160, 160])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))

    elements.append(table)

    doc.build(elements)

    return response


@login_required
@permission_required('sitetibl.view_escala', raise_exception=True)
def relatorio_escalas_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_escalas.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Escalas",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # 🔹 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 TÍTULO
    elements.append(
        Paragraph("<b>Relatório Geral de Escalas</b>", styles['Title'])
    )

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # 🔹 CABEÇALHO DA TABELA
    data = [[
        'Irmão',
        'Actividade',
        'Função',
        'Início',
        'Fim',
        'Data'
    ]]

    # 🔹 DADOS
    for escala in Escala.objects.select_related('irmao', 'actividade').all():
        data.append([
            escala.irmao.nome if escala.irmao else '-',
            escala.actividade.designacao.designacao if escala.actividade else '-',
            escala.funcao,
            escala.actividade.inicio.strftime('%H:%M') if escala.actividade and escala.actividade.inicio else '-',
            escala.actividade.fim.strftime('%H:%M') if escala.actividade and escala.actividade.fim else '-',
            escala.actividade.data.strftime('%d/%m/%Y') if escala.actividade and escala.actividade.data else '-',
        ])

    # 🔹 TABELA
    table = Table(data, colWidths=[90, 120, 70, 60, 60, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_actividade', raise_exception=True)
def relatorio_actividades_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_actividades.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Relatório de Actividades",
        author="Sistema TIBL"
    )

    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']

    cell_style = ParagraphStyle(
        'cell',
        fontSize=9,
        leading=11,
        wordWrap='CJK'
    )

    # 🔹 LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    # 🔹 TÍTULO
    elements.append(Paragraph("Relatório de Actividades", title_style))

    elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 CABEÇALHO DA TABELA
    data = [
        [
            "Designação",
            "Início",
            "Fim",
            "Data",
            "Tema",
            "Local"
        ]
    ]

    # 🔹 DADOS
    for actividade in Actividade.objects.all():
        data.append([
            Paragraph(str(actividade.designacao or '-'), cell_style),
            Paragraph(actividade.inicio.strftime('%H:%M') if actividade.inicio else '-', cell_style),
            Paragraph(actividade.fim.strftime('%H:%M') if actividade.fim else '-', cell_style),
            Paragraph(actividade.data.strftime('%d/%m/%Y') if actividade.data else '-', cell_style),
            Paragraph(str(actividade.tema or '-'), cell_style),
            Paragraph(str(actividade.localactividade or '-'), cell_style),
        ])

    # 🔹 TABELA
    table = Table(
        data,
        colWidths=[
            4 * cm,
            2 * cm,
            2 * cm,
            2.5 * cm,
            4 * cm,
            3.5 * cm
        ],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-3, -1), 'CENTER'),

        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

        # Fundo
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_inventariopatrimonio', raise_exception=True)
def relatorio_inventario_patrimonio_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_inventario_patrimonio.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Inventário de Património",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # 🔹 ESTILO PARA CÉLULAS (QUEBRA DE LINHA)
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )

    # 🔹 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Inventário de Património</b>", styles['Title'])
    )
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # 🔹 CABEÇALHO DA TABELA
    data = [[
        'Nome',
        'Descrição',
        'Categoria',
        'Código',
        'Preço',
        'Moeda',
        'Quantidade'
    ]]

    # 🔹 DADOS
    for i in InventarioPatrimonio.objects.all():
        data.append([
            Paragraph(i.nome or '-', cell_style),
            Paragraph(i.descricao or '-', cell_style),
            Paragraph(i.categoria_patrimonio.designacao if i.categoria_patrimonio else '-', cell_style),
            Paragraph(i.codigo or '-', cell_style),
            Paragraph(f"{i.preco:.2f}" if i.preco else '0.00', cell_style),
            Paragraph(i.moeda.designacao or '-', cell_style),
            Paragraph(str(i.quantidade), cell_style),
        ])

    # 🔹 TABELA
    table = Table(
        data,
        colWidths=[70, 110, 80, 60, 50, 40, 50]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response



@login_required
@permission_required('sitetibl.view_saidacaixa', raise_exception=True)
def relatorio_saida_caixa_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_saida_caixa.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Saídas de Caixa",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # 🔹 Estilo para quebra automática nas células
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )

    # 🔹 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Paragraph("<br/>", styles['Normal']))

    # 🔹 TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Saídas de Caixa</b>", styles['Title'])
    )
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # 🔹 CABEÇALHO DA TABELA
    data = [[
        'Departamento',
        'Projecto',
        'Montante',
        'Moeda',
        'Requerente',
        'Status',
        'Aprovador',
        'Data'
    ]]

    # 🔹 DADOS
    for p in PedidoSaida.objects.all():
        data.append([
            Paragraph(str(p.departamento) if p.departamento else '-', cell_style),
            Paragraph(str(p.projecto) if p.projecto else '-', cell_style),
            Paragraph(f"{p.montante:.2f}" if p.montante else '0.00', cell_style),
            Paragraph(p.moeda.designacao or '-', cell_style),
            Paragraph(str(p.requerente) if p.requerente else '-', cell_style),
            Paragraph(str(p.status_de_aprovacao), cell_style),
            Paragraph(str(p.aprovador) if p.aprovador else '-', cell_style),
            Paragraph(
                p.data_criacao.strftime('%d/%m/%Y') if p.data_criacao else '-',
                cell_style
            ),
        ])

    # 🔹 TABELA
    table = Table(
        data,
        colWidths=[80, 70, 55, 40, 70, 55, 60, 50]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
def dashboard(request):
    from datetime import date as dt_date, timedelta
    import random
    hoje = dt_date.today()
    user = request.user

    # --- Versículo do dia (roda pela data para variar diariamente) ---
    VERSICULOS = [
        {'texto': 'Porque eu bem sei os pensamentos que penso de vós, diz o Senhor; pensamentos de paz e não de mal, para vos dar o fim que esperais.', 'ref': 'Jeremias 29:11'},
        {'texto': 'Tudo posso naquele que me fortalece.', 'ref': 'Filipenses 4:13'},
        {'texto': 'O Senhor é o meu pastor; nada me faltará.', 'ref': 'Salmos 23:1'},
        {'texto': 'Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento.', 'ref': 'Provérbios 3:5'},
        {'texto': 'Mas os que esperam no Senhor renovarão as suas forças; subirão com asas como águias; correrão e não se cansarão; caminharão e não se fatigarão.', 'ref': 'Isaías 40:31'},
        {'texto': 'Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus; eu te fortaleço, e te ajudo, e te sustento com a destra da minha justiça.', 'ref': 'Isaías 41:10'},
        {'texto': 'Dá instrução ao sábio, e ele se fará mais sábio; ensina ao justo, e ele crescerá em entendimento.', 'ref': 'Provérbios 9:9'},
        {'texto': 'O amor é paciente, o amor é bondoso. Não inveja, não se vangloria, não se orgulha.', 'ref': '1 Coríntios 13:4'},
        {'texto': 'Alegrai-vos sempre no Senhor; outra vez digo: alegrai-vos.', 'ref': 'Filipenses 4:4'},
        {'texto': 'Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei.', 'ref': 'Mateus 11:28'},
        {'texto': 'Porque Deus amou o mundo de tal maneira que deu o seu Filho unigénito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.', 'ref': 'João 3:16'},
        {'texto': 'E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus.', 'ref': 'Romanos 8:28'},
        {'texto': 'Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo por onde quer que andares.', 'ref': 'Josué 1:9'},
        {'texto': 'O Senhor é a minha luz e a minha salvação; a quem temerei? O Senhor é a força da minha vida; de quem me recearei?', 'ref': 'Salmos 27:1'},
        {'texto': 'Lançando sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós.', 'ref': '1 Pedro 5:7'},
        {'texto': 'Sede fortes e corajosos, não temais, nem vos assusteis por causa deles, pois o Senhor, vosso Deus, é quem vai convosco; não vos deixará, nem vos desamparará.', 'ref': 'Deuteronómio 31:6'},
        {'texto': 'Eu sou a videira, vós, as varas; quem está em mim, e eu nele, este dá muito fruto, porque sem mim nada podeis fazer.', 'ref': 'João 15:5'},
        {'texto': 'A tua palavra é lâmpada que ilumina os meus passos e luz que clareia o meu caminho.', 'ref': 'Salmos 119:105'},
        {'texto': 'Porque onde estiverem dois ou três reunidos em meu nome, aí estou eu no meio deles.', 'ref': 'Mateus 18:20'},
        {'texto': 'Entrega o teu caminho ao Senhor; confia nele, e ele tudo fará.', 'ref': 'Salmos 37:5'},
        {'texto': 'Irmãos, não julgo havê-lo alcançado; mas uma coisa faço: esquecendo-me das coisas que ficaram para trás e avançando para as que estão adiante, prossigo para o alvo.', 'ref': 'Filipenses 3:13-14'},
    ]
    idx_versiculo = hoje.toordinal() % len(VERSICULOS)
    versiculo_do_dia = VERSICULOS[idx_versiculo]

    # --- Dados visíveis para TODOS ---
    anuncios = Anuncio.objects.order_by('-data')[:5]

    proximas_actividades = (
        Actividade.objects
        .filter(data__gte=hoje, data__lte=hoje + timedelta(days=14))
        .select_related('designacao', 'localactividade')
        .order_by('data', 'inicio')[:6]
    )

    # Escalas do membro logado + verificação de célula
    minhas_escalas_list = []
    irmao_obj = Irmao.objects.filter(user=user).select_related('celula').first()
    tem_celula = False
    if irmao_obj:
        tem_celula = irmao_obj.celula is not None
        minhas_escalas_list = (
            Escala.objects
            .filter(irmao=irmao_obj, actividade__data__gte=hoje)
            .select_related('actividade__designacao', 'funcao')
            .order_by('actividade__data')[:5]
        )

    # Aniversariantes do mês
    aniversariantes = (
        Irmao.objects
        .filter(datanascimento__month=hoje.month)
        .order_by('datanascimento__day')[:10]
    )

    # --- Dados financeiros (passados apenas se utilizador tem permissão) ---
    pedidos_pendentes = None
    saldos_bancarios = None
    total_membros = Irmao.objects.count()

    if user.has_perm('sitetibl.view_pedidosaida'):
        pedidos_pendentes = (
            PedidoSaida.objects
            .exclude(status_de_aprovacao__designacao__icontains='aprovad')
            .select_related('requerente', 'departamento', 'status_de_aprovacao')
            .order_by('-data_criacao')[:5]
        )

    if user.has_perm('sitetibl.view_contabancaria'):
        contas = Contabancaria.objects.filter(is_active=True).select_related('banco')
        saldos_bancarios = []
        for c in contas:
            saldos_bancarios.append({
                'banco': str(c.banco),
                'numero': c.numeroconta[-4:] if len(c.numeroconta) >= 4 else c.numeroconta,
                'moeda': c.moeda,
                'saldo': c.saldo_actual(),
            })

    context = {
        'titulo': 'Dashboard',
        'versiculo': versiculo_do_dia,
        'tem_celula': tem_celula,
        'tem_perfil': irmao_obj is not None,
        'anuncios': anuncios,
        'proximas_actividades': proximas_actividades,
        'minhas_escalas': minhas_escalas_list,
        'aniversariantes': aniversariantes,
        'pedidos_pendentes': pedidos_pendentes,
        'saldos_bancarios': saldos_bancarios,
        'total_membros': total_membros,
    }
    return render(request, 'dashboard.html', context)

def root_redirect(request):
    return redirect('dashboard')

@login_required
def minhas_escalas(request):
    from datetime import date as dt_date
    hoje = dt_date.today()

    irmao_obj = Irmao.objects.filter(user=request.user).first()
    if not irmao_obj:
        messages.warning(request, 'O seu utilizador não está associado a nenhum perfil de irmão.')
        return render(request, 'minhasescalas.html', {
            'escalas_futuras': [],
            'escalas_passadas': [],
            'titulo': 'As Minhas Escalas',
        })

    base_qs = Escala.objects.filter(irmao=irmao_obj).select_related(
        'actividade',
        'actividade__designacao',
        'actividade__localactividade',
        'funcao',
    )
    escalas_futuras = base_qs.filter(actividade__data__gte=hoje).order_by('actividade__data', 'actividade__inicio')
    escalas_passadas = base_qs.filter(actividade__data__lt=hoje).order_by('-actividade__data', '-actividade__inicio')[:20]

    context = {
        'escalas_futuras': escalas_futuras,
        'escalas_passadas': escalas_passadas,
        'titulo': 'As Minhas Escalas',
    }
    return render(request, 'minhasescalas.html', context)

@login_required
def escalar_em_massa(request, actividade_id):
    if request.method == 'POST':
        funcao_id = request.POST.get('funcao')
        irmaos_ids = request.POST.getlist('irmaos') # Multiple select returns list
        
        if funcao_id and irmaos_ids:
            actividade = get_object_or_404(Actividade, id=actividade_id)
            funcao = get_object_or_404(Funcao, id=funcao_id)
            
            novas_escalas = []
            ids_processados = set()
            
            for irmao_id in irmaos_ids:
                if irmao_id in ids_processados:
                    continue
                ids_processados.add(irmao_id)
                
                # Evitar que o membro seja escalado duas vezes na mesma Actividade (mesmo que com funções diferentes)
                if not Escala.objects.filter(actividade=actividade, irmao_id=irmao_id).exists():
                    novas_escalas.append(Escala(
                        actividade=actividade,
                        irmao_id=irmao_id,
                        funcao=funcao
                    ))
            
            if novas_escalas:
                Escala.objects.bulk_create(novas_escalas)
                messages.success(request, f'{len(novas_escalas)} irmãos escalados para {funcao.designacao} com sucesso!')
            else:
                messages.info(request, 'As pessoas selecionadas já estavam escaladas para esta actividade.')
                
    # Redirect back to the details page regardless of success/failure
    return redirect(f'/tibl/actividades/detalhe/{actividade_id}/')