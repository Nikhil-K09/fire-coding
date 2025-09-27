// editor.js
const langModes = {
  '54': 'text/x-c++src',
  '71': 'python',
  '62': 'text/x-java',
  '50': 'text/x-csrc',
  '51': 'text/x-csharp',
  '46': 'shell'
};

const langSelect = document.getElementById('lang');
const stdoutEl = document.getElementById('output');
const stdinEl = document.getElementById('stdin');
const expectedEl = document.getElementById('expected_output');

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

// Load starter code
function loadStarterFor(langId) {
  if (STARTER_MAP && STARTER_MAP[langId]) {
    editor.setValue(STARTER_MAP[langId]);
  } else {
    editor.setValue('');
  }
}
loadStarterFor(langSelect.value);

langSelect.addEventListener('change', (e) => {
  editor.setOption('mode', langModes[e.target.value] || 'text/x-c++src');
  const current = editor.getValue().trim();
  const prevStarter = STARTER_MAP[langSelect.value] || '';
  if (!current || current === prevStarter) loadStarterFor(e.target.value);
});

// Run / Submit code
async function runCode() {
  const payload = {
    code: editor.getValue(),
    lang: langSelect.value,
    input: stdinEl.value || '',
    expected_output: expectedEl.value || '',
    problem_id: PROBLEM_ID
  };

  stdoutEl.textContent = '⚙️ Running...';

  try {
    const res = await fetch('/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    let outputText = `Status: ${data.status || 'Unknown'}\n\n`;
    if (data.output) outputText += data.output;
    stdoutEl.textContent = outputText || 'No output';
  } catch (err) {
    stdoutEl.textContent = 'Error: ' + err.message;
  }
}

document.getElementById('run').addEventListener('click', runCode);
window.addEventListener('keydown', (e) => { if (e.ctrlKey && e.key === 'Enter') runCode(); });
