"""Textos fixos das páginas públicas (PT/EN) e escolha de língua.

Solução deliberadamente simples: sem gettext nem prefixos de língua nas
rotas. A língua vem de ``?lang=`` (e fica num cookie) ou do cookie.
"""

LINGUAS = ('pt', 'en')
LINGUA_OMISSAO = 'pt'
COOKIE_LINGUA = 'boletim_lang'
COOKIE_IDADE = 60 * 60 * 24 * 365

TEXTOS = {
    'pt': {
        'html_lang': 'pt',
        'og_locale': 'pt_PT',
        'boletim': 'Boletim',
        'ordem_culto': 'Ordem do culto',
        'leitura': 'Leitura bíblica',
        'hino': 'Hino',
        'escalas': 'Ao serviço neste culto',
        'anuncios': 'Anúncios',
        'adicionar_calendario': 'Adicionar ao calendário',
        'programas': 'Programas semanais',
        'sou_visitante': 'Sou visitante',
        'pedido_oracao': 'Pedido de oração',
        'redes': 'Acompanhe-nos',
        'site': 'Site',
        'transmissao': 'Ver em directo',
        'depois_culto': 'Depois do culto',
        'gravacao': 'Ver a gravação',
        'notas_sermao': 'Notas do sermão',
        'tema': 'Tema',
        'pdf': 'Versão para imprimir (PDF)',
        'pdf_btn': 'Descarregar PDF',
        'partilhar': 'Compartilhar',
        'partilhar_longo': 'Compartilhar este boletim',
        'copiado': 'Link copiado',
        'arquivo': 'Boletins anteriores',
        'outros_cultos': 'Outros cultos neste dia',
        'lideranca': 'Liderança pastoral',
        'sem_boletim': 'Ainda não há nenhum boletim publicado.',
        'arquivo_titulo': 'Arquivo de boletins',
        'anterior': 'Anterior',
        'seguinte': 'Seguinte',
        'pagina': 'Página',
        'de': 'de',
        'voltar': 'Voltar ao boletim',
        'enviar': 'Enviar',
        'obrigatorio': 'obrigatório',
        'pre_visualizacao': 'Pré-visualização — este boletim ainda não está publicado.',
        'visitante_titulo': 'Bem-vindo à nossa igreja!',
        'visitante_intro': 'Gostaríamos de o conhecer. Deixe-nos o seu contacto e alguém da igreja falará consigo.',
        'oracao_titulo': 'Pedido de oração',
        'oracao_intro': 'Partilhe connosco o seu pedido. A equipa pastoral vai orar por si.',
        'obrigado_visitante': 'Obrigado pela sua visita! Foi uma alegria tê-lo connosco. Em breve entraremos em contacto.',
        'obrigado_oracao': 'Recebemos o seu pedido. Estamos a orar por si.',
        'erro_neutro': 'Não foi possível processar o seu pedido neste momento. Por favor, tente mais tarde.',
        'campo_nome': 'Nome',
        'campo_telefone': 'Telefone',
        'campo_email': 'Email (opcional)',
        'campo_primeira_vez': 'É a primeira vez que nos visita?',
        'sim': 'Sim',
        'nao': 'Não',
        'campo_como_soube': 'Como soube da nossa igreja? (opcional)',
        'campo_consentimento': 'Aceito ser contactado pela igreja através dos dados que indiquei.',
        'campo_nome_opcional': 'Nome (opcional)',
        'campo_contacto_opcional': 'Contacto (opcional)',
        'campo_pedido': 'O seu pedido',
        'campo_confidencial': 'Confidencial (só a equipa pastoral o lê)',
        'erro_telefone': 'Indique um número de telefone válido.',
        'erro_consentimento': 'Precisamos do seu consentimento para o contactar.',
        'dias': ('Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira',
                 'Sexta-feira', 'Sábado', 'Domingo'),
        'meses': ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
                  'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'),
        'outra_lingua': 'en',
        'outra_lingua_nome': 'English',
    },
    'en': {
        'html_lang': 'en',
        'og_locale': 'en_GB',
        'boletim': 'Bulletin',
        'ordem_culto': 'Order of service',
        'leitura': 'Scripture reading',
        'hino': 'Hymn',
        'escalas': 'Serving today',
        'anuncios': 'Announcements',
        'adicionar_calendario': 'Add to calendar',
        'programas': 'Weekly programme',
        'sou_visitante': "I'm a visitor",
        'pedido_oracao': 'Prayer request',
        'redes': 'Follow us',
        'site': 'Website',
        'transmissao': 'Watch live',
        'depois_culto': 'After the service',
        'gravacao': 'Watch the recording',
        'notas_sermao': 'Sermon notes',
        'tema': 'Theme',
        'pdf': 'Printable version (PDF)',
        'pdf_btn': 'Download PDF',
        'partilhar': 'Share',
        'partilhar_longo': 'Share this bulletin',
        'copiado': 'Link copied',
        'arquivo': 'Past bulletins',
        'outros_cultos': 'Other services on this day',
        'lideranca': 'Pastoral leadership',
        'sem_boletim': 'No bulletin has been published yet.',
        'arquivo_titulo': 'Bulletin archive',
        'anterior': 'Previous',
        'seguinte': 'Next',
        'pagina': 'Page',
        'de': 'of',
        'voltar': 'Back to the bulletin',
        'enviar': 'Send',
        'obrigatorio': 'required',
        'pre_visualizacao': 'Preview — this bulletin has not been published yet.',
        'visitante_titulo': 'Welcome to our church!',
        'visitante_intro': "We'd love to get to know you. Leave us your contact details and someone from the church will be in touch.",
        'oracao_titulo': 'Prayer request',
        'oracao_intro': 'Share your request with us. The pastoral team will pray for you.',
        'obrigado_visitante': "Thank you for visiting! It was a joy to have you with us. We'll be in touch soon.",
        'obrigado_oracao': 'We have received your request. We are praying for you.',
        'erro_neutro': 'We could not process your request right now. Please try again later.',
        'campo_nome': 'Name',
        'campo_telefone': 'Phone',
        'campo_email': 'Email (optional)',
        'campo_primeira_vez': 'Is this your first visit?',
        'sim': 'Yes',
        'nao': 'No',
        'campo_como_soube': 'How did you hear about us? (optional)',
        'campo_consentimento': 'I agree to be contacted by the church using the details I have given.',
        'campo_nome_opcional': 'Name (optional)',
        'campo_contacto_opcional': 'Contact (optional)',
        'campo_pedido': 'Your request',
        'campo_confidencial': 'Confidential (only the pastoral team will read it)',
        'erro_telefone': 'Please enter a valid phone number.',
        'erro_consentimento': 'We need your consent to contact you.',
        'dias': ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
        'meses': ('January', 'February', 'March', 'April', 'May', 'June', 'July',
                  'August', 'September', 'October', 'November', 'December'),
        'outra_lingua': 'pt',
        'outra_lingua_nome': 'Português',
    },
}


