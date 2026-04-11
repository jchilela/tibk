document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.lang = 'pt';

    document.querySelectorAll('a[data-bs-target="#mkdocs_search_modal"]').forEach(function (element) {
        element.innerHTML = '<i class="fa fa-search"></i> Pesquisar';
    });

    document.querySelectorAll('a[rel="prev"]').forEach(function (element) {
        element.innerHTML = '<i class="fa fa-arrow-left"></i> Anterior';
    });

    document.querySelectorAll('a[rel="next"]').forEach(function (element) {
        element.innerHTML = 'Seguinte <i class="fa fa-arrow-right"></i>';
    });
});