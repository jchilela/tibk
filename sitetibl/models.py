 #!/usr/bi/python
# -*- encoding: utf-8 -*-

from django.db import models
from datetime import datetime
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError

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
     def __str__(self):
         return '%s %s %s' % (self.nome, self.apelido, self.outrosnomes)
     class Admin:
         pass
     
class Irmao(Pessoa):
     CULTO = (('P','Português'),('I','Inglês'),)
     celula = models.ForeignKey(Sitio, blank=True, null=True, default=None, on_delete = models.PROTECT, related_name="celula")
     localcongregacao = models.ForeignKey(Sitio,verbose_name="Local de Congregação", blank=True, null=True, default=None, on_delete = models.PROTECT,related_name="igreja")
     culto = models.CharField(max_length=2, choices = CULTO, default = 'P')
     dizimista = models.CharField(max_length = 10, choices = ACTIVO, default = 'nao')
     batizado = models.BooleanField(default=False)
     user = models.OneToOneField(User, verbose_name="User Django", blank=True, null=True, on_delete=models.CASCADE)
     data_criacao = models.DateTimeField(auto_now_add=True)
     data_atualizacao = models.DateTimeField(auto_now=True)

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
        ('secretario', 'Secretário(a)'),
        ('tesoureiro', 'Tesoureiro(a)'),
        ('coordenador', 'Coordenador(a)'),
    ]
    FUNCOES_EXCLUSIVAS = {'lider', 'vice_lider', 'secretario', 'tesoureiro', 'coordenador'}

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

        entradas = Entradabanco.objects.filter(
            contaaacreditar=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        saidas = Saidabanco.objects.filter(
            conta=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        transferencias_saida = Entradabanco.objects.filter(
            contaorigem=self
        ).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        return self.saldo + entradas - saidas - transferencias_saida

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
     irmao = models.ForeignKey(Irmao, on_delete = models.CASCADE)
     actividade = models.ForeignKey(Actividade, on_delete = models.CASCADE)
     funcao = models.ForeignKey(Funcao, on_delete = models.CASCADE, blank=True, null=True)
     def __str__(self):
         return '%s %s %s' % (self.irmao, self.actividade, self.funcao)
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

class Entradacaixa(models.Model):
    valor = models.DecimalField(max_digits = 11, decimal_places = 2)
    moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
    data = models.DateField()
    hora = models.TimeField()
    responsavel = models.ForeignKey(Irmao, on_delete = models.CASCADE)
    rubrica = models.ForeignKey(Rubricaentrada, on_delete = models.CASCADE)
    observacao = models.TextField("Observação", blank = True)
    def __str__(self):
        return '%s %s' % (self.valor, self.data)
    class Admin:
        pass

class Saidacaixa(models.Model):
    valor = models.DecimalField(max_digits = 11, decimal_places = 2)
    moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
    data = models.DateField(default = datetime.today)
    hora = models.TimeField(default = timezone.now)
    responsavel = models.ForeignKey(Irmao, on_delete = models.CASCADE)
    rubrica = models.ForeignKey(Rubricasaida, on_delete = models.CASCADE)
    datacontrolo = models.DateField( auto_now = True)
    observacao = models.TextField("Observação", blank = True)
    def __str__(self):
        return '%s %s' % (self.valor, self.data)
    class Admin:
        pass

class Entradabanco(models.Model):
    contaaacreditar = models.ForeignKey(Contabancaria, on_delete = models.CASCADE,  blank = True, null = True)
    valor = models.DecimalField(max_digits = 11, decimal_places = 2)
    moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
    data = models.DateField(default = datetime.today)
    hora = models.TimeField(default = timezone.now)
    via = models.CharField(max_length = 200, choices = VIA)
    rubrica = models.ForeignKey(Rubricaentrada, on_delete = models.CASCADE)
    contaorigem = models.ForeignKey(Contabancaria, related_name = 'contadeprovinencia', on_delete = models.CASCADE, blank = True, null = True)
    responsavel = models.ForeignKey(Irmao, on_delete = models.CASCADE)
    datacontrolo = models.DateField( auto_now = True)
    observacao = models.TextField("Observação", blank = True)

    def clean(self):

        # valida apenas se for transferência
        if self.contaorigem:

            saldo_origem = self.contaorigem.saldo_actual()

            if self.valor > saldo_origem:
                raise ValidationError(
                    {"valor": f"Saldo insuficiente na conta origem ({saldo_origem})"}
                )

            if self.contaorigem == self.contaaacreditar:
                raise ValidationError(
                    "Conta origem não pode ser igual à conta destino."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s' % (self.valor, self.contaaacreditar, self.data)
    class Admin:
        pass

class Saidabanco(models.Model):
    conta = models.ForeignKey(Contabancaria, on_delete = models.CASCADE)
    valor = models.DecimalField(max_digits = 11, decimal_places = 2)
    moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
    data = models.DateField(default = datetime.today)
    hora = models.TimeField(default = timezone.now)
    rubrica = models.ForeignKey(Rubricaentrada, on_delete = models.CASCADE)
    responsavel = models.ForeignKey(Irmao, on_delete = models.CASCADE)
    contaaacreditar = models.ForeignKey(Contabancaria, related_name = 'contadestino', blank = True, null = True, on_delete = models.CASCADE)
    datacontrolo = models.DateField( auto_now = True)
    observacao = models.TextField("Observação", blank = True)

    def clean(self):

        saldo = self.conta.saldo_actual()

        # quando editar registo existente
        if self.pk:
            anterior = Saidabanco.objects.get(pk=self.pk)
            saldo += anterior.valor

        if self.valor > saldo:
            raise ValidationError(
                {"valor": f"Saldo insuficiente. Saldo actual: {saldo}"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s' % (self.valor, self.conta, self.data)
    class Admin:
        pass

class Cestabasica(models.Model):
    codigo = models.DateField(unique = True)
    saiudobanco = models.ForeignKey(Saidabanco, verbose_name='Saiu do banco', blank = True, null = True, on_delete = models.CASCADE)
    saiudacaixa = models.ForeignKey(Saidacaixa, verbose_name='Saiu da caixa', blank = True, null = True, on_delete = models.CASCADE)
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
    entradabanco = models.ForeignKey(Entradabanco, blank = True, null = True, on_delete = models.CASCADE)
    entradacaixa = models.ForeignKey(Entradacaixa, blank = True, null = True, on_delete = models.CASCADE)

    def clean(self):
        if self.entradabanco and self.entradacaixa:
            raise ValidationError(
                "O dízimo/oferta só pode estar vinculado ao banco ou à caixa, nunca aos dois."
            )

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
     saiudobanco = models.ForeignKey(Saidabanco, verbose_name='Saiu do banco', blank = True, null = True, on_delete = models.CASCADE)
     saiudacaixa = models.ForeignKey(Saidacaixa, verbose_name='Saiu da caixa', blank = True, null = True, on_delete = models.CASCADE)
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
    saiudobanco = models.ForeignKey(Saidabanco, verbose_name='Saiu do banco', blank = True, null = True, on_delete = models.CASCADE)
    saiudacaixa = models.ForeignKey(Saidacaixa, verbose_name='Saiu da caixa', blank = True, null = True, on_delete = models.CASCADE)
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
         return '%s' % (self.nome_celula1.designacao)
    

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
    sms = models.BooleanField(default=False)
    email = models.BooleanField(default=False)
    quemenviou = models.ForeignKey(Irmao, blank=True, null=True, default=None, on_delete = models.CASCADE)
    destinatarios = models.ManyToManyField(Irmao, blank=True, related_name='mensagens_recebidas', verbose_name='Destinatários')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)