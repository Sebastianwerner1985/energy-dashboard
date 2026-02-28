// Cost calculation utilities
function calculateDailyCost(powerWatts, hours, ratePerKwh) {
    const energyKwh = (powerWatts * hours) / 1000;
    return energyKwh * ratePerKwh;
}

function calculateMonthlyCost(dailyCost) {
    return dailyCost * 30;
}

function formatCurrency(amount, currency = '$') {
    return currency + amount.toFixed(2);
}

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateDailyCost,
        calculateMonthlyCost,
        formatCurrency
    };
}
