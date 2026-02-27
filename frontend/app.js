/**
 * Global Tax-Code Translator Agent - Frontend Application
 */

// API Configuration - Set RAILWAY_API_URL for production or use localhost for development
// In production, this will be set to your Railway backend URL
const API_BASE_URL = window.API_BASE_URL || 'https://global-tax-translator-production.up.railway.app';

// Sample Documents
const SAMPLE_DOCUMENTS = {
    brazil: {
        country: 'BR',
        text: `BRAZILIAN TAX UPDATE 2024

CHAPTER 1: ICMS (State VAT) Regulations

Article 1 - Standard Rates
The standard ICMS rate shall be 17% (seventeen percent) for interstate transactions within Brazil.
For intrastate transactions, the following rates apply:
- São Paulo: 18%
- Rio de Janeiro: 20%
- Other states: 17-19% (varies by state)

Article 2 - Reduced Rates
A reduced rate of 12% (twelve percent) applies to:
- Basic food items (rice, beans, bread)
- Public transportation services
- Agricultural inputs

A super-reduced rate of 7% (seven percent) applies to:
- Essential medicines
- Medical equipment
- Books and educational materials

Article 3 - Exemptions
The following are exempt from ICMS:
- Exports of goods and services
- International transportation
- Operations with gold as financial asset

Article 4 - Filing Requirements
ICMS returns must be filed:
- Monthly: By the 15th day of the following month
- Annual reconciliation: By March 31st

Registration threshold: BRL 81,000 annual revenue for simplified regime (Simples Nacional).

Article 5 - Penalties
Late payment penalty: 0.33% per day, capped at 20%
Late filing penalty: 2% of tax due per month, minimum BRL 200`
    },
    eu_vat: {
        country: 'DE',
        text: `EUROPEAN UNION VAT DIRECTIVE IMPLEMENTATION - GERMANY

Section 1: VAT Rates

1.1 Standard Rate
The standard VAT rate (Umsatzsteuer) in Germany is 19% (nineteen percent).
This rate applies to all goods and services unless otherwise specified.

1.2 Reduced Rate
A reduced rate of 7% (seven percent) applies to:
- Food and beverages (excluding restaurant services)
- Books, newspapers, and periodicals
- Public transportation (short distance)
- Hotel accommodation
- Cultural events and museums
- Medical and dental services (certain categories)

1.3 Zero Rate
Zero-rated supplies include:
- Intra-EU supplies to VAT-registered businesses
- Exports to third countries
- International transport services

Section 2: Registration and Thresholds

2.1 Registration Threshold
- Standard threshold: EUR 22,000 annual turnover (small business exemption)
- Distance selling threshold: EUR 10,000 (EU-wide)
- No threshold for non-EU businesses

2.2 VAT Identification Number
Format: DE followed by 9 digits (e.g., DE123456789)

Section 3: Filing Requirements

3.1 VAT Returns (Umsatzsteuervoranmeldung)
- Monthly: If prior year VAT liability exceeded EUR 7,500
- Quarterly: If prior year VAT liability between EUR 1,000 and EUR 7,500
- Annually: If prior year VAT liability below EUR 1,000

3.2 Deadlines
- Monthly/Quarterly returns: 10th day of following month
- Annual return: July 31st of following year
- EC Sales List: 25th day of following month

Section 4: Special Schemes

4.1 One-Stop Shop (OSS)
Applicable for:
- Distance sales of goods to EU consumers
- Digital services to EU consumers

4.2 Import One-Stop Shop (IOSS)
For goods imported with value up to EUR 150.`
    },
    us_income: {
        country: 'US',
        text: `UNITED STATES FEDERAL INCOME TAX - 2024 TAX YEAR

PART I: INDIVIDUAL INCOME TAX BRACKETS

Section 1: Tax Rates for Single Filers

Tax Bracket 1: 10%
- Taxable income: $0 to $11,600

Tax Bracket 2: 12%
- Taxable income: $11,601 to $47,150

Tax Bracket 3: 22%
- Taxable income: $47,151 to $100,525

Tax Bracket 4: 24%
- Taxable income: $100,526 to $191,950

Tax Bracket 5: 32%
- Taxable income: $191,951 to $243,725

Tax Bracket 6: 35%
- Taxable income: $243,726 to $609,350

Tax Bracket 7: 37%
- Taxable income: Over $609,350

Section 2: Standard Deduction
- Single: $14,600
- Married Filing Jointly: $29,200
- Head of Household: $21,900

Section 3: Filing Requirements

3.1 Filing Deadlines
- Individual returns (Form 1040): April 15th
- Extension deadline: October 15th
- Estimated tax payments: April 15, June 15, September 15, January 15

3.2 Minimum Income to File
- Single, under 65: $14,600
- Single, 65 or older: $16,550
- Married filing jointly, both under 65: $29,200

Section 4: Key Deductions and Credits

4.1 Child Tax Credit
- Amount: $2,000 per qualifying child
- Phase-out begins: $200,000 (single), $400,000 (married filing jointly)

4.2 Earned Income Tax Credit (EITC)
- Maximum credit (3+ children): $7,430
- Income limit (3+ children): $59,899 (single), $66,819 (married filing jointly)

Section 5: Withholding Requirements
Employers must withhold federal income tax based on Form W-4.
Self-employed individuals must make quarterly estimated payments if expected tax liability exceeds $1,000.`
    }
};

