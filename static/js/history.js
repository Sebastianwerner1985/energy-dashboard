// History analysis utilities
function analyzePattern(historyData) {
    if (!historyData || historyData.length === 0) {
        return null;
    }

    // Calculate average
    const avg = historyData.reduce((sum, d) => sum + d.power, 0) / historyData.length;

    // Find peak
    const peak = Math.max(...historyData.map(d => d.power));
    const peakTime = historyData.find(d => d.power === peak)?.timestamp;

    // Find minimum
    const min = Math.min(...historyData.map(d => d.power));

    return {
        average: avg,
        peak: peak,
        peakTime: peakTime,
        minimum: min
    };
}

function detectAnomalies(historyData, threshold = 2) {
    if (!historyData || historyData.length === 0) {
        return [];
    }

    const values = historyData.map(d => d.power);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const stdDev = Math.sqrt(
        values.reduce((sq, n) => sq + Math.pow(n - avg, 2), 0) / values.length
    );

    return historyData.filter(d => {
        return Math.abs(d.power - avg) > threshold * stdDev;
    });
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        analyzePattern,
        detectAnomalies
    };
}
