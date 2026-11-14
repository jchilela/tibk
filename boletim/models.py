from django.contrib.auth.models import User
from django.db import models

from sitetibl.models import Actividade, CasoPastoral, Funcao


DIAS_SEMANA = (
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo'),
)


class Boletim(models.Model):
    ESTADO_RASCUNHO = 'rascunho'
    ESTADO_PUBLICADO = 'publicado'
    ESTADO_CHOICES = (
        (ESTADO_RASCUNHO, 'Rascunho'),
        (ESTADO_PUBLICADO, 'Publicado'),
    )

    actividade = models.OneToOneField(
        Actividade, on_delete=models.CASCADE, related_name='boletim',
        verbose_name='Culto (actividade)',
    )
    estado = models.CharField('Estado', max_length=10, choices=ESTADO_CHOICES, default=ESTADO_RASCUNHO)
    titulo_pt = models.CharField('Título', max_length=200, default='Ordem do Culto')
    titulo_en = models.CharField('Título (EN)', max_length=200, blank=True, default='Order of Service')
    leitura_referencia = models.CharField('Leitura bíblica (referência)', max_length=200, blank=True)
    leitura_texto_pt = models.TextField('Texto da leitura', blank=True)
    leitura_texto_en = models.TextField('Texto da leitura (EN)', blank=True)
    hino_referencia = models.CharField('Hino (referência)', max_length=300, blank=True)
    hino_letra = models.TextField('Letra do hino', blank=True)
    link_transmissao = models.URLField('Link da transmissão', blank=True)
    link_gravacao = models.URLField('Link da gravação', blank=True)
    notas_sermao = models.TextField('Notas do sermão', blank=True)
    publicado_em = models.DateTimeField('Publicado em', null=True, blank=True)
    criado_por = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='boletins_criados', verbose_name='Criado por',
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    actualizado_em = models.DateTimeField('Actualizado em', auto_now=True)

    class Meta:
        ordering = ['-actividade__data', '-actividade__inicio']
        verbose_name = 'Boletim'
        verbose_name_plural = 'Boletins'

    def __str__(self):
        return f'{self.titulo_pt} — {self.actividade.data:%d/%m/%Y}'

    @property
    def data(self):
        return self.actividade.data

    @property
    def publicado(self):
        return self.estado == self.ESTADO_PUBLICADO


class ItemOrdemCulto(models.Model):
    boletim = models.ForeignKey(Boletim, on_delete=models.CASCADE, related_name='itens')
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)
    titulo_pt = models.CharField('Título', max_length=200)
    titulo_en = models.CharField('Título (EN)', max_length=200, blank=True)
    detalhe = models.CharField('Detalhe', max_length=200, blank=True,
                               help_text='Por exemplo, «Salmos 29:1-4» ou «Hino 10».')

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Item da ordem do culto'
        verbose_name_plural = 'Itens da ordem do culto'

    def __str__(self):
        return self.titulo_pt


class ModeloOrdemCulto(models.Model):
    nome = models.CharField('Nome', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Modelo de ordem do culto'
        verbose_name_plural = 'Modelos de ordem do culto'

    def __str__(self):
        return self.nome


class ItemModeloOrdemCulto(models.Model):
    modelo = models.ForeignKey(ModeloOrdemCulto, on_delete=models.CASCADE, related_name='itens')
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)
    titulo_pt = models.CharField('Título', max_length=200)
    titulo_en = models.CharField('Título (EN)', max_length=200, blank=True)
    detalhe = models.CharField('Detalhe', max_length=200, blank=True)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Item do modelo'
        verbose_name_plural = 'Itens do modelo'

    def __str__(self):
        return self.titulo_pt


class FuncaoBoletim(models.Model):
    funcao = models.OneToOneField(Funcao, on_delete=models.CASCADE, related_name='funcao_boletim',
                                  verbose_name='Função da escala')
    rotulo_pt = models.CharField('Rótulo', max_length=100)
    rotulo_en = models.CharField('Rótulo (EN)', max_length=100, blank=True)
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Função no boletim'
        verbose_name_plural = 'Funções no boletim'

    def __str__(self):
        return f'{self.funcao} → {self.rotulo_pt}'


class ProgramaSemanal(models.Model):
    dia_semana = models.PositiveSmallIntegerField('Dia da semana', choices=DIAS_SEMANA)
    hora_inicio = models.TimeField('Hora de início')
    hora_fim = models.TimeField('Hora de fim', null=True, blank=True)
    titulo_pt = models.CharField('Título', max_length=200)
    titulo_en = models.CharField('Título (EN)', max_length=200, blank=True)
    activo = models.BooleanField('Activo', default=True)
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)

    class Meta:
        ordering = ['ordem', 'dia_semana', 'hora_inicio']
        verbose_name = 'Programa semanal'
        verbose_name_plural = 'Programas semanais'

    def __str__(self):
        return f'{self.get_dia_semana_display()} {self.hora_inicio:%H:%M} — {self.titulo_pt}'


class ConfiguracaoBoletim(models.Model):
    """Registo único (pk=1) com os dados fixos do boletim."""

    nome_igreja_pt = models.CharField('Nome da igreja', max_length=200,
                                      default='Terceira Igreja Baptista de Luanda')
    nome_igreja_en = models.CharField('Nome da igreja (EN)', max_length=200, blank=True,
                                      default='Third Baptist Church of Luanda')
    congregacao_pt = models.CharField('Congregação', max_length=200, blank=True)
    congregacao_en = models.CharField('Congregação (EN)', max_length=200, blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)
    site_url = models.URLField('Site', blank=True)
    lideranca_pastoral = models.TextField('Liderança pastoral', blank=True,
                                          help_text='Texto livre, uma linha por pessoa.')

    class Meta:
        verbose_name = 'Configuração do boletim'
        verbose_name_plural = 'Configuração do boletim'

    def __str__(self):
        return 'Configuração do boletim'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Registo único: não se elimina.
        return (0, {})

    @classmethod
    def obter(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PedidoOracao(models.Model):
    ESTADO_CHOICES = (
        ('novo', 'Novo'),
        ('lido', 'Lido'),
        ('convertido', 'Convertido em caso pastoral'),
        ('arquivado', 'Arquivado'),
    )

    nome = models.CharField('Nome', max_length=100, blank=True)
    contacto = models.CharField('Contacto', max_length=100, blank=True)
    pedido = models.TextField('Pedido')
    confidencial = models.BooleanField('Confidencial', default=True)
    estado = models.CharField('Estado', max_length=12, choices=ESTADO_CHOICES, default='novo')
    caso_pastoral = models.ForeignKey(
        CasoPastoral, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='pedidos_oracao', verbose_name='Caso pastoral',
    )
    criado_em = models.DateTimeField('Recebido em', auto_now_add=True)
    ip_hash = models.CharField('IP (hash)', max_length=64, blank=True, editable=False)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pedido de oração'
        verbose_name_plural = 'Pedidos de oração'

    def __str__(self):
        quem = self.nome or 'Anónimo'
        return f'{quem} — {self.criado_em:%d/%m/%Y %H:%M}'
