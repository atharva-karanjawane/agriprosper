// Theme Management
const themeManager = {
    init() {
        this.themeToggle = document.querySelector('.theme-toggle');
        this.initTheme();
        this.bindEvents();
    },

    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (this.themeToggle) {
            this.themeToggle.checked = savedTheme === 'dark';
        }
    },

    bindEvents() {
        if (this.themeToggle) {
            this.themeToggle.addEventListener('change', () => {
                const newTheme = this.themeToggle.checked ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
            });
        }
    }
};

// Sidebar Management
const sidebarManager = {
    init() {
        this.sidebar = document.querySelector('.sidebar');
        this.toggleBtn = document.querySelector('.sidebar-toggle');
        this.bindEvents();
        this.handleResize();
    },

    bindEvents() {
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => {
                this.sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebarState', 
                    this.sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded'
                );
            });
        }

        window.addEventListener('resize', this.handleResize.bind(this));
    },

    handleResize() {
        if (window.innerWidth <= 768) {
            this.sidebar?.classList.add('collapsed');
        } else {
            const savedState = localStorage.getItem('sidebarState');
            if (savedState === 'expanded') {
                this.sidebar?.classList.remove('collapsed');
            }
        }
    }
};

// Alert Management
const alertManager = {
    init() {
        this.bindAlertActions();
    },

    bindAlertActions() {
        document.querySelectorAll('.alert .close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const alert = e.target.closest('.alert');
                this.dismissAlert(alert);
            });
        });
    },

    dismissAlert(alert) {
        alert.style.opacity = '0';
        setTimeout(() => {
            alert.remove();
        }, 300);
    },

    createAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="close">&times;</button>
        `;

        document.querySelector('.alerts-container').appendChild(alert);
        this.bindAlertActions();
    }
};

// Form Validation
const formValidator = {
    init() {
        this.bindForms();
    },

    bindForms() {
        document.querySelectorAll('form[data-validate]').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    },

    validateForm(form) {
        let isValid = true;

        // Required fields
        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                this.showError(field, 'This field is required');
                isValid = false;
            }
        });

        // Email validation
        form.querySelectorAll('[type="email"]').forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                this.showError(field, 'Please enter a valid email');
                isValid = false;
            }
        });

        return isValid;
    },

    showError(field, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;

        field.classList.add('error');
        field.parentNode.appendChild(errorDiv);

        setTimeout(() => {
            errorDiv.remove();
            field.classList.remove('error');
        }, 3000);
    },

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
};

// Chart Utilities
const chartUtils = {
    colors: {
        primary: '#2ecc71',
        secondary: '#27ae60',
        danger: '#e74c3c',
        warning: '#f1c40f',
        info: '#3498db'
    },

    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top'
            }
        }
    },

    createLineChart(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: { ...this.defaultOptions, ...options }
        });
    },

    createBarChart(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: { ...this.defaultOptions, ...options }
        });
    },

    createDoughnutChart(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: { ...this.defaultOptions, ...options }
        });
    }
};

// Data Formatting Utilities
const formatUtils = {
    currency(amount, currency = '₹') {
        return `${currency}${amount.toLocaleString('en-IN')}`;
    },

    percentage(value) {
        return `${Math.round(value)}%`;
    },

    date(date) {
        return new Date(date).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    time(date) {
        return new Date(date).toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Initialize all modules
document.addEventListener('DOMContentLoaded', () => {
    themeManager.init();
    sidebarManager.init();
    alertManager.init();
    formValidator.init();
});
