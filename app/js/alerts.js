// Alerts Management System
class AlertsManager {
    constructor() {
        this.initializeComponents();
        this.bindEvents();
        this.languages = {
            assamese: {
                high_temp: "তাপমাত্ৰা বৃদ্ধি পাইছে। অনুগ্ৰহ কৰি ভেন্টিলেচন চালু কৰক।",
                low_moisture: "মাটিৰ আর্দ্ৰতা কম। জলসিঞ্চনৰ প্ৰয়োজন।"
            },
            mizo: {
                high_temp: "Boruak a lum lutuk. Ventilation on rawh.",
                low_moisture: "Lei hnawnin a tlem lutuk. Tui pek a ngai."
            },
            khasi: {
                high_temp: "Ka jingshit ka long palat. Sngewbha plie ia ki ventilation.",
                low_moisture: "Ka jingtheh um ka duna. Donkam ban pynkhleh um."
            }
        };
    }

    initializeComponents() {
        this.alertsList = document.querySelector('.alert-list');
        this.languageButtons = document.querySelectorAll('.language-btn');
        this.voicePreview = document.querySelector('.voice-preview');
        this.playButton = document.querySelector('.play-btn');
        this.currentLanguage = 'assamese';
    }

    bindEvents() {
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleFilter(e));
        });

        // Language selection
        this.languageButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleLanguageChange(e));
        });

        // Play button
        if (this.playButton) {
            this.playButton.addEventListener('click', () => this.playVoiceAlert());
        }

        // Alert actions
        if (this.alertsList) {
            this.alertsList.addEventListener('click', (e) => this.handleAlertAction(e));
        }
    }

    handleFilter(e) {
        const filter = e.target.dataset.filter;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        e.target.classList.add('active');

        // Filter alerts
        document.querySelectorAll('.alert-item').forEach(alert => {
            if (filter === 'all' || alert.classList.contains(`alert-${filter}`)) {
                alert.style.display = 'flex';
            } else {
                alert.style.display = 'none';
            }
        });
    }

    handleLanguageChange(e) {
        this.languageButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        this.currentLanguage = e.target.dataset.language;
        this.updateVoicePreview();
    }

    updateVoicePreview() {
        if (this.voicePreview) {
            const messageType = 'high_temp'; // Default message type
            const message = this.languages[this.currentLanguage][messageType];
            this.voicePreview.querySelector('p').textContent = message;
        }
    }

    playVoiceAlert() {
        // Simulate voice playing
        this.playButton.innerHTML = '<i class="fas fa-pause"></i>';
        setTimeout(() => {
            this.playButton.innerHTML = '<i class="fas fa-play"></i>';
        }, 2000);
    }

    handleAlertAction(e) {
        const button = e.target.closest('.alert-btn');
        if (!button) return;

        const action = button.dataset.action;
        const alertItem = button.closest('.alert-item');

        switch(action) {
            case 'acknowledge':
                this.acknowledgeAlert(alertItem);
                break;
            case 'dismiss':
                this.dismissAlert(alertItem);
                break;
            case 'details':
                this.showAlertDetails(alertItem);
                break;
        }
    }

    acknowledgeAlert(alertItem) {
        alertItem.classList.add('acknowledged');
        const btn = alertItem.querySelector('[data-action="acknowledge"]');
        if (btn) {
            btn.textContent = 'Acknowledged';
            btn.disabled = true;
        }
        this.updateAlertStats();
    }

    dismissAlert(alertItem) {
        alertItem.style.opacity = '0';
        setTimeout(() => {
            alertItem.remove();
            this.updateAlertStats();
        }, 300);
    }

    showAlertDetails(alertItem) {
        // Implement alert details view
        console.log('Show details for:', alertItem.dataset.alertId);
    }

    updateAlertStats() {
        const stats = {
            critical: document.querySelectorAll('.alert-critical:not(.acknowledged)').length,
            warning: document.querySelectorAll('.alert-warning:not(.acknowledged)').length,
            info: document.querySelectorAll('.alert-info:not(.acknowledged)').length
        };

        // Update stats display
        Object.entries(stats).forEach(([type, count]) => {
            const statElement = document.querySelector(`.stat-${type}`);
            if (statElement) {
                statElement.textContent = count;
            }
        });
    }

    createAlert(type, title, message) {
        const alert = document.createElement('div');
        alert.className = `alert-item alert-${type}`;
        alert.innerHTML = `
            <div class="alert-icon">
                <i class="fas fa-${type === 'critical' ? 'exclamation-triangle' : 
                               type === 'warning' ? 'exclamation-circle' : 
                               'info-circle'}"></i>
            </div>
            <div class="alert-content">
                <h4>${title}</h4>
                <p>${message}</p>
                <div class="alert-meta">
                    <span>Just now</span>
                    <div class="alert-actions">
                        <button class="alert-btn" data-action="acknowledge">Acknowledge</button>
                        <button class="alert-btn" data-action="details">View Details</button>
                    </div>
                </div>
            </div>
        `;

        this.alertsList.insertBefore(alert, this.alertsList.firstChild);
        this.updateAlertStats();
    }
}

// Initialize Alerts System
document.addEventListener('DOMContentLoaded', () => {
    const alertsManager = new AlertsManager();
});
