#!/usr/bi/python
# -*- encoding: utf-8 -*-

from django.db import models
from datetime import datetime
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

# Create your models here.
PROVINCIAS = (('BNG','Bengo'),('BGL','Benguela'),('BIE','Bié'),('CAB','Cabinda'),('CNE','Cunene'),('HMB','Huambo'),('HLA','Huila'),('KKG','Kuando kubango'),('KZN','Kuanza Norte'),('KZS','Kuanza Sul'),('LDA','Luanda'),('LDN','Lunda Norte'),('LDS','Lunda Sul'),('MLG','Malange'),('MXC','Moxico'),('NMB','Namibe'),('UGE','Uige'),('ZAR','Zaire'))
MESES = (('1','Janeiro'),('2','Fevereiro'),('3','Março'),('4','Abril'),('5','Maio'),('6','Junho'),('7','Julho'),('8','Agosto'),('9','Setembro'),('10','Outubro'),('9','Novembro'),('10','Dezembro'))
MOEDA = (('AKZ','Kwanza'),('USD','USA Dólar'),('EU','Euro'),('R','Reais'),('RAN','ZA Rands'),('NAMD','Dólar Namibiano'), ('LB','Libra Inglesa'))
MUNICIPIOO = (('BE','Belas'),('CZ','Cazenga'),('KK','Kilamba Kiaxi'),('LU','Luanda'),('CA','Cacuaco'),('IC','Icolo e Bengo'),('TT','Talatona'),('VI','Viana'),('QU','Quissama'))
SEMANA = (('Seg','Segunda'),('Ter','Terça'),('Qua','Quarta'),('Qui','Quinta'),('Sex','Sexta'),('Sab','Sábado'),('Dom','Domingo'))
ACTIVO = (('sim','Sim'),('nao','Não'),)
VIA = (('1','Depósito'),('2','Transferência bancária'),('3','Multicaixa'),)



class Profissao(models.Model):
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
     municipio = models.CharField(max_length=60, blank=True)
     provincia = models.CharField(max_length=30, choices = PROVINCIAS, default = "LDA")
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
     profissao = models.ForeignKey(Profissao, on_delete = models.CASCADE, null = True, blank=True)
     especialidade = models.CharField("Especialidade",max_length=50, blank=True)
     localdetrabalho = models.CharField("Local de Trabalho",max_length=50, blank=True)
     ruaenumero = models.CharField("Rua e Número",max_length=60,blank=True)
     bairro = models.CharField(max_length=50, blank=True)
     municipio = models.CharField("Município",max_length=50, choices = MUNICIPIOO, blank=True)
     provincia = models.CharField("Província",max_length=50, choices = PROVINCIAS, default = "LDA")
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
    irmao = models.ForeignKey(Irmao, verbose_name = 'Irmão', on_delete = models.CASCADE)
    departamento = models.ForeignKey(Departamento, on_delete = models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete = models.CASCADE)
    inicio = models.DateField('Desde', blank = True, null = True)
    fim = models.DateField('Até', blank = True, null = True)
    def __str__(self):
        return ('%s %s %s') % (self.irmao, self.departamento, self.cargo)
    class Admin:
        pass
    class Meta:
         unique_together = ('irmao', 'departamento', 'cargo','inicio')

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
     banco = models.ForeignKey(Banco, on_delete = models.CASCADE)
     numeroconta = models.CharField('Número da conta', max_length =100, unique = True)
     iban = models.CharField('IBAN', max_length =100, unique = True)
     moeda = models.CharField(max_length=50, choices = MOEDA, default = "AKZ")
     saldo = models.DecimalField( max_digits = 11, decimal_places = 2, default =0)
     proprietario = models.ForeignKey(Pessoa, on_delete = models.CASCADE, blank=True, null=True )
     instituicao = models.ForeignKey(Sitio, on_delete = models.CASCADE, blank=True, null=True )
     def __str__(self):
         return '%s' % (self.numeroconta)
     class Admin:
         pass

class Listaactividades(models.Model):
    designacao = models.CharField(max_length = 200, unique = True)
    descricao = models.TextField("Descrição", blank=True)
    def __str__(self):
        return '%s' % self.designacao
    class Admin:
        pass

class Actividade(models.Model):
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
    contaaacreditar = models.ForeignKey(Contabancaria, on_delete = models.CASCADE)
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
    def __str__(self):
        return '%s %s %s' % (self.valor, self.conta, self.data)
    class Admin:
        pass

class Cestabasica(models.Model):
    codigo = models.DateField(unique = True)
    saiudobanco = models.ForeignKey(Saidabanco, blank = True, null = True, on_delete = models.CASCADE)
    saiudacaixa = models.ForeignKey(Saidacaixa, blank = True, null = True, on_delete = models.CASCADE)
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
    datacorrespondente = models.DateField()
    irmao = models.ForeignKey(Irmao, verbose_name = 'irmaodizimista', on_delete = models.CASCADE)
    actividade = models.ForeignKey(Actividade, on_delete = models.CASCADE, blank = True, null = True)
    datacontrolo = models.DateField( auto_now = True)
    dataregisto = models.DateField(default = datetime.today)
    entradabanco = models.ForeignKey(Entradabanco, blank = True, null = True, on_delete = models.CASCADE)
    entradacaixa = models.ForeignKey(Entradacaixa, blank = True, null = True, on_delete = models.CASCADE)
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
     ajuda = models.ForeignKey(Tipoajuda, on_delete = models.CASCADE)
     beneficiario = models.ForeignKey(Pessoa, on_delete = models.CASCADE)
     patrocinador = models.ForeignKey(Pessoa, related_name = 'valordoador', on_delete = models.CASCADE, blank = True, null = True)
     valor = models.DecimalField('Valor[AKZ]', max_digits = 11, decimal_places = 2, default =0)
     cesta = models.ForeignKey(Cestabasica, on_delete = models.CASCADE, blank = True, null = True)
     data = models.DateField()
     saiudobanco = models.ForeignKey(Saidabanco, blank = True, null = True, on_delete = models.CASCADE)
     saiudacaixa = models.ForeignKey(Saidacaixa, blank = True, null = True, on_delete = models.CASCADE)
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
    saiudobanco = models.ForeignKey(Saidabanco, blank = True, null = True, on_delete = models.CASCADE)
    saiudacaixa = models.ForeignKey(Saidacaixa, blank = True, null = True, on_delete = models.CASCADE)
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
    departamento = models.ForeignKey(Departamento, null=True, blank=True, on_delete=models.CASCADE)
    projecto = models.CharField(max_length=100)
    montante = models.FloatField()
    moeda = models.ForeignKey(Tipo_Moeda, null=True, blank=True, on_delete=models.CASCADE)
    centro_custo = models.ForeignKey(Centro_Custo, null=True, blank=True, on_delete=models.CASCADE)
    requerente = models.ForeignKey(Irmao, blank=True, null=True, default=None, on_delete = models.CASCADE, related_name='requerente')
    tipificacao_custo = models.ForeignKey(Tipificacao_Custo, null=True, blank=True, on_delete=models.CASCADE)
    iban = models.CharField(max_length=50)
    justificativa_custo = models.TextField()
    documento_justificativo = models.FileField(upload_to='', blank=True,) 
    status_de_aprovacao = models.ForeignKey(Status_Aprovacao, null=True, blank=True, on_delete=models.CASCADE)
    aprovador = models.ForeignKey(Irmao, blank=True, null=True, default=None, on_delete = models.CASCADE, related_name='aprovador')
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
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)