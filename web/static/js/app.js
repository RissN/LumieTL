// LumieTL Web Monolith Application Logic
document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navTabs = document.querySelectorAll('.nav-tab');
  const sections = document.querySelectorAll('.view-section');

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.dataset.tab;
      navTabs.forEach(t => t.classList.remove('active'));
      sections.forEach(s => s.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(targetId).classList.add('active');

      if (targetId === 'models-view') loadModelsStatus();
      if (targetId === 'history-view') loadHistory();
      if (targetId === 'settings-view') loadSettings();
    });
  });

  // Toasts
  window.showToast = function(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  };

  // --- 1. SINGLE TRANSLATE ---
  const singleDropzone = document.getElementById('single-dropzone');
  const singleFileInput = document.getElementById('single-file-input');
  const singleTranslateBtn = document.getElementById('single-translate-btn');
  const singleProgress = document.getElementById('single-progress');
  const singleProgressBar = document.getElementById('single-progress-bar');
  const singleProgressText = document.getElementById('single-progress-text');
  const viewerContainer = document.getElementById('viewer-container');
  const imgBefore = document.getElementById('img-before');
  const imgAfter = document.getElementById('img-after');
  const afterWrapper = document.getElementById('after-wrapper');
  const sliderHandle = document.getElementById('slider-handle');
  const downloadResultBtn = document.getElementById('download-result-btn');

  let selectedFile = null;
  let currentResultBase64 = null;
  let currentOutputFilename = 'translated.png';

  // File selection
  singleFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  singleDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    singleDropzone.classList.add('dragover');
  });

  singleDropzone.addEventListener('dragleave', () => {
    singleDropzone.classList.remove('dragover');
  });

  singleDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    singleDropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  function handleFileSelected(file) {
    selectedFile = file;
    document.getElementById('single-dropzone-title').textContent = `Berkas: ${file.name}`;
    document.getElementById('single-dropzone-subtitle').textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB - Klik untuk mengganti berkas`;
    singleTranslateBtn.disabled = false;

    // Preview original
    const reader = new FileReader();
    reader.onload = (e) => {
      imgBefore.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Translation execution
  singleTranslateBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const sourceLang = document.getElementById('source-lang').value;
    const targetLang = document.getElementById('target-lang').value;
    const engine = document.getElementById('engine-select').value;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);
    formData.append('engine', engine);

    singleTranslateBtn.disabled = true;
    singleProgress.style.display = 'block';
    singleProgressBar.style.width = '45%';
    singleProgressText.textContent = 'Mendeteksi teks dan menerjemahkan...';

    try {
      const response = await fetch('/api/translate/single', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Terjadi kesalahan saat menerjemahkan');
      }

      singleProgressBar.style.width = '100%';
      singleProgressText.textContent = `Selesai dalam ${data.duration}s`;

      currentResultBase64 = data.result_image_base64;
      currentOutputFilename = data.output_filename || 'translated.png';

      imgAfter.src = currentResultBase64;
      viewerContainer.style.display = 'block';
      setupSlider();
      showToast(`Penerjemahan berhasil (${data.duration} detik)`, 'success');

    } catch (err) {
      showToast(err.message, 'error');
      singleProgressText.textContent = 'Gagal menerjemahkan.';
    } finally {
      singleTranslateBtn.disabled = false;
    }
  });

  // Split Slider Logic
  function setupSlider() {
    let isDragging = false;

    function updateSlider(x) {
      const rect = viewerContainer.getBoundingClientRect();
      let percent = ((x - rect.left) / rect.width) * 100;
      percent = Math.max(0, Math.min(100, percent));
      afterWrapper.style.width = `${percent}%`;
      sliderHandle.style.left = `${percent}%`;
    }

    sliderHandle.onmousedown = (e) => {
      isDragging = true;
      e.preventDefault();
    };

    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', (e) => {
      if (isDragging) updateSlider(e.clientX);
    });

    // Touch support
    sliderHandle.ontouchstart = () => isDragging = true;
    window.addEventListener('touchend', () => isDragging = false);
    window.addEventListener('touchmove', (e) => {
      if (isDragging && e.touches[0]) updateSlider(e.touches[0].clientX);
    });
  }

  // Download & copy
  downloadResultBtn.addEventListener('click', () => {
    if (!currentResultBase64) return;
    const a = document.createElement('a');
    a.href = currentResultBase64;
    a.download = currentOutputFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });

  // --- 2. BATCH TRANSLATE ---
  const batchFileInput = document.getElementById('batch-file-input');
  const batchQueueList = document.getElementById('batch-queue-list');
  const batchStartBtn = document.getElementById('batch-start-btn');
  const batchProgress = document.getElementById('batch-progress');
  const batchProgressBar = document.getElementById('batch-progress-bar');
  const batchProgressText = document.getElementById('batch-progress-text');
  let batchFiles = [];

  batchFileInput.addEventListener('change', (e) => {
    batchFiles = Array.from(e.target.files);
    renderBatchQueue();
  });

  function renderBatchQueue() {
    batchQueueList.innerHTML = '';
    if (batchFiles.length === 0) {
      batchStartBtn.disabled = true;
      return;
    }

    batchStartBtn.disabled = false;
    document.getElementById('batch-dropzone-title').textContent = `${batchFiles.length} berkas dipilih`;

    batchFiles.forEach((f, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td>${f.name}</td>
        <td>${(f.size / 1024).toFixed(1)} KB</td>
        <td id="batch-item-status-${idx}"><span class="badge badge-warning">Menunggu</span></td>
      `;
      batchQueueList.appendChild(tr);
    });
  }

  batchStartBtn.addEventListener('click', async () => {
    if (batchFiles.length === 0) return;
    batchStartBtn.disabled = true;
    batchProgress.style.display = 'block';

    const sourceLang = document.getElementById('batch-source-lang').value;
    const targetLang = document.getElementById('batch-target-lang').value;
    const engine = document.getElementById('batch-engine-select').value;

    let successCount = 0;
    for (let i = 0; i < batchFiles.length; i++) {
      const file = batchFiles[i];
      const statusEl = document.getElementById(`batch-item-status-${i}`);
      statusEl.innerHTML = '<span class="badge badge-warning">Memproses...</span>';
      
      const pct = Math.round(((i) / batchFiles.length) * 100);
      batchProgressBar.style.width = `${pct}%`;
      batchProgressText.textContent = `Memproses berkas ${i + 1} dari ${batchFiles.length} (${file.name})...`;

      const formData = new FormData();
      formData.append('file', file);
      formData.append('source_lang', sourceLang);
      formData.append('target_lang', targetLang);
      formData.append('engine', engine);

      try {
        const res = await fetch('/api/translate/single', { method: 'POST', body: formData });
        if (!res.ok) throw new Error();
        statusEl.innerHTML = '<span class="badge badge-success">Sukses</span>';
        successCount++;
      } catch (err) {
        statusEl.innerHTML = '<span class="badge badge-danger">Gagal</span>';
      }
    }

    batchProgressBar.style.width = '100%';
    batchProgressText.textContent = `Selesai: ${successCount} dari ${batchFiles.length} berkas berhasil diterjemahkan.`;
    showToast(`Batch selesai (${successCount}/${batchFiles.length})`, 'success');
    batchStartBtn.disabled = false;
  });

  // --- 3. MODELS VIEW ---
  async function loadModelsStatus() {
    const tableBody = document.getElementById('models-table-body');
    const downloadBtn = document.getElementById('download-models-btn');
    tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Memuat status model...</td></tr>';

    try {
      const res = await fetch('/api/models/status');
      const data = await res.json();
      tableBody.innerHTML = '';

      let hasMissing = false;
      data.models.forEach(m => {
        if (!m.present) hasMissing = true;
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${m.name}</strong></td>
          <td>${m.filename}</td>
          <td>${m.size_str}</td>
          <td>
            <span class="badge ${m.present ? 'badge-success' : 'badge-danger'}">
              ${m.present ? 'Tersedia' : 'Belum Ada'}
            </span>
          </td>
        `;
        tableBody.appendChild(tr);
      });

      downloadBtn.disabled = !hasMissing;
      if (!hasMissing) {
        document.getElementById('models-summary-text').textContent = 'Semua model ONNX lengkap dan siap digunakan.';
      } else {
        document.getElementById('models-summary-text').textContent = 'Terdapat model yang belum diunduh.';
      }

    } catch (err) {
      showToast('Gagal memuat status model', 'error');
    }
  }

  const downloadModelsBtn = document.getElementById('download-models-btn');
  downloadModelsBtn.addEventListener('click', async () => {
    downloadModelsBtn.disabled = true;
    showToast('Memulai unduhan model...', 'info');

    try {
      const res = await fetch('/api/models/download', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'already_ready') {
        showToast(data.message, 'success');
        return;
      }

      // Poll download task
      const taskId = data.task_id;
      const progressBox = document.getElementById('models-progress-box');
      const progressBar = document.getElementById('models-progress-bar');
      const progressText = document.getElementById('models-progress-text');
      progressBox.style.display = 'block';

      const interval = setInterval(async () => {
        const pollRes = await fetch(`/api/models/download/${taskId}`);
        const pollData = await pollRes.json();

        progressBar.style.width = `${pollData.progress}%`;
        progressText.textContent = `Mengunduh ${pollData.current_model || ''} (${pollData.progress}%)...`;

        if (pollData.status === 'finished') {
          clearInterval(interval);
          progressText.textContent = 'Semua model berhasil diunduh!';
          showToast('Unduhan model selesai!', 'success');
          loadModelsStatus();
        } else if (pollData.status === 'error') {
          clearInterval(interval);
          progressText.textContent = `Error: ${pollData.error}`;
          showToast(pollData.error, 'error');
          downloadModelsBtn.disabled = false;
        }
      }, 1500);

    } catch (err) {
      showToast('Gagal memulai unduhan model', 'error');
      downloadModelsBtn.disabled = false;
    }
  });

  // --- 4. HISTORY VIEW ---
  async function loadHistory() {
    const tableBody = document.getElementById('history-table-body');
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Memuat riwayat...</td></tr>';

    try {
      const res = await fetch('/api/history?limit=50');
      const data = await res.json();
      tableBody.innerHTML = '';

      if (data.items.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">Belum ada riwayat penerjemahan.</td></tr>';
        return;
      }

      data.items.forEach(h => {
        const tr = document.createElement('tr');
        const inputName = h.input_path ? h.input_path.split('\\').pop().split('/').pop() : '-';
        tr.innerHTML = `
          <td>#${h.id}</td>
          <td>${h.timestamp ? h.timestamp.split('.')[0] : '-'}</td>
          <td title="${h.input_path}">${inputName}</td>
          <td>${h.source_lang} &rarr; ${h.target_lang}</td>
          <td><span class="badge badge-warning">${h.engine}</span></td>
          <td>${h.duration ? h.duration.toFixed(2) + 's' : '-'}</td>
          <td><span class="badge ${h.success ? 'badge-success' : 'badge-danger'}">${h.success ? 'Berhasil' : 'Gagal'}</span></td>
        `;
        tableBody.appendChild(tr);
      });

    } catch (err) {
      showToast('Gagal memuat riwayat', 'error');
    }
  }

  document.getElementById('clear-history-btn').addEventListener('click', async () => {
    if (!confirm('Apakah Anda yakin ingin menghapus seluruh riwayat penerjemahan?')) return;
    try {
      await fetch('/api/history', { method: 'DELETE' });
      showToast('Riwayat berhasil dibersihkan', 'success');
      loadHistory();
    } catch (err) {
      showToast('Gagal membersihkan riwayat', 'error');
    }
  });

  // --- 5. SETTINGS VIEW ---
  async function loadSettings() {
    try {
      const [settingsRes, keysRes] = await Promise.all([
        fetch('/api/settings'),
        fetch('/api/settings/api-keys')
      ]);

      const settings = await settingsRes.json();
      const keys = await keysRes.json();

      document.getElementById('setting-default-source').value = settings.default_source_lang;
      document.getElementById('setting-default-target').value = settings.default_target_lang;
      document.getElementById('setting-default-engine').value = settings.default_engine;
      document.getElementById('setting-font-size').value = settings.font_size || 14;

      document.getElementById('status-deepl-key').textContent = keys.deepl_set ? 'Sudah tersimpan' : 'Belum diatur';
      document.getElementById('status-deepl-key').className = `badge ${keys.deepl_set ? 'badge-success' : 'badge-warning'}`;
      document.getElementById('status-openai-key').textContent = keys.openai_set ? 'Sudah tersimpan' : 'Belum diatur';
      document.getElementById('status-openai-key').className = `badge ${keys.openai_set ? 'badge-success' : 'badge-warning'}`;

    } catch (err) {
      showToast('Gagal memuat pengaturan', 'error');
    }
  }

  document.getElementById('save-settings-btn').addEventListener('click', async () => {
    const payload = {
      default_source_lang: document.getElementById('setting-default-source').value,
      default_target_lang: document.getElementById('setting-default-target').value,
      default_engine: document.getElementById('setting-default-engine').value,
      font_size: parseInt(document.getElementById('setting-font-size').value, 10),
      gpu_enabled: false
    };

    try {
      const res = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error();

      // Save API keys if entered
      const deeplKey = document.getElementById('input-deepl-key').value.trim();
      if (deeplKey) {
        await fetch('/api/settings/api-keys', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider: 'deepl', key: deeplKey })
        });
      }

      const openaiKey = document.getElementById('input-openai-key').value.trim();
      if (openaiKey) {
        await fetch('/api/settings/api-keys', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider: 'openai', key: openaiKey })
        });
      }

      showToast('Pengaturan berhasil disimpan', 'success');
      loadSettings();

    } catch (err) {
      showToast('Gagal menyimpan pengaturan', 'error');
    }
  });

  // Initial check on load
  fetch('/api/models/status')
    .then(r => r.json())
    .then(d => {
      const dot = document.getElementById('server-status-dot');
      dot.className = 'status-dot online';
      document.getElementById('server-status-text').textContent = d.ready ? 'Siap' : 'Model belum lengkap';
    })
    .catch(() => {
      document.getElementById('server-status-text').textContent = 'Offline';
    });
});
