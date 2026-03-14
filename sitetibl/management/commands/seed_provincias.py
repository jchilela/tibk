"""
Seeder idempotente para Províncias e Municípios de Angola.
Uso: python manage.py seed_provincias
"""
from django.core.management.base import BaseCommand
from sitetibl.models import Provincia, Municipio


# Dados oficiais: 18 províncias, 164 municípios
DADOS_ANGOLA = {
    'BNG': {
        'nome': 'Bengo',
        'municipios': [
            'Ambriz', 'Bula Atumba', 'Dande', 'Dembos',
            'Nambuangongo', 'Pango Aluquém',
        ],
    },
    'BGL': {
        'nome': 'Benguela',
        'municipios': [
            'Baía Farta', 'Balombo', 'Benguela', 'Bocoio',
            'Caimbambo', 'Catumbela', 'Chongoroi', 'Cubal',
            'Ganda', 'Lobito',
        ],
    },
    'BIE': {
        'nome': 'Bié',
        'municipios': [
            'Andulo', 'Camacupa', 'Catabola', 'Chinguar',
            'Chitembo', 'Cuemba', 'Cunhinga', 'Cuíto',
            'Nharea',
        ],
    },
    'CAB': {
        'nome': 'Cabinda',
        'municipios': [
            'Belize', 'Buco-Zau', 'Cabinda', 'Cacongo',
        ],
    },
    'CNE': {
        'nome': 'Cunene',
        'municipios': [
            'Cahama', 'Cuanhama', 'Curoca', 'Cuvelai',
            'Namacunde', 'Ombadja',
        ],
    },
    'HMB': {
        'nome': 'Huambo',
        'municipios': [
            'Bailundo', 'Cachiungo', 'Caála', 'Ecunha',
            'Huambo', 'Londuimbali', 'Longonjo', 'Mungo',
            'Tchicala-Tcholoanga', 'Tchindjenje', 'Ucuma',
        ],
    },
    'HLA': {
        'nome': 'Huíla',
        'municipios': [
            'Caconda', 'Cacula', 'Caluquembe', 'Chiange',
            'Chibia', 'Chicomba', 'Chipindo', 'Cuvango',
            'Gambos', 'Humpata', 'Jamba', 'Lubango',
            'Matala', 'Quilengues',
        ],
    },
    'KKG': {
        'nome': 'Kuando Kubango',
        'municipios': [
            'Calai', 'Cuangar', 'Cuchi', 'Cuito Cuanavale',
            'Dirico', 'Mavinga', 'Menongue', 'Nancova',
            'Rivungo',
        ],
    },
    'KZN': {
        'nome': 'Cuanza Norte',
        'municipios': [
            'Ambaca', 'Banga', 'Bolongongo', 'Cambambe',
            'Cazengo', 'Golungo Alto', 'Gonguembo', 'Lucala',
            'Quiculungo', 'Samba Cajú',
        ],
    },
    'KZS': {
        'nome': 'Cuanza Sul',
        'municipios': [
            'Amboim', 'Cassongue', 'Cela', 'Conda',
            'Ebo', 'Libolo', 'Mussende', 'Porto Amboim',
            'Quibala', 'Quilenda', 'Seles', 'Sumbe',
        ],
    },
    'LDA': {
        'nome': 'Luanda',
        'municipios': [
            'Belas', 'Cacuaco', 'Cazenga', 'Ícolo e Bengo',
            'Kilamba Kiaxi', 'Luanda', 'Quissama',
            'Talatona', 'Viana',
        ],
    },
    'LDN': {
        'nome': 'Lunda Norte',
        'municipios': [
            'Cambulo', 'Capenda-Camulemba', 'Caungula',
            'Chitato', 'Cuango', 'Cuílo', 'Lubalo',
            'Lucapa', 'Xá-Muteba',
        ],
    },
    'LDS': {
        'nome': 'Lunda Sul',
        'municipios': [
            'Cacolo', 'Dala', 'Muconda', 'Saurimo',
        ],
    },
    'MLG': {
        'nome': 'Malange',
        'municipios': [
            'Cacuso', 'Calandula', 'Cambundi-Catembo',
            'Cangandala', 'Caombo', 'Cuaba Nzoji',
            'Cunda-dia-Baze', 'Luquembo', 'Malange',
            'Marimba', 'Massango', 'Mucari',
            'Quela', 'Quirima',
        ],
    },
    'MXC': {
        'nome': 'Moxico',
        'municipios': [
            'Alto Zambeze', 'Bundas', 'Camanongue',
            'Cameia', 'Leua', 'Luau', 'Luacano',
            'Luchazes', 'Moxico',
        ],
    },
    'NMB': {
        'nome': 'Namibe',
        'municipios': [
            'Bibala', 'Camucuio', 'Moçâmedes', 'Tômbwa',
            'Virei',
        ],
    },
    'UGE': {
        'nome': 'Uíge',
        'municipios': [
            'Alto Cauale', 'Ambuíla', 'Bembe', 'Buengas',
            'Bungo', 'Damba', 'Maquela do Zombo', 'Mucaba',
            'Negage', 'Puri', 'Quimbele', 'Quitexe',
            'Sanza Pombo', 'Songo', 'Uíge', 'Zombo',
        ],
    },
    'ZAR': {
        'nome': 'Zaire',
        'municipios': [
            'Cuimba', 'Mbanza Congo', 'Nóqui', 'Nzeto',
            'Soyo', 'Tomboco',
        ],
    },
}


class Command(BaseCommand):
    help = 'Popula províncias e municípios de Angola (idempotente)'

    def handle(self, *args, **options):
        prov_criadas = 0
        mun_criados = 0

        for codigo, dados in DADOS_ANGOLA.items():
            provincia, created = Provincia.objects.get_or_create(
                codigo=codigo,
                defaults={'nome': dados['nome']},
            )
            if created:
                prov_criadas += 1

            for nome_mun in dados['municipios']:
                _, m_created = Municipio.objects.get_or_create(
                    nome=nome_mun,
                    provincia=provincia,
                )
                if m_created:
                    mun_criados += 1

        total_prov = Provincia.objects.count()
        total_mun = Municipio.objects.count()

        self.stdout.write(
            f'Províncias: criadas {prov_criadas} | totais {total_prov}'
        )
        self.stdout.write(
            f'Municípios: criados {mun_criados} | totais {total_mun}'
        )
        self.stdout.write(self.style.SUCCESS('Seed concluído com sucesso.'))
