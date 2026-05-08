from sitetibl.models import Irmao
from sitetibl.models import Ajuda
from sitetibl.models import Cestabasica
from sitetibl.models import Banco
from sitetibl.models import Contabancaria
from sitetibl.models import SolicitacaoInterdepartamental
from sitetibl.models import CasoPastoral
from sitetibl.models import RegistoAcompanhamento
from sitetibl.models import VisitanteRecorrente
from sitetibl.models import AlertaPastoral
from sitetibl.models import Actividade
from sitetibl.models import Departamento
from sitetibl.models import Mandato
from sitetibl.models import Cargo
from sitetibl.models import Escala
from sitetibl.models import Funcao
from sitetibl.models import Saidacaixa
from sitetibl.models import Saidabanco
from sitetibl.models import Entradacaixa
from sitetibl.models import Entradabanco
from sitetibl.models import Dizimooferta
from sitetibl.models import Pagamentoservico
from sitetibl.models import Gruporubrica
from sitetibl.models import Servico
from sitetibl.models import Sitio
from sitetibl.models import Municipio
from sitetibl.models import RelatorioSemanalCelula
from sitetibl.models import PedidoSaida
from sitetibl.models import OrcamentoDepartamento
from sitetibl.models import InventarioPatrimonio
from sitetibl.models import ConteudoEnsino
from sitetibl.models import EnvioMensagem
from sitetibl.models import TipoOferta
from sitetibl.models import Listaactividades
from sitetibl.models import Celula

from django.forms import ModelForm , CheckboxSelectMultiple
from django.utils import timezone as tz
from schedule.models import Calendar, Rule, Event as ScheduleEvent
from django import forms
from datetime import date, datetime, timedelta
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm


