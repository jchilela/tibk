 #!/usr/bi/python
# -*- encoding: utf-8 -*-

from django.db import models
from datetime import datetime, date
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.db.models import JSONField

# Create your models here.
MESES = (('1','Janeiro'),('2','Fevereiro'),('3','Março'),('4','Abril'),('5','Maio'),('6','Junho'),('7','Julho'),('8','Agosto'),('9','Setembro'),('10','Outubro'),('9','Novembro'),('10','Dezembro'))
MOEDA = (('AKZ','Kwanza'),('USD','USA Dólar'),('EU','Euro'),('R','Reais'),('RAN','ZA Rands'),('NAMD','Dólar Namibiano'), ('LB','Libra Inglesa'))
SEMANA = (('Seg','Segunda'),('Ter','Terça'),('Qua','Quarta'),('Qui','Quinta'),('Sex','Sexta'),('Sab','Sábado'),('Dom','Domingo'))
ACTIVO = (('sim','Sim'),('nao','Não'),)
VIA = (('1','Depósito'),('2','Transferência bancária'),('3','Multicaixa'),)



class Provincia(models.Model):
     nome = models.CharField(max_length=50, unique=True)
     codigo = models.CharField(max_length=3, unique=True)
     class Meta:
         ordering = ['nome']
         verbose_name = 'Província'
         verbose_name_plural = 'Províncias'
     def __str__(self):
         return self.nome

class Municipio(models.Model):
     nome = models.CharField(max_length=100)
     provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='municipios')
     class Meta:
         ordering = ['nome']
         verbose_name = 'Município'
         verbose_name_plural = 'Municípios'
         unique_together = ['nome', 'provincia']
     def __str__(self):
         return self.nome

