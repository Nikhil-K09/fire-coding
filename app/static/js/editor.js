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

langSelect.addEventListener('change', e => {
  editor.setOption('mode', langModes[e.target.value] || 'text/x-c++src');
  const current = editor.getValue().trim();
  const prevStarter = STARTER_MAP[langSelect.value] || '';
  if (!current || current === prevStarter) loadStarterFor(e.target.value);
});

// run code
async function runCode() {
  const payload = {
    code: editor.getValue(),
    lang: langSelect.value,
    problem_id: PROBLEM_ID
  };

  stdoutEl.textContent = '⚙️ Running...\n';

  try {
    const res = await fetch('/submit', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    let line = `Test Case Status: ${data.status}\n`;
    if (data.stdout) line += `Output:\n${data.stdout}\n`;
    //if (data.stderr) line += `Error:\n${data.stderr}\n`;

    stdoutEl.textContent = line;

  } catch(err) {
    stdoutEl.textContent = 'Error: ' + err.message;
  }
}

document.getElementById('run').addEventListener('click', runCode);
window.addEventListener('keydown', e => { if(e.ctrlKey && e.key === 'Enter') runCode(); });
