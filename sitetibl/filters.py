import django_filters
from .models import Contabancaria

class ContabancariaFilter(django_filters.FilterSet): # 'icontains' permite buscar partes do nome do banco(ex: "Sol" acha "Banco Sol")
    banco = django_filters.CharFilter(field_name='banco__designacao', lookup_expr='icontains',label='Banco') #'exact' para moeda, já que normalmente é uma escolha fixa
    moeda = django_filters.ChoiceFilter(choices=[('AKZ', 'Kwanza'),('USD','Dólar'),('EUR','Euro')], label='Moeda')

    class Meta:
        model = Contabancaria
        fields = ['banco','moeda']