const langModes = {
  '54': 'text/x-c++src',   // C++
  '71': 'python',          // Python
  '62': 'text/x-java',     // Java
  '50': 'text/x-csrc',     // C
  '51': 'text/x-csharp',   // C#
  '46': 'shell'            // Bash
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

// load starter code for selected language
function loadStarterFor(langId) {
  editor.setValue(STARTER_MAP[langId] || '');
}
loadStarterFor(langSelect.value);

// language switch handler
langSelect.addEventListener('change', e => {
  const newLang = e.target.value;
  editor.setOption('mode', langModes[newLang] || 'text/x-c++src');

  const current = editor.getValue().trim();
  const prevStarter = STARTER_MAP[langSelect.value] || '';
  const newStarter = STARTER_MAP[newLang] || '';

  // only replace code if it's still default / empty
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

  stdoutEl.textContent = '⚙️ Running...\n';
  stdoutEl.classList.remove("accepted", "rejected");

  try {
    const res = await fetch('/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    stdoutEl.textContent = ""; // clear previous

    switch (data.status) {
      case "Accepted":
        stdoutEl.textContent = "✅ Accepted";
        stdoutEl.classList.add("accepted");
        break;

      case "Rejected":
        let rejMsg = "❌ Rejected\n";
        if (data.stdout) rejMsg += `Your Output:\n${data.stdout}\n`;
        if (data.expected) rejMsg += `Expected Output:\n${data.expected}\n`;
        stdoutEl.textContent = rejMsg;
        stdoutEl.classList.add("rejected");
        break;

      case "Error":
        let errMsg = "⚠️ Error\n";
        if (data.error) errMsg += `${data.error}\n`;
        if (data.stderr) errMsg += `${data.stderr}\n`;
        stdoutEl.textContent = errMsg;
        stdoutEl.classList.add("rejected");
        break;

      default:
        stdoutEl.textContent = "⚠️ Unknown response from server.";
        stdoutEl.classList.add("rejected");
        break;
    }

  } catch (err) {
    stdoutEl.textContent = '⚠️ Request Failed: ' + err.message;
    stdoutEl.classList.add("rejected");
  }
}

document.getElementById('run').addEventListener('click', runCode);
