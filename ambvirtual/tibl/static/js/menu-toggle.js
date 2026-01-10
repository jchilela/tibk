document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.menu-toggle').forEach(function(btn){
    btn.addEventListener('click', function(){
      var targetId = btn.getAttribute('aria-controls');
      var target = document.getElementById(targetId);
      if (!target) return;
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', (!expanded).toString());
      target.classList.toggle('open');

      // Force inline display to avoid CSS cascade issues on some setups
      var isOpen = target.classList.contains('open');
      if (isOpen) {
        // prefer flex for menus; fall back to block if flex not supported
        try { target.style.display = 'flex'; } catch(e) { target.style.display = 'block'; }
      } else {
        // explicitly hide on close to avoid cascade issues
        target.style.display = 'none';
      }
    });
  });

  // Close open menus with Escape
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') {
      document.querySelectorAll('.menu-toggle[aria-expanded="true"]').forEach(function(btn){
        var targetId = btn.getAttribute('aria-controls');
        var target = document.getElementById(targetId);
        btn.setAttribute('aria-expanded','false');
        if (target) {
          target.classList.remove('open');
          target.style.display = 'none';
        }
      });
    }
  });

  // Optional: close when clicking outside an open menu
  document.addEventListener('click', function(e){
    var clickedToggle = e.target.closest('.menu-toggle');
    if (clickedToggle) return; // clicked a toggle button

    document.querySelectorAll('.menu-toggle[aria-expanded="true"]').forEach(function(btn){
      var targetId = btn.getAttribute('aria-controls');
      var target = document.getElementById(targetId);
      if (!target) return;
      if (!target.contains(e.target)) {
        btn.setAttribute('aria-expanded','false');
        target.classList.remove('open');
        target.style.display = 'none';
      }
    });
  });

  // Initialize mobile menus: ensure they're hidden via inline styles on small screens
  if (window.matchMedia && window.matchMedia('(max-width: 900px)').matches) {
    ['menu-bar','header-nav'].forEach(function(id){
      var el = document.getElementById(id);
      if (!el) return;
      if (!el.classList.contains('open')) el.style.display = 'none';
    });
  }

  // Reset inline styles when resizing so the CSS rules take effect correctly
  window.addEventListener('resize', function(){
    var small = window.matchMedia && window.matchMedia('(max-width: 900px)').matches;
    ['menu-bar','header-nav'].forEach(function(id){
      var el = document.getElementById(id);
      if (!el) return;
      if (small) {
        if (!el.classList.contains('open')) el.style.display = 'none';
      } else {
        // remove inline styles on larger screens so desktop layout is controlled by CSS
        el.style.display = '';
      }
    });
  });
});