def lingua_do_pedido(request):
    """Devolve (lingua, mudou) — ``mudou`` indica que é preciso gravar o cookie."""
    pedida = (request.GET.get('lang') or '').lower()
    if pedida in LINGUAS:
        return pedida, pedida != request.COOKIES.get(COOKIE_LINGUA)
    cookie = (request.COOKIES.get(COOKIE_LINGUA) or '').lower()
    if cookie in LINGUAS:
        return cookie, False
    return LINGUA_OMISSAO, False


def gravar_cookie_lingua(response, lingua):
    response.set_cookie(COOKIE_LINGUA, lingua, max_age=COOKIE_IDADE, samesite='Lax')
    return response


def tr(lingua, pt, en):
    """Texto na língua pedida; cai para PT quando o campo EN está vazio."""
    if lingua == 'en' and en and str(en).strip():
        return en
    return pt or ''


def data_extenso(d, lingua):
    t = TEXTOS[lingua]
    dia = t['dias'][d.weekday()]
    mes = t['meses'][d.month - 1]
    if lingua == 'en':
        return f'{dia}, {d.day} {mes} {d.year}'
    return f'{dia}, {d.day} de {mes} de {d.year}'


def hora(h):
    if not h:
        return ''
    return f'{h.hour:02d}h{h.minute:02d}'
