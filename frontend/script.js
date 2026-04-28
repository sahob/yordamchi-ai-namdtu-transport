const statusEl = document.getElementById('status');
const sourcesEl = document.getElementById('sources');
const answerEl = document.getElementById('answer');
const form = document.getElementById('askForm');
const questionEl = document.getElementById('question');
const modeEl = document.getElementById('mode');
const submitBtn = document.getElementById('submitBtn');
const quickPrompts = document.getElementById('quickPrompts');

async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    statusEl.textContent = `Ishlamoqda · ${data.chunks} bo‘lak`;
    statusEl.className = 'status ok';
  } catch (error) {
    statusEl.textContent = 'Backend ulanmagan';
    statusEl.className = 'status error';
  }
}

async function loadSources() {
  try {
    const res = await fetch('/api/sources');
    const data = await res.json();
    sourcesEl.innerHTML = '';
    data.sources.forEach((source) => {
      const li = document.createElement('li');
      const num = source.document_number ? ` — ${source.document_number}` : '';
      const date = source.date ? ` (${source.date})` : '';
      li.textContent = `${source.title}${num}${date}`;
      sourcesEl.appendChild(li);
    });
  } catch (error) {
    sourcesEl.innerHTML = '<li>Manbalar yuklanmadi</li>';
  }
}

function renderAnswer(data) {
  const citationText = data.citations.map((c, idx) => {
    const ref = [c.title, c.document_number, c.date, c.section].filter(Boolean).join(', ');
    return `${idx + 1}. ${ref}\n   ${c.url || ''}`;
  }).join('\n');

  answerEl.classList.remove('hidden');
  answerEl.innerHTML = `<h3>Javob</h3>${escapeHtml(data.answer)}${citationText ? `\n\n<h3>Topilgan manbalar</h3>${escapeHtml(citationText)}` : ''}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionEl.value.trim();
  if (!question) return;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Javob tayyorlanmoqda...';
  answerEl.classList.remove('hidden');
  answerEl.textContent = 'Savolga mos manbalar qidirilmoqda...';

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, mode: modeEl.value }),
    });
    if (!res.ok) throw new Error('API xatosi');
    const data = await res.json();
    renderAnswer(data);
  } catch (error) {
    answerEl.textContent = 'Javob olishda xatolik yuz berdi. Backend ishga tushganini tekshiring.';
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Javob olish';
  }
});

quickPrompts.addEventListener('click', (event) => {
  if (event.target.tagName !== 'BUTTON') return;
  questionEl.value = event.target.textContent;
  questionEl.focus();
});

checkHealth();
loadSources();
