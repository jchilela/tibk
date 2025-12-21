from sitetibl.models import Irmao
from sitetibl.models import Ajuda
from sitetibl.models import Cestabasica
from sitetibl.models import Banco
from sitetibl.models import Contabancaria
from sitetibl.models import Actividade
from sitetibl.models import Departamento
from sitetibl.models import Mandato
from sitetibl.models import Escala
from sitetibl.models import Saidacaixa
from sitetibl.models import Saidabanco
from sitetibl.models import Entradacaixa
from sitetibl.models import Entradabanco
from sitetibl.models import Dizimooferta
from sitetibl.models import Pagamentoservico
from sitetibl.models import Gruporubrica
from sitetibl.models import Servico
from sitetibl.models import Sitio
from sitetibl.models import RelatorioSemanalCelula
from sitetibl.models import PedidoSaida
from sitetibl.models import OrcamentoDepartamento
from sitetibl.models import InventarioPatrimonio
from sitetibl.models import ConteudoEnsino
from sitetibl.models import EnvioMensagem

from django.forms import ModelForm , CheckboxSelectMultiple
from django import forms
from django.core.validators import RegexValidator




class IrmaoForm(ModelForm):
    telefone = forms.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='O telefone deve conter exatamente 9 números.'
            )
        ]
    )

    class Meta:
        model = Irmao
        fields = '__all__'
        widgets = {
            'datanascimento': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #filtrar as dropdown para aparecer ou celula ou igreja
        self.fields['celula'].queryset = Sitio.objects.filter(tipo='2')
        self.fields['localcongregacao'].queryset = Sitio.objects.filter(tipo='1')

class AjudaForm(ModelForm):
    class Meta:
        model = Ajuda
        fields = '__all__'

class CestabasicaForm(ModelForm):
    class Meta:
        model = Cestabasica
        fields = '__all__'

class BancoForm(ModelForm):
    class Meta:
        model = Banco
        fields = '__all__'

class ContabancariaForm(ModelForm):
    class Meta:
        model = Contabancaria
        fields = '__all__'

class ActividadeForm(ModelForm):
    class Meta:
        model = Actividade
        exclude = ('participantes',)
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'inicio': forms.DateInput(attrs={'type': 'time'}),
            'fim': forms.DateInput(attrs={'type': 'time'}),
        }

class DepartamentoForm(ModelForm):
    class Meta:
        model = Departamento
        exclude = ('integrantes',)

class MandatoForm(ModelForm):
    class Meta:
        model = Mandato
        fields = '__all__'

class EscalaForm(ModelForm):
    class Meta:
        model = Escala
        fields = '__all__'

class DizimoofertaForm(ModelForm):
    class Meta:
        model = Dizimooferta
        fields = '__all__'
        widgets = {
            'dataregisto': forms.DateInput(attrs={'type': 'date'})
        }

class SaidacaixaForm(ModelForm):
    class Meta:
        model = Saidacaixa
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'}),
        }
        

class EntradacaixaForm(ModelForm):
    class Meta:
        model = Entradacaixa
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'})
        }
        

class SaidabancoForm(ModelForm):
    class Meta:
        model = Saidabanco
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'})
        }
        


class EntradabancoForm(ModelForm):
    class Meta:
        model = Entradabanco
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'})
        }
        



class PagamentoservicoForm(ModelForm):
    class Meta:
        model = Pagamentoservico
        fields = '__all__'

class GruporubricaForm(ModelForm):
    class Meta:
        model = Gruporubrica
        fields = '__all__'
        
class ServicoForm(ModelForm):
    class Meta:
        model = Servico
        fields = '__all__'


class  RelatorioSemanalCelulaForm(ModelForm):
    class Meta:
        model = RelatorioSemanalCelula
        fields = '__all__'
        widgets = {
            'momentos_realizados': forms.CheckboxSelectMultiple(),
            'data_reuniao': forms.DateInput(attrs={'type': 'date'})
        }
       
#Exclusão de um determinado campo no formulario de cadastro
class PedidoSaidaForm(ModelForm):
    class Meta:
        model = PedidoSaida
        fields = '__all__'
        exclude = ['status_de_aprovacao']

class PedidoSaidaUpdateForm(ModelForm):
    class Meta:
        model = PedidoSaida
        fields = '__all__'

class OrcamentoDepartamentoForm(ModelForm):
    class Meta:
        model = OrcamentoDepartamento
        fields = '__all__'

class InventarioPatrimonioForm(ModelForm):
    class Meta:
        model = InventarioPatrimonio
        fields = '__all__'
        widgets = {
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}),
            'data_ultima_manutencao': forms.DateInput(attrs={'type': 'date'}),
            'data_proxima_manutencao': forms.DateInput(attrs={'type': 'date'}),
        }

class ConteudoEnsinoForm(ModelForm):
    class Meta:
        model = ConteudoEnsino
        fields = '__all__'

class EnvioMensagemForm(ModelForm):
    class Meta:
        model = EnvioMensagem
        fields = '__all__'