from datetime import date, timedelta

from django import forms
from django.forms import inlineformset_factory

from boletim.models import Boletim, ItemOrdemCulto, ModeloOrdemCulto
from boletim.services import normalizar_telefone
from boletim.textos import TEXTOS
from sitetibl.models import Actividade, Anuncio, CasoPastoral, Irmao


# ── Formulários públicos ─────────────────────────────────────

class _FormularioPublico(forms.Form):
    # Honeypot: escondido por CSS; pessoas não o preenchem, robots sim.
    website = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'autocomplete': 'off', 'tabindex': '-1'}))

    def __init__(self, *args, lingua='pt', **kwargs):
        super().__init__(*args, **kwargs)
        self.lingua = lingua
        self.t = TEXTOS[lingua]
        self.fields['website'].label = 'Website'

    def is_robot(self):
        return bool((self.data.get('website') or '').strip())


class CartaoVisitanteForm(_FormularioPublico):
    nome = forms.CharField(max_length=100)
    telefone = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'type': 'tel', 'autocomplete': 'tel', 'inputmode': 'tel'}))
    email = forms.EmailField(required=False, max_length=254, widget=forms.EmailInput(
        attrs={'autocomplete': 'email'}))
    primeira_vez = forms.ChoiceField(widget=forms.RadioSelect, initial='sim')
    como_soube = forms.CharField(required=False, max_length=200)
    consentimento = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        t = self.t
        self.fields['nome'].label = t['campo_nome']
        self.fields['nome'].widget.attrs['autocomplete'] = 'name'
        self.fields['telefone'].label = t['campo_telefone']
        self.fields['email'].label = t['campo_email']
        self.fields['primeira_vez'].label = t['campo_primeira_vez']
        self.fields['primeira_vez'].choices = (('sim', t['sim']), ('nao', t['nao']))
        self.fields['como_soube'].label = t['campo_como_soube']
        self.fields['consentimento'].label = t['campo_consentimento']
        self.fields['consentimento'].error_messages['required'] = t['erro_consentimento']
        # Campos de visitante primeiro, honeypot no fim.
        self.order_fields(['nome', 'telefone', 'email', 'primeira_vez', 'como_soube', 'consentimento', 'website'])

    def clean_telefone(self):
        tel = normalizar_telefone(self.cleaned_data['telefone'])
        if not (9 <= len(tel) <= 15):
            raise forms.ValidationError(self.t['erro_telefone'])
        return tel


class PedidoOracaoForm(_FormularioPublico):
    nome = forms.CharField(required=False, max_length=100)
    contacto = forms.CharField(required=False, max_length=100)
    pedido = forms.CharField(max_length=3000, widget=forms.Textarea(attrs={'rows': 6}))
    confidencial = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        t = self.t
        self.fields['nome'].label = t['campo_nome_opcional']
        self.fields['contacto'].label = t['campo_contacto_opcional']
        self.fields['pedido'].label = t['campo_pedido']
        self.fields['confidencial'].label = t['campo_confidencial']
        self.order_fields(['nome', 'contacto', 'pedido', 'confidencial', 'website'])


# ── Formulários internos (gestão) ────────────────────────────

class _Estilo:
    """Aplica a classe CSS dos formulários internos a todos os campos."""

    def _aplicar_estilo(self):
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            w.attrs['class'] = (w.attrs.get('class', '') + ' bl-input').strip()


def actividades_para_boletim():
    """Actividades sem boletim, de 30 dias atrás em diante (sem séries-pai recorrentes)."""
    return (Actividade.objects
            .filter(data__gte=date.today() - timedelta(days=30), boletim__isnull=True)
            .exclude(is_recorrente=True, parent_event__isnull=True)
            .select_related('designacao')
            .order_by('data', 'inicio'))


