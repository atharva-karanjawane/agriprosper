// Chart Configurations and Utilities
const chartConfigs = {
    // Environmental Chart Configuration
    environmentChart: {
        type: 'line',
        options: {
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.4
                },
                point: {
                    radius: 2
                }
            }
        }
    },

    // Energy Usage Chart Configuration
    energyChart: {
        type: 'doughnut',
        options: {
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    },

    // Profit Analysis Chart Configuration
    profitChart: {
        type: 'bar',
        options: {
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    }
};

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.colors = {
            temperature: '#3498db',
            humidity: '#2ecc71',
            soil: '#f1c40f',
            light: '#e67e22',
            solar: '#f1c40f',
            battery: '#2ecc71',
            grid: '#3498db'
        };
    }

    initializeCharts() {
        // Initialize Environmental Chart
        const envCtx = document.getElementById('environmentChart')?.getContext('2d');
        if (envCtx) {
            this.createEnvironmentalChart(envCtx);
        }

        // Initialize Energy Chart
        const energyCtx = document.getElementById('energyChart')?.getContext('2d');
        if (energyCtx) {
            this.createEnergyChart(energyCtx);
        }

        // Initialize Profit Chart
        const profitCtx = document.getElementById('profitChart')?.getContext('2d');
        if (profitCtx) {
            this.createProfitChart(profitCtx);
        }
    }

    createEnvironmentalChart(ctx) {
        const chart = new Chart(ctx, {
            ...chartConfigs.environmentChart,
            data: {
                labels: Array.from({length: 24}, (_, i) => `${i}:00`),
                datasets: [{
                    label: 'Temperature (°C)',
                    data: this.generateRandomData(24, 20, 30),
                    borderColor: this.colors.temperature,
                    fill: false
                }, {
                    label: 'Humidity (%)',
                    data: this.generateRandomData(24, 50, 70),
                    borderColor: this.colors.humidity,
                    fill: false
                }]
            }
        });
        this.charts.set('environmental', chart);
    }

    createEnergyChart(ctx) {
        const chart = new Chart(ctx, {
            ...chartConfigs.energyChart,
            data: {
                labels: ['Solar', 'Battery', 'Grid'],
                datasets: [{
                    data: [65, 25, 10],
                    backgroundColor: [
                        this.colors.solar,
                        this.colors.battery,
                        this.colors.grid
                    ]
                }]
            }
        });
        this.charts.set('energy', chart);
    }

    createProfitChart(ctx) {
        const chart = new Chart(ctx, {
            ...chartConfigs.profitChart,
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: this.generateRandomData(6, 40000, 90000),
                    backgroundColor: this.colors.humidity
                }]
            }
        });
        this.charts.set('profit', chart);
    }

    generateRandomData(points, min, max) {
        return Array.from({length: points}, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chartManager = new ChartManager();
    chartManager.initializeCharts();
});
