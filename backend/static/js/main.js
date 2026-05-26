/* =============================================================
   File: backend/static/js/main.js
   Purpose: Global JavaScript for the AI Internship Portal
   ============================================================= */

'use strict';

/* ----------------------------------------------------------
   CSRF TOKEN — read from <meta name="csrf-token"> and attach
   to all AJAX fetch() POST/PUT/DELETE requests automatically
   ---------------------------------------------------------- */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// Wrap fetch to auto-inject X-CSRFToken header on mutating requests
const _origFetch = window.fetch;
window.fetch = function(url, opts = {}) {
    const method = (opts.method || 'GET').toUpperCase();
    if (['POST','PUT','PATCH','DELETE'].includes(method)) {
        opts.headers = opts.headers || {};
        if (!(opts.headers instanceof Headers)) {
            opts.headers['X-CSRFToken'] = getCsrfToken();
        }
    }
    return _origFetch(url, opts);
};

            - Form validation
            - UI utilities
   ============================================================= */

'use strict';

/* ----------------------------------------------------------
   SIDEBAR TOGGLE (Mobile responsiveness)
   ---------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', function () {

    const sidebar       = document.getElementById('sidebar');
    const mainContent   = document.getElementById('mainContent');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const footer        = document.querySelector('.footer');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('sidebar-collapsed');
            if (mainContent) mainContent.classList.toggle('expanded');
            if (footer)      footer.classList.toggle('expanded');
        });
    }

    /* ----------------------------------------------------------
       AUTO-DISMISS ALERTS after 5 seconds
       ---------------------------------------------------------- */
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    /* ----------------------------------------------------------
       ACTIVE NAV LINK highlight based on current URL
       ---------------------------------------------------------- */
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    /* ----------------------------------------------------------
       CONFIRM DIALOGS for destructive actions (delete buttons)
       ---------------------------------------------------------- */
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const msg = form.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    /* ----------------------------------------------------------
       PASSWORD STRENGTH METER
       ---------------------------------------------------------- */
    const passwordInput = document.getElementById('passwordStrengthInput');
    const strengthBar   = document.getElementById('passwordStrengthBar');
    const strengthText  = document.getElementById('passwordStrengthText');

    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', function () {
            const val      = passwordInput.value;
            const strength = getPasswordStrength(val);
            updateStrengthBar(strength, strengthBar, strengthText);
        });
    }

    /* ----------------------------------------------------------
       TOOLTIP initialization (Bootstrap tooltips)
       ---------------------------------------------------------- */
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    /* ----------------------------------------------------------
       DATATABLE-LIKE: Client-side table search
       ---------------------------------------------------------- */
    const tableSearch = document.getElementById('tableSearch');
    if (tableSearch) {
        tableSearch.addEventListener('input', function () {
            const query = this.value.toLowerCase();
            const rows  = document.querySelectorAll('tbody tr');
            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    /* ----------------------------------------------------------
       FILE INPUT: Show selected filename
       ---------------------------------------------------------- */
    document.querySelectorAll('.custom-file-input').forEach(function (input) {
        input.addEventListener('change', function () {
            const fileName = this.files[0] ? this.files[0].name : 'Choose file';
            const label = this.nextElementSibling;
            if (label) label.textContent = fileName;
        });
    });

    /* ----------------------------------------------------------
       SKILL TAGS: Convert comma input to badges
       ---------------------------------------------------------- */
    const skillsInput    = document.getElementById('skillsInput');
    const skillsPreview  = document.getElementById('skillsPreview');
    if (skillsInput && skillsPreview) {
        skillsInput.addEventListener('input', function () {
            const skills = this.value.split(',').map(s => s.trim()).filter(Boolean);
            skillsPreview.innerHTML = skills.map(s =>
                `<span class="badge bg-primary me-1 mb-1">${escapeHtml(s)}</span>`
            ).join('');
        });
    }

    /* ----------------------------------------------------------
       LOADING SPINNER on form submit
       ---------------------------------------------------------- */
    document.querySelectorAll('form.needs-spinner').forEach(function (form) {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                btn.disabled = true;
            }
        });
    });

    /* ----------------------------------------------------------
       RESUME ANALYZER: AJAX submission
       ---------------------------------------------------------- */
    const resumeForm   = document.getElementById('resumeAnalyzeForm');
    const resultBox    = document.getElementById('analyzeResultBox');

    if (resumeForm) {
        resumeForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(resumeForm);
            const submitBtn = resumeForm.querySelector('button[type="submit"]');

            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
            submitBtn.disabled = true;
            if (resultBox) resultBox.innerHTML = '';

            fetch('/ai/resume-analyze', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.innerHTML = '<i class="fas fa-robot me-2"></i>Analyze Resume';
                submitBtn.disabled = false;

                if (data.success && resultBox) {
                    renderResumeResult(data.result, resultBox);
                } else if (resultBox) {
                    resultBox.innerHTML = `<div class="alert alert-danger">${data.error || 'Analysis failed.'}</div>`;
                }
            })
            .catch(err => {
                submitBtn.innerHTML = '<i class="fas fa-robot me-2"></i>Analyze Resume';
                submitBtn.disabled = false;
                if (resultBox) resultBox.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
            });
        });
    }

    /* ----------------------------------------------------------
       PERFORMANCE PREDICTOR: AJAX submission
       ---------------------------------------------------------- */
    const perfForm   = document.getElementById('perfPredictForm');
    const perfResult = document.getElementById('perfResultBox');

    if (perfForm) {
        perfForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const submitBtn = perfForm.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Predicting...';
            submitBtn.disabled = true;

            const payload = {
                attendance_pct:    parseFloat(document.getElementById('inp_attendance').value) || 0,
                task_completion:   parseFloat(document.getElementById('inp_tasks').value) || 0,
                report_submissions:parseInt(document.getElementById('inp_reports').value) || 0,
                mentor_rating:     parseFloat(document.getElementById('inp_rating').value) || 3.0
            };

            fetch('/ai/performance-predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Predict Performance';
                submitBtn.disabled = false;
                if (data.success && perfResult) {
                    renderPerfResult(data.prediction, perfResult);
                } else if (perfResult) {
                    perfResult.innerHTML = `<div class="alert alert-danger">${data.error || 'Prediction failed.'}</div>`;
                }
            })
            .catch(err => {
                submitBtn.innerHTML = '<i class="fas fa-brain me-2"></i>Predict Performance';
                submitBtn.disabled = false;
                if (perfResult) perfResult.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
            });
        });
    }

});