class NovoBoletimForm(_Estilo, forms.Form):
    actividade = forms.ModelChoiceField(queryset=Actividade.objects.none(), label='Culto (actividade)')
    modelo = forms.ModelChoiceField(queryset=ModeloOrdemCulto.objects.none(), required=False,
                                    label='Modelo da ordem do culto',
                                    empty_label='— Sem modelo (ordem vazia) —')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['actividade'].queryset = actividades_para_boletim()
        self.fields['actividade'].label_from_instance = (
            lambda a: f'{a.data:%d/%m/%Y} {a.inicio:%H:%M} — {a.designacao}' + (f' ({a.tema})' if a.tema else ''))
        self.fields['modelo'].queryset = ModeloOrdemCulto.objects.filter(activo=True)
        self._aplicar_estilo()


class BoletimForm(_Estilo, forms.ModelForm):
    class Meta:
        model = Boletim
        fields = [
            'titulo_pt', 'titulo_en', 'leitura_referencia', 'leitura_texto_pt', 'leitura_texto_en',
            'hino_referencia', 'hino_letra', 'link_transmissao', 'link_gravacao', 'notas_sermao',
        ]
        widgets = {
            'leitura_texto_pt': forms.Textarea(attrs={'rows': 4}),
            'leitura_texto_en': forms.Textarea(attrs={'rows': 4}),
            'hino_letra': forms.Textarea(attrs={'rows': 6}),
            'notas_sermao': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aplicar_estilo()


class ItemOrdemCultoForm(_Estilo, forms.ModelForm):
    class Meta:
        model = ItemOrdemCulto
        fields = ['ordem', 'titulo_pt', 'titulo_en', 'detalhe']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aplicar_estilo()


ItensFormSet = inlineformset_factory(
    Boletim, ItemOrdemCulto, form=ItemOrdemCultoForm, extra=2, can_delete=True,
)


class AnuncioForm(_Estilo, forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = [
            'titulo', 'texto', 'titulo_en', 'texto_en', 'data_inicio', 'data_fim',
            'publico', 'ordem', 'actividade', 'quemanuncia',
        ]
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4}),
            'texto_en': forms.Textarea(attrs={'rows': 4}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {'quemanuncia': 'Quem anuncia', 'texto': 'Texto'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_inicio'].required = True
        qs_act = Actividade.objects.filter(data__gte=date.today() - timedelta(days=60)).exclude(
            is_recorrente=True, parent_event__isnull=True).select_related('designacao').order_by('data', 'inicio')
        if self.instance.pk and self.instance.actividade_id:
            qs_act = qs_act | Actividade.objects.filter(pk=self.instance.actividade_id)
        self.fields['actividade'].queryset = qs_act.distinct()
        self.fields['actividade'].label_from_instance = lambda a: f'{a.data:%d/%m/%Y} {a.inicio:%H:%M} — {a.designacao}'
        self.fields['quemanuncia'].queryset = Irmao.objects.order_by('nome', 'apelido')
        self._aplicar_estilo()

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and fim < inicio:
            self.add_error('data_fim', 'A data de fim não pode ser anterior à data de início.')
        return dados

    def save(self, commit=True):
        anuncio = super().save(commit=False)
        # Campo antigo, obrigatório: acompanha a data de início.
        anuncio.data = anuncio.data_inicio
        if commit:
            anuncio.save()
        return anuncio


class ConverterPedidoForm(_Estilo, forms.Form):
    membro = forms.ModelChoiceField(queryset=Irmao.objects.none(), label='Membro (Irmão)')
    tipo = forms.ChoiceField(choices=CasoPastoral.TIPO_CHOICES, initial='aconselhamento', label='Tipo de caso')
    prioridade = forms.ChoiceField(choices=CasoPastoral.PRIORIDADE_CHOICES, initial='normal', label='Prioridade')
    titulo = forms.CharField(max_length=200, initial='Pedido de oração', label='Título')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['membro'].queryset = Irmao.objects.order_by('nome', 'apelido')
        self._aplicar_estilo()
