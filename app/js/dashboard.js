// Dashboard Management System
class DashboardManager {
    constructor() {
        this.initializeComponents();
        this.bindEvents();
    }

    initializeComponents() {
        this.taskList = document.querySelector('.task-list');
        this.metricCards = document.querySelectorAll('.metric-card');
        this.weatherWidget = document.querySelector('.weather-widget');
    }

    bindEvents() {
        // Task Management
        if (this.taskList) {
            this.taskList.addEventListener('click', (e) => {
                if (e.target.classList.contains('task-checkbox')) {
                    this.toggleTask(e.target);
                }
            });
        }

        // Metric Card Updates
        this.initializeMetricUpdates();

        // Weather Updates
        this.initializeWeatherUpdates();
    }

    toggleTask(checkbox) {
        checkbox.classList.toggle('checked');
        const taskItem = checkbox.closest('.task-item');

        if (checkbox.classList.contains('checked')) {
            taskItem.style.opacity = '0.7';
            this.updateTaskProgress();
        } else {
            taskItem.style.opacity = '1';
            this.updateTaskProgress();
        }
    }

    updateTaskProgress() {
        const total = document.querySelectorAll('.task-checkbox').length;
        const completed = document.querySelectorAll('.task-checkbox.checked').length;
        const progress = (completed / total) * 100;

        // Update progress bar if exists
        const progressBar = document.querySelector('.task-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
    }

    initializeMetricUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            this.metricCards.forEach(card => {
                const value = card.querySelector('.metric-value');
                if (value) {
                    const currentValue = parseFloat(value.textContent);
                    const newValue = this.generateRandomFluctuation(currentValue, 5);
                    value.textContent = newValue.toFixed(1) + value.textContent.replace(/[0-9.]/g, '');

                    // Update trend indicator
                    const trend = card.querySelector('.metric-trend');
                    if (trend) {
                        if (newValue > currentValue) {
                            trend.innerHTML = '<i class="fas fa-arrow-up"></i> Increasing';
                            trend.className = 'metric-trend trend-up';
                        } else {
                            trend.innerHTML = '<i class="fas fa-arrow-down"></i> Decreasing';
                            trend.className = 'metric-trend trend-down';
                        }
                    }
                }
            });
        }, 5000);
    }

    initializeWeatherUpdates() {
        if (this.weatherWidget) {
            // Simulate weather updates
            setInterval(() => {
                this.updateWeatherData();
            }, 300000); // Update every 5 minutes
        }
    }

    updateWeatherData() {
        // Simulate weather data update
        const temperature = this.generateRandomFluctuation(25, 2);
        const humidity = this.generateRandomFluctuation(65, 5);

        const weatherTemp = this.weatherWidget.querySelector('.weather-temp');
        if (weatherTemp) {
            weatherTemp.textContent = `${temperature.toFixed(1)}°C`;
        }

        const weatherHumidity = this.weatherWidget.querySelector('.weather-humidity');
        if (weatherHumidity) {
            weatherHumidity.textContent = `${Math.round(humidity)}%`;
        }
    }

    generateRandomFluctuation(baseValue, maxFluctuation) {
        return baseValue + (Math.random() * maxFluctuation * 2 - maxFluctuation);
    }
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardManager();
});
