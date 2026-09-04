from django.test import TestCase
from django.contrib.auth.models import User
from sitetibl.models import (
    Contribuicao, Irmao, Entrada, Dizimooferta, TipoOferta,
    Rubricaentrada, Gruporubrica, Municipio, Provincia, Sitio,
)
from sitetibl.views import _integrar_contribuicao_financeira, _anular_contribuicao_financeira


class IntegracaoContribuicaoTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_fin', password='Teste@123',
            first_name='Test', last_name='Fin',
        )

        luanda, _ = Provincia.objects.get_or_create(
            nome='Luanda',
            defaults={'codigo': 'LDA'},
        )
        mun, _ = Municipio.objects.get_or_create(
            nome='Luanda',
            defaults={'provincia': luanda},
        )
        sede, _ = Sitio.objects.get_or_create(
            designacao='Sede',
            defaults={'provincia': luanda, 'municipio': mun, 'tipo': '1'},
        )

        self.irmao, _ = Irmao.objects.get_or_create(
            email='testfin@tibl.local',
            defaults={
                'nome': 'Test', 'apelido': 'Fin',
                'sexo': 'M', 'telefone': '900000001',
                'municipio': mun, 'provincia': luanda,
                'localcongregacao': sede,
                'categoria': 'membro_batizado',
                'batizado': True,
                'user': self.user,
            }
        )

    def test_integracao_cria_entrada_e_dizimo(self):
        c = Contribuicao.objects.create(
            irmao=self.irmao,
            tipo='dizimo',
            valor=5000,
            moeda='AKZ',
            estado='confirmada',
        )
        _integrar_contribuicao_financeira(c)
        c.refresh_from_db()

        self.assertIsNotNone(c.entrada_id, 'Entrada nao foi criada')
        self.assertIsNotNone(c.dizimooferta_id, 'Dizimooferta nao foi criado')

        entrada = Entrada.objects.get(id=c.entrada_id)
        self.assertEqual(entrada.valor, 5000)
        self.assertEqual(entrada.moeda, 'AKZ')
        self.assertEqual(entrada.tipo, 'caixa')

        dizimo = Dizimooferta.objects.get(id=c.dizimooferta_id)
        self.assertEqual(dizimo.valor, 5000)
        self.assertEqual(dizimo.irmao, self.irmao)
        self.assertEqual(dizimo.entrada_id, entrada.id)

    def test_anular_remove_entrada_e_dizimo(self):
        c = Contribuicao.objects.create(
            irmao=self.irmao,
            tipo='oferta',
            valor=2000,
            moeda='AKZ',
            estado='confirmada',
        )
        _integrar_contribuicao_financeira(c)
        entrada_id = c.entrada_id
        dizimo_id = c.dizimooferta_id

        _anular_contribuicao_financeira(c)
        c.refresh_from_db()

        self.assertIsNone(c.entrada_id)
        self.assertIsNone(c.dizimooferta_id)
        self.assertFalse(Entrada.objects.filter(id=entrada_id).exists())
        self.assertFalse(Dizimooferta.objects.filter(id=dizimo_id).exists())

    def test_nao_duplica_entrada_ao_confirmar_duas_vezes(self):
        c = Contribuicao.objects.create(
            irmao=self.irmao,
            tipo='dizimo',
            valor=1000,
            moeda='AKZ',
            estado='confirmada',
        )
        _integrar_contribuicao_financeira(c)
        primeira_entrada = c.entrada_id

        # Chamar novamente nao deve criar segunda entrada
        _integrar_contribuicao_financeira(c)
        c.refresh_from_db()
        self.assertEqual(c.entrada_id, primeira_entrada)
