const handle = document.getElementById("drag-handle");
const problemPanel = document.getElementById("problem-panel");
const editorPanel = document.getElementById("editor-panel");

let isDragging = false;

handle.addEventListener("mousedown", () => {
  isDragging = true;
  document.body.style.cursor = "ew-resize";
});

document.addEventListener("mousemove", (e) => {
  if (!isDragging) return;
  const offset = e.pageX;
  const minWidth = 200;
  const maxWidth = 700;
  if (offset > minWidth && offset < maxWidth) {
    problemPanel.style.width = offset + "px";
  }
});

document.addEventListener("mouseup", () => {
  isDragging = false;
  document.body.style.cursor = "default";
});
