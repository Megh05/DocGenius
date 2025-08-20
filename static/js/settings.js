/**
 * Settings modal JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toggle API key visibility
    const toggleApiKeyBtn = document.getElementById('toggleApiKey');
    const apiKeyInput = document.getElementById('mistralApiKey');
    
    if (toggleApiKeyBtn && apiKeyInput) {
        toggleApiKeyBtn.addEventListener('click', function() {
            const isPassword = apiKeyInput.type === 'password';
            apiKeyInput.type = isPassword ? 'text' : 'password';
            
            const icon = toggleApiKeyBtn.querySelector('i');
            icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
        });
    }
    
    // Test connection
    const testConnectionBtn = document.getElementById('testConnection');
    const connectionStatus = document.getElementById('connectionStatus');
    
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', async function() {
            const apiKey = apiKeyInput.value.trim();
            
            if (!apiKey) {
                showConnectionStatus('error', 'Please enter an API key first');
                return;
            }
            
            // Disable button during test
            testConnectionBtn.disabled = true;
            testConnectionBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
            
            try {
                const response = await fetch('/api/test-mistral-connection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ api_key: apiKey })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showConnectionStatus('success', `Connection successful! ${result.models_available} models available`);
                } else {
                    showConnectionStatus('error', `Connection failed: ${result.error}`);
                }
            } catch (error) {
                showConnectionStatus('error', `Network error: ${error.message}`);
            } finally {
                // Re-enable button
                testConnectionBtn.disabled = false;
                testConnectionBtn.innerHTML = '<i class="fas fa-plug me-1"></i>Test Connection';
            }
        });
    }
    
    // Save settings
    const saveSettingsBtn = document.getElementById('saveSettings');
    
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', async function() {
            const apiKey = apiKeyInput.value.trim();
            const enableMistralOCR = document.getElementById('enableMistralOCR').checked;
            const enableFieldValidation = document.getElementById('enableFieldValidation').checked;
            
            // Disable button during save
            saveSettingsBtn.disabled = true;
            saveSettingsBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
            
            try {
                const response = await fetch('/api/save-settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        mistral_api_key: apiKey,
                        enable_mistral_ocr: enableMistralOCR,
                        enable_field_validation: enableFieldValidation
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert('success', 'Settings saved successfully!');
                    
                    // Close modal after a short delay
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
                        modal.hide();
                    }, 1000);
                } else {
                    showAlert('error', `Failed to save settings: ${result.error}`);
                }
            } catch (error) {
                showAlert('error', `Network error: ${error.message}`);
            } finally {
                // Re-enable button
                saveSettingsBtn.disabled = false;
                saveSettingsBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Settings';
            }
        });
    }
    
    function showConnectionStatus(type, message) {
        if (!connectionStatus) return;
        
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
        
        connectionStatus.innerHTML = `
            <div class="alert ${alertClass} alert-sm mb-0" role="alert">
                <i class="${icon} me-1"></i>${message}
            </div>
        `;
    }
    
    function showAlert(type, message) {
        // Create a temporary alert at the top of the page
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // Load settings when modal is opened
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.addEventListener('show.bs.modal', function() {
            loadCurrentSettings();
        });
    }
    
    async function loadCurrentSettings() {
        try {
            const response = await fetch('/api/get-settings');
            const settings = await response.json();
            
            if (settings.success) {
                document.getElementById('enableMistralOCR').checked = settings.enable_mistral_ocr !== false;
                document.getElementById('enableFieldValidation').checked = settings.enable_field_validation !== false;
                
                // API key is already populated from session in the template
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }
});