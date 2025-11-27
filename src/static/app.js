// Warehouse Management JavaScript

// Toast notification
function showToast(message, isError = false) {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast' + (isError ? ' error' : '');
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Animate progress bar
function animateProgressBar(element, targetPercent) {
    element.classList.add('animating');
    element.style.width = targetPercent + '%';
    setTimeout(() => element.classList.remove('animating'), 800);
}

// Update warehouse info display
function updateWarehouseInfo(data) {
    const capacityEl = document.getElementById('capacity-value');
    const balanceEl = document.getElementById('balance-value');
    const freeSpaceEl = document.getElementById('free-space-value');
    const percentEl = document.getElementById('percent-value');
    const progressBar = document.querySelector('.progress-bar-fill');

    if (capacityEl) capacityEl.textContent = data.tilavuus;
    if (balanceEl) balanceEl.textContent = data.saldo;
    if (freeSpaceEl) freeSpaceEl.textContent = data.free_space;

    const percent = data.tilavuus > 0 ?
        (data.saldo / data.tilavuus) * 100 : 0;
    if (percentEl) percentEl.textContent = percent.toFixed(1);
    if (progressBar) animateProgressBar(progressBar, percent);
}

// API helper
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || 'Request failed');
    }

    return result;
}

// Create warehouse via AJAX
async function createWarehouse(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        name: form.querySelector('#name').value,
        tilavuus: parseFloat(form.querySelector('#tilavuus').value),
        alku_saldo: parseFloat(form.querySelector('#alku_saldo').value) || 0
    };

    submitBtn.classList.add('loading');

    try {
        const result = await apiRequest('/api/warehouse', 'POST', data);
        showToast('Warehouse created successfully!');
        window.location.href = '/';
    } catch (error) {
        showToast(error.message, true);
    } finally {
        submitBtn.classList.remove('loading');
    }
}

// Edit warehouse via AJAX
async function editWarehouse(event, warehouseId) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        name: form.querySelector('#name').value,
        tilavuus: parseFloat(form.querySelector('#tilavuus').value)
    };

    submitBtn.classList.add('loading');

    try {
        const result = await apiRequest(
            `/api/warehouse/${warehouseId}`,
            'PUT',
            data
        );
        showToast('Warehouse updated successfully!');
        window.location.href = `/warehouse/${warehouseId}`;
    } catch (error) {
        showToast(error.message, true);
    } finally {
        submitBtn.classList.remove('loading');
    }
}

// Delete warehouse via AJAX
async function deleteWarehouse(warehouseId, confirmDelete = true) {
    if (confirmDelete && !confirm('Delete this warehouse?')) {
        return;
    }

    try {
        await apiRequest(`/api/warehouse/${warehouseId}`, 'DELETE');
        showToast('Warehouse deleted successfully!');

        // Remove row from table if on index page
        const row = document.querySelector(`tr[data-id="${warehouseId}"]`);
        if (row) {
            row.remove();
            // Check if table is empty
            const tbody = document.querySelector('tbody');
            if (tbody && tbody.children.length === 0) {
                location.reload();
            }
        } else {
            window.location.href = '/';
        }
    } catch (error) {
        showToast(error.message, true);
    }
}

// Add content to warehouse via AJAX
async function addContent(event, warehouseId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input[name="maara"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    const amount = parseFloat(input.value);

    if (amount <= 0) {
        showToast('Please enter a positive amount', true);
        return;
    }

    submitBtn.classList.add('loading');

    try {
        const result = await apiRequest(
            `/api/warehouse/${warehouseId}/add`,
            'POST',
            { maara: amount }
        );
        updateWarehouseInfo(result);
        input.value = '0';
        showToast(`Added ${amount} to warehouse`);
    } catch (error) {
        showToast(error.message, true);
    } finally {
        submitBtn.classList.remove('loading');
    }
}

// Remove content from warehouse via AJAX
async function removeContent(event, warehouseId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input[name="maara"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    const amount = parseFloat(input.value);

    if (amount <= 0) {
        showToast('Please enter a positive amount', true);
        return;
    }

    submitBtn.classList.add('loading');

    try {
        const result = await apiRequest(
            `/api/warehouse/${warehouseId}/remove`,
            'POST',
            { maara: amount }
        );
        updateWarehouseInfo(result);
        input.value = '0';
        showToast(`Removed ${result.removed} from warehouse`);
    } catch (error) {
        showToast(error.message, true);
    } finally {
        submitBtn.classList.remove('loading');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Set up delete buttons on index page
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const warehouseId = this.dataset.id;
            deleteWarehouse(warehouseId);
        });
    });
});
