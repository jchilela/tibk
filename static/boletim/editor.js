/* Editor de formatação dos textos do boletim (Quill). Se o Quill não carregar, a caixa de texto normal continua visível. */
(function () {
  if (!window.Quill) { return; }

  function escapar(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function paraHtml(valor) {
    if (!valor) { return ''; }
    if (/<\s*(p|br|strong|b|em|i|u|ul|ol|li|blockquote|h2|h3|a)\b/i.test(valor)) { return valor; }
    return valor.split(/\n{2,}/).map(function (bloco) {
      return '<p>' + escapar(bloco).replace(/\n/g, '<br>') + '</p>';
    }).join('');
  }

  document.querySelectorAll('textarea.bl-richtext').forEach(function (ta) {
    var holder = document.createElement('div');
    holder.className = 'bl-editor';
    ta.parentNode.insertBefore(holder, ta);
    ta.style.display = 'none';
    var editor = new Quill(holder, {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ header: [2, 3, false] }],
          ['bold', 'italic', 'underline'],
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['blockquote', 'link'],
          ['clean']
        ]
      }
    });
    var inicial = paraHtml(ta.value);
    if (inicial) { editor.clipboard.dangerouslyPasteHTML(inicial); }
    var form = ta.closest('form');
    if (!form) { return; }
    form.addEventListener('submit', function () {
      var html = editor.getSemanticHTML ? editor.getSemanticHTML() : editor.root.innerHTML;
      ta.value = editor.getText().trim() ? html : '';
    });
  });
})();
