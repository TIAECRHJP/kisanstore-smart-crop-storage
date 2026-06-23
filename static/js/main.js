let selectedCrop = null;

function selectCrop(cropKey, btn) {
    selectedCrop = cropKey;
    document.querySelectorAll('.crop-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
}

async function getRecommendation() {
    if (!selectedCrop) {
        alert('कृपया पहले एक फसल चुनें।');
        return;
    }

    const temp = parseFloat(document.getElementById('temp').value);
    const humidity = parseFloat(document.getElementById('humidity').value);
    const moisture = parseFloat(document.getElementById('moisture').value);
    const duration = document.getElementById('duration').value;

    if (isNaN(temp) || isNaN(humidity)) {
        alert('कृपया तापमान और नमी की सही जानकारी दें।');
        return;
    }

    const btn = document.querySelector('.btn-submit');
    btn.textContent = 'जानकारी ले रहे हैं...';
    btn.disabled = true;

    try {
        const response = await fetch('/get_recommendation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ crop: selectedCrop, temp, humidity, moisture, duration })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        displayResult(data);

    } catch (err) {
        alert('कुछ गलत हुआ। कृपया फिर से कोशिश करें।');
        console.error(err);
    } finally {
        btn.textContent = 'सलाह दें 🔍';
        btn.disabled = false;
    }
}

function displayResult(data) {
    const crop = data.crop_data;
    const analysis = data.analysis;

    // Header
    document.getElementById('resultIcon').textContent = crop.icon;
    document.getElementById('resultCropName').textContent = crop.hindi;

    const badge = document.getElementById('riskBadge');
    badge.textContent = analysis.risk_level;
    badge.className = 'risk-badge' + (analysis.risk_level.includes('उच्च') ? ' high' : '');

    // Info cards
    document.getElementById('idealTemp').textContent = crop.ideal_temp;
    document.getElementById('idealHumidity').textContent = crop.ideal_humidity;
    document.getElementById('maxDuration').textContent = crop.max_duration;
    document.getElementById('storageType').textContent = crop.storage_type;

    // Warnings (from crop data)
    const warningsBox = document.getElementById('warningsBox');
    const warningsList = document.getElementById('warningsList');
    if (crop.warnings && crop.warnings.length > 0) {
        warningsList.innerHTML = crop.warnings.map(w => `<li>${w}</li>`).join('');
        warningsBox.style.display = 'block';
    } else {
        warningsBox.style.display = 'none';
    }

    // Issues (from analysis)
    const issuesBox = document.getElementById('issuesBox');
    const issuesList = document.getElementById('issuesList');
    if (analysis.issues && analysis.issues.length > 0) {
        issuesList.innerHTML = analysis.issues.map(i => `<li>${i}</li>`).join('');
        issuesBox.style.display = 'block';
    } else {
        issuesBox.style.display = 'none';
    }

    // Suggestions from analysis
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = analysis.suggestions.map(s => `<li>${s}</li>`).join('');

    // Tips
    const tipsList = document.getElementById('tipsList');
    tipsList.innerHTML = crop.tips.map(t => `<li>${t}</li>`).join('');

    // Show result
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetForm() {
    selectedCrop = null;
    document.querySelectorAll('.crop-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}