class MeuPerfilForm(ModelForm):
    """Campos que o próprio utilizador pode alterar no seu perfil."""
    class Meta:
        model = Irmao
        fields = ['foto', 'telefone', 'telefonewhatsapp', 'email']
        widgets = {
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 923000000'}),
            'telefonewhatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 923000000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class MeuPerfilPasswordForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['old_password'].label = 'Senha actual'
        self.fields['old_password'].help_text = ''
        self.fields['new_password1'].label = 'Nova senha'
        self.fields['new_password1'].help_text = (
            'A senha deve ter pelo menos 8 caracteres. '
            'Não pode ser apenas números nem semelhante ao nome de utilizador.'
        )
        self.fields['new_password2'].label = 'Confirmar nova senha'
        self.fields['new_password2'].help_text = 'Repita a nova senha para confirmar.'


class TiblPasswordResetForm(DjangoPasswordResetForm):
    def save(self, *args, **kwargs):
        if not kwargs.get('domain_override'):
            domain_override = getattr(settings, 'PASSWORD_RESET_DOMAIN', '').strip()
            if not domain_override:
                trusted_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
                if trusted_origins:
                    domain_override = urlparse(trusted_origins[0]).netloc
            if domain_override:
                kwargs['domain_override'] = domain_override

        protocol_override = getattr(settings, 'PASSWORD_RESET_PROTOCOL', '').strip().lower()
        if protocol_override in {'http', 'https'}:
            kwargs['use_https'] = protocol_override == 'https'

        return super().save(*args, **kwargs)


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

    departamentos = forms.ModelMultipleChoiceField(
        queryset=Departamento.objects.order_by('designacao'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Departamentos',
        help_text='Seleccione um ou mais departamentos (opcional).',
    )

    class Meta:
        model = Irmao
        fields = [
            # --- Identificação pessoal ---
            'nome', 'apelido', 'outrosnomes', 'sexo', 'foto',
            'datanascimento', 'estadocivil',
            # --- Contactos ---
            'telefone', 'telefonewhatsapp', 'email',
            # --- Localização ---
            'ruaenumero', 'bairro', 'provincia', 'municipio',
            # --- Vida eclesiástica ---
            'localcongregacao', 'celula', 'culto', 'batizado', 'dizimista',
            # --- Profissão e trabalho ---
            'profissao', 'especialidade', 'grauescolaridade', 'localdetrabalho',
            # --- Outros ---
            'observacao',
        ]
        widgets = {
            'datanascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar dropdowns: só células ou só igrejas
        self.fields['celula'].queryset = Sitio.objects.filter(tipo='2')
        self.fields['localcongregacao'].queryset = Sitio.objects.filter(tipo='1')

        # Cascading: município depende da província seleccionada
        if self.instance and self.instance.pk and self.instance.provincia_id:
            # Edição: mostrar municípios da província do registo
            self.fields['municipio'].queryset = Municipio.objects.filter(
                provincia_id=self.instance.provincia_id
            )
        elif 'provincia' in self.data:
            # POST: filtrar pela província enviada
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['municipio'].queryset = Municipio.objects.filter(
                    provincia_id=provincia_id
                )
            except (ValueError, TypeError):
                self.fields['municipio'].queryset = Municipio.objects.none()
        else:
            # Criação: município vazio até escolher província
            self.fields['municipio'].queryset = Municipio.objects.none()

class AjudaForm(ModelForm):
    class Meta:
        model = Ajuda
        fields = '__all__'
        widgets = {
            'ajuda': forms.TextInput(attrs={'placeholder': 'Descreva o tipo de ajuda'}),
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

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
        labels = {
            'is_active': 'Está activo',
        }
        widgets = {
            'numeroconta': forms.TextInput(attrs={
                'placeholder': '1XXXXXXXX'
            }),
            'iban': forms.TextInput(attrs={
                'placeholder': 'AO06 XXXX XXXX XXXX XXXX XXXX X'
            }),
            'saldo': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
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
    designacao = forms.CharField(
        label='Designação',
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Nome da actividade...'}),
    )
    dias_semana = forms.MultipleChoiceField(
        choices=[
            ('6', 'Domingo'),
            ('0', 'Segunda-feira'),
            ('1', 'Terça-feira'),
            ('2', 'Quarta-feira'),
            ('3', 'Quinta-feira'),
            ('4', 'Sexta-feira'),
            ('5', 'Sábado'),
        ],
        label='Dias da Semana',
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    frequencia = forms.ChoiceField(
        choices=[
            ('WEEKLY', 'Semanal'),
            ('DAILY', 'Diária'),
            ('MONTHLY', 'Mensal'),
        ],
        label='Frequência',
        required=False,
        initial='WEEKLY',
    )

    class Meta:
        model = Actividade
        exclude = ('participantes', 'criado_por', 'event', 'parent_event')
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'inicio': forms.DateInput(attrs={'type': 'time'}),
            'fim': forms.DateInput(attrs={'type': 'time'}),
            'recorrencia_fim': forms.DateInput(attrs={'type': 'date'}),
            'is_recorrente': forms.CheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-preencher com o valor actual ao editar
        if self.instance and self.instance.pk and self.instance.designacao_id:
            self.initial['designacao'] = self.instance.designacao.designacao
        # Pré-preencher os dias ao editar
        if self.instance and self.instance.pk and self.instance.dias_semana:
            self.initial['dias_semana'] = self.instance.dias_semana.split(',')
        # Pré-preencher frequência pelo evento existente
        if self.instance and self.instance.pk and self.instance.event_id:
            self.initial['frequencia'] = self.instance.event.rule.frequency if self.instance.event.rule else 'WEEKLY'

        # Labels legíveis
        self.fields['inicio'].label = 'Hora de Início'
        self.fields['fim'].label = 'Hora de Fim'
        self.fields['data'].label = 'Data'
        self.fields['tema'].label = 'Tema'
        self.fields['localactividade'].label = 'Local'
        self.fields['versosbiblicos'].label = 'Versos Bíblicos'
        self.fields['hinos'].label = 'Hinos'
        self.fields['totalpresentes'].label = 'Total de Presentes'
        self.fields['departamento'].label = 'Departamento'
        self.fields['is_recorrente'].label = 'É Recorrente?'
        self.fields['recorrencia_fim'].label = 'Recorrência até'
        self.fields['frequencia'].label = 'Frequência'

        # Campos opcionais
        self.fields['totalpresentes'].required = False
        self.fields['totalpresentes'].initial = 0
        self.fields['tema'].required = False
        self.fields['versosbiblicos'].required = False
        self.fields['hinos'].required = False
        self.fields['localactividade'].required = False
        self.fields['departamento'].required = False
        self.fields['is_recorrente'].required = False
        self.fields['recorrencia_fim'].required = False

    def clean_designacao(self):
        """Converte a string para instância Listaactividades durante a validação,
        antes de _post_clean() tentar atribuí-la ao campo FK do modelo."""
        nome = self.cleaned_data.get('designacao', '').strip()
        if not nome:
            raise forms.ValidationError('Este campo é obrigatório.')
        lista_obj, _ = Listaactividades.objects.get_or_create(designacao=nome)
        return lista_obj

    def clean(self):
        import datetime
        cleaned = super().clean()
        data = cleaned.get('data')
        recorrencia_fim = cleaned.get('recorrencia_fim')
        is_recorrente = cleaned.get('is_recorrente')
        if data and data < datetime.date.today():
            self.add_error('data', 'Não é possível criar actividades com data no passado.')
        if is_recorrente and recorrencia_fim:
            if data and recorrencia_fim <= data:
                self.add_error('recorrencia_fim', 'A data de fim da recorrência deve ser posterior à data da actividade.')
        return cleaned

    def save(self, commit=True):
        import datetime
        # clean_designacao() já devolveu um Listaactividades, super().save() atribui-o correctamente
        instance = super().save(commit=False)
        if instance.totalpresentes is None:
            instance.totalpresentes = 0
        # Guardar dias da semana como string separada por vírgula
        dias = self.cleaned_data.get('dias_semana') or []
        instance.dias_semana = ','.join(sorted(dias))

        # Criar / actualizar evento no django-scheduler se recorrente
        if instance.is_recorrente:
            nome = instance.designacao.designacao
            frequencia = self.cleaned_data.get('frequencia') or 'WEEKLY'
            # Params: byweekday apenas faz sentido para WEEKLY com dias seleccionados
            rule_params = ''
            if frequencia == 'WEEKLY' and dias:
                rule_params = 'byweekday:' + ','.join(sorted(dias))
            rule_name = f'{nome} ({frequencia})'
            # Reutilizar ou criar Rule
            if instance.event and instance.event.rule:
                rule = instance.event.rule
                rule.frequency = frequencia
                rule.params = rule_params
                rule.name = rule_name
                rule.description = rule_name
                rule.save()
            else:
                rule = Rule.objects.create(
                    name=rule_name,
                    description=rule_name,
                    frequency=frequencia,
                    params=rule_params,
                )
            # Combinar data + horas para DateTimeField do django-scheduler
            data_inicio = instance.data
            hora_inicio = instance.inicio or datetime.time(0, 0)
            hora_fim = instance.fim or datetime.time(23, 59)
            start_dt = datetime.datetime.combine(data_inicio, hora_inicio)
            end_dt = datetime.datetime.combine(data_inicio, hora_fim)
            # end_recurring_period: respeitar recorrencia_fim ou usar horizonte de 10 anos
            if instance.recorrencia_fim:
                end_recurring = datetime.datetime.combine(instance.recorrencia_fim, datetime.time(23, 59))
            else:
                end_recurring = datetime.datetime.combine(
                    data_inicio + datetime.timedelta(days=3650), datetime.time(23, 59)
                )
            calendar, _ = Calendar.objects.get_or_create(slug='tibl', defaults={'name': 'TIBL'})
            if instance.event:
                ev = instance.event
                ev.title = instance.designacao.designacao
                ev.start = start_dt
                ev.end = end_dt
                ev.rule = rule
                ev.end_recurring_period = end_recurring
                ev.save()
            else:
                ev = ScheduleEvent.objects.create(
                    title=instance.designacao.designacao,
                    start=start_dt,
                    end=end_dt,
                    rule=rule,
                    end_recurring_period=end_recurring,
                    calendar=calendar,
                )
            instance.event = ev

        if commit:
            instance.save()
            self._save_m2m()
        return instance


DIAS_SEMANA_CHOICES = [
    (6, 'Domingo'),
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
]


class ActividadesRecorrentesForm(forms.Form):
    """Cria múltiplas actividades de uma vez para uma série semanal."""
    nome_actividade = forms.CharField(
        label='Designação da Actividade',
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Ex.: Culto de Oracao, Estudo Bíblico...'}),
    )
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all().order_by('designacao'),
        label='Departamento',
        required=False,
        empty_label='Geral (sem departamento)',
    )
    localactividade = forms.ModelChoiceField(
        queryset=Sitio.objects.all().order_by('designacao'),
        label='Local',
        required=False,
        empty_label='Seleccione...',
    )
    inicio = forms.TimeField(
        label='Hora de Início',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    fim = forms.TimeField(
        label='Hora de Fim',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    data_inicio = forms.DateField(
        label='Data de Início',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    data_fim = forms.DateField(
        label='Data de Fim',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    dias_semana = forms.MultipleChoiceField(
        choices=DIAS_SEMANA_CHOICES,
        label='Dias da Semana',
        widget=forms.CheckboxSelectMultiple,
    )

    def clean(self):
        cleaned = super().clean()
        data_inicio = cleaned.get('data_inicio')
        data_fim = cleaned.get('data_fim')
        inicio = cleaned.get('inicio')
        fim = cleaned.get('fim')
        dias = cleaned.get('dias_semana')

        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data de fim deve ser igual ou posterior à data de início.')
        if inicio and fim and fim <= inicio:
            raise forms.ValidationError('A hora de fim deve ser posterior à hora de início.')
        if not dias:
            raise forms.ValidationError('Seleccione pelo menos um dia da semana.')
        return cleaned


class DepartamentoForm(ModelForm):
    lider_departamento = forms.ModelChoiceField(
        queryset=Irmao.objects.order_by('nome', 'apelido'),
        required=False,
        label='Líder do Departamento',
        widget=forms.Select(attrs={'class': 'tomselect'}),
    )
    vice_lider_departamento = forms.ModelChoiceField(
        queryset=Irmao.objects.order_by('nome', 'apelido'),
        required=False,
        label='Vice-Líder do Departamento',
        widget=forms.Select(attrs={'class': 'tomselect'}),
    )

    class Meta:
        model = Departamento
        exclude = ('integrantes',)

class MandatoForm(ModelForm):
    irmao = forms.ModelChoiceField(
        queryset=Irmao.objects.order_by('nome', 'apelido'),
        label='Irmão',
        widget=forms.Select(attrs={'class': 'tomselect'}),
    )

    class Meta:
        model = Mandato
        fields = ['irmao', 'departamento', 'funcao', 'inicio', 'fim']
        widgets = {
            'inicio': forms.DateInput(attrs={'type': 'date'}),
            'fim': forms.DateInput(attrs={'type': 'date'}),
        }

    def validate_unique(self):
        # Ignorar erro de unique_together — o view trata de actualizar o existente
        pass

class EscalaForm(ModelForm):
    class Meta:
        model = Escala
        fields = ('irmao', 'actividade', 'funcao')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['irmao'].label = 'Irmão'
        self.fields['irmao'].queryset = (
            Irmao.objects.select_related('celula').order_by('nome', 'apelido')
        )
        self.fields['actividade'].label = 'Actividade'
        self.fields['actividade'].queryset = (
            Actividade.objects.select_related('designacao', 'departamento')
            .filter(parent_event__isnull=True)
            .order_by('data', 'designacao__designacao')
        )
        self.fields['funcao'].label = 'Função'
        self.fields['funcao'].required = False
        self.fields['funcao'].queryset = (
            Funcao.objects.select_related('departamento')
            .order_by('departamento__designacao', 'designacao')
        )

class DizimoofertaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Evita N+1 ao montar as opções de actividade (usa Actividade.__str__).
        if 'actividade' in self.fields:
            self.fields['actividade'].queryset = (
                Actividade.objects
                .select_related('designacao')
                .order_by('-data', 'inicio')
            )

        if 'irmao' in self.fields:
            self.fields['irmao'].queryset = Irmao.objects.order_by('nome', 'apelido')

    class Meta:
        model = Dizimooferta
        exclude = ('entradabanco', 'entradacaixa')
        labels = {
            'datacorrespondente': 'Data correspondente',
            'dataregisto': 'Data registo',
        }
        widgets = {
            'dataregisto': forms.DateInput(attrs={'type': 'date'}),
            'datacorrespondente': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }

class DizimoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'actividade' in self.fields:
            self.fields['actividade'].queryset = (
                Actividade.objects
                .select_related('designacao')
                .order_by('-data', 'inicio')
            )

        if 'irmao' in self.fields:
            self.fields['irmao'].queryset = Irmao.objects.order_by('nome', 'apelido')

    class Meta:
        model = Dizimooferta
        exclude = ('entradabanco', 'entradacaixa')
        widgets = {
            'valor': forms.TextInput(attrs={'class': 'form-control money-input', 'placeholder': '0,00'}),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
            'tipooferta': forms.Select(attrs={'class': 'form-control'}),
            'datacorrespondente': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'irmao': forms.Select(attrs={'class': 'form-control'}),
            'actividade': forms.Select(attrs={'class': 'form-control'}),
            'dataregisto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
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
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
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
            'hora': forms.DateInput(attrs={'type': 'time'}),
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
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
            self.fields['contaaacreditar'].label = 'Conta a creditar'
            self.fields['contaaacreditar'].label_from_instance = (
                lambda obj: f"{obj.numeroconta} - Saldo: {obj.saldo_actual():.2f} {obj.moeda}"
            )

    class Meta:
        model = Saidabanco
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.DateInput(attrs={'type': 'time'}),
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }
        


class EntradabancoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show real-time balance in account dropdowns for safer bank operations.
        if 'contaaacreditar' in self.fields:
            self.fields['contaaacreditar'].label = 'Conta a creditar'
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
            'hora': forms.DateInput(attrs={'type': 'time'}),
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }
        



class PagamentoservicoForm(ModelForm):
    class Meta:
        model = Pagamentoservico
        fields = '__all__'
        widgets = {
            'valor': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }

class GruporubricaForm(ModelForm):
    class Meta:
        model = Gruporubrica
        fields = '__all__'
        
class ServicoForm(ModelForm):
    class Meta:
        model = Servico
        fields = '__all__'


class CelulaForm(ModelForm):
    class Meta:
        model = Celula
        fields = '__all__'
        widgets = {
            'hora_reuniao': forms.TimeInput(attrs={'type': 'time'}),
        }

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
        fields = [
            'departamento', 'projecto', 'montante', 'moeda',
            'centro_custo', 'tipificacao_custo', 'iban',
            'justificativa_custo', 'documento_justificativo',
        ]
        widgets = {
            'montante': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }

class PedidoSaidaUpdateForm(ModelForm):
    class Meta:
        model = PedidoSaida
        fields = [
            'departamento', 'projecto', 'montante', 'moeda',
            'centro_custo', 'tipificacao_custo', 'iban',
            'justificativa_custo', 'documento_justificativo',
        ]
        widgets = {
            'montante': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }

class OrcamentoDepartamentoForm(ModelForm):
    class Meta:
        model = OrcamentoDepartamento
        fields = '__all__'
        widgets = {
            'ano': forms.Select(choices=[('', '---------')] + [(y, y) for y in range(datetime.now().year - 2, datetime.now().year + 6)]),
            'orcamento': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }

class InventarioPatrimonioForm(ModelForm):
    class Meta:
        model = InventarioPatrimonio
        fields = '__all__'
        widgets = {
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}),
            'data_ultima_manutencao': forms.DateInput(attrs={'type': 'date'}),
            'data_proxima_manutencao': forms.DateInput(attrs={'type': 'date'}),
            'preco': forms.TextInput(attrs={'class': 'money-input', 'placeholder': '0,00'}),
        }

class ConteudoEnsinoForm(ModelForm):
    class Meta:
        model = ConteudoEnsino
        fields = '__all__'

class EnvioMensagemForm(ModelForm):
    class Meta:
        model = EnvioMensagem
        fields = '__all__'
        labels = {
            'quemenviou': 'Quem enviou',
            'destinatarios': 'Destinatários',
            'mensagem': 'Mensagem',
        }
        widgets = {
            'mensagem': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Escreva a sua mensagem aqui...'}),
            'destinatarios': forms.CheckboxSelectMultiple(),
        }


class SolicitacaoForm(ModelForm):
    class Meta:
        model = SolicitacaoInterdepartamental
        fields = [
            'departamento_solicitante', 'departamento_destinatario', 'assunto', 'categoria',
            'descricao', 'data_necessidade', 'prioridade', 'documento_anexo',
            'montante', 'moeda', 'centro_custo', 'tipificacao_custo', 'iban', 'justificativa_custo',
        ]
        widgets = {
            'departamento_solicitante': forms.Select(attrs={'class': 'form-control'}),
            'departamento_destinatario': forms.Select(attrs={'class': 'form-control'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resumo breve do pedido'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'id': 'id_categoria'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o pedido em detalhe...'}),
            'data_necessidade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'documento_anexo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'montante': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
            'centro_custo': forms.Select(attrs={'class': 'form-control'}),
            'tipificacao_custo': forms.Select(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IBAN para transferência'}),
            'justificativa_custo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Justifique o custo solicitado...'}),
        }


class SolicitacaoUpdateForm(ModelForm):
    class Meta:
        model = SolicitacaoInterdepartamental
        fields = [
            'departamento_destinatario', 'assunto', 'categoria', 'descricao',
            'data_necessidade', 'prioridade', 'documento_anexo',
            'montante', 'moeda', 'centro_custo', 'tipificacao_custo', 'iban', 'justificativa_custo',
        ]
        widgets = {
            'departamento_destinatario': forms.Select(attrs={'class': 'form-control'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'id': 'id_categoria'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'data_necessidade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'documento_anexo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'montante': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
            'centro_custo': forms.Select(attrs={'class': 'form-control'}),
            'tipificacao_custo': forms.Select(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IBAN para transferência'}),
            'justificativa_custo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Justifique o custo solicitado...'}),
        }

class CasoPastoralForm(ModelForm):
    class Meta:
        model = CasoPastoral
        fields = [
            'membro', 'tipo', 'prioridade', 'titulo', 'descricao',
            'confidencial', 'responsavel',
        ]
        widgets = {
            'membro': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'confidencial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'responsavel': forms.Select(attrs={'class': 'form-control'}),
        }


class CasoPastoralUpdateForm(ModelForm):
    class Meta:
        model = CasoPastoral
        fields = [
            'tipo', 'prioridade', 'estado', 'titulo', 'descricao',
            'confidencial', 'responsavel',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'confidencial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'responsavel': forms.Select(attrs={'class': 'form-control'}),
        }


class RegistoAcompanhamentoForm(ModelForm):
    class Meta:
        model = RegistoAcompanhamento
        fields = [
            'tipo_contacto', 'descricao', 'documento_anexo',
            'proximo_passo', 'data_proximo_contacto',
        ]
        widgets = {
            'tipo_contacto': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'documento_anexo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'proximo_passo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'data_proximo_contacto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class VisitanteRecorrenteForm(ModelForm):
    class Meta:
        model = VisitanteRecorrente
        fields = [
            'nome', 'telefone', 'email', 'celula', 'estado',
            'responsavel_integracao', 'numero_visitas',
            'primeira_visita', 'ultima_visita', 'observacao',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'celula': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'responsavel_integracao': forms.Select(attrs={'class': 'form-control'}),
            'numero_visitas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'primeira_visita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ultima_visita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
