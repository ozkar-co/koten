import { analyzeLexiconWord, getRootDetail, getWordImageUrl } from "../service.js";

function renderAnalysisCard(data, rootDetailsMap) {
  const roots = data.roots || [];

  if (!roots.length) {
    return "<p>No se encontraron raices.</p>";
  }

  const rows = roots
    .map((root) => {
      const lapagRoots = root.lapag_roots || [];
      const details = lapagRoots
        .map((r) => rootDetailsMap.get(r))
        .filter(Boolean)
        .map((detail) => {
          const equivalents = (detail.equivalents || [])
            .map((eq) => `${eq.language_code}: ${eq.language_root}`)
            .join(" | ");

          return `<div><strong>${detail.lapag_root}</strong>: ${detail.meaning || "sin significado"}<br><small>${equivalents}</small></div>`;
        })
        .join("");

      return `
        <div class="root-item">
          <div><strong>Fragmento:</strong> ${root.source_root}</div>
          <div><strong>Raices lapag:</strong> ${lapagRoots.join(", ") || "-"}</div>
          ${details || ""}
        </div>
      `;
    })
    .join("");

  return `
    <div>
      <div><strong>Palabra:</strong> ${data.word}</div>
      <div><strong>Normalizada:</strong> ${data.normalized_word || data.word}</div>
      <div><strong>Idioma:</strong> ${data.language_code}</div>
      ${rows}
    </div>
  `;
}

export function createLexiconViewController(container, languages) {
  container.innerHTML = "";

  // Build DOM
  const select = document.createElement("select");
  select.id = "language";
  select.required = true;
  languages.forEach((language) => {
    const code = language.code;
    const name = language.name;
    if (!code) return;
    const opt = document.createElement("option");
    opt.value = code;
    opt.textContent = name || code;
    select.appendChild(opt);
  });

  const wordInput = document.createElement("input");
  wordInput.type = "text";
  wordInput.id = "word";
  wordInput.placeholder = "kamama";
  wordInput.minLength = 1;
  wordInput.required = true;

  const submitBtn = document.createElement("button");
  submitBtn.className = "btn btn-pill";
  submitBtn.type = "submit";
  submitBtn.textContent = "Analizar";

  const form = document.createElement("form");
  form.id = "analyze-form";
  form.className = "tool-form";

  const langLabel = document.createElement("label");
  langLabel.textContent = "Idioma";
  langLabel.appendChild(select);

  const wordLabel = document.createElement("label");
  wordLabel.textContent = "Palabra";
  wordLabel.appendChild(wordInput);

  form.append(langLabel, wordLabel, submitBtn);

  const wordImage = document.createElement("img");
  wordImage.id = "word-image";
  wordImage.alt = "Render de palabra";
  wordImage.style.cursor = "pointer";
  wordImage.title = "Ver en tamaño completo";

  const analysisOutput = document.createElement("div");
  analysisOutput.id = "analysis-output";
  analysisOutput.className = "analysis-output empty";
  analysisOutput.textContent = "Ejecuta un analisis para ver resultados.";

  const renderBox = document.createElement("div");
  renderBox.className = "panel";
  renderBox.innerHTML = "<h3>Render</h3>";
  renderBox.appendChild(wordImage);

  const analysisBox = document.createElement("div");
  analysisBox.className = "panel";
  analysisBox.innerHTML = "<h3>Analisis</h3>";
  analysisBox.appendChild(analysisOutput);

  const results = document.createElement("section");
  results.className = "results";
  results.append(renderBox, analysisBox);

  container.append(form, results);

  // Logic
  async function analyzeWord(event) {
    event.preventDefault();
    const language = select.value;
    const word = wordInput.value.trim();
    if (!word) return;

    analysisOutput.classList.remove("empty");
    analysisOutput.textContent = "Analizando...";
    wordImage.src = getWordImageUrl(language, word);

    try {
      const analysis = await analyzeLexiconWord(language, word);
      const uniqueRoots = [
        ...new Set(
          (analysis.roots || []).flatMap((r) =>
            (r.lapag_roots || []).filter((root) => typeof root === "string")
          )
        ),
      ];
      const rootResponses = await Promise.all(
        uniqueRoots.map(async (root) => {
          try { return [root, await getRootDetail(root)]; }
          catch { return [root, null]; }
        })
      );
      analysisOutput.innerHTML = renderAnalysisCard(analysis, new Map(rootResponses));
    } catch (error) {
      analysisOutput.textContent = `No se pudo analizar: ${error.message}`;
    }
  }

  form.addEventListener("submit", analyzeWord);

  return {};
}
