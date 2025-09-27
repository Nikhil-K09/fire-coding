const langModes = {
  '54': 'text/x-c++src',  // C++
  '71': 'python',         // Python 3
  '62': 'text/x-java',    // Java
  '50': 'text/x-csrc',    // C
  '51': 'text/x-csharp',  // C#
  '46': 'shell'           // Bash
};

const langSelect = document.getElementById('lang');
const stdoutEl = document.getElementById('output');
const stdinEl = document.getElementById('stdin');
const expectedEl = document.getElementById('expected_output');

// init CodeMirror
const textarea = document.getElementById('editor');
let editor = CodeMirror.fromTextArea(textarea, {
  lineNumbers: true,
  mode: langModes[langSelect.value] || 'text/x-c++src',
  theme: 'material',
  indentUnit: 4,
  tabSize: 4,
  matchBrackets: true,       // highlight matching brackets
  autoCloseBrackets: true,    // auto-close (), {}, [], ""
  extraKeys: {
    "Ctrl-Enter": () => runCode()
  }
});

// load starter code depending on language
function loadStarterFor(langId) {
  if (STARTER_MAP && STARTER_MAP[langId]) {
    editor.setValue(STARTER_MAP[langId]);
  } else {
    editor.setValue('');
  }
}

// initial load
loadStarterFor(langSelect.value);

langSelect.addEventListener('change', (e) => {
  const mode = langModes[e.target.value] || 'text/x-c++src';
  editor.setOption('mode', mode);

  // only auto-load starter if editor is empty or equals previous starter
  const currentValue = editor.getValue().trim();
  const prevStarter = STARTER_MAP[langSelect.value] || '';
  if (!currentValue || currentValue === prevStarter) {
    loadStarterFor(e.target.value);
  }
});

// run / submit
async function runCode() {
  const payload = {
    code: editor.getValue(),
    lang: langSelect.value,
    input: stdinEl.value || '',
    expected_output: expectedEl.value || '',
    problem_id: PROBLEM_ID
  };

  stdoutEl.textContent = '⚙️ Submitting...';
  try {
    const res = await fetch('/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    // display result: prefer stdout, then compile_output, then stderr
    let out = '';
    const status = (data.status && data.status.description) ? data.status.description : '';

    if (data.compile_output) out += `Compile output:\n${data.compile_output}\n\n`;
    if (data.stdout) out += `Stdout:\n${data.stdout}\n\n`;
    if (data.stderr) out += `Stderr:\n${data.stderr}\n\n`;
    if (!out) out = JSON.stringify(data, null, 2);

    stdoutEl.textContent = `Status: ${status}\n\n` + out;
  } catch (err) {
    stdoutEl.textContent = 'Error: ' + err.message;
  }
}

// run on button
document.getElementById('run').addEventListener('click', runCode);

// Ctrl+Enter to run
window.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') runCode();
});
