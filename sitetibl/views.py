# Create your views here.
from django.contrib import admin, messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaulttags import register
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from datetime import date
from django import forms
from django.urls import reverse
from django.template import loader
from django.db.models import Sum, Count, F
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib import colors
import os
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncMonth
import json
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from collections import OrderedDict
from django.db.models.functions import ExtractWeekDay
from django.shortcuts import redirect
from pathlib import Path
import mimetypes

try:
    import markdown
except ImportError:
    markdown = None

#from django.db.models import Count

# Register your models here.
#from gestaoinfra.models import Contacto
from sitetibl.models import Irmao
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
from sitetibl.models import Cargo
from sitetibl.models import Mandato
from sitetibl.models import Escala
from sitetibl.models import Profissao
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
from sitetibl.forms import OrcamentoDepartamento
from sitetibl.forms import InventarioPatrimonio
from sitetibl.forms import ConteudoEnsino
from sitetibl.forms import EnvioMensagem

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

PROVINCIAS = {'BNG':'Bengo','BGL':'Benguela','BIE':'Bié','CAB':'Cabinda','CNE':'Cunene','HMB':'Huambo','HLA':'Huila','KKG':'Kuando kubango','KZN':'Kuanza Norte','KZS':'Kuanza Sul','LDA':'Luanda','LDN':'Lunda Norte','LDS':'Lunda Sul','MLG':'Malange','MXC':'Moxico','NMB':'Namibe','UGE':'Uige','ZAR':'Zaire'}

MOEDA = {'AKZ':'Kwanza','USD':'USA Dólar','EU':'Euro','R':'Reais','RAN':'ZA Rands','NAMD':'Dólar Namibiano', 'LB':'Libra Inglesa'}
MESES = {'1':'Janeiro','2':'Fevereiro','3':'Março','4':'Abril','5':'Maio','6':'Junho','7':'Julho','8':'Agosto','9':'Setembro','10':'Outubro','11':'Novembro','12':'Dezembro'}
TIPO = {'1':'Saude','2':'Falecimento','3':'Propina','4':'Cesta básica','5':'Casamento','6':'Outra'}
listafuncoes = Funcao.objects.values('id','designacao')
listaactividades = Listaactividades.objects.values('id','designacao')
listacargos = Cargo.objects.values('id','designacao')
listadepartamentos = Departamento.objects.values('id','designacao')
listaprofissoes = Profissao.objects.values('id','designacao')
listarubricasentrada = Rubricaentrada.objects.values('id', 'designacao')
listarubricassaida = Rubricasaida.objects.values('id', 'designacao')
#listacontasigreja = Contabancaria.objects.values('id', 'numeroconta','instituicao').filter( instituicao = 1 )
listacontasigreja = Contabancaria.objects.values('id','numeroconta','instituicao_id').filter(instituicao_id = 1)
tipoajuda = Tipoajuda.objects.values('id','designacao')

def comeco(request):
    return render(request, 'index.html')

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def mostraGestao(request,gestaoescolhida,pagina):
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
             'orcamentodepartamento':OrcamentoDepartamento,
             'inventariopatrimonio': InventarioPatrimonio,
             'conteudoensino':ConteudoEnsino,
             'enviomensagem':EnvioMensagem,
             }
    if (gestaoescolhida == 'irmaos'):
        resultado = lista[gestaoescolhida].objects.order_by('nome','outrosnomes')
    else:
        resultado = lista[gestaoescolhida].objects.order_by('id') 
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    if (gestaoescolhida == 'ajudas') or (gestaoescolhida == 'cestas') or (gestaoescolhida == 'actividades'):
        context = { 'bb':paginaresultado, 'listameses' : MESES, 'tipoajuda' : tipoajuda, 'listafuncoes' : listafuncoes, 'listaactividades' : listaactividades}
    elif gestaoescolhida == 'departamentos':
        context = { 'bb':paginaresultado, 'listadepartamentos' : listadepartamentos, 'listacargos' : listacargos}
    elif (gestaoescolhida == 'entradascaixa') or (gestaoescolhida == 'saidascaixa') or (gestaoescolhida == 'entradabancos') or (gestaoescolhida == 'saidabancos'):
        context = { 'bb':paginaresultado, 'listarubricasentrada' : listarubricasentrada, 'listarubricassaida' : listarubricassaida, 'listameses' : MESES, 'listacontasigreja' : listacontasigreja }
    else:
        context = { 'bb':paginaresultado, 'listaprofissoes' : listaprofissoes, 'listameses' : MESES }

    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, gestaoescolhida, context)


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