/* ----------------------------------------------------------
   HELPER: Password strength calculation
   ---------------------------------------------------------- */
function getPasswordStrength(password) {
    let score = 0;
    if (password.length >= 8)  score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
}

function updateStrengthBar(score, bar, text) {
    const levels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    const colors = ['', 'danger', 'warning', 'info', 'primary', 'success'];
    bar.style.width = (score * 20) + '%';
    bar.className = `progress-bar bg-${colors[score] || 'secondary'}`;
    if (text) { text.textContent = levels[score] || ''; text.className = `text-${colors[score] || 'secondary'}`; }
}

/* ----------------------------------------------------------
   HELPER: Escape HTML to prevent XSS
   ---------------------------------------------------------- */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

/* ----------------------------------------------------------
   HELPER: Render resume analysis results
   ---------------------------------------------------------- */
function renderResumeResult(result, container) {
    const scoreColor = result.match_score >= 70 ? 'success' : result.match_score >= 40 ? 'warning' : 'danger';
    const matched    = (result.matched_skills || []).map(s => `<span class="badge bg-success me-1 mb-1">${escapeHtml(s)}</span>`).join('');
    const missing    = (result.missing_skills || []).map(s => `<span class="badge bg-danger me-1 mb-1">${escapeHtml(s)}</span>`).join('');
    const extracted  = (result.extracted_skills || []).slice(0, 20).map(s => `<span class="badge bg-primary me-1 mb-1">${escapeHtml(s)}</span>`).join('');

    container.innerHTML = `
    <div class="card border-0 shadow-sm rounded-4 mt-3">
        <div class="card-body">
            <div class="row align-items-center mb-3">
                <div class="col-md-4 text-center">
                    <div class="score-circle score-${scoreColor} mx-auto">
                        <span class="score-number">${result.match_score}%</span>
                        <span class="score-label">Match Score</span>
                    </div>
                </div>
                <div class="col-md-8">
                    <h5 class="fw-bold">Resume Analysis Complete</h5>
                    <div class="d-flex gap-3 mb-2">
                        <span class="badge bg-${scoreColor} fs-6 px-3 py-2">${result.recommendation || 'N/A'}</span>
                        <span class="badge bg-secondary fs-6 px-3 py-2">Grade: ${result.grade || 'N/A'}</span>
                    </div>
                    <div class="progress mb-1" style="height:12px">
                        <div class="progress-bar bg-${scoreColor} rounded-pill" style="width:${result.match_score}%"></div>
                    </div>
                    <small class="text-muted">Skill Match: ${result.skill_score || 0}% | TF-IDF: ${result.tfidf_score || 0}%</small>
                </div>
            </div>
            <hr>
            <div class="row g-3">
                <div class="col-md-4">
                    <h6 class="fw-semibold text-success"><i class="fas fa-check-circle me-1"></i>Matched Skills</h6>
                    <div>${matched || '<span class="text-muted small">None matched</span>'}</div>
                </div>
                <div class="col-md-4">
                    <h6 class="fw-semibold text-danger"><i class="fas fa-times-circle me-1"></i>Missing Skills</h6>
                    <div>${missing || '<span class="text-muted small">None missing!</span>'}</div>
                </div>
                <div class="col-md-4">
                    <h6 class="fw-semibold text-primary"><i class="fas fa-brain me-1"></i>All Extracted Skills</h6>
                    <div>${extracted || '<span class="text-muted small">None found</span>'}</div>
                </div>
            </div>
        </div>
    </div>`;
}

