export const API_BASE = "";

export function normalizeLoreHtml(html) {
  return html
    .replace(/src="\/image\/([^"]+)\.[^".]+"/g, 'src="/image/$1_thumb"');
}

export async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    let detail = `Error ${response.status}`;

    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      // Keep fallback message.
    }

    throw new Error(detail);
  }

  return response.json();
}

export async function fetchText(path) {
  const response = await fetch(`${API_BASE}${path}`);

  if (!response.ok) {
    throw new Error(`No se pudo cargar: ${path}`);
  }

  return response.text();
}

export function getWordImageUrl(language, word, { small = false } = {}) {
  const base = `${API_BASE}/word/${encodeURIComponent(language)}/${encodeURIComponent(word)}`;
  return small ? `${base}?small=true` : base;
}

export async function getLoreIndex() {
  return fetchJson("/lore/index");
}

export async function getLoreDocument(type, slug) {
  return fetchText(`/lore/${type}/${slug}`);
}

export function loreRoute(type, slug) {
  return !slug || slug === type ? `/${type}` : `/${type}/${slug}`;
}

export async function renderMarkdown(text) {
  const response = await fetch(`${API_BASE}/lore/render`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error("No se pudo renderizar el texto");
  }

  return response.text();
}

export async function analyzeLexiconWord(language, word) {
  return fetchJson("/lexicon/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language_code: language, word }),
  });
}

export async function getRootDetail(root) {
  return fetchJson(`/lexicon/roots/${encodeURIComponent(root)}`);
}

export async function getLexiconLanguages() {
  let payload = null;

  try {
    payload = await fetchJson("/lexicon/languages");
  } catch {
    return [];
  }

  const list = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.languages)
      ? payload.languages
      : Array.isArray(payload?.data)
        ? payload.data
        : [];

  return list
    .map((language) => ({
      code: language.code || language.slug || "",
      name: language.name || language.title || language.code || language.slug || "",
      prefix: language.prefix || "",
    }))
    .filter((language) => language.code && !/^lang(?:\/lang)?$/i.test(language.code));
}