// State
let selectedFile = null;
let currentResults = null;

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');
const textInput = document.getElementById('text-input');
const countrySelect = document.getElementById('country');
const outputFormatSelect = document.getElementById('output-format');
const contextInput = document.getElementById('context');
const processBtn = document.getElementById('process-btn');
const loadingState = document.getElementById('loading-state');
const emptyState = document.getElementById('empty-state');
const results = document.getElementById('results');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initDropzone();
    initSamples();
    initOutputTabs();
    initCopyButtons();
    initProcessButton();
});

// Tab Navigation
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

// Dropzone
function initDropzone() {
    dropzone.addEventListener('click', () => fileInput.click());
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    removeFileBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        dropzone.style.display = 'block';
    });
}

function handleFileSelect(file) {
    const allowedTypes = ['.pdf', '.txt', '.docx'];
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(extension)) {
        alert('Invalid file type. Please upload PDF, TXT, or DOCX files.');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    dropzone.style.display = 'none';
    fileInfo.style.display = 'flex';
}

// Sample Documents
function initSamples() {
    const sampleBtns = document.querySelectorAll('.sample-btn');
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleKey = btn.dataset.sample;
            const sample = SAMPLE_DOCUMENTS[sampleKey];
            
            if (sample) {
                // Switch to text tab
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelector('[data-tab="text"]').classList.add('active');
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.getElementById('text-tab').classList.add('active');
                
                // Set text and country
                textInput.value = sample.text;
                countrySelect.value = sample.country;
                
                // Clear file selection
                selectedFile = null;
                fileInput.value = '';
                fileInfo.style.display = 'none';
                dropzone.style.display = 'block';
            }
        });
    });
}

// Output Tabs
function initOutputTabs() {
    const outputTabs = document.querySelectorAll('.output-tab');
    outputTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const outputId = tab.dataset.output;
            
            outputTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.querySelectorAll('.output-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${outputId}-output`).classList.add('active');
        });
    });
}

// Copy Buttons
function initCopyButtons() {
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const copyType = btn.dataset.copy;
            let textToCopy = '';
            
            switch (copyType) {
                case 'json':
                    textToCopy = document.getElementById('json-code').textContent;
                    break;
                case 'sql':
                    textToCopy = document.getElementById('sql-code').textContent;
                    break;
                case 'policy':
                    textToCopy = document.getElementById('policy-code').textContent;
                    break;
                case 'code':
                    textToCopy = document.getElementById('python-code').textContent;
                    break;
            }
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            });
        });
    });
}

// Process Button
function initProcessButton() {
    processBtn.addEventListener('click', async () => {
        const activeTab = document.querySelector('.tab.active').dataset.tab;
        
        if (activeTab === 'file' && !selectedFile) {
            alert('Please select a file to process.');
            return;
        }
        
        if (activeTab === 'text' && !textInput.value.trim()) {
            alert('Please enter some text to process.');
            return;
        }
        
        await processDocument(activeTab);
    });
}

