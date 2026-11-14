"""Invalidação da cache pública quando muda algo que aparece no boletim."""
from django.db.models.signals import post_delete, post_save

from boletim import cache as boletim_cache
from boletim.models import (
    Boletim, ConfiguracaoBoletim, FuncaoBoletim, ItemOrdemCulto, ProgramaSemanal,
)
from sitetibl.models import Actividade, Anuncio, Escala

MODELOS_OBSERVADOS = (
    Boletim, ItemOrdemCulto, ConfiguracaoBoletim, FuncaoBoletim, ProgramaSemanal,
    Anuncio, Escala, Actividade,
)


def _invalidar(sender, **kwargs):
    boletim_cache.invalidar()


for _modelo in MODELOS_OBSERVADOS:
    post_save.connect(_invalidar, sender=_modelo, dispatch_uid=f'boletim_inv_save_{_modelo.__name__}')
    post_delete.connect(_invalidar, sender=_modelo, dispatch_uid=f'boletim_inv_del_{_modelo.__name__}')
