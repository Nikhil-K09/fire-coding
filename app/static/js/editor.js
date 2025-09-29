const langModes = {
  '54': 'text/x-c++src',   // C++
  '71': 'python',          // Python
  '62': 'text/x-java',     // Java
  '50': 'text/x-csrc',     // C
  '51': 'text/x-csharp',   // C#
  '46': 'shell'            // Bash
};

const langSelect = document.getElementById('lang');
const textarea = document.getElementById('editor');

let editor = CodeMirror.fromTextArea(textarea, {
  lineNumbers: true,
  mode: langModes[langSelect.value] || 'text/x-c++src',
  theme: 'material',
  indentUnit: 4,
  tabSize: 4,
  matchBrackets: true,
  autoCloseBrackets: true,
  extraKeys: { "Ctrl-Enter": () => runCode() }
});

// load starter code
function loadStarterFor(langId) {
  editor.setValue(STARTER_MAP[langId] || '');
}
loadStarterFor(langSelect.value);

// switch language
langSelect.addEventListener('change', e => {
  const newLang = e.target.value;
  editor.setOption('mode', langModes[newLang] || 'text/x-c++src');

  const current = editor.getValue().trim();
  const prevStarter = STARTER_MAP[langSelect.value] || '';
  const newStarter = STARTER_MAP[newLang] || '';

  if (!current || current === prevStarter) {
    loadStarterFor(newLang);
  }
});

// run code
async function runCode() {
  const payload = {
    code: editor.getValue(),
    lang: langSelect.value,
    problem_id: PROBLEM_ID
  };

  // UI refs
  const resultBox = document.getElementById('result-box');
  const outputEl = document.getElementById('output');
  const errorBox = document.getElementById('error-box');

  // reset UI
  resultBox.style.display = 'none';
  resultBox.className = 'result-box';
  resultBox.textContent = '';
  outputEl.textContent = '⚙️ Running...';
  outputEl.classList.remove('accepted', 'rejected');
  errorBox.style.display = 'none';
  errorBox.textContent = '';

  try {
    const res = await fetch('/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.status === 'Error') {
      errorBox.style.display = 'block';
      errorBox.textContent =
        data.compile_output || data.stderr || data.error || 'Unknown error';

      outputEl.textContent =
        (data.stdout && data.stdout.trim()) ? `Output:\n${data.stdout}` : '';
      outputEl.classList.add('rejected');
      return;
    }

    if (data.status === 'Accepted') {
      resultBox.style.display = 'block';
      resultBox.classList.add('accepted');
      resultBox.textContent = 'Accepted';

      outputEl.textContent = data.stdout || '(no output)';
      return;
    }

    if (data.status === 'Rejected') {
      resultBox.style.display = 'block';
      resultBox.classList.add('rejected');
      resultBox.textContent = 'Rejected';

      let html = '';
      if (data.stdout) html += `Your Output:\n${data.stdout}\n\n`;
      if (data.expected) html += `Expected Output:\n${data.expected}\n\n`;
      outputEl.textContent = html || '(no output)';
      return;
    }

    // fallback
    resultBox.style.display = 'block';
    resultBox.classList.add('rejected');
    resultBox.textContent = 'Unknown response from server';

  } catch (err) {
    errorBox.style.display = 'block';
    errorBox.textContent = err.message || String(err);

    resultBox.style.display = 'block';
    resultBox.classList.add('rejected');
    resultBox.textContent = 'Request Failed';
  }
}

document.getElementById('run').addEventListener('click', runCode);
