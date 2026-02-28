// Real-time monitoring auto-refresh
let refreshInterval;
const REFRESH_RATE = 5000; // 5 seconds

function startAutoRefresh() {
    refreshInterval = setInterval(async () => {
        await refreshData();
    }, REFRESH_RATE);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

async function refreshData() {
    try {
        const response = await fetch('/api/realtime');
        const data = await response.json();

        if (data.success) {
            updateDeviceTable(data.devices);
        }
    } catch (error) {
        console.error('Failed to refresh data:', error);
    }
}

function updateDeviceTable(devices) {
    const tbody = document.getElementById('deviceTableBody');
    if (!tbody || !devices) return;

    // Sort devices: active devices by power (high to low), then idle devices
    const sortedDevices = devices.sort((a, b) => {
        // Both idle or both active - sort by power
        if ((a.power === 0 && b.power === 0) || (a.power > 0 && b.power > 0)) {
            return b.power - a.power; // High to low
        }
        // Active devices come before idle
        if (a.power > 0 && b.power === 0) return -1;
        if (a.power === 0 && b.power > 0) return 1;
        return 0;
    });

    tbody.innerHTML = sortedDevices.map(device => `
        <tr>
            <td>${device.name}</td>
            <td>${device.room || 'Unknown'}</td>
            <td class="number">${device.power.toFixed(1)}</td>
            <td>
                ${device.power > 0
                    ? '<span class="badge badge-success">Active</span>'
                    : '<span class="badge badge-warning">Idle</span>'
                }
            </td>
        </tr>
    `).join('');
}

// Stop refresh when leaving page
window.addEventListener('beforeunload', stopAutoRefresh);
