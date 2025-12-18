const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const ingestResult = document.getElementById('ingestResult');
const indexBtn = document.getElementById('indexBtn');
const docIdsInput = document.getElementById('docIds');
const indexResult = document.getElementById('indexResult');
const queryBtn = document.getElementById('queryBtn');
const questionInput = document.getElementById('question');
const answerDiv = document.getElementById('answer');
const contextsDiv = document.getElementById('contexts');
const generateBtn = document.getElementById('generateBtn');
const generatePrompt = document.getElementById('generatePrompt');
const generationDiv = document.getElementById('generation');

uploadBtn.onclick = async () => {
  const files = fileInput.files;
  const form = new FormData();
  for (const f of files) form.append('files', f);
  const res = await fetch(`${apiBase}/ingest`, { method: 'POST', body: form });
  const data = await res.json();
  ingestResult.textContent = JSON.stringify(data.ingested, null, 2);
};

indexBtn.onclick = async () => {
  const docIds = docIdsInput.value.split(',').map((d) => d.trim()).filter(Boolean);
  const form = new FormData();
  docIds.forEach((id) => form.append('document_ids', id));
  const res = await fetch(`${apiBase}/index`, { method: 'POST', body: form });
  const data = await res.json();
  indexResult.textContent = JSON.stringify(data.indexed, null, 2);
};

queryBtn.onclick = async () => {
  const form = new FormData();
  form.append('question', questionInput.value);
  const res = await fetch(`${apiBase}/query`, { method: 'POST', body: form });
  const data = await res.json();
  answerDiv.textContent = data.answer;
  renderContexts(data.contexts);
};

generateBtn.onclick = async () => {
  const form = new FormData();
  form.append('prompt', generatePrompt.value);
  const res = await fetch(`${apiBase}/generate`, { method: 'POST', body: form });
  const data = await res.json();
  generationDiv.textContent = data.output;
  renderContexts(data.contexts);
};

function renderContexts(contexts) {
  contextsDiv.innerHTML = '';
  contexts.forEach((c) => {
    const div = document.createElement('div');
    div.className = 'context';
    div.innerHTML = `<strong>${c.document_id}</strong> (score ${c.score?.toFixed(3)}): ${c.text}`;
    contextsDiv.appendChild(div);
  });
}
