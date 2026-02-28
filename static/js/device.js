// Device utilities
function formatDeviceName(name) {
    return name.replace(/_/g, ' ')
               .split(' ')
               .map(word => word.charAt(0).toUpperCase() + word.slice(1))
               .join(' ');
}

function calculateDeviceEfficiency(power, category) {
    // Simple efficiency rating based on device category
    const standards = {
        'lighting': 15,
        'appliance': 100,
        'heating': 1500,
        'electronics': 50
    };

    const standard = standards[category] || 100;
    const efficiency = (standard / power) * 100;

    return Math.min(efficiency, 100);
}

function getDeviceIcon(category) {
    const icons = {
        'lighting': '💡',
        'appliance': '🔌',
        'heating': '🔥',
        'cooling': '❄️',
        'electronics': '📺',
        'kitchen': '🍳'
    };

    return icons[category] || '🔌';
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDeviceName,
        calculateDeviceEfficiency,
        getDeviceIcon
    };
}