def mostraDetalhe(request, gestaoescolhida, identificador):
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
             'pedidosaida': PedidoSaida,
             'orcamentodepartamento': OrcamentoDepartamento,
             'inventariopatrimonio': InventarioPatrimonio,
             'conteudoensino':ConteudoEnsino,
             'enviomensagem':EnvioMensagem,
             'escalas':Escala,  
             }
    registoachado = lista[gestaoescolhida].objects.filter(id = identificador)
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
    else:
        context = {'registoachado' : registoachado, 'gestaoescolhida' : gestaoescolhida}
    return render(request, ficheirodetalhado, context)

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

    if request.method == 'POST':
        registo.delete()
        messages.success(request, 'Eliminação foi bem sucedida')
        return redirect('index')

    # GET → mostra confirmação
    return render(request, 'confirmar_eliminacao.html', {
        'registo': registo,
        'gestao': gestaoescolhida
    })

def mostraCriacao(request, gestaoescolhida):
    listaformularios = {'escalas' : EscalaForm, 
                        'manadatos': MandatoForm, 
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
            formulario.save()
            messages.success(request, 'Dados salvos com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Foram encontrados erros ao preencher o formulário')
    else:
        formulario = form_class()

    return render(request, 'formulario_criacao.html', {'formulario': formulario})

def encontraIrmao(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    municipiov = request.GET['municipiov']
    bairrov = request.GET['bairrov']
    profissaov = int(request.GET['profissaov'])
    pagina= request.GET['pagina']
    kwargs= {'nome__icontains':nomev, 'apelido__icontains' : apelidov, 'bairro__icontains' : bairrov, 'profissao_id' : profissaov }
    if (profissaov == 0):
        del kwargs['profissao_id']
    resultado = Irmao.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'irmaosfiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

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
    resultado = RelatorioSemanalCelula.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'relatoriosemanalcelulafiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

def encontraPedidoSaida(request):
    nomev = request.GET['projectov']
    liderv = request.GET['montantev']
    localv = request.GET['ibanv']
    kwargs= {'projecto__icontains':nomev, 
             'montante__icontains' : liderv, 
             'iban__icontains' : localv, 
              }
    pagina= request.GET['pagina']
    resultado = PedidoSaida.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'pedidosaidafiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

def encontraContasbancarias(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    bancov = request.GET['bancov']
    kwargs= {'proprietario__nome__icontains':nomev, 'proprietario__apelido__icontains' : apelidov, 'banco__designacao__icontains' : bancov }
    resultado = Contabancaria.objects.filter(**kwargs)
    return render(request,'contasbancariasfiltradas.html', {'bb': resultado })

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
    resultado = Ajuda.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'ajudasfiltradas.html', {'bb':paginaresultado})

def encontraCestas(request):
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'codigo__month':mesv, 'codigo__year' : anov}
    if (mesv == '0'):
        del kwargs['codigo__month']
    if (anov == '0'):
        del kwargs['codigo__year']
    resultado = Cestabasica.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'cestasfiltradas.html', {'bb':paginaresultado})

