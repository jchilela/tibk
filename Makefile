# =============================================================================
#  Makefile — atalhos para a documentação ProperDocs
# =============================================================================

.PHONY: docs docs-serve docs-clean

## Constrói o site estático em docs/site/
docs:
	properdocs build --config-file properdocs.yml

## Servidor de desenvolvimento com auto-reload (http://localhost:8001)
docs-serve:
	properdocs serve --config-file properdocs.yml --dev-addr 127.0.0.1:8001

## Remove o site gerado
docs-clean:
	properdocs build --config-file properdocs.yml --clean
