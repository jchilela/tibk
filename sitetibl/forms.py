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
from sitetibl.models import TipoOferta

from django.forms import ModelForm , CheckboxSelectMultiple
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re


class ContabancariaForm(forms.ModelForm):
    class Meta:
        model = Contabancaria
        fields = ['banco','numeroconta','iban','moeda','proprietario','instituicao']
        #Estilos bootstrap
        widgets = {
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'numeroconta': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nº da Conta'}),
            'iban': forms.TextInput(attrs={'class': 'form-control','placeholder': 'AO06...'}),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
            'proprietario': forms.Select(attrs={'class': 'form-control'}),
            'instituicao': forms.Select(attrs={'class': 'form-control'}),
        }

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
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@tibl.com'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '9XXXXXXXX'
            }),
            
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("O email é obrigatório.")

        # Validação explícita de email válido
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Digite um email válido.")

        return email.lower()

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        if not telefone:
            raise forms.ValidationError("O telefone é obrigatório.")

        # Permitir apenas números
        if not telefone.isdigit():
            raise forms.ValidationError("O telefone deve conter apenas números.")

        # (Opcional) validar tamanho — exemplo: 9 dígitos
        if len(telefone) < 9:
            raise forms.ValidationError("O telefone deve conter no minimo 9 dígitos.")

        return telefone

            


class ContabancariaForm(ModelForm):
    class Meta:
        model = Contabancaria
        fields = '__all__'
        widgets = {
            'numeroconta': forms.TextInput(attrs={
                'placeholder': '1XXXXXXXX'
            }),
            'iban': forms.TextInput(attrs={
                'placeholder': 'AO06 XXXX XXXX XXXX XXXX XXXX X'
            }),
        }
    
    def clean_numeroconta(self):
        numero = self.cleaned_data.get('numeroconta')

        if not numero:
            raise forms.ValidationError("O número da conta é obrigatório.")

        # Apenas números
        if not numero.isdigit():
            raise forms.ValidationError("O número da conta deve conter apenas números.")

        # Exemplo: mínimo de 10 dígitos (ajuste conforme o banco)
        if len(numero) < 10:
            raise forms.ValidationError("O número da conta deve conter no mínimo 10 dígitos.")

        return numero

    def clean_iban(self):
        iban = self.cleaned_data.get('iban')

        if not iban:
            raise forms.ValidationError("O IBAN é obrigatório.")

        iban = iban.replace(' ', '').upper()

        # Validação específica para Angola (AO)
        if not iban.startswith('AO'):
            raise forms.ValidationError("O IBAN deve ser de Angola e começar com (AO06).")
        
        # Validação básica de IBAN (estrutura)
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$', iban):
            raise forms.ValidationError("IBAN inválido.")


        return iban

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
        widgets = {
            'inicio': forms.DateInput(attrs={'type': 'date'}),
            'fim': forms.DateInput(attrs={'type': 'date'}),
        }

class EscalaForm(ModelForm):
    class Meta:
        model = Escala
        fields = '__all__'

class DizimoofertaForm(ModelForm):
    class Meta:
        model = Dizimooferta
        fields = '__all__'
        widgets = {
            'dataregisto': forms.DateInput(attrs={'type': 'date'}),
            'datacorrespondente': forms.DateInput(attrs={'type': 'date'})
        }

class DizimoForm(ModelForm):
    class Meta:
        model = Dizimooferta
        fields = '__all__'
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
            'tipooferta': forms.Select(attrs={'class': 'form-control'}),
            'datacorrespondente': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'irmao': forms.Select(attrs={'class': 'form-control'}),
            'actividade': forms.Select(attrs={'class': 'form-control'}),
            'dataregisto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'entradabanco': forms.Select(attrs={'class': 'form-control'}),
            'entradacaixa': forms.Select(attrs={'class': 'form-control'}),
        }

class OfertaForm(ModelForm):
    class Meta:
        model = TipoOferta
        fields = '__all__'
        widgets = {
            'designacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designação da Oferta'}),
        }

class SaidacaixaForm(ModelForm):
    class Meta:
        model = Saidacaixa
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'}),
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')

       
        if valor < 0:
            raise forms.ValidationError("O valor digitado não pode ser negativo.")
        
        return valor

class EntradacaixaForm(ModelForm):
    class Meta:
        model = Entradacaixa
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'})
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')

       
        if valor < 0:
            raise forms.ValidationError("O valor digitado não pode ser negativo.")
        
        return valor

class SaidabancoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show real-time balance in account dropdowns for safer bank operations.
        if 'conta' in self.fields:
            self.fields['conta'].label_from_instance = (
                lambda obj: f"{obj.numeroconta} - Saldo: {obj.saldo_actual():.2f} {obj.moeda}"
            )
        if 'contaaacreditar' in self.fields:
            self.fields['contaaacreditar'].label_from_instance = (
                lambda obj: f"{obj.numeroconta} - Saldo: {obj.saldo_actual():.2f} {obj.moeda}"
            )

    class Meta:
        model = Saidabanco
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'})
        }
        


class EntradabancoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show real-time balance in account dropdowns for safer bank operations.
        if 'contaaacreditar' in self.fields:
            self.fields['contaaacreditar'].label_from_instance = (
                lambda obj: f"{obj.numeroconta} - Saldo: {obj.saldo_actual():.2f} {obj.moeda}"
            )
        if 'contaorigem' in self.fields:
            self.fields['contaorigem'].label_from_instance = (
                lambda obj: f"{obj.numeroconta} - Saldo: {obj.saldo_actual():.2f} {obj.moeda}"
            )

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
        exclude = ['status_de_aprovacao', 'aprovador']

class PedidoSaidaUpdateForm(ModelForm):
    class Meta:
        model = PedidoSaida
        fields = '__all__'
        exclude = ['aprovador']

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