def encontraActividades(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    actividadev = int(request.GET['actividadev'])
    funcaov = int(request.GET['funcaov'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'irmao__nome__icontains' : nomev, 'irmao__apelido__icontains' : apelidov, 'actividade__designacao' : actividadev, 'funcao_id' : funcaov, 'actividade__data__month':mesv, 'actividade__data__year' : anov}
    if (actividadev == 0):
        del kwargs['actividade__designacao']
    if (funcaov == 0):
        del kwargs['funcao_id']
    if (mesv == '0'):
        del kwargs['actividade__data__month']
    if (anov == '0'):
        del kwargs['actividade__data__year']
    resultado = Escala.objects.values('actividade_id','actividade__designacao','actividade__designacao__designacao','actividade__data','funcao__designacao','irmao__nome','irmao__apelido','actividade__local').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'actividadesfiltradas.html', {'bb':paginaresultado})

def encontraDepartamentos(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    departamentov = int(request.GET['departamentov'])
    cargov = int(request.GET['cargov'])
    pagina= request.GET['pagina']
    kwargs= {'irmao__nome__icontains':nomev, 'irmao__apelido__icontains' : apelidov, 'cargo_id' : cargov, 'departamento_id' : departamentov }
    if (departamentov == 0):
        del kwargs['departamento_id']
    if (cargov == 0):
        del kwargs['cargo_id']
    resultado = Mandato.objects.values('departamento_id', 'departamento__designacao', 'cargo__designacao', 'irmao__nome', 'irmao__apelido').filter(**kwargs).order_by('departamento__designacao')
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'departamentosfiltrados.html', {'bb':paginaresultado})


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
    resultado = Dizimooferta.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'dizimosofertasfiltradas.html', {'bb':paginaresultado})

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

def encontraEntradasbanco(request):
    contabancariav = int(request.GET['contabancariav'])
    rubricav = int(request.GET['rubricav'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'contaaacreditar':contabancariav, 'rubrica':rubricav, 'data__month':mesv, 'data__year':anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (rubricav == 0):
        del kwargs['rubrica']
    if (contabancariav == 0):
        del kwargs['contaaacreditar']
    resultado = Entradabanco.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'entradasbancofiltradas.html', {'bb':paginaresultado})


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

def encontraEscalas(request):
    actividade = request.GET['actividade']
    funcao = request.GET['funcao']
    
    
    kwargs= {'actividade__designacao__designacao__icontains':actividade, 
             'funcao__designacao__icontains' : funcao, 
             
            }
    pagina= request.GET['pagina']
    resultado = Escala.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'escalasfiltrados.html', {'bb':paginaresultado})


#VIEWS PARA OS DASHBOARDS

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



#VIEWS QUE GERAM RELATÓRIOS
@login_required
def pagina_relatorios(request):
    return render(request, 'relatorios/template_relatorio.html')


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
    context = {
        'titulo': 'Dashboard',
    }
    return render(request, 'dashboard.html', context)


def serve_documentacao(request, path=''):
    site_dir = Path(settings.BASE_DIR) / 'docs' / 'site'
    file_path = site_dir / path if path else site_dir / 'index.html'

    if file_path.is_dir():
        file_path = file_path / 'index.html'

    if not file_path.exists() or not file_path.is_file():
        raise Http404

    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        open(file_path, 'rb'),
        content_type=content_type or 'application/octet-stream',
    )


@login_required
def guia_utilizador(request, modulo=None):
    docs_dir = (Path(settings.BASE_DIR) / 'docs').resolve()

    if modulo:
        guia_path = (docs_dir / modulo).resolve()
        if guia_path.suffix.lower() != '.md':
            return HttpResponse('Modulo do guia nao encontrado.', status=404)
        if docs_dir not in guia_path.parents or not guia_path.exists():
            return HttpResponse('Modulo do guia nao encontrado.', status=404)
    else:
        guia_path = docs_dir / 'GUIA_UTILIZADOR.md'

    if guia_path.exists():
        conteudo_markdown = guia_path.read_text(encoding='utf-8')
    else:
        conteudo_markdown = '# Guia do Utilizador\n\nO ficheiro de documentacao nao foi encontrado.'

    if markdown is not None:
        guia_html = markdown.markdown(
            conteudo_markdown,
            extensions=['extra', 'toc', 'sane_lists'],
        )
    else:
        guia_html = '<pre>{}</pre>'.format(escape(conteudo_markdown))

    context = {
        'titulo': 'Guia do Utilizador' if modulo is None else f'Guia do Utilizador - {modulo.replace("_", " ").title()}',
        'guia_html': mark_safe(guia_html),
    }
    return render(request, 'guia_utilizador_markdown.html', context)

def root_redirect(request):
    return redirect('dashboard')