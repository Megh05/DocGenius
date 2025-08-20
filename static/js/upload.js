// Enhanced upload functionality with compact design
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const uploadAreas = document.querySelectorAll('.upload-area');

    // Handle file uploads - Fixed double prompt issue
    uploadAreas.forEach(area => {
        const input = area.querySelector('.file-input');
        const placeholder = area.querySelector('.upload-placeholder');
        const fileInfo = area.querySelector('.file-info');
        const filename = fileInfo.querySelector('.filename');
        const removeBtn = fileInfo.querySelector('.remove-file');

        // File selection handler - only trigger on actual file input change
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFileSelection(file, placeholder, fileInfo, filename, area);
            }
        });

        // Click handler - prevent double file dialog
        area.addEventListener('click', (e) => {
            // Don't trigger if clicking on remove button or if file is already selected
            if (e.target === removeBtn || e.target.closest('.remove-file') || fileInfo && !fileInfo.classList.contains('d-none')) {
                return;
            }
            // Only trigger input click if no file is selected
            if (!input.files || input.files.length === 0) {
                input.click();
            }
        });

        // Drag and drop functionality
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });

        area.addEventListener('dragleave', (e) => {
            e.preventDefault();
            if (!area.contains(e.relatedTarget)) {
                area.classList.remove('dragover');
            }
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'application/pdf') {
                    // Create a new FileList-like object
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                    handleFileSelection(file, placeholder, fileInfo, filename, area);
                } else {
                    showAlert('Please select a PDF file only.', 'warning');
                }
            }
        });

        // Remove file handler
        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                
                input.value = '';
                input.files = null;
                placeholder.classList.remove('d-none');
                fileInfo.classList.add('d-none');
                area.classList.remove('file-selected', 'dragover');
            });
        }
    });

    function handleFileSelection(file, placeholder, fileInfo, filename, area) {
        // Validate file type
        if (file.type !== 'application/pdf') {
            showAlert('Please select a PDF file only.', 'warning');
            return;
        }

        // Validate file size (16MB limit)
        if (file.size > 16 * 1024 * 1024) {
            showAlert('File size must be less than 16MB.', 'warning');
            return;
        }

        // Update UI
        placeholder.classList.add('d-none');
        fileInfo.classList.remove('d-none');
        filename.textContent = truncateFilename(file.name, 20);
        area.classList.add('file-selected');
        
        // Add success visual feedback
        area.style.borderColor = 'var(--success)';
        setTimeout(() => {
            area.style.borderColor = '';
        }, 2000);
    }

    function truncateFilename(filename, maxLength) {
        if (filename.length <= maxLength) return filename;
        const extension = filename.split('.').pop();
        const name = filename.substring(0, filename.lastIndexOf('.'));
        const truncatedName = name.substring(0, maxLength - extension.length - 4) + '...';
        return truncatedName + '.' + extension;
    }

    // Form submission handler
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Don't prevent default - let it submit normally to avoid issues
            
            // Validate form first
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }

            // Show loading state
            showLoadingState();
            
            // Form will submit normally, no need for fetch API
        });
    }

    function validateForm() {
        const productName = document.getElementById('company_product_name');
        const coaFile = document.getElementById('supplier_coa');
        const msdsFile = document.getElementById('supplier_msds');
        const tdsFile = document.getElementById('supplier_tds');

        // Clear previous validation states
        clearValidationStates();

        let isValid = true;

        // Validate product name
        if (!productName.value.trim()) {
            showFieldError(productName, 'Product name is required');
            isValid = false;
        }

        // Validate files
        if (!coaFile.files || coaFile.files.length === 0) {
            showAlert('Please select a Certificate of Analysis (COA) file.', 'warning');
            highlightUploadArea(coaFile);
            isValid = false;
        }

        if (!msdsFile.files || msdsFile.files.length === 0) {
            showAlert('Please select a Material Safety Data Sheet (MSDS) file.', 'warning');
            highlightUploadArea(msdsFile);
            isValid = false;
        }

        if (!tdsFile.files || tdsFile.files.length === 0) {
            showAlert('Please select a Technical Data Sheet (TDS) file.', 'warning');
            highlightUploadArea(tdsFile);
            isValid = false;
        }

        return isValid;
    }

    function clearValidationStates() {
        document.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        document.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });
        document.querySelectorAll('.upload-area').forEach(area => {
            area.style.borderColor = '';
        });
    }

    function showFieldError(field, message) {
        field.classList.add('is-invalid');
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback text-xs';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
        field.focus();
    }

    function highlightUploadArea(input) {
        const uploadArea = input.closest('.upload-area');
        if (uploadArea) {
            uploadArea.style.borderColor = 'var(--danger)';
            setTimeout(() => {
                uploadArea.style.borderColor = '';
            }, 3000);
        }
    }

    function showLoadingState() {
        if (submitBtn) {
            submitBtn.disabled = true;
            const spinner = submitBtn.querySelector('.spinner-border');
            const icon = submitBtn.querySelector('i.fas');
            
            if (spinner) spinner.classList.remove('d-none');
            if (icon) icon.classList.add('d-none');
            
            // Update button text
            const textNode = Array.from(submitBtn.childNodes).find(node => 
                node.nodeType === Node.TEXT_NODE && node.textContent.trim()
            );
            if (textNode) {
                textNode.textContent = ' Processing Documents...';
            }
            
            // Disable form
            const form = document.getElementById('uploadForm');
            if (form) {
                form.classList.add('processing');
                form.style.opacity = '0.7';
                form.style.pointerEvents = 'none';
            }
        }
    }

    function hideLoadingState() {
        if (submitBtn) {
            submitBtn.disabled = false;
            const spinner = submitBtn.querySelector('.spinner-border');
            const icon = submitBtn.querySelector('i.fas');
            
            if (spinner) spinner.classList.add('d-none');
            if (icon) icon.classList.remove('d-none');
            
            // Restore button text
            const textNode = Array.from(submitBtn.childNodes).find(node => 
                node.nodeType === Node.TEXT_NODE
            );
            if (textNode) {
                textNode.textContent = ' Process Documents';
            }
            
            // Re-enable form
            const form = document.getElementById('uploadForm');
            if (form) {
                form.classList.remove('processing');
                form.style.opacity = '';
                form.style.pointerEvents = '';
            }
        }
    }

    function showAlert(message, type = 'info') {
        // Remove existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.style.minWidth = '300px';
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                ${getAlertIcon(type)}
                <div class="ms-2">${message}</div>
            </div>
            <button type="button" class="btn-close btn-close-sm ms-auto" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Append to body
        document.body.appendChild(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    function getAlertIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle text-success"></i>',
            warning: '<i class="fas fa-exclamation-triangle text-warning"></i>',
            danger: '<i class="fas fa-exclamation-circle text-danger"></i>',
            error: '<i class="fas fa-exclamation-circle text-danger"></i>',
            info: '<i class="fas fa-info-circle text-info"></i>'
        };
        return icons[type] || icons.info;
    }

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // File progress visualization
    function updateUploadProgress(fileType, progress) {
        const progressBar = document.querySelector(`#${fileType}-progress`);
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
    }
});

// Global utility functions
window.downloadFile = function(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'download';
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

window.downloadAllAsZip = function(docSetId) {
    const link = document.createElement('a');
    link.href = `/download-zip/${docSetId}`;
    link.download = `documents_${docSetId}.zip`;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

window.copyToClipboard = function(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard', 'success');
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
};

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard', 'success');
    } catch (err) {
        console.error('Fallback: Could not copy text: ', err);
        showToast('Could not copy text', 'error');
    }
    
    document.body.removeChild(textArea);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '250px';
    toast.innerHTML = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}