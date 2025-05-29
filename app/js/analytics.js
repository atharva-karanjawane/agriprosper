// Analytics Page Management
class AnalyticsManager {
    constructor() {
        this.initializeComponents();
        this.bindEvents();
    }

    initializeComponents() {
        this.roiCalculator = document.querySelector('.roi-calculator');
        this.chartFilters = document.querySelectorAll('.chart-filters .filter-btn');
        this.initializeCharts();
    }

    bindEvents() {
        if (this.roiCalculator) {
            this.roiCalculator.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', () => this.calculateROI());
            });
        }

        this.chartFilters.forEach(filter => {
            filter.addEventListener('click', (e) => this.handleChartFilter(e));
        });
    }

    initializeCharts() {
        // Revenue Chart
        const revenueCtx = document.getElementById('revenueChart')?.getContext('2d');
        if (revenueCtx) {
            this.revenueChart = new Chart(revenueCtx, {
                type: 'line',
                data: this.getRevenueData(),
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: value => '₹' + value
                            }
                        }
                    }
                }
            });
        }

        // Resource Usage Chart
        const resourceCtx = document.getElementById('resourceChart')?.getContext('2d');
        if (resourceCtx) {
            this.resourceChart = new Chart(resourceCtx, {
                type: 'doughnut',
                data: this.getResourceData(),
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    getRevenueData() {
        return {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue',
                data: [45000, 52000, 49000, 60000, 55000, 85000],
                borderColor: '#2ecc71',
                tension: 0.4
            }, {
                label: 'Costs',
                data: [30000, 35000, 32000, 38000, 35000, 32000],
                borderColor: '#e74c3c',
                tension: 0.4
            }]
        };
    }

    getResourceData() {
        return {
            labels: ['Water', 'Energy', 'Labor', 'Materials'],
            datasets: [{
                data: [35, 25, 20, 20],
                backgroundColor: [
                    '#3498db',
                    '#2ecc71',
                    '#f1c40f',
                    '#e67e22'
                ]
            }]
        };
    }

    calculateROI() {
        const investment = parseFloat(this.roiCalculator.querySelector('#investment').value) || 0;
        const monthlyCosts = parseFloat(this.roiCalculator.querySelector('#monthlyCosts').value) || 0;
        const monthlyRevenue = parseFloat(this.roiCalculator.querySelector('#monthlyRevenue').value) || 0;

        const monthlyProfit = monthlyRevenue - monthlyCosts;
        const breakEvenMonths = investment / monthlyProfit;

        const resultValue = this.roiCalculator.querySelector('.result-value');
        if (resultValue) {
            resultValue.textContent = isFinite(breakEvenMonths) ? 
                `${breakEvenMonths.toFixed(1)} months` : 
                'Invalid Input';
        }
    }

    handleChartFilter(e) {
        const period = e.target.dataset.period;
        this.chartFilters.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        // Update chart data based on selected period
        // This would typically fetch new data from the server
        this.updateChartData(period);
    }

    updateChartData(period) {
        // Simulate data update
        setTimeout(() => {
            const newData = this.generateRandomData(period);
            if (this.revenueChart) {
                this.revenueChart.data.datasets[0].data = newData;
                this.revenueChart.update();
            }
        }, 500);
    }

    generateRandomData(period) {
        const points = period === '7d' ? 7 : period === '30d' ? 30 : 12;
        return Array.from({length: points}, () => 
            Math.floor(Math.random() * 50000) + 30000
        );
    }
}

// Initialize Analytics
document.addEventListener('DOMContentLoaded', () => {
    const analytics = new AnalyticsManager();
});