// Process Document
async function processDocument(mode) {
    showLoading();
    
    try {
        let response;
        
        if (mode === 'file') {
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('country', countrySelect.value);
            formData.append('output_format', outputFormatSelect.value);
            if (contextInput.value) {
                formData.append('context', contextInput.value);
            }
            
            response = await fetch(`${API_BASE_URL}/api/process`, {
                method: 'POST',
                body: formData
            });
        } else {
            response = await fetch(`${API_BASE_URL}/api/process-text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: textInput.value,
                    country: countrySelect.value,
                    output_format: outputFormatSelect.value,
                    context: contextInput.value || null
                })
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Processing failed');
        }
        
        const data = await response.json();
        currentResults = data;
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Error processing document: ${error.message}`);
        showEmpty();
    }
}

// Show Loading State
function showLoading() {
    emptyState.style.display = 'none';
    results.style.display = 'none';
    loadingState.style.display = 'block';
    processBtn.disabled = true;
}

// Show Empty State
function showEmpty() {
    loadingState.style.display = 'none';
    results.style.display = 'none';
    emptyState.style.display = 'block';
    processBtn.disabled = false;
}

// Display Results
function displayResults(data) {
    loadingState.style.display = 'none';
    emptyState.style.display = 'none';
    results.style.display = 'block';
    processBtn.disabled = false;
    
    // Summary
    document.getElementById('result-country').textContent = `${data.country_name} (${data.country})`;
    document.getElementById('result-language').textContent = data.language_detected.toUpperCase();
    document.getElementById('result-time').textContent = data.processing_time_ms;
    document.getElementById('result-confidence').textContent = Math.round(data.confidence_score * 100);
    document.getElementById('result-summary').textContent = data.summary;
    
    // Warnings
    const warningsContainer = document.getElementById('warnings-container');
    const warningsList = document.getElementById('warnings-list');
    if (data.warnings && data.warnings.length > 0) {
        warningsList.innerHTML = data.warnings.map(w => `<li>${w}</li>`).join('');
        warningsContainer.style.display = 'block';
    } else {
        warningsContainer.style.display = 'none';
    }
    
    // Entities
    displayEntities(data.entities);
    
    // Outputs
    if (data.json_config) {
        document.getElementById('json-code').textContent = JSON.stringify(data.json_config, null, 2);
    }
    
    if (data.sql_migration) {
        document.getElementById('sql-code').textContent = 
            `-- Migration: ${data.sql_migration.migration_name}\n` +
            `-- Description: ${data.sql_migration.description}\n` +
            `-- Tables: ${data.sql_migration.tables_affected.join(', ')}\n\n` +
            `${data.sql_migration.up_script}\n\n` +
            `-- ROLLBACK:\n${data.sql_migration.down_script}`;
    }
    
    if (data.policy_definition) {
        document.getElementById('policy-code').textContent = JSON.stringify(data.policy_definition, null, 2);
    }
    
    if (data.generated_code) {
        document.getElementById('python-code').textContent = 
            `# ${data.generated_code.filename}\n` +
            `# ${data.generated_code.description}\n` +
            `# Dependencies: ${data.generated_code.dependencies.join(', ') || 'None'}\n\n` +
            data.generated_code.code;
    }
}

// Display Entities
function displayEntities(entities) {
    const grid = document.getElementById('entities-grid');
    grid.innerHTML = '';
    
    // Tax Types
    if (entities.tax_types && entities.tax_types.length > 0) {
        grid.innerHTML += `
            <div class="entity-card">
                <h4>Tax Types</h4>
                <div class="value">${entities.tax_types.length}</div>
                <div class="label">${entities.tax_types.join(', ')}</div>
            </div>
        `;
    }
    
    // Rates
    if (entities.rates && entities.rates.length > 0) {
        grid.innerHTML += `
            <div class="entity-card">
                <h4>Tax Rates</h4>
                <div class="value">${entities.rates.length}</div>
                <div class="label">${entities.rates.map(r => `${r.name}: ${(r.rate * 100).toFixed(1)}%`).join(', ')}</div>
            </div>
        `;
    }
    
    // Brackets
    if (entities.brackets && entities.brackets.length > 0) {
        grid.innerHTML += `
            <div class="entity-card">
                <h4>Tax Brackets</h4>
                <div class="value">${entities.brackets.length}</div>
                <div class="label">Progressive brackets defined</div>
            </div>
        `;
    }
    
    // Thresholds
    if (entities.thresholds && entities.thresholds.length > 0) {
        grid.innerHTML += `
            <div class="entity-card">
                <h4>Thresholds</h4>
                <div class="value">${entities.thresholds.length}</div>
                <div class="label">${entities.thresholds.map(t => t.name).join(', ')}</div>
            </div>
        `;
    }
    
    // Deadlines
    if (entities.deadlines && entities.deadlines.length > 0) {
        grid.innerHTML += `
            <div class="entity-card">
                <h4>Deadlines</h4>
                <div class="value">${entities.deadlines.length}</div>
                <div class="label">${entities.deadlines.map(d => d.name).join(', ')}</div>
            </div>
        `;
    }
    
    // Rules
    if (entities.rules && entities.rules.length > 0) {
        grid.innerHTML += `
            <div class="entity-card">
                <h4>Rules</h4>
                <div class="value">${entities.rules.length}</div>
                <div class="label">Tax rules extracted</div>
            </div>
        `;
    }
}