class Profissao(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    def __str__(self):
        return '%s' % self.designacao
    class Admin:
        pass

class TipoOferta(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    def __str__(self):
        return '%s' % self.designacao
    class Admin:
        pass


class MomentosRealizados(models.Model):
    designacao = models.CharField(max_length = 200)
    def __str__(self):
        return self.designacao
    
class Tipo_Celula(models.Model):
    designacao = models.CharField(max_length = 200)
    def __str__(self):
        return self.designacao

DIAS_REUNIAO = (
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terça-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sábado'),
    ('domingo', 'Domingo'),
)

class Celula(models.Model):
    designacao = models.CharField('Designação', max_length=200, unique=True)
    lider = models.ForeignKey('Irmao', verbose_name='Líder', blank=True, null=True, on_delete=models.SET_NULL, related_name='celula_lider')
    vice_lider = models.ForeignKey('Irmao', verbose_name='Vice-Líder', blank=True, null=True, on_delete=models.SET_NULL, related_name='celula_vice_lider')
    local_reuniao = models.CharField('Local de Reunião', max_length=200, blank=True)
    dia_reuniao = models.CharField('Dia de Reunião', max_length=10, choices=DIAS_REUNIAO, blank=True)
    hora_reuniao = models.TimeField('Hora de Reunião', blank=True, null=True)
    descricao = models.TextField('Descrição', blank=True)
    activa = models.BooleanField('Activa', default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Célula'
        verbose_name_plural = 'Células'
        ordering = ['designacao']

    def __str__(self):
        return self.designacao
    
class Centro_Custo(models.Model):
    designacao = models.CharField(max_length = 200)
    def __str__(self):
        return self.designacao
    
class Status_Aprovacao(models.Model):
    designacao = models.CharField(max_length = 200)
    def __str__(self):
        return self.designacao

class Tipificacao_Custo(models.Model):
    designacao = models.CharField(max_length = 200)
    def __str__(self):
        return self.designacao
    
class Tipo_Moeda(models.Model):
    designacao = models.CharField(max_length = 200)
    abreviatura = models.CharField(max_length = 20)
    def __str__(self):
        return self.designacao

class Funcao(models.Model):
     designacao = models.CharField(max_length=50, unique = True )
     descricao = models.TextField("Descrição", blank=True)
     departamento = models.ForeignKey('Departamento', null=True, blank=True, on_delete=models.SET_NULL, related_name='funcoes')
     def __str__(self):
         return '%s' % self.designacao
     class Admin:
         pass

class Cargo(models.Model):
     designacao = models.CharField(max_length=50)
     descricao = models.TextField("Descrição", blank=True)
     def __str__(self):
         return '%s' % self.designacao
     class Admin:
         pass
     
class Categoria_Patrimonio(models.Model):
     designacao = models.CharField(max_length=50)
     def __str__(self):
         return '%s' % (self.designacao)
     class Admin:
         pass

class Estado_Patrimonio(models.Model):
     designacao = models.CharField(max_length=50)
     def __str__(self):
         return '%s' % (self.designacao)
     class Admin:
         pass

class Sitio(models.Model):
     TIPO = (('1', 'Igreja'),('2','Célula'),('3','Posto de Pregação'),('4','Colégio'),('5','Missão'))
     designacao = models.CharField('Designação', max_length =100, unique = True)
     ruaenumero = models.CharField("Rua e Número", max_length=60, blank=True)
     bairro = models.CharField(max_length=30, blank=True)
     provincia = models.ForeignKey(Provincia, verbose_name="Província", on_delete=models.SET_NULL, null=True, blank=True)
     municipio = models.ForeignKey(Municipio, verbose_name="Município", on_delete=models.SET_NULL, null=True, blank=True)
     dataFundacao = models.DateField("Data de Fundação",blank=True, null=True, default=None)
     numerodemembros = models.IntegerField(default=0)
     tipo = models.CharField(max_length=3, choices = TIPO)
     descricao = models.TextField("Descrição", blank=True)
     def __str__(self):
         return '%s' % self.designacao
     class Admin:
         pass

class Pessoa(models.Model):
     ESTADO_CIVIL = (('S','Solteiro(a)'),('C','Casado(a)'),('V','Viuvo(a)'),('A','Amaritado(a)'),('D','Divorciado(a)'),)
     GENERO = (('M','Masculino'),('F','Feminino'),)
     ESCOLARIDADE = (('basico','Básico'),('medio','Médio'),('superior','Superior'),)
     nome = models.CharField("Nome",max_length=30)
     apelido = models.CharField("Apelido",max_length=30)
     outrosnomes = models.CharField("Outros Nomes",max_length=60, blank=True)
     sexo = models.CharField(max_length=2, choices = GENERO, default = "M")
     foto = models.ImageField(upload_to="static/fotos/%Y", blank=True, null = True)
     datanascimento = models.DateField("Data de Nascimento", blank=True, null = True)
     estadocivil = models.CharField("Estado Civil",max_length=30, choices = ESTADO_CIVIL, default = "S")
     grauescolaridade = models.CharField("Grau de Escolaridade",max_length=50, choices = ESCOLARIDADE, blank=True)
     profissao = models.CharField("Profissão", max_length=100, blank=True, default="")
     especialidade = models.CharField("Especialidade",max_length=50, blank=True)
     localdetrabalho = models.CharField("Local de Trabalho",max_length=50, blank=True)
     ruaenumero = models.CharField("Rua e Número",max_length=60,blank=True)
     bairro = models.CharField(max_length=50, blank=True)
     provincia = models.ForeignKey(Provincia, verbose_name="Província", on_delete=models.SET_NULL, null=True, blank=True)
     municipio = models.ForeignKey(Municipio, verbose_name="Município", on_delete=models.SET_NULL, null=True, blank=True)
     telefone = models.CharField("Telefones",max_length=50, blank=True)
     telefonewhatsapp = models.CharField("Telefone do Whatsapp",max_length=50, blank=True)
     email = models.EmailField( blank=True)
     observacao = models.TextField("Observação", blank=True)

     @property
     def idade(self):
         """Idade em anos a partir da data de nascimento (None se desconhecida)."""
         if not self.datanascimento:
             return None
         hoje = date.today()
         anos = hoje.year - self.datanascimento.year
         if (hoje.month, hoje.day) < (self.datanascimento.month, self.datanascimento.day):
             anos -= 1
         return anos

     @property
     def e_menor(self):
         """True quando a idade conhecida é inferior a 18 anos."""
         idade = self.idade
         return idade is not None and idade < 18

     def __str__(self):
         return '%s %s %s' % (self.nome, self.apelido, self.outrosnomes)
     class Admin:
         pass
     
class Irmao(Pessoa):
     CULTO = (('P','Português'),('I','Inglês'),)
     CATEGORIA_CHOICES = (
         ('membro_batizado', 'Membro'),
         ('crianca', 'Criança'),
         ('assistente', 'Assistente'),
     )
     celula = models.ForeignKey(Sitio, blank=True, null=True, default=None, on_delete = models.PROTECT, related_name="celula")
     localcongregacao = models.ForeignKey(Sitio,verbose_name="Local de Congregação", blank=True, null=True, default=None, on_delete = models.PROTECT,related_name="igreja")
     culto = models.CharField(max_length=2, choices = CULTO, default = 'P')
     categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='assistente')
     dizimista = models.CharField(max_length = 10, choices = ACTIVO, default = 'nao')
     batizado = models.BooleanField(default=False)
     user = models.OneToOneField(User, verbose_name="User Django", blank=True, null=True, on_delete=models.CASCADE)
     data_criacao = models.DateTimeField(auto_now_add=True)
     data_atualizacao = models.DateTimeField(auto_now=True)

     def save(self, *args, **kwargs):
         # Rede de segurança: idade conhecida abaixo de 18 implica categoria 'crianca'.
         if self.e_menor:
             self.categoria = 'crianca'
         self.batizado = self.categoria == 'membro_batizado'
         super().save(*args, **kwargs)

     def __str__(self):
         return '%s %s' % (self.nome, self.apelido)
     class Admin:
         pass

class Departamento(models.Model):
     designacao = models.CharField('Designação', max_length =100, unique = True)
     abreviacao = models.CharField('Abreviação', max_length =10, unique = True, blank=True, null=True)
     descricao = models.TextField("Descrição", blank=True)
     lider_departamento = models.ForeignKey(Irmao, blank=True, null=True, on_delete=models.CASCADE, related_name="lider_departamento")
     vice_lider_departamento = models.ForeignKey(Irmao, blank=True, null=True, on_delete=models.CASCADE, related_name="Vice_lider_departamento")
     integrantes = models.ManyToManyField(Irmao, through = 'Mandato', blank=True, related_name= "integrantes_departamento")
     def __str__(self):
         return '%s' % self.designacao
     class Admin:
         pass

class Mandato(models.Model):
    FUNCAO_CHOICES = [
        ('membro', 'Membro'),
        ('lider', 'Líder'),
        ('vice_lider', 'Vice-Líder'),
        ('secretario', 'Secretário(a) departamental'),
        ('secretario_geral', 'Secretário(a) Geral'),
        ('tesoureiro', 'Tesoureiro(a)'),
        ('coordenador', 'Coordenador(a)'),
    ]
    FUNCOES_EXCLUSIVAS = {'lider', 'vice_lider', 'secretario', 'secretario_geral', 'tesoureiro', 'coordenador'}

    irmao = models.ForeignKey(Irmao, verbose_name = 'Irmão', on_delete = models.CASCADE)
    departamento = models.ForeignKey(Departamento, on_delete = models.CASCADE)
    funcao = models.CharField('Cargo', max_length=20, choices=FUNCAO_CHOICES, default='membro')
    inicio = models.DateField('Desde', blank = True, null = True)
    fim = models.DateField('Até', blank = True, null = True)
    def __str__(self):
        return '%s — %s (%s)' % (self.irmao, self.departamento, self.get_funcao_display())

    def save(self, *args, **kwargs):
        if self.funcao in self.FUNCOES_EXCLUSIVAS:
            qs = Mandato.objects.filter(
                departamento=self.departamento, funcao=self.funcao,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                qs.update(funcao='membro')
        super().save(*args, **kwargs)

        # Sincronizar FK do Departamento com mandato lider/vice_lider
        if self.funcao == 'lider':
            Departamento.objects.filter(pk=self.departamento_id).update(lider_departamento=self.irmao)
        elif self.funcao == 'vice_lider':
            Departamento.objects.filter(pk=self.departamento_id).update(vice_lider_departamento=self.irmao)
        else:
            # Se deixou de ser líder/vice, limpar FK correspondente
            Departamento.objects.filter(pk=self.departamento_id, lider_departamento=self.irmao).update(lider_departamento=None)
            Departamento.objects.filter(pk=self.departamento_id, vice_lider_departamento=self.irmao).update(vice_lider_departamento=None)

    class Admin:
        pass
    class Meta:
         unique_together = ('irmao', 'departamento')

class Banco(models.Model):
     designacao = models.CharField('Designação', max_length =100, unique = True)
     abreviacao = models.CharField('Abreviação', max_length =10, unique = True, blank=True, null=True)
     gestor = models.CharField('Gestor', max_length =200, blank=True, null=True)
     telefone = models.CharField(max_length = 200, blank=True, null=True)
     email = models.CharField(max_length = 200, blank=True, null=True)
     def __str__(self):
         return '%s' % self.designacao
     class Admin:
         pass

class Contabancaria(models.Model):
     is_active = models.BooleanField(default=True)
     banco = models.ForeignKey(Banco, on_delete = models.CASCADE)
     numeroconta = models.CharField('Número da conta', max_length =100, unique = True)
     iban = models.CharField('IBAN', max_length =100, unique = True)
     moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
     saldo = models.DecimalField( max_digits = 11, decimal_places = 2, default =0)
     proprietario = models.ForeignKey(Pessoa, on_delete = models.CASCADE, blank=True, null=True )
     instituicao = models.ForeignKey(Sitio, on_delete = models.CASCADE, blank=True, null=True )

     # ✅ saldo dinâmico
     def saldo_actual(self):

        entradas = Entrada.objects.filter(
            tipo='banco', contaaacreditar=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        saidas = Saida.objects.filter(
            tipo='banco', conta=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        transferencias_saida = Entrada.objects.filter(
            tipo='banco', contaorigem=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        transferencias_entrada = Saida.objects.filter(
            tipo='banco', contaaacreditar=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        return self.saldo + entradas - saidas - transferencias_saida + transferencias_entrada

     def __str__(self):
        return self.numeroconta

class Listaactividades(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    descricao = models.TextField("Descrição", blank=True)
    def __str__(self):
        return '%s' % self.designacao
    class Admin:
        pass

class Actividade(models.Model):
     DIAS_SEMANA_NOMES = {
         '0': 'Segunda-feira', '1': 'Terça-feira', '2': 'Quarta-feira',
         '3': 'Quinta-feira', '4': 'Sexta-feira', '5': 'Sábado', '6': 'Domingo',
     }

     designacao = models.ForeignKey(Listaactividades, on_delete = models.CASCADE )
     inicio = models.TimeField(max_length=10)
     fim = models.TimeField(max_length=60)
     data = models.DateField()
     tema = models.CharField(max_length = 500, blank = True)
     localactividade = models.ForeignKey(Sitio, blank=True, null=True, on_delete = models.DO_NOTHING)
     versosbiblicos = models.CharField(max_length = 200, blank = True)
     hinos = models.CharField(max_length = 300, blank = True)
     participantes = models.ManyToManyField(Irmao, through='Escala', related_name = 'particact')
     totalpresentes = models.IntegerField(default = 2)
     observacao = models.TextField("Observação", blank = True)
     departamento = models.ForeignKey('Departamento', null=True, blank=True, on_delete=models.SET_NULL, related_name='actividades')
     criado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='actividades_criadas')
     is_recorrente = models.BooleanField('É recorrente', default=False)
     recorrencia_fim = models.DateField('Recorrência até', null=True, blank=True)
     dias_semana = models.CharField('Dias da semana', max_length=20, blank=True,
                                    help_text='Números separados por vírgula (0=Segunda … 6=Domingo)')
     # Ligação ao django-scheduler (motor de recorrência — só nas actividades-pai)
     event = models.OneToOneField(
         'schedule.Event', null=True, blank=True, on_delete=models.SET_NULL,
         related_name='actividade', verbose_name='Evento (scheduler)',
     )
     # Actividades-filho (ocorrências expandidas) apontam para a actividade-pai
     parent_event = models.ForeignKey(
         'self', null=True, blank=True, on_delete=models.CASCADE,
         related_name='ocorrencias', verbose_name='Série pai',
     )

     def get_dias_semana_display(self):
         if not self.dias_semana:
             return ''
         return ', '.join(
             self.DIAS_SEMANA_NOMES.get(d.strip(), d.strip())
             for d in self.dias_semana.split(',')
         )
     def __str__(self):
         return '%s %s' % (self.designacao, self.data)
     class Admin:
         pass

class Escala(models.Model):
     irmao = models.ForeignKey(Irmao, on_delete = models.CASCADE, help_text='Irmão principal da escala')
     actividade = models.ForeignKey(Actividade, on_delete = models.CASCADE)
     funcao = models.ForeignKey(Funcao, on_delete = models.CASCADE, blank=True, null=True)
     eh_protocolo = models.BooleanField(default=False, verbose_name='É Protocolo?', help_text='Marque se esta escala é para protocolo (permite múltiplos irmãos)')
     irmao_protocolo = models.ManyToManyField(Irmao, related_name='escalas_protocolo', blank=True, verbose_name='Irmãos do Protocolo (máx. 10)', help_text='Selecione até 10 irmãos para protocolo')
     def __str__(self):
         return '%s %s %s' % (self.irmao, self.actividade, self.funcao)
     def clean(self):
         from django.core.exceptions import ValidationError
         if self.eh_protocolo and self.pk and self.irmao_protocolo.count() > 10:
             raise ValidationError('Máximo de 10 irmãos permitidos para protocolo')
     class Admin:
         pass
     class Meta:
         unique_together = ('irmao', 'actividade', 'funcao')

class Localizacao(models.Model):
     codigo = models.CharField(max_length=5)
     designacao = models.CharField(max_length=50)
     def __str__(self):
         return '%s %s' % (self.codigo, self.designacao)
     class Admin:
         pass

class Anuncio(models.Model):
     data = models.DateField()
     texto = models.TextField()
     quemanuncia = models.ForeignKey(Irmao, on_delete = models.CASCADE)
     def __str__(self):
         return '%s' % self.data
     class Admin:
         pass


class Gruporubrica(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    def __str__(self):
        return '%s' % (self.designacao)
    class Admin:
        pass

class Rubricaentrada(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    gruporubrica = models.ForeignKey(Gruporubrica, on_delete = models.CASCADE, blank = True, null = True)
    def __str__(self):
        return '%s' % (self.designacao)
    class Admin:
        pass

class Rubricasaida(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    gruporubrica = models.ForeignKey(Gruporubrica, on_delete = models.CASCADE, blank = True, null = True)
    def __str__(self):
        return '%s' % (self.designacao)
    class Admin:
        pass

class Servico(models.Model):
     designacao = models.CharField(max_length=200, unique = True)
     def __str__(self):
         return '%s' % (self.designacao)
     class Admin:
         pass

TIPO_MOVIMENTO = (('caixa', 'Caixa'), ('banco', 'Banco'),)

class Entrada(models.Model):
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_MOVIMENTO, default='caixa')
    valor = models.DecimalField(max_digits=11, decimal_places=2)
    moeda = models.CharField(max_length=50, choices=MOEDA, default="AKZ")
    data = models.DateField(default=datetime.today)
    hora = models.TimeField(default=timezone.now)
    rubrica = models.ForeignKey(Rubricaentrada, on_delete=models.CASCADE)
    responsavel = models.ForeignKey(Irmao, on_delete=models.CASCADE)
    observacao = models.TextField("Observação", blank=True)
    datacontrolo = models.DateField(auto_now=True)
    # Campos exclusivos para banco (opcionais quando tipo=caixa)
    contaaacreditar = models.ForeignKey(Contabancaria, verbose_name='Conta a creditar', on_delete=models.CASCADE, blank=True, null=True)
    via = models.CharField('Via', max_length=200, choices=VIA, blank=True)
    contaorigem = models.ForeignKey(Contabancaria, related_name='entradas_origem', verbose_name='Conta origem (transferência)', on_delete=models.CASCADE, blank=True, null=True)

    def clean(self):
        if self.tipo == 'banco':
            if not self.contaaacreditar:
                raise ValidationError({"contaaacreditar": "Conta bancária é obrigatória para entradas de banco."})
            if self.contaorigem:
                saldo_origem = self.contaorigem.saldo_actual()
                if self.valor > saldo_origem:
                    raise ValidationError({"valor": f"Saldo insuficiente na conta origem ({saldo_origem})"})
                if self.contaorigem == self.contaaacreditar:
                    raise ValidationError("Conta origem não pode ser igual à conta destino.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s' % (self.valor, self.get_tipo_display(), self.data)
    class Admin:
        pass

class Saida(models.Model):
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_MOVIMENTO, default='caixa')
    valor = models.DecimalField(max_digits=11, decimal_places=2)
    moeda = models.CharField(max_length=50, choices=MOEDA, default="AKZ")
    data = models.DateField(default=datetime.today)
    hora = models.TimeField(default=timezone.now)
    rubrica = models.ForeignKey(Rubricasaida, on_delete=models.CASCADE)
    responsavel = models.ForeignKey(Irmao, on_delete=models.CASCADE)
    observacao = models.TextField("Observação", blank=True)
    datacontrolo = models.DateField(auto_now=True)
    # Campos exclusivos para banco (opcionais quando tipo=caixa)
    conta = models.ForeignKey(Contabancaria, verbose_name='Conta', on_delete=models.CASCADE, blank=True, null=True)
    contaaacreditar = models.ForeignKey(Contabancaria, related_name='saidas_destino', verbose_name='Conta a creditar (transferência)', on_delete=models.CASCADE, blank=True, null=True)

    def clean(self):
        if self.tipo == 'banco':
            if not self.conta:
                raise ValidationError({"conta": "Conta bancária é obrigatória para saídas de banco."})
            if self.contaaacreditar and self.contaaacreditar == self.conta:
                raise ValidationError("Conta a creditar não pode ser igual à conta de origem.")
            saldo = self.conta.saldo_actual()
            if self.pk:
                anterior = Saida.objects.get(pk=self.pk)
                saldo += anterior.valor
            if self.valor > saldo:
                raise ValidationError({"valor": f"Saldo insuficiente. Saldo actual: {saldo}"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s' % (self.valor, self.get_tipo_display(), self.data)
    class Admin:
        pass

class Cestabasica(models.Model):
    codigo = models.DateField(unique = True)
    saida = models.ForeignKey('Saida', verbose_name='Saída', blank=True, null=True, on_delete=models.CASCADE)
    Datadisponvalor = models.DateField('Valor diponiblizado aos',blank = True, null = True)
    observacao = models.TextField('Observação', blank = True)
    def __str__(self):
        return '%s' % (self.codigo)
    class Admin:
         pass

class ComposicaoCesta(models.Model):
    cesta = models.ForeignKey(Cestabasica, on_delete = models.CASCADE)
    produto = models.CharField( max_length = 50 )
    quantidade = models.DecimalField( max_digits = 8, decimal_places = 2)
    precounitario = models.DecimalField(max_digits = 11, decimal_places = 2)
    def __str__(self):
        return '%s %s %s' % (self.produto, self.cesta, self.quantidade)
    class Admin:
        pass

class Dizimooferta(models.Model):
    valor = models.DecimalField(max_digits = 11, decimal_places = 2)
    moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
    tipooferta = models.ForeignKey(TipoOferta, verbose_name = 'Tipo de oferta', on_delete = models.CASCADE)
    datacorrespondente = models.DateField()
    irmao = models.ForeignKey(Irmao, verbose_name = 'Irmao Dizimista', on_delete = models.CASCADE)
    actividade = models.ForeignKey(Actividade, on_delete = models.CASCADE, blank = True, null = True)
    datacontrolo = models.DateField( auto_now = True)
    dataregisto = models.DateField(default = datetime.today)
    entrada = models.ForeignKey(Entrada, blank=True, null=True, on_delete=models.CASCADE)

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.irmao, self.datacorrespondente)
    class Admin:
        pass

class Tipoajuda(models.Model):
     designacao = models.CharField(max_length=200, unique = True)
     def __str__(self):
         return '%s' % (self.designacao)
     class Admin:
         pass

class Ajuda(models.Model):
     ajuda = models.CharField('Ajuda', max_length=200)
     beneficiario = models.ForeignKey(Pessoa, on_delete = models.CASCADE)
     patrocinador = models.ForeignKey(Pessoa, related_name = 'valordoador', on_delete = models.CASCADE, blank = True, null = True)
     valor = models.DecimalField('Valor[AKZ]', max_digits = 11, decimal_places = 2, default =0)
     cesta = models.ForeignKey(Cestabasica, on_delete = models.CASCADE, blank = True, null = True)
     data = models.DateField()
     saida = models.ForeignKey('Saida', verbose_name='Saída', blank=True, null=True, on_delete=models.CASCADE)
     observacao = models.TextField('Observação', blank = True, null = True)
     def __str__(self):
         return '%s %s' % (self.beneficiario, self.patrocinador)
     class Admin:
         pass

class Pagamentoservico(models.Model):
    servico = models.ForeignKey(Servico, on_delete = models.CASCADE)
    valor = models.DecimalField(max_digits = 11, decimal_places = 2)
    moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
    data = models.DateField(default = datetime.today)
    responsavel = models.ForeignKey(Irmao, on_delete = models.CASCADE)
    saida = models.ForeignKey('Saida', verbose_name='Saída', blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return '%s %s %s' % (self.servico, self.valor, self.data)
    class Admin:
        pass


class InventarioPatrimonio(models.Model):
     nome = models.CharField(max_length=100)
     descricao = models.CharField(max_length=100)
     categoria_patrimonio = models.ForeignKey(Categoria_Patrimonio, blank=True, null=True, default=None, on_delete = models.CASCADE)
     codigo = models.CharField(max_length=100, unique = True)
     quantidade = models.IntegerField()
     localizacao = models.CharField(max_length=100)
     preco = models.BigIntegerField()
     moeda = models.ForeignKey(Tipo_Moeda, on_delete=models.CASCADE, null=True, blank=True)
     data_aquisicao = models.DateField("Data de aquisição",null=True, blank=True)
     responsavel = models.ForeignKey(Irmao, blank=True, null=True, default=None, on_delete = models.CASCADE)
     foto = models.FileField(upload_to='', blank=True,)
     estado = models.ForeignKey(Estado_Patrimonio, on_delete=models.CASCADE, blank=True, null=True)
     observacao = models.TextField("Observação", blank = True, null=True)
     registo_danos = models.TextField("Registro de danos", blank = True, null=True)
     data_ultima_manutencao = models.DateField("Data da ultima Manutenção", null=True, blank=True)
     data_proxima_manutencao = models.DateField("Data da Proxima Manutenção", null=True, blank=True)
     descricao_manutencao_realizada = models.TextField("Descrição da manutenção realizada", blank = True)
     
     data_criacao = models.DateTimeField(auto_now_add=True)
     data_atualizacao = models.DateTimeField(auto_now=True)
     def __str__(self):
         return '%s' % (self.nome)
     class Admin:
         pass



class RelatorioSemanalCelula(models.Model):
    celula = models.ForeignKey(Celula, verbose_name='Célula', blank=True, null=True, on_delete=models.CASCADE, related_name='relatorios')
    nome_celula = models.ForeignKey(Tipo_Celula, blank=True, null=True, on_delete=models.CASCADE)
    lider_responsavel = models.ForeignKey(Irmao, blank = True, null = True, on_delete = models.CASCADE)
    local_reuniao = models.CharField(max_length=50)
    numero_participantes_membros = models.IntegerField()
    numero_participantes_visitantes = models.IntegerField()
    numero_participantes_criancas = models.IntegerField()
    momentos_realizados = models.ManyToManyField(MomentosRealizados)
    tema_palavra = models.CharField(max_length=50)
    versiculo_chave = models.CharField(max_length=50)
    resumo_mensagem = models.TextField()
    topicos_de_oracao = models.TextField()
    alvos_e_accoes_para_proxima_semana = models.TextField()
    observacoes_e_necessidades = models.TextField()
    assinatura_lider = models.CharField(max_length=100)
    data_reuniao = models.DateField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    def __str__(self):
         if self.celula:
             return self.celula.designacao
         if self.nome_celula:
             return self.nome_celula.designacao
         return f'Relatório #{self.pk}'
    

class PedidoSaida(models.Model):
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    PAGAMENTO_CHOICES = [
        ('nao_aplicavel', 'Não Aplicável'),
        ('aguardando', 'Aguardando Pagamento'),
        ('pago', 'Pago'),
    ]

    departamento = models.ForeignKey(Departamento, null=True, blank=True, on_delete=models.CASCADE)
    projecto = models.CharField('Projecto / Finalidade', max_length=100)
    montante = models.FloatField()
    moeda = models.ForeignKey(Tipo_Moeda, null=True, blank=True, on_delete=models.CASCADE)
    centro_custo = models.ForeignKey(Centro_Custo, null=True, blank=True, on_delete=models.CASCADE)
    requerente = models.ForeignKey(Irmao, blank=True, null=True, default=None, on_delete = models.CASCADE, related_name='requerente')
    tipificacao_custo = models.ForeignKey(Tipificacao_Custo, null=True, blank=True, on_delete=models.CASCADE)
    iban = models.CharField(max_length=50)
    justificativa_custo = models.TextField()
    documento_justificativo = models.FileField(upload_to='pedidos/', blank=True)
    # Aprovação
    status_de_aprovacao = models.ForeignKey(Status_Aprovacao, null=True, blank=True, on_delete=models.CASCADE)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendente')
    aprovador = models.ForeignKey(Irmao, blank=True, null=True, default=None, on_delete = models.CASCADE, related_name='aprovador')
    observacao_aprovador = models.TextField('Observação do Aprovador', blank=True)
    data_aprovacao = models.DateTimeField('Data de Aprovação', null=True, blank=True)
    # Efectivação / Pagamento
    estado_pagamento = models.CharField('Estado de Pagamento', max_length=20, choices=PAGAMENTO_CHOICES, default='nao_aplicavel')
    comprovativo_pagamento = models.FileField('Comprovativo de Pagamento', upload_to='comprovativos/', blank=True)
    data_pagamento = models.DateTimeField('Data de Pagamento', null=True, blank=True)
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    def __str__(self):
         return '%s' % (self.projecto)


class OrcamentoDepartamento(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=True, null=True)
    orcamento = models.FloatField()
    moeda = models.ForeignKey(Tipo_Moeda, on_delete=models.CASCADE, blank=True, null=True)
    ano = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    def __str__(self):
         return 'Orçamento do departamento --- %s' % (self.departamento.designacao) 


class ConteudoEnsino(models.Model):
    autor = models.ForeignKey(Irmao, on_delete=models.CASCADE, blank=True, null=True)
    titulo = models.CharField(max_length=100)
    ficheiro = models.FileField(upload_to='', blank=True,) 
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

class EnvioMensagem(models.Model):
    mensagem = models.TextField()
    sms = models.BooleanField(default=False, verbose_name='Enviar por SMS')
    email = models.BooleanField(default=False, verbose_name='Enviar por Email')
    sms_enviado = models.BooleanField(default=False, verbose_name='SMS enviado com sucesso')
    email_enviado = models.BooleanField(default=False, verbose_name='Email enviado com sucesso')
    quemenviou = models.ForeignKey(Departamento, blank=True, null=True, default=None, on_delete=models.SET_NULL, verbose_name='Departamento remetente')
    destinatarios = models.ManyToManyField(Irmao, blank=True, related_name='mensagens_recebidas', verbose_name='Destinatários')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)


class SolicitacaoInterdepartamental(models.Model):
    CATEGORIA_CHOICES = [
        ('material_criativo', 'Material Criativo'),
        ('equipamento', 'Equipamento'),
        ('verba', 'Verba'),
        ('cobertura_evento', 'Cobertura de Evento'),
        ('apoio_logistico', 'Apoio Logístico'),
        ('outro', 'Outro'),
    ]
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('concluido', 'Concluído'),
    ]
    # Transições de estado permitidas
    TRANSICOES_VALIDAS = {
        'pendente': ['em_analise'],
        'em_analise': ['aprovado', 'rejeitado'],
        'aprovado': ['concluido'],
        'rejeitado': [],
        'concluido': [],
    }

    departamento_solicitante = models.ForeignKey(
        Departamento, on_delete=models.CASCADE,
        related_name='solicitacoes_enviadas', verbose_name='Departamento Solicitante',
    )
    departamento_destinatario = models.ForeignKey(
        Departamento, on_delete=models.CASCADE,
        related_name='solicitacoes_recebidas', verbose_name='Departamento Destinatário',
    )
    solicitante = models.ForeignKey(
        Irmao, on_delete=models.CASCADE,
        related_name='solicitacoes_criadas', verbose_name='Solicitante',
    )
    assunto = models.CharField('Assunto', max_length=200)
    descricao = models.TextField('Descrição')
    categoria = models.CharField('Categoria', max_length=30, choices=CATEGORIA_CHOICES, default='outro')
    data_necessidade = models.DateField('Data de Necessidade')
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='normal')
    documento_anexo = models.FileField('Documento Anexo', upload_to='solicitacoes/', blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendente')
    responsavel_resposta = models.ForeignKey(
        Irmao, blank=True, null=True, on_delete=models.CASCADE,
        related_name='solicitacoes_respondidas', verbose_name='Responsável pela Resposta',
    )
    justificacao_resposta = models.TextField('Justificação da Resposta', blank=True)
    data_resposta = models.DateTimeField('Data da Resposta', null=True, blank=True)
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)
    # Campos financeiros (preenchidos quando categoria='verba')
    montante = models.FloatField('Montante', null=True, blank=True)
    moeda = models.ForeignKey(Tipo_Moeda, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Moeda')
    centro_custo = models.ForeignKey(Centro_Custo, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Centro de Custo')
    tipificacao_custo = models.ForeignKey(Tipificacao_Custo, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Tipificação de Custo')
    iban = models.CharField('IBAN', max_length=50, blank=True)
    justificativa_custo = models.TextField('Justificativa de Custo', blank=True)
    estado_pagamento = models.CharField('Estado de Pagamento', max_length=20, choices=PedidoSaida.PAGAMENTO_CHOICES, default='nao_aplicavel')
    comprovativo_pagamento = models.FileField('Comprovativo de Pagamento', upload_to='comprovativos/', blank=True)
    data_pagamento = models.DateTimeField('Data de Pagamento', null=True, blank=True)
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Solicitação Interdepartamental'
        verbose_name_plural = 'Solicitações Interdepartamentais'

    def __str__(self):
        return f'{self.assunto} ({self.departamento_solicitante} → {self.departamento_destinatario})'

    def pode_transitar_para(self, novo_estado):
        return novo_estado in self.TRANSICOES_VALIDAS.get(self.estado, [])


class HistoricoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(
        SolicitacaoInterdepartamental, on_delete=models.CASCADE,
        related_name='historico',
    )
    estado_anterior = models.CharField('Estado Anterior', max_length=20, blank=True, choices=SolicitacaoInterdepartamental.ESTADO_CHOICES)
    estado_novo = models.CharField('Estado Novo', max_length=20, choices=SolicitacaoInterdepartamental.ESTADO_CHOICES)
    responsavel = models.ForeignKey(Irmao, on_delete=models.CASCADE, verbose_name='Responsável')
    observacao = models.TextField('Observação', blank=True)
    documento_anexo = models.FileField('Documento Anexo', upload_to='solicitacoes/historico/', blank=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data']
        verbose_name = 'Histórico de Solicitação'
        verbose_name_plural = 'Históricos de Solicitação'

    def __str__(self):
        return f'{self.solicitacao.assunto}: {self.estado_anterior} → {self.estado_novo}'


class ComentarioSolicitacao(models.Model):
    solicitacao = models.ForeignKey(
        SolicitacaoInterdepartamental, on_delete=models.CASCADE,
        related_name='comentarios',
    )
    autor = models.ForeignKey(Irmao, on_delete=models.CASCADE, verbose_name='Autor')
    texto = models.TextField('Comentário')
    anexo = models.FileField('Anexo', upload_to='solicitacoes/comentarios/', blank=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data']
        verbose_name = 'Comentário de Solicitação'
        verbose_name_plural = 'Comentários de Solicitação'

    def __str__(self):
        return f'{self.autor} — {self.solicitacao.assunto}'


class NotificacaoSistema(models.Model):
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField('Título', max_length=200)
    mensagem = models.TextField('Mensagem')
    lida = models.BooleanField('Lida', default=False)
    url = models.CharField('URL', max_length=500, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return self.titulo


# ── Painel de Acompanhamento Pastoral ──────────────────────────

class CasoPastoral(models.Model):
    TIPO_CHOICES = [
        ('luto', 'Luto'),
        ('doenca', 'Doença'),
        ('aconselhamento', 'Aconselhamento'),
        ('crise_familiar', 'Crise Familiar'),
        ('hospitalizacao', 'Hospitalização'),
        ('necessidade_material', 'Necessidade Material'),
        ('integracao', 'Integração de Novo Membro'),
        ('restauracao', 'Restauração'),
        ('outro', 'Outro'),
    ]
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    ESTADO_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_acompanhamento', 'Em Acompanhamento'),
        ('resolvido', 'Resolvido'),
        ('encerrado', 'Encerrado'),
    ]

    membro = models.ForeignKey(Irmao, on_delete=models.CASCADE, related_name='casos_pastorais', verbose_name='Membro')
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_CHOICES)
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='normal')
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='aberto')
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição')
    confidencial = models.BooleanField('Confidencial', default=True)
    responsavel = models.ForeignKey(Irmao, on_delete=models.SET_NULL, null=True, blank=True, related_name='casos_atribuidos', verbose_name='Responsável')
    criado_por = models.ForeignKey(Irmao, on_delete=models.SET_NULL, null=True, blank=True, related_name='casos_criados', verbose_name='Criado por')
    data_abertura = models.DateTimeField('Data de Abertura', auto_now_add=True)
    data_encerramento = models.DateTimeField('Data de Encerramento', null=True, blank=True)
    data_atualizacao = models.DateTimeField('Última Actualização', auto_now=True)

    class Meta:
        ordering = ['-data_abertura']
        verbose_name = 'Caso Pastoral'
        verbose_name_plural = 'Casos Pastorais'

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.membro}'


class RegistoAcompanhamento(models.Model):
    TIPO_CHOICES = [
        ('visita_domiciliar', 'Visita Domiciliar'),
        ('chamada_telefonica', 'Chamada Telefónica'),
        ('mensagem', 'Mensagem (WhatsApp/SMS)'),
        ('reuniao_presencial', 'Reunião Presencial'),
        ('oracao', 'Oração'),
        ('encaminhamento', 'Encaminhamento'),
        ('outro', 'Outro'),
    ]

    caso = models.ForeignKey(CasoPastoral, on_delete=models.CASCADE, related_name='registos', verbose_name='Caso')
    tipo_contacto = models.CharField('Tipo de Contacto', max_length=30, choices=TIPO_CHOICES)
    descricao = models.TextField('Descrição')
    realizado_por = models.ForeignKey(Irmao, on_delete=models.SET_NULL, null=True, verbose_name='Realizado por')
    documento_anexo = models.FileField('Documento Anexo', upload_to='pastoral/registos/', blank=True)
    data = models.DateTimeField('Data', auto_now_add=True)
    proximo_passo = models.TextField('Próximo Passo', blank=True)
    data_proximo_contacto = models.DateField('Data do Próximo Contacto', null=True, blank=True)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Registo de Acompanhamento'
        verbose_name_plural = 'Registos de Acompanhamento'

    def __str__(self):
        return f'{self.get_tipo_contacto_display()} — {self.caso}'


class AlertaPastoral(models.Model):
    TIPO_CHOICES = [
        ('inactividade', 'Inactividade Prolongada'),
        ('novo_sem_acompanhamento', 'Novo Convertido sem Acompanhamento'),
        ('sem_celula', 'Sem Célula Atribuída'),
        ('ausencia_dizimo', 'Ausência de Dízimo'),
        ('aniversario', 'Aniversário'),
        ('visitante_recorrente', 'Visitante Recorrente'),
        ('queda_celula', 'Queda de Participação na Célula'),
        ('manual', 'Alerta Manual'),
    ]
    ESTADO_CHOICES = [
        ('novo', 'Novo'),
        ('visto', 'Visto'),
        ('em_tratamento', 'Em Tratamento'),
        ('resolvido', 'Resolvido'),
        ('ignorado', 'Ignorado'),
    ]

    membro = models.ForeignKey(Irmao, on_delete=models.CASCADE, null=True, blank=True, related_name='alertas_pastorais', verbose_name='Membro')
    celula = models.ForeignKey('Sitio', on_delete=models.CASCADE, null=True, blank=True, related_name='alertas_pastorais', verbose_name='Célula')
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_CHOICES)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='novo')
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição')
    dados_json = JSONField('Dados de Contexto', default=dict, blank=True)
    caso_associado = models.ForeignKey(CasoPastoral, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas', verbose_name='Caso Associado')
    gerado_automaticamente = models.BooleanField('Gerado Automaticamente', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Actualização', auto_now=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Alerta Pastoral'
        verbose_name_plural = 'Alertas Pastorais'

    def __str__(self):
        return self.titulo


class VisitanteRecorrente(models.Model):
    ESTADO_CHOICES = [
        ('visitante', 'Visitante'),
        ('em_integracao', 'Em Integração'),
        ('integrado', 'Integrado (tornou-se membro)'),
        ('desistiu', 'Desistiu'),
    ]

    nome = models.CharField('Nome', max_length=100)
    telefone = models.CharField('Telefone', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    celula = models.ForeignKey('Sitio', on_delete=models.CASCADE, null=True, blank=True, related_name='visitantes_recorrentes', verbose_name='Célula')
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='visitante')
    responsavel_integracao = models.ForeignKey(Irmao, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitantes_acompanhados', verbose_name='Responsável pela Integração')
    irmao_convertido = models.ForeignKey(Irmao, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitante_origem', verbose_name='Membro Convertido')
    numero_visitas = models.IntegerField('Número de Visitas', default=1)
    primeira_visita = models.DateField('Primeira Visita')
    ultima_visita = models.DateField('Última Visita')
    observacao = models.TextField('Observação', blank=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Actualização', auto_now=True)

    class Meta:
        ordering = ['-ultima_visita']
        verbose_name = 'Visitante Recorrente'
        verbose_name_plural = 'Visitantes Recorrentes'

    def __str__(self):
        return f'{self.nome} ({self.get_estado_display()})'


# ── Portal do Membro: Contribuições ──────────────────────────

TIPO_CONTRIBUICAO = (
    ('dizimo', 'Dízimo'),
    ('oferta', 'Oferta'),
    ('oferta_missionaria', 'Oferta Missionária'),
    ('oferta_construcao', 'Oferta para Construção'),
    ('doacao', 'Doação'),
    ('outra', 'Outra'),
)

ESTADO_CONTRIBUICAO = (
    ('pendente', 'Pendente'),
    ('confirmada', 'Confirmada'),
    ('rejeitada', 'Rejeitada/Anulada'),
)


class Contribuicao(models.Model):
    irmao = models.ForeignKey(Irmao, verbose_name='Membro', on_delete=models.CASCADE)
    tipo = models.CharField('Tipo de Contribuição', max_length=30, choices=TIPO_CONTRIBUICAO, default='dizimo')
    valor = models.DecimalField('Valor', max_digits=11, decimal_places=2)
    moeda = models.CharField('Moeda', max_length=50, choices=MOEDA, default='AKZ')
    data = models.DateField('Data da Contribuição', default=datetime.today)
    observacao = models.TextField('Observação', blank=True, null=True)
    comprovativo = models.FileField('Comprovativo', upload_to='comprovativos/', blank=True, null=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CONTRIBUICAO, default='pendente')
    data_registo = models.DateTimeField('Data de Registo', auto_now_add=True)
    data_validacao = models.DateTimeField('Data de Validação', blank=True, null=True)
    validado_por = models.ForeignKey(User, verbose_name='Validado por', on_delete=models.SET_NULL, blank=True, null=True, related_name='contribuicoes_validadas')
    nota_validacao = models.TextField('Nota de Validação', blank=True, null=True)
    entrada = models.ForeignKey('Entrada', verbose_name='Entrada gerada', on_delete=models.SET_NULL, blank=True, null=True, related_name='contribuicoes')
    dizimooferta = models.ForeignKey('Dizimooferta', verbose_name='Dízimo/Oferta gerado', on_delete=models.SET_NULL, blank=True, null=True, related_name='contribuicoes')

    class Meta:
        ordering = ['-data', '-data_registo']
        verbose_name = 'Contribuição'
        verbose_name_plural = 'Contribuições'

    def __str__(self):
        return f'{self.irmao} - {self.get_tipo_display()} - {self.data}'

    @property
    def valor_formatado(self):
        simbolo = {'AKZ': 'Kz', 'USD': '$', 'EUR': '€'}.get(self.moeda, '')
        return f'{float(self.valor):,.2f} {simbolo}'.replace(',', ' ').replace('.', ',').replace(' ,', ',')


# ── Checklists por Actividade e Departamento ─────────────────────

FREQUENCIA_CHECKLIST = (
    ('unica', 'Única'),
    ('diaria', 'Diária'),
    ('semanal', 'Semanal'),
    ('mensal', 'Mensal'),
)

DIAS_SEMANA_CHECKLIST = (
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo'),
)

class ChecklistActividade(models.Model):
    actividade = models.ForeignKey(Actividade, verbose_name='Actividade', on_delete=models.CASCADE, related_name='checklists')
    departamento = models.ForeignKey(Departamento, verbose_name='Departamento', on_delete=models.CASCADE, related_name='checklists')
    observacao = models.TextField('Observação', blank=True, null=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_actualizacao = models.DateTimeField('Última Actualização', auto_now=True)

    # ── Recorrência ──
    recorrencia = models.CharField('Recorrência', max_length=10, choices=FREQUENCIA_CHECKLIST, default='unica')
    dia_activacao = models.IntegerField('Dia de Activação', null=True, blank=True, help_text='Para semanal: 0=Segunda … 6=Domingo. Para mensal: dia do mês (1-31).')
    hora_notificacao = models.TimeField('Hora de Notificação', null=True, blank=True, help_text='Hora em que os responsáveis recebem a notificação.')
    notificar_responsaveis = models.BooleanField('Notificar responsáveis', default=True)
    ultima_geracao = models.DateTimeField('Última geração automática', null=True, blank=True)

    class Meta:
        verbose_name = 'Checklist de Actividade'
        verbose_name_plural = 'Checklists de Actividades'
        unique_together = ('actividade', 'departamento')
        ordering = ['departamento__designacao']

    def __str__(self):
        return f'{self.departamento} — {self.actividade}'

    @property
    def total_items(self):
        if hasattr(self, '_items_count_cache'):
            return self._items_count_cache
        return self.items.count()

    @property
    def items_concluidos(self):
        if hasattr(self, '_items_concluidos_cache'):
            return self._items_concluidos_cache
        return self.items.filter(concluido=True).count()

    @property
    def progresso(self):
        total = self.total_items
        if total == 0:
            return 0
        return int((self.items_concluidos / total) * 100)

    def prefetch_counts(self):
        """Pré-calcula contadores a partir de items já prefetched, evitando N+1."""
        items = list(self.items.all())
        self._items_count_cache = len(items)
        self._items_concluidos_cache = sum(1 for i in items if i.concluido)

    @property
    def recorrencia_display(self):
        if self.recorrencia == 'unica':
            return 'Única'
        label = dict(FREQUENCIA_CHECKLIST).get(self.recorrencia, self.recorrencia)
        if self.recorrencia == 'semanal' and self.dia_activacao is not None:
            dia = dict(DIAS_SEMANA_CHECKLIST).get(self.dia_activacao, '')
            return f'{label} — {dia}'
        if self.recorrencia == 'mensal' and self.dia_activacao is not None:
            return f'{label} — Dia {self.dia_activacao}'
        return label

    @property
    def notificacao_display(self):
        if self.hora_notificacao:
            return self.hora_notificacao.strftime('%Hh%M')
        return '—'

    def deve_gerar_hoje(self):
        from datetime import date
        hoje = date.today()
        if self.recorrencia == 'unica':
            return False
        if self.recorrencia == 'diaria':
            return True
        if self.recorrencia == 'semanal':
            return hoje.weekday() == self.dia_activacao
        if self.recorrencia == 'mensal':
            return hoje.day == self.dia_activacao
        return False


class ItemChecklist(models.Model):
    checklist = models.ForeignKey(ChecklistActividade, verbose_name='Checklist', on_delete=models.CASCADE, related_name='items')
    descricao = models.CharField('Descrição', max_length=300)
    ordem = models.IntegerField('Ordem', default=0)
    concluido = models.BooleanField('Concluído', default=False)
    responsavel = models.ForeignKey(Irmao, verbose_name='Responsável', on_delete=models.SET_NULL, blank=True, null=True)
    data_conclusao = models.DateTimeField('Data de Conclusão', blank=True, null=True)
    criado_por = models.ForeignKey(User, verbose_name='Criado por', on_delete=models.SET_NULL, blank=True, null=True, related_name='items_checklist_criados')

    class Meta:
        ordering = ['concluido', 'ordem', 'id']
        verbose_name = 'Item de Checklist'
        verbose_name_plural = 'Items de Checklist'

    def __str__(self):
        return f'{self.descricao} — {self.checklist.departamento} / {self.checklist.actividade}'


# ── Notificações de Checklist ────────────────────────────────────

TIPO_NOTIFICACAO = (
    ('atribuicao', 'Tarefa atribuída'),
    ('disponivel', 'Checklist disponível'),
    ('lembrete', 'Lembrete de execução'),
    ('proxima_prazo', 'Tarefa próxima do prazo'),
    ('atrasada', 'Tarefa atrasada'),
)


class NotificacaoChecklist(models.Model):
    destinatario = models.ForeignKey(Irmao, verbose_name='Destinatário', on_delete=models.CASCADE, related_name='notificacoes_checklist')
    checklist = models.ForeignKey(ChecklistActividade, verbose_name='Checklist', on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes')
    item = models.ForeignKey(ItemChecklist, verbose_name='Item', on_delete=models.SET_NULL, null=True, blank=True, related_name='notificacoes')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_NOTIFICACAO, default='disponivel')
    titulo = models.CharField('Título', max_length=200)
    mensagem = models.TextField('Mensagem')
    lida = models.BooleanField('Lida', default=False)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_leitura = models.DateTimeField('Data de Leitura', null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação de Checklist'
        verbose_name_plural = 'Notificações de Checklist'

    def __str__(self):
        return f'{self.destinatario} — {self.titulo}'

    @property
    def icon_class(self):
        icons = {
            'atribuicao': 'fa-user-plus',
            'disponivel': 'fa-clipboard-list',
            'lembrete': 'fa-bell',
            'proxima_prazo': 'fa-clock',
            'atrasada': 'fa-exclamation-triangle',
        }
        return icons.get(self.tipo, 'fa-bell')

    @property
    def color_class(self):
        colors = {
            'atribuicao': '#3b82f6',
            'disponivel': '#6366f1',
            'lembrete': '#10b981',
            'proxima_prazo': '#f59e0b',
            'atrasada': '#ef4444',
        }
        return colors.get(self.tipo, '#6b7280')