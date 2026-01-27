// WMS Dashboard JavaScript
const API_BASE = 'http://localhost:8080';

// Global state
let products = [];
let warehouses = [];
let documents = [];
let inventory = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    setInterval(updateTime, 1000);
    loadDashboardData();
    setupEventListeners();
});

// Update current time
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent =
        now.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
}

// Setup event listeners
function setupEventListeners() {
    // Navigation - remove conflicting listeners, use inline onclick instead
    // document.querySelectorAll('.nav-btn').forEach(btn => {
    //     btn.addEventListener('click', function() {
    //         showSection(this.textContent.toLowerCase());
    //     });
    // });

    // Forms
    document.getElementById('product-form').addEventListener('submit', handleCreateProduct);
    document.getElementById('warehouse-form').addEventListener('submit', handleCreateWarehouse);
    document.getElementById('document-form').addEventListener('submit', handleCreateDocument);
}

// Navigation
function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    // Find the button that was clicked and add active class
    const clickedBtn = Array.from(document.querySelectorAll('.nav-btn')).find(btn => 
        btn.textContent.toLowerCase() === sectionName
    );
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }

    // Show section
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');

    // Load section data
    switch(sectionName) {
        case 'products':
            loadProducts();
            break;
        case 'warehouses':
            loadWarehouses();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'documents':
            loadDocuments();
            break;
        case 'overview':
            loadDashboardData();
            break;
    }
}

// API helper functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showError(`API Error: ${error.message}`);
        throw error;
    }
}

// Load dashboard overview data
async function loadDashboardData() {
    try {
        // Load all data in parallel
        const [productsRes, warehousesRes, inventoryRes, documentsRes] = await Promise.allSettled([
            apiRequest('/api/products'),
            apiRequest('/api/warehouses'),
            apiRequest('/api/inventory'),
            apiRequest('/api/documents')
        ]);

        // Update stats
        if (productsRes.status === 'fulfilled') {
            products = productsRes.value || [];
            document.getElementById('total-products').textContent = products.length;
        }

        if (warehousesRes.status === 'fulfilled') {
            warehouses = warehousesRes.value || [];
            document.getElementById('total-warehouses').textContent = warehouses.length;
        }

        if (inventoryRes.status === 'fulfilled') {
            inventory = inventoryRes.value || [];
            const totalItems = inventory.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('total-inventory').textContent = totalItems;
        }

        if (documentsRes.status === 'fulfilled') {
            documents = documentsRes.value || [];
            const today = new Date().toISOString().split('T')[0];
            const todayDocs = documents.filter(doc => doc.created_at.startsWith(today));
            document.getElementById('today-documents').textContent = todayDocs.length;
        }

        // Load recent activity
        loadRecentActivity();

    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        updateConnectionStatus(false);
    }
}

// Load recent activity
function loadRecentActivity() {
    const activityList = document.getElementById('recent-activity-list');
    const recentItems = [];

    // Get recent documents
    const recentDocs = documents
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);

    recentDocs.forEach(doc => {
        recentItems.push({
            title: `${doc.doc_type.toUpperCase()} Document #${doc.document_id}`,
            description: `Created ${new Date(doc.created_at).toLocaleString()}`,
            type: 'document'
        });
    });

    if (recentItems.length === 0) {
        activityList.innerHTML = '<p>No recent activity</p>';
        return;
    }

    activityList.innerHTML = recentItems.map(item => `
        <div class="activity-item">
            <h4>${item.title}</h4>
            <p>${item.description}</p>
        </div>
    `).join('');
}

