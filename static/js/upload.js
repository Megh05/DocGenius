// Upload functionality and form handling
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const uploadAreas = document.querySelectorAll('.upload-area');

    // Handle file uploads
    uploadAreas.forEach(area => {
        const input = area.querySelector('.file-input');
        const placeholder = area.querySelector('.upload-placeholder');
        const fileInfo = area.querySelector('.file-info');
        const filename = fileInfo.querySelector('.filename');
        const removeBtn = fileInfo.querySelector('.remove-file');

        // Click to upload
        area.addEventListener('click', (e) => {
            if (e.target === removeBtn || e.target.closest('.remove-file')) {
                return;
            }
            input.click();
        });

        // File selection
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFileSelection(file, placeholder, fileInfo, filename, area);
            }
        });

        // Drag and drop
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });

        area.addEventListener('dragleave', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'application/pdf') {
                    input.files = files;
                    handleFileSelection(file, placeholder, fileInfo, filename, area);
                } else {
                    showAlert('Please select a PDF file.', 'error');
                }
            }
        });

        // Remove file
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            input.value = '';
            placeholder.classList.remove('d-none');
            fileInfo.classList.add('d-none');
            area.classList.remove('file-selected');
        });
    });

    function handleFileSelection(file, placeholder, fileInfo, filename, area) {
        if (file.type !== 'application/pdf') {
            showAlert('Please select a PDF file.', 'error');
            return;
        }

        if (file.size > 16 * 1024 * 1024) { // 16MB
            showAlert('File size must be less than 16MB.', 'error');
            return;
        }

        placeholder.classList.add('d-none');
        fileInfo.classList.remove('d-none');
        filename.textContent = file.name;
        area.classList.add('file-selected');
    }

    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (!validateForm()) {
                return;
            }

            // Show loading state
            showLoadingState();

            // Submit form
            const formData = new FormData(uploadForm);
            
            fetch(uploadForm.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.text();
                }
            })
            .then(html => {
                if (html) {
                    // If we get HTML back, it means there was an error
                    document.body.innerHTML = html;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred while processing your documents. Please try again.', 'error');
                hideLoadingState();
            });
        });
    }

    function validateForm() {
        const productName = document.getElementById('company_product_name').value.trim();
        const coaFile = document.getElementById('supplier_coa').files[0];
        const msdsFile = document.getElementById('supplier_msds').files[0];
        const tdsFile = document.getElementById('supplier_tds').files[0];

        if (!productName) {
            showAlert('Please enter a company product name.', 'error');
            document.getElementById('company_product_name').focus();
            return false;
        }

        if (!coaFile) {
            showAlert('Please select a COA file.', 'error');
            return false;
        }

        if (!msdsFile) {
            showAlert('Please select an MSDS file.', 'error');
            return false;
        }

        if (!tdsFile) {
            showAlert('Please select a TDS file.', 'error');
            return false;
        }

        return true;
    }

    function showLoadingState() {
        submitBtn.disabled = true;
        submitBtn.querySelector('.spinner-border').classList.remove('d-none');
        submitBtn.querySelector('i.fas').classList.add('d-none');
        
        const form = document.getElementById('uploadForm');
        form.classList.add('processing');
        
        // Change button text
        const buttonText = submitBtn.childNodes[submitBtn.childNodes.length - 1];
        buttonText.textContent = ' Processing...';
    }

    function hideLoadingState() {
        submitBtn.disabled = false;
        submitBtn.querySelector('.spinner-border').classList.add('d-none');
        submitBtn.querySelector('i.fas').classList.remove('d-none');
        
        const form = document.getElementById('uploadForm');
        form.classList.remove('processing');
        
        // Restore button text
        const buttonText = submitBtn.childNodes[submitBtn.childNodes.length - 1];
        buttonText.textContent = ' Process Documents';
    }

    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of main content
        const main = document.querySelector('main.container');
        main.insertBefore(alertDiv, main.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // File size formatting helper
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Progress tracking (if needed for future enhancements)
    function updateProgress(step, total) {
        const progressSteps = document.querySelectorAll('.progress-step');
        progressSteps.forEach((stepEl, index) => {
            if (index < step) {
                stepEl.classList.add('completed');
                stepEl.classList.remove('active');
            } else if (index === step) {
                stepEl.classList.add('active');
                stepEl.classList.remove('completed');
            } else {
                stepEl.classList.remove('active', 'completed');
            }
        });
    }

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Global utility functions
window.downloadFile = function(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(function() {
        console.log('Copied to clipboard');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
};
