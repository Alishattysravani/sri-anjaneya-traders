document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }
});

function addRow(containerId, templateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);
    if (container && template) {
        const clone = template.content.cloneNode(true);
        container.appendChild(clone);
        attachRowEvents(container.lastElementChild);
    }
}

function attachRowEvents(row) {
    const qtyInput = row.querySelector('.item-qty');
    const priceInput = row.querySelector('.item-price');
    const totalSpan = row.querySelector('.item-total');
    const productSelect = row.querySelector('.item-product');

    function updateTotal() {
        const qty = parseFloat(qtyInput?.value) || 0;
        const price = parseFloat(priceInput?.value) || 0;
        if (totalSpan) totalSpan.textContent = (qty * price).toFixed(2);
        updateGrandTotal();
    }

    if (productSelect) {
        productSelect.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];
            const price = option.dataset.price;
            const stock = option.dataset.stock;
            if (priceInput && price) priceInput.value = price;
            if (qtyInput && stock) qtyInput.max = stock;
            updateTotal();
        });
    }

    if (qtyInput) qtyInput.addEventListener('input', updateTotal);
    if (priceInput) priceInput.addEventListener('input', updateTotal);

    const removeBtn = row.querySelector('.remove-row');
    if (removeBtn) {
        removeBtn.addEventListener('click', function () {
            row.remove();
            updateGrandTotal();
        });
    }
}

function updateGrandTotal() {
    let subtotal = 0;
    document.querySelectorAll('.item-row').forEach(function (row) {
        const qty = parseFloat(row.querySelector('.item-qty')?.value) || 0;
        const price = parseFloat(row.querySelector('.item-price')?.value) || 0;
        subtotal += qty * price;
    });

    const subtotalEl = document.getElementById('subtotal');
    const discountEl = document.getElementById('discount');
    const gstEl = document.getElementById('gst');
    const grandTotalEl = document.getElementById('grand_total');
    const paidEl = document.getElementById('paid_amount');
    const balanceEl = document.getElementById('balance');

    if (subtotalEl) subtotalEl.textContent = subtotal.toFixed(2);
    const discount = parseFloat(discountEl?.value) || 0;
    const gst = parseFloat(gstEl?.value) || 0;
    const grandTotal = Math.max(0, subtotal - discount + gst);
    if (grandTotalEl) grandTotalEl.textContent = grandTotal.toFixed(2);
    const paid = parseFloat(paidEl?.value) || 0;
    if (balanceEl) balanceEl.textContent = (grandTotal - paid).toFixed(2);
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.item-row').forEach(attachRowEvents);
    ['discount', 'gst', 'paid_amount'].forEach(function (id) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', updateGrandTotal);
    });
});
