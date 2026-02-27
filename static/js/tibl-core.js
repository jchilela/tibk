/**
 * TIBL Core Frontend System v2.0
 * Senior-level frontend utilities: CSRF, cookies, UX automation, error handling
 * @author Kamukotelo Frontend Modernization
 */

(function () {
    'use strict';

    // =========================================================================
    // 1. CSRF / COOKIE MANAGEMENT
    // =========================================================================

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Auto-inject CSRF token into all AJAX/fetch requests
    const originalFetch = window.fetch;
    window.fetch = function (url, options) {
        options = options || {};
        if (!options.headers) options.headers = {};
        const csrfToken = getCookie('csrftoken');
        if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes((options.method || 'GET').toUpperCase())) {
            options.headers['X-CSRFToken'] = csrfToken;
        }
        return originalFetch.call(this, url, options);
    };

    // SameSite cookie fix: ensure forms always have fresh CSRF tokens
    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('form').forEach(function (form) {
            const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
            const csrfCookie = getCookie('csrftoken');
            if (csrfInput && csrfCookie) {
                csrfInput.value = csrfCookie;
            }
        });
    });

    // =========================================================================
    // 2. TOAST NOTIFICATION SYSTEM
    // =========================================================================

    function createToastContainer() {
        let container = document.getElementById('tibl-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'tibl-toast-container';
            container.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:10000;display:flex;flex-direction:column;gap:0.75rem;max-width:400px;';
            document.body.appendChild(container);
        }
        return container;
    }

    function showToast(message, type) {
        type = type || 'info';
        const container = createToastContainer();
        const toast = document.createElement('div');

        const colors = {
            success: { bg: '#f0fdf4', border: '#10b981', icon: 'fa-check-circle', color: '#065f46' },
            error: { bg: '#fef2f2', border: '#ef4444', icon: 'fa-exclamation-circle', color: '#991b1b' },
            warning: { bg: '#fffbeb', border: '#f59e0b', icon: 'fa-exclamation-triangle', color: '#92400e' },
            info: { bg: '#eff6ff', border: '#3b82f6', icon: 'fa-info-circle', color: '#1e40af' }
        };
        const c = colors[type] || colors.info;

        toast.style.cssText = 'background:' + c.bg + ';border:1px solid ' + c.border + ';border-left:5px solid ' + c.border + ';border-radius:8px;padding:1rem 1.25rem;color:' + c.color + ';font-size:0.9rem;display:flex;align-items:center;gap:0.75rem;box-shadow:0 4px 20px rgba(0,0,0,0.12);animation:tiblSlideIn 0.3s ease;cursor:pointer;';

        const icon = document.createElement('i');
        icon.className = 'fas ' + c.icon;
        toast.appendChild(icon);

        const textSpan = document.createElement('span');
        textSpan.textContent = message;
        toast.appendChild(textSpan);

        toast.addEventListener('click', function () { toast.remove(); });

        container.appendChild(toast);
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(function () { toast.remove(); }, 300);
        }, 5000);
    }

    window.TIBL = window.TIBL || {};
    window.TIBL.toast = showToast;

    // =========================================================================
    // 3. GLOBAL LOADING OVERLAY
    // =========================================================================

    function createLoadingOverlay() {
        let overlay = document.getElementById('tibl-loading');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'tibl-loading';
            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,255,255,0.85);z-index:9999;display:none;justify-content:center;align-items:center;backdrop-filter:blur(4px);';
            overlay.innerHTML = '<div style="text-align:center;"><div class="tibl-spinner" style="width:48px;height:48px;border:4px solid #e2e8f0;border-top-color:#548c2f;border-radius:50%;animation:tiblSpin 0.8s linear infinite;margin:0 auto 1rem;"></div><p style="color:#548c2f;font-weight:600;font-size:0.95rem;">Processando...</p></div>';
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    window.TIBL.showLoading = function () {
        const overlay = createLoadingOverlay();
        overlay.style.display = 'flex';
    };

    window.TIBL.hideLoading = function () {
        const overlay = document.getElementById('tibl-loading');
        if (overlay) overlay.style.display = 'none';
    };

    // =========================================================================
    // 4. FORM SUBMISSION AUTOMATION
    // =========================================================================

    document.addEventListener('DOMContentLoaded', function () {

        // 4a. Auto-show loading on form submit (creation/update forms)
        document.querySelectorAll('form.modern-form, form[method="post"]').forEach(function (form) {
            // Skip login & logout forms (they are lightweight)
            if (form.closest('.landing-hero') || form.action.indexOf('logout') > -1) return;

            form.addEventListener('submit', function (e) {
                // Double-submit protection
                if (form.dataset.submitting === 'true') {
                    e.preventDefault();
                    return;
                }
                form.dataset.submitting = 'true';

                const btn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (btn) {
                    btn.disabled = true;
                    btn.dataset.originalText = btn.innerHTML || btn.value;
                    if (btn.tagName === 'BUTTON') {
                        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Aguarde...';
                    } else {
                        btn.value = 'Aguarde...';
                    }
                }
            });
        });

        // 4b. Confirmation dialog for delete links
        document.querySelectorAll('a[href*="/eliminar/"]').forEach(function (link) {
            link.addEventListener('click', function (e) {
                if (!confirm('⚠️ Tem a certeza que deseja eliminar este registo?\n\nEsta acção é irreversível.')) {
                    e.preventDefault();
                }
            });
        });

        // 4c. Auto-dismiss Django messages after 6 seconds
        document.querySelectorAll('.messages-container .modern-card').forEach(function (msg) {
            setTimeout(function () {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                msg.style.transition = 'all 0.3s ease';
                setTimeout(function () { msg.remove(); }, 300);
            }, 6000);
        });
    });

    // =========================================================================
    // 5. SESSION TIMEOUT WARNING
    // =========================================================================

    (function () {
        var sessionTimeout = 30 * 60 * 1000; // 30 min default Django session
        var warningTime = 25 * 60 * 1000;     // warn at 25 min
        var warned = false;

        setTimeout(function () {
            if (!warned && document.querySelector('.modern-sidebar')) {
                warned = true;
                showToast('⏱ A sua sessão irá expirar em 5 minutos. Guarde o seu trabalho.', 'warning');
            }
        }, warningTime);
    })();

    // =========================================================================
    // 6. GLOBAL ERROR HANDLER
    // =========================================================================

    window.addEventListener('error', function (e) {
        console.error('TIBL Error:', e.message, e.filename, e.lineno);
    });

    // Fetch error interceptor for API calls (dashboard charts, etc.)
    window.addEventListener('unhandledrejection', function (e) {
        if (e.reason && e.reason.message && e.reason.message.indexOf('Failed to fetch') > -1) {
            showToast('⚠️ Falha na comunicação com o servidor. Verifique sua conexão.', 'error');
        }
    });

    // =========================================================================
    // 7. RESPONSIVE SIDEBAR ENHANCEMENTS
    // =========================================================================

    document.addEventListener('DOMContentLoaded', function () {
        // Close sidebar on click outside (mobile)
        document.addEventListener('click', function (e) {
            var sidebar = document.getElementById('sidebar');
            var toggle = document.getElementById('sidebar-toggle');
            if (sidebar && sidebar.classList.contains('open') && !sidebar.contains(e.target) && (!toggle || !toggle.contains(e.target))) {
                sidebar.classList.remove('open');
            }
        });

        // Highlight active nav item based on URL
        var currentPath = window.location.pathname;
        document.querySelectorAll('.nav-item').forEach(function (item) {
            var href = item.getAttribute('href');
            if (href && href !== '#' && currentPath.indexOf(href.split('/').slice(0, -2).join('/')) > -1 && href.length > 4) {
                item.classList.add('active');
            }
        });
    });

    // =========================================================================
    // 8. TABLE SEARCH (client-side quick filter)
    // =========================================================================

    window.TIBL.initTableSearch = function (inputId, tableSelector) {
        var input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('keyup', function () {
            var filter = this.value.toLowerCase();
            var tables = document.querySelectorAll(tableSelector || '.modern-table');

            tables.forEach(function (table) {
                var rows = table.querySelectorAll('tbody tr');
                var matchCount = 0;

                rows.forEach(function (row) {
                    var text = row.textContent.toLowerCase();
                    var isMatch = text.indexOf(filter) > -1;
                    row.style.display = isMatch ? '' : 'none';
                    if (isMatch) matchCount++;
                });

                // Optional: handle empty results visually
                var emptyMsg = table.parentNode.querySelector('.table-empty-search');
                if (matchCount === 0 && filter !== '') {
                    if (!emptyMsg) {
                        emptyMsg = document.createElement('div');
                        emptyMsg.className = 'table-empty-search';
                        emptyMsg.style.cssText = 'padding: 2rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;';
                        emptyMsg.innerHTML = '<i class="fas fa-search-minus" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i> Nenhum resultado encontrado para "' + filter + '"';
                        table.style.display = 'none';
                        table.parentNode.appendChild(emptyMsg);
                    }
                } else {
                    table.style.display = '';
                    if (emptyMsg) emptyMsg.remove();
                }
            });
        });
    };

    // Auto-init global search
    document.addEventListener('DOMContentLoaded', function () {
        window.TIBL.initTableSearch('global-search', '.modern-table');
    });

    // =========================================================================
    // 9. EXPORT & PRINT UTILITIES (Premium Features)
    // =========================================================================

    window.TIBL.print = function () {
        window.print();
    };

    window.TIBL.exportTableToCSV = function (tableSelector, filename) {
        var table = document.querySelector(tableSelector);
        if (!table) {
            window.TIBL.toast("Nenhuma tabela encontrada para exportar", "warning");
            return;
        }

        var csv = [];
        var rows = table.querySelectorAll("tr");

        for (var i = 0; i < rows.length; i++) {
            var row = [], cols = rows[i].querySelectorAll("td, th");
            for (var j = 0; j < cols.length; j++) {
                // Remove elements that shouldn't be exported (like buttons)
                var clone = cols[j].cloneNode(true);
                var toRemove = clone.querySelectorAll('.bt-primary, .bt-secondary, button, i');
                toRemove.forEach(r => r.remove());

                var data = clone.textContent.replace(/(\r\n|\n|\r)/gm, " ").trim();
                // Escape quotes and wrap in quotes for CSV safety
                data = data.replace(/"/g, '""');
                row.push('"' + data + '"');
            }
            csv.push(row.join(";")); // Use ; for better Excel compatibility in PT/AO region
        }

        // Download CSV
        var csvFile = new Blob(["\uFEFF" + csv.join("\n")], { type: "text/csv;charset=utf-8;" });
        var downloadLink = document.createElement("a");
        downloadLink.download = filename + ".csv";
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);

        window.TIBL.toast("Dados exportados com sucesso!", "success");
    };

    // =========================================================================
    // 10. INJECT CSS ANIMATIONS
    // =========================================================================

    var style = document.createElement('style');
    style.textContent = '\
@keyframes tiblSpin { to { transform: rotate(360deg); } }\
@keyframes tiblSlideIn { from { opacity:0;transform:translateX(100%); } to { opacity:1;transform:translateX(0); } }\
@keyframes tiblFadeIn { from { opacity:0;transform:translateY(10px); } to { opacity:1;transform:translateY(0); } }\
.modern-table tbody tr { animation: tiblFadeIn 0.3s ease backwards; }\
.modern-table tbody tr:nth-child(1) { animation-delay: 0.05s; }\
.modern-table tbody tr:nth-child(2) { animation-delay: 0.1s; }\
.modern-table tbody tr:nth-child(3) { animation-delay: 0.15s; }\
.modern-table tbody tr:nth-child(4) { animation-delay: 0.2s; }\
.modern-table tbody tr:nth-child(5) { animation-delay: 0.25s; }\
@media print {\
  .modern-sidebar, .modern-topbar, .sidebar-toggle, .bt-primary, .form-actions { display:none !important; }\
  .modern-main { margin-left:0 !important; padding:0 !important; }\
}\
';
    document.head.appendChild(style);

})();
