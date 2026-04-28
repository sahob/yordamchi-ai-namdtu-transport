const statusEl = document.getElementById('status');
const sourcesEl = document.getElementById('sources');
const answerEl = document.getElementById('answer');
const form = document.getElementById('askForm');
const questionEl = document.getElementById('question');
const modeEl = document.getElementById('mode');
const submitBtn = document.getElementById('submitBtn');
const quickPrompts = document.getElementById('quickPrompts');
const chunkCountEl = document.getElementById('chunkCount');
const vectorStatusEl = document.getElementById('vectorStatus');

async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    statusEl.textContent = `Ishlamoqda · ${data.chunks} bo‘lak`;
    statusEl.className = 'status ok';
    chunkCountEl.textContent = data.chunks ?? '—';
    vectorStatusEl.textContent = data.vector?.available ? 'Vector' : 'Keyword';
  } catch (error) {
    statusEl.textContent = 'Backend ulanmagan';
    statusEl.className = 'status error';
    chunkCountEl.textContent = '—';
    vectorStatusEl.textContent = 'Xato';
  }
}

async function loadSources() {
  try {
    const res = await fetch('/api/sources');
    const data = await res.json();
    sourcesEl.innerHTML = '';
    data.sources.forEach((source) => {
      const li = document.createElement('li');
      const title = document.createElement('strong');
      title.textContent = source.title || 'Nomsiz manba';
      const meta = document.createElement('small');
      const details = [source.document_number, source.date, source.status].filter(Boolean).join(' · ');
      meta.textContent = details || 'Ma’lumot kiritilmagan';
      li.append(title, meta);
      sourcesEl.appendChild(li);
    });
  } catch (error) {
    sourcesEl.innerHTML = '<li>Manbalar yuklanmadi</li>';
  }
}

function renderAnswer(data) {
  answerEl.classList.remove('hidden');
  answerEl.innerHTML = '';

  const title = document.createElement('h3');
  title.textContent = 'Javob';
  const text = document.createElement('div');
  text.className = 'answer__text';
  text.textContent = data.answer || 'Javob qaytmadi.';
  answerEl.append(title, text);

  if (data.citations && data.citations.length) {
    const sourceWrap = document.createElement('div');
    sourceWrap.className = 'answer__sources';
    const sourceTitle = document.createElement('h3');
    sourceTitle.textContent = 'Topilgan manbalar';
    sourceWrap.appendChild(sourceTitle);

    data.citations.forEach((c, idx) => {
      const card = document.createElement('div');
      card.className = 'source-card';

      const name = document.createElement('strong');
      name.textContent = `${idx + 1}. ${c.title || 'Manba'}`;

      const meta = document.createElement('span');
      const ref = [c.document_number, c.date, c.section].filter(Boolean).join(' · ');
      meta.textContent = ref || 'Qo‘shimcha ma’lumot yo‘q';

      card.append(name, meta);
      if (c.url) {
        const link = document.createElement('a');
        link.href = c.url;
        link.target = '_blank';
        link.rel = 'noopener';
        link.textContent = c.url;
        card.appendChild(link);
      }
      sourceWrap.appendChild(card);
    });
    answerEl.appendChild(sourceWrap);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionEl.value.trim();
  if (!question) return;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Javob tayyorlanmoqda...';
  answerEl.classList.remove('hidden');
  answerEl.textContent = 'Savolga mos normativ-huquqiy manbalar qidirilmoqda...';

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
    answerEl.textContent = 'Javob olishda xatolik yuz berdi. Backend ishga tushganini, .env sozlamalarini va API billing holatini tekshiring.';
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
