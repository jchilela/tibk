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
from sitetibl.models import Patrimonio

from django.forms import ModelForm




class IrmaoForm(ModelForm):
    class Meta:
        model = Irmao
        fields = '__all__'

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

class SaidacaixaForm(ModelForm):
    class Meta:
        model = Saidacaixa
        fields = '__all__'

class EntradacaixaForm(ModelForm):
    class Meta:
        model = Entradacaixa
        fields = '__all__'

class SaidabancoForm(ModelForm):
    class Meta:
        model = Saidabanco
        fields = '__all__'

class EntradabancoForm(ModelForm):
    class Meta:
        model = Entradabanco
        fields = '__all__'

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

class PatrimonioForm(ModelForm):
    class Meta:
        model = Patrimonio
        fields = '__all__'
