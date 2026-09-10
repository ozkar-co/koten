import { getWordImageUrl, renderMarkdown } from "../service.js";

function createPanel(title) {
  const box = document.createElement("section");
  box.className = "panel";
  const heading = document.createElement("h3");
  heading.textContent = title;
  box.appendChild(heading);
  return box;
}

export function createToolsViewController(container, languages) {
  container.innerHTML = "";

  // --- Tool 1: symbol image creation ---
  const imageBox = createPanel("Crear imagen (simbolos)");

  const langSelect = document.createElement("select");
  languages.forEach((language) => {
    if (!language.code) return;
    const opt = document.createElement("option");
    opt.value = language.code;
    opt.textContent = language.name || language.code;
    langSelect.appendChild(opt);
  });

  const wordInput = document.createElement("input");
  wordInput.type = "text";
  wordInput.placeholder = "palabra";
  wordInput.minLength = 1;

  const generateBtn = document.createElement("button");
  generateBtn.type = "submit";
  generateBtn.className = "btn btn-pill";
  generateBtn.textContent = "Generar";

  const imageForm = document.createElement("form");
  imageForm.className = "tool-form";

  const langLabel = document.createElement("label");
  langLabel.textContent = "Idioma";
  langLabel.appendChild(langSelect);

  const wordLabel = document.createElement("label");
  wordLabel.textContent = "Palabra";
  wordLabel.appendChild(wordInput);

  imageForm.append(langLabel, wordLabel, generateBtn);

  const preview = document.createElement("img");
  preview.id = "tools-image";
  preview.alt = "Imagen generada";

  imageBox.append(imageForm, preview);

  imageForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const word = wordInput.value.trim();
    if (!word) return;
    preview.src = getWordImageUrl(langSelect.value, word);
  });

  // --- Tool 2: Markdown → HTML transformation ---
  const transformBox = createPanel("Transformar Markdown a HTML");

  const mdInput = document.createElement("textarea");
  mdInput.placeholder = "/lapag/  ...";
  mdInput.rows = 6;

  const renderBtn = document.createElement("button");
  renderBtn.type = "submit";
  renderBtn.className = "btn btn-pill";
  renderBtn.textContent = "Renderizar";

  const transformForm = document.createElement("form");
  transformForm.className = "tool-stack";
  transformForm.append(mdInput, renderBtn);

  const previewHtml = document.createElement("div");
  previewHtml.className = "lore-content";

  transformBox.append(transformForm, previewHtml);

  transformForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = mdInput.value;
    if (!text.trim()) return;

    try {
      previewHtml.innerHTML = await renderMarkdown(text);
    } catch (error) {
      previewHtml.innerHTML = `<p>${error.message}</p>`;
    }
  });

  container.append(imageBox, transformBox);

  return {};
}