/* ----------------------------------------------------------
   HELPER: Render performance prediction results
   ---------------------------------------------------------- */
function renderPerfResult(prediction, container) {
    const colorMap = {
        'Excellent': 'success', 'Good': 'info', 'Average': 'warning', 'Needs Improvement': 'danger'
    };
    const iconMap = {
        'Excellent': 'fa-trophy', 'Good': 'fa-thumbs-up', 'Average': 'fa-minus-circle', 'Needs Improvement': 'fa-exclamation-triangle'
    };
    const grade    = prediction.performance_grade;
    const color    = colorMap[grade] || 'secondary';
    const icon     = iconMap[grade] || 'fa-chart-line';
    const recs     = (prediction.recommendations || []).map(r => `<li class="mb-1">${escapeHtml(r)}</li>`).join('');
    const bd       = prediction.breakdown || {};

    container.innerHTML = `
    <div class="card border-0 shadow-sm rounded-4 mt-3 border-${color}" style="border-left:4px solid !important">
        <div class="card-body">
            <div class="text-center mb-3">
                <i class="fas ${icon} fa-3x text-${color} mb-2"></i>
                <h3 class="fw-bold text-${color}">${grade}</h3>
                <p class="text-muted mb-0">Overall Score: <strong>${prediction.overall_score}%</strong>
                ${prediction.confidence ? `| Confidence: <strong>${prediction.confidence}%</strong>` : ''}</p>
                <small class="text-muted">Model: ${escapeHtml(prediction.model_used || 'N/A')}</small>
            </div>
            <hr>
            <div class="row g-2 mb-3">
                ${[
                    ['Attendance', bd.attendance, 'success'],
                    ['Task Completion', bd.task_completion, 'primary'],
                    ['Reports', bd.report_submissions + ' submitted', 'info'],
                    ['Mentor Rating', bd.mentor_rating + '/5', 'warning']
                ].map(([label, val, c]) => `
                <div class="col-6 col-md-3 text-center">
                    <div class="p-2 rounded-3 bg-light">
                        <div class="fw-bold text-${c}">${typeof val === 'number' ? val + '%' : val}</div>
                        <small class="text-muted">${label}</small>
                    </div>
                </div>`).join('')}
            </div>
            <hr>
            <h6 class="fw-semibold"><i class="fas fa-lightbulb me-2 text-warning"></i>Recommendations</h6>
            <ul class="mb-0 text-muted">${recs}</ul>
        </div>
    </div>`;
}

/* ----------------------------------------------------------
   UTILITY: Format date to readable string
   ---------------------------------------------------------- */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

/* ----------------------------------------------------------
   UTILITY: Copy text to clipboard
   ---------------------------------------------------------- */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy.', 'danger');
    });
}

/* ----------------------------------------------------------
   UTILITY: Show bootstrap toast notification
   ---------------------------------------------------------- */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    const id = 'toast_' + Date.now();
    const html = `
    <div id="${id}" class="toast align-items-center text-bg-${type} border-0" role="alert">
        <div class="d-flex">
            <div class="toast-body">${escapeHtml(message)}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    </div>`;
    toastContainer.insertAdjacentHTML('beforeend', html);
    const toastEl = document.getElementById(id);
    const toast   = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function createToastContainer() {
    const div = document.createElement('div');
    div.id = 'toastContainer';
    div.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    div.style.zIndex = '9999';
    document.body.appendChild(div);
    return div;
}