// Load products
async function loadProducts() {
    try {
        const productsList = document.getElementById('products-list');
        productsList.innerHTML = '<p>Loading products...</p>';

        if (products.length === 0) {
            const response = await apiRequest('/api/products');
            products = response || [];
        }

        if (products.length === 0) {
            productsList.innerHTML = '<p>No products found. Create your first product!</p>';
            return;
        }

        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${products.map(product => `
                        <tr>
                            <td>${product.product_id}</td>
                            <td>${product.name}</td>
                            <td>$${product.price.toFixed(2)}</td>
                            <td>${product.description || '-'}</td>
                            <td>
                                <button class="btn-secondary" onclick="editProduct(${product.product_id})">Edit</button>
                                <button class="btn-secondary" onclick="deleteProduct(${product.product_id})" style="background: #dc3545;">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        productsList.innerHTML = tableHTML;
    } catch (error) {
        document.getElementById('products-list').innerHTML = '<p class="error">Failed to load products</p>';
    }
}

// Load warehouses
async function loadWarehouses() {
    try {
        const warehousesList = document.getElementById('warehouses-list');
        warehousesList.innerHTML = '<p>Loading warehouses...</p>';

        if (warehouses.length === 0) {
            const response = await apiRequest('/api/warehouses');
            warehouses = response || [];
        }

        if (warehouses.length === 0) {
            warehousesList.innerHTML = '<p>No warehouses found. Create your first warehouse!</p>';
            return;
        }

        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Location</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${warehouses.map(warehouse => `
                        <tr>
                            <td>${warehouse.warehouse_id}</td>
                            <td>${warehouse.location}</td>
                            <td>
                                <button class="btn-secondary" onclick="viewWarehouseInventory(${warehouse.warehouse_id})">View Inventory</button>
                                <button class="btn-secondary" onclick="editWarehouse(${warehouse.warehouse_id})">Edit</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        warehousesList.innerHTML = tableHTML;
    } catch (error) {
        document.getElementById('warehouses-list').innerHTML = '<p class="error">Failed to load warehouses</p>';
    }
}

// Load inventory
async function loadInventory() {
    try {
        const inventoryDiv = document.getElementById('inventory-overview');
        inventoryDiv.innerHTML = '<p>Loading inventory data...</p>';

        if (inventory.length === 0) {
            const response = await apiRequest('/api/inventory');
            inventory = response || [];
        }

        if (inventory.length === 0) {
            inventoryDiv.innerHTML = '<p>No inventory data available</p>';
            return;
        }

        // Group by warehouse
        const warehouseInventory = {};
        inventory.forEach(item => {
            if (!warehouseInventory[item.warehouse_id]) {
                warehouseInventory[item.warehouse_id] = [];
            }
            warehouseInventory[item.warehouse_id].push(item);
        });

        const inventoryHTML = Object.entries(warehouseInventory).map(([warehouseId, items]) => {
            const warehouse = warehouses.find(w => w.warehouse_id == warehouseId);
            const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
            const totalValue = items.reduce((sum, item) => {
                const product = products.find(p => p.product_id === item.product_id);
                return sum + (product ? product.price * item.quantity : 0);
            }, 0);

            return `
                <div class="inventory-item">
                    <h3>Warehouse ${warehouseId} ${warehouse ? `- ${warehouse.location}` : ''}</h3>
                    <div class="inventory-stats">
                        <div class="stat-item">
                            <span class="number">${items.length}</span>
                            <span class="label">Products</span>
                        </div>
                        <div class="stat-item">
                            <span class="number">${totalItems}</span>
                            <span class="label">Total Items</span>
                        </div>
                        <div class="stat-item">
                            <span class="number">$${totalValue.toFixed(2)}</span>
                            <span class="label">Total Value</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        inventoryDiv.innerHTML = inventoryHTML;
    } catch (error) {
        document.getElementById('inventory-overview').innerHTML = '<p class="error">Failed to load inventory</p>';
    }
}

// Load documents
async function loadDocuments() {
    try {
        const documentsList = document.getElementById('documents-list');
        documentsList.innerHTML = '<p>Loading documents...</p>';

        if (documents.length === 0) {
            const response = await apiRequest('/api/documents');
            documents = response || [];
        }

        if (documents.length === 0) {
            documentsList.innerHTML = '<p>No documents found. Create your first document!</p>';
            return;
        }

        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${documents.slice(0, 20).map(doc => `
                        <tr>
                            <td>${doc.document_id}</td>
                            <td>${doc.doc_type}</td>
                            <td>${doc.status}</td>
                            <td>${new Date(doc.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn-secondary" onclick="viewDocument(${doc.document_id})">View</button>
                                ${doc.status === 'draft' ? `<button class="btn-primary" onclick="postDocument(${doc.document_id})">Post</button>` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        documentsList.innerHTML = tableHTML;
    } catch (error) {
        document.getElementById('documents-list').innerHTML = '<p class="error">Failed to load documents</p>';
    }
}

// Form handlers
async function handleCreateProduct(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const productData = {
        product_id: Date.now(), // Simple ID generation
        name: document.getElementById('product-name').value,
        price: parseFloat(document.getElementById('product-price').value),
        description: document.getElementById('product-description').value
    };

    try {
        await apiRequest('/api/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });

        showSuccess('Product created successfully!');
        closeModal('product-modal');
        event.target.reset();
        products = []; // Reset cache
        loadProducts();
        loadDashboardData();
    } catch (error) {
        showError('Failed to create product');
    }
}

async function handleCreateWarehouse(event) {
    event.preventDefault();

    const warehouseData = {
        location: document.getElementById('warehouse-location').value
    };

    try {
        await apiRequest('/api/warehouses', {
            method: 'POST',
            body: JSON.stringify(warehouseData)
        });

        showSuccess('Warehouse created successfully!');
        closeModal('warehouse-modal');
        event.target.reset();
        warehouses = []; // Reset cache
        loadWarehouses();
        loadDashboardData();
    } catch (error) {
        showError('Failed to create warehouse');
    }
}

async function handleCreateDocument(event) {
    event.preventDefault();

    const docType = document.getElementById('doc-type').value;
    const documentData = {
        doc_type: docType,
        items: []
    };

    // Add warehouse info based on type
    if (docType === 'import') {
        documentData.destination_warehouse_id = parseInt(document.getElementById('dest-warehouse').value);
    } else if (docType === 'export') {
        documentData.source_warehouse_id = parseInt(document.getElementById('source-warehouse').value);
    } else if (docType === 'transfer') {
        documentData.source_warehouse_id = parseInt(document.getElementById('source-warehouse').value);
        documentData.destination_warehouse_id = parseInt(document.getElementById('dest-warehouse').value);
    }

    // Collect items
    const itemRows = document.querySelectorAll('.item-row');
    itemRows.forEach(row => {
        const productSelect = row.querySelector('.product-select');
        const quantityInput = row.querySelector('.quantity-input');
        const priceInput = row.querySelector('.price-input');

        if (productSelect.value && quantityInput.value && priceInput.value) {
            documentData.items.push({
                product_id: parseInt(productSelect.value),
                quantity: parseInt(quantityInput.value),
                unit_price: parseFloat(priceInput.value)
            });
        }
    });

    try {
        const response = await apiRequest('/api/documents', {
            method: 'POST',
            body: JSON.stringify(documentData)
        });

        showSuccess('Document created successfully!');
        closeModal('document-modal');
        event.target.reset();
        documents = []; // Reset cache
        loadDocuments();
        loadDashboardData();
    } catch (error) {
        showError('Failed to create document');
    }
}

// Modal functions
function showCreateProductModal() {
    document.getElementById('product-modal').style.display = 'block';
}

function showCreateWarehouseModal() {
    document.getElementById('warehouse-modal').style.display = 'block';
}

function showCreateDocumentModal() {
    // Load warehouses for dropdowns
    updateWarehouseDropdowns();
    // Load products for item selection
    updateProductDropdowns();
    document.getElementById('document-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function updateDocumentForm() {
    const docType = document.getElementById('doc-type').value;
    const sourceGroup = document.getElementById('source-warehouse-group');
    const destGroup = document.getElementById('dest-warehouse-group');

    if (docType === 'import') {
        sourceGroup.style.display = 'none';
        destGroup.style.display = 'block';
    } else if (docType === 'export') {
        sourceGroup.style.display = 'block';
        destGroup.style.display = 'none';
    } else if (docType === 'transfer') {
        sourceGroup.style.display = 'block';
        destGroup.style.display = 'block';
    }
}

function updateWarehouseDropdowns() {
    const warehouseSelects = ['source-warehouse', 'dest-warehouse'];

    warehouseSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select Warehouse</option>';

        warehouses.forEach(warehouse => {
            const option = document.createElement('option');
            option.value = warehouse.warehouse_id;
            option.textContent = `${warehouse.warehouse_id} - ${warehouse.location}`;
            select.appendChild(option);
        });
    });
}

function updateProductDropdowns() {
    const productSelects = document.querySelectorAll('.product-select');

    productSelects.forEach(select => {
        select.innerHTML = '<option value="">Select Product</option>';

        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.product_id;
            option.textContent = `${product.product_id} - ${product.name}`;
            select.appendChild(option);
        });
    });
}

function addItem() {
    const itemsContainer = document.getElementById('document-items');
    const itemRow = document.createElement('div');
    itemRow.className = 'item-row';

    itemRow.innerHTML = `
        <select class="product-select" required>
            <option value="">Select Product</option>
        </select>
        <input type="number" class="quantity-input" placeholder="Quantity" min="1" required>
        <input type="number" class="price-input" placeholder="Unit Price" step="0.01" required>
        <button type="button" class="btn-secondary" onclick="removeItem(this)">Remove</button>
    `;

    itemsContainer.appendChild(itemRow);
    updateProductDropdowns();
}

function removeItem(button) {
    button.closest('.item-row').remove();
}

// Report functions
async function generateInventoryReport() {
    try {
        const response = await apiRequest('/api/reports/inventory');
        displayReportResults('Inventory Report', response);
    } catch (error) {
        showError('Failed to generate inventory report');
    }
}

async function generateProductReport() {
    try {
        const response = await apiRequest('/api/reports/products');
        displayReportResults('Product Report', response);
    } catch (error) {
        showError('Failed to generate product report');
    }
}

async function generateDocumentReport() {
    try {
        const response = await apiRequest('/api/reports/documents');
        displayReportResults('Document Report', response);
    } catch (error) {
        showError('Failed to generate document report');
    }
}

async function generateWarehouseReport() {
    try {
        const response = await apiRequest('/api/reports/warehouses');
        displayReportResults('Warehouse Report', response);
    } catch (error) {
        showError('Failed to generate warehouse report');
    }
}

function displayReportResults(title, data) {
    const resultsDiv = document.getElementById('report-results');

    if (!data || data.length === 0) {
        resultsDiv.innerHTML = `<h3>${title}</h3><p>No data available</p>`;
        return;
    }

    let html = `<h3>${title}</h3>`;

    if (Array.isArray(data)) {
        html += '<table><thead><tr>';
        const keys = Object.keys(data[0]);
        keys.forEach(key => {
            html += `<th>${key.replace(/_/g, ' ').toUpperCase()}</th>`;
        });
        html += '</tr></thead><tbody>';

        data.forEach(item => {
            html += '<tr>';
            keys.forEach(key => {
                html += `<td>${item[key] || '-'}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
    } else {
        html += `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }

    resultsDiv.innerHTML = html;
}

// Utility functions
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (connected) {
        statusElement.textContent = '● Connected';
        statusElement.className = 'status-connected';
    } else {
        statusElement.textContent = '● Disconnected';
        statusElement.className = 'status-disconnected';
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    errorDiv.style.position = 'fixed';
    errorDiv.style.top = '20px';
    errorDiv.style.right = '20px';
    errorDiv.style.zIndex = '1001';
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    successDiv.style.position = 'fixed';
    successDiv.style.top = '20px';
    successDiv.style.right = '20px';
    successDiv.style.zIndex = '1001';
    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Placeholder functions for future implementation
async function editProduct(id) {
    // Find the product
    const product = products.find(p => p.product_id === id);
    if (!product) {
        showError('Product not found');
        return;
    }

    // Populate the form
    document.getElementById('product-name').value = product.name;
    document.getElementById('product-price').value = product.price;
    document.getElementById('product-description').value = product.description;

    // Change form submit handler
    const form = document.getElementById('product-form');
    form.onsubmit = (event) => handleUpdateProduct(event, id);

    // Show modal
    document.getElementById('product-modal').style.display = 'block';
}

async function deleteProduct(id) {
    if (!confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
        return;
    }

    try {
        await apiRequest(`/api/products/${id}`, { method: 'DELETE' });
        showSuccess('Product deleted successfully!');
        products = products.filter(p => p.product_id !== id);
        loadProducts();
        loadDashboardData();
    } catch (error) {
        showError('Failed to delete product');
    }
}

async function handleUpdateProduct(event, id) {
    event.preventDefault();

    const productData = {
        name: document.getElementById('product-name').value,
        price: parseFloat(document.getElementById('product-price').value),
        description: document.getElementById('product-description').value
    };

    try {
        await apiRequest(`/api/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });

        showSuccess('Product updated successfully!');
        closeModal('product-modal');
        event.target.reset();
        products = []; // Reset cache
        loadProducts();
        loadDashboardData();

        // Reset form handler
        event.target.onsubmit = handleCreateProduct;
    } catch (error) {
        showError('Failed to update product');
    }
}

function editWarehouse(id) {
    showError('Edit warehouse functionality coming soon!');
}

function viewWarehouseInventory(id) {
    showError('Warehouse inventory view coming soon!');
}

function viewDocument(id) {
    showError('Document view functionality coming soon!');
}

async function postDocument(id) {
    try {
        await apiRequest(`/api/documents/${id}/post`, { method: 'POST' });
        showSuccess('Document posted successfully!');
        documents = []; // Reset cache
        loadDocuments();
        loadDashboardData();
    } catch (error) {
        showError('Failed to post document');
    }
}