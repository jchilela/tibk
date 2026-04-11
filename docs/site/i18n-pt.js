document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.lang = 'pt';

    var textMap = {
        'Search': 'Pesquisar',
        'Previous': 'Anterior',
        'Next': 'Seguinte',
        'Keyboard Shortcuts': 'Atalhos do teclado',
        'Keys': 'Teclas',
        'Action': 'Acao',
        'Open this help': 'Abrir esta ajuda',
        'Next page': 'Pagina seguinte',
        'Previous page': 'Pagina anterior'
    };

    var selectorMap = [
        ['#searchModalLabel', 'Pesquisar'],
        ['#keyboardModalLabel', 'Atalhos do teclado']
    ];

    selectorMap.forEach(function (entry) {
        document.querySelectorAll(entry[0]).forEach(function (element) {
            element.textContent = entry[1];
        });
    });

    document.querySelectorAll('a, button, th, td, p').forEach(function (element) {
        var text = element.textContent.trim();
        if (textMap[text]) {
            element.textContent = textMap[text];
        }
    });

    document.querySelectorAll('[aria-label="Toggle navigation"]').forEach(function (element) {
        element.setAttribute('aria-label', 'Alternar navegacao');
    });

    document.querySelectorAll('[title="Table of Contents"]').forEach(function (element) {
        element.setAttribute('title', 'Indice da pagina');
    });

    document.querySelectorAll('.btn-close[aria-label="Close"]').forEach(function (element) {
        element.setAttribute('aria-label', 'Fechar');
    });

    document.querySelectorAll('.headerlink[title="Permanent link"]').forEach(function (element) {
        element.setAttribute('title', 'Ligacao permanente');
    });

    document.querySelectorAll('#mkdocs_search_modal p').forEach(function (element) {
        if (element.textContent.indexOf('From here you can search these documents.') !== -1) {
            element.textContent = 'A partir daqui pode pesquisar nesta documentacao. Introduza os termos de pesquisa abaixo.';
        }
    });

    document.querySelectorAll('#mkdocs-search-query').forEach(function (element) {
        element.setAttribute('placeholder', 'Pesquisar...');
        element.setAttribute('title', 'Digite o termo a pesquisar');
    });

    document.querySelectorAll('#mkdocs-search-results').forEach(function (element) {
        element.setAttribute('data-no-results-text', 'Nenhum resultado encontrado');
    });
});