from django.contrib import admin

# Register your models here.
from sitetibl.models import Sitio
from sitetibl.models import Departamento
from sitetibl.models import Banco
from sitetibl.models import Contabancaria
from sitetibl.models import Pessoa
from sitetibl.models import Irmao
from sitetibl.models import Funcao
from sitetibl.models import Cestabasica
from sitetibl.models import Ajuda
from sitetibl.models import ComposicaoCesta
from sitetibl.models import Actividade
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
from sitetibl.models import Categoria_Patrimonio
from sitetibl.models import InventarioPatrimonio
from sitetibl.models import Tipoajuda
from sitetibl.models import RelatorioSemanalCelula
from sitetibl.models import PedidoSaida
from sitetibl.models import MomentosRealizados
from sitetibl.models import Tipo_Celula
from sitetibl.models import Centro_Custo
from sitetibl.models import Tipificacao_Custo
from sitetibl.models import Status_Aprovacao
from sitetibl.models import Tipo_Moeda
from sitetibl.models import OrcamentoDepartamento
from sitetibl.models import Estado_Patrimonio
from sitetibl.models import ConteudoEnsino
from .forms import IrmaoForm

@admin.register(Irmao)
class SitioAdmin(admin.ModelAdmin):
    form = IrmaoForm


admin.site.register(Sitio)
admin.site.register(Departamento)
admin.site.register(Banco)
admin.site.register(Contabancaria)
admin.site.register(Pessoa)
#admin.site.register(Irmao)
admin.site.register(RelatorioSemanalCelula)
admin.site.register(Funcao)
admin.site.register(Cestabasica)
admin.site.register(Ajuda)
admin.site.register(ComposicaoCesta)
admin.site.register(Actividade)
admin.site.register(Listaactividades)
admin.site.register(Cargo)
admin.site.register(Mandato)
admin.site.register(Escala)
admin.site.register(Profissao)
admin.site.register(Rubricaentrada)
admin.site.register(Rubricasaida)
admin.site.register(Saidacaixa)
admin.site.register(Saidabanco)
admin.site.register(Entradacaixa)
admin.site.register(Entradabanco)
admin.site.register(Dizimooferta)
admin.site.register(Pagamentoservico)
admin.site.register(Gruporubrica)
admin.site.register(Servico)
admin.site.register(Categoria_Patrimonio)
admin.site.register(InventarioPatrimonio)
admin.site.register(Tipoajuda)
admin.site.register(PedidoSaida)
admin.site.register(MomentosRealizados)
admin.site.register(Tipo_Celula)
admin.site.register(Centro_Custo)
admin.site.register(Tipificacao_Custo)
admin.site.register(Status_Aprovacao)
admin.site.register(Tipo_Moeda)
admin.site.register(OrcamentoDepartamento)
admin.site.register(Estado_Patrimonio)
admin.site.register(ConteudoEnsino)