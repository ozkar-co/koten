import { createLexiconViewController } from "./views/lexiconView.js";
import { createLoreViewController } from "./views/loreView.js";
import { createToolsViewController } from "./views/toolsView.js";
import { getLexiconLanguages } from "./service.js";

const siteNav      = document.getElementById("site-nav");
const sidebar      = document.getElementById("sidebar");
const loreContent  = document.getElementById("lore-content");
const loreView     = document.getElementById("lore-view");
const lexiconView  = document.getElementById("lexicon-view");
const toolsView    = document.getElementById("tools-view");

let loreViewController;
let lexiconViewController;
let toolsViewController;
let sectionTargets = [];
let homeDocument = null;

function getImageName(src) {
  try {
    const url = new URL(src, window.location.href);
    const pathParts = url.pathname.split("/").filter(Boolean);
    return decodeURIComponent(pathParts[pathParts.length - 1] || "imagen");
  } catch {
    return "imagen";
  }
}

function resolveFullImageSrc(src) {
  try {
    const url = new URL(src, window.location.href);
    url.pathname = url.pathname.replace(/_thumb(?=\.[^/.]+$|$)/, "");
    url.searchParams.delete("small");
    return url.toString();
  } catch {
    return src
      .replace(/_thumb(?=\.[^/.]+$|$)/, "")
      .replace(/[?&]small(?:=[^&]*)?(?=&|$)/, "")
      .replace(/[?&]$/, "");
  }
}

function openImageModal(src, alt = "") {
  const fullSrc = resolveFullImageSrc(src);
  const modal = document.createElement("div");
  modal.className = "image-modal";

  const content = document.createElement("div");
  content.className = "image-modal-content";

  const fullImage = document.createElement("img");
  fullImage.src = fullSrc;
  fullImage.alt = alt;

  const caption = document.createElement("p");
  caption.className = "image-modal-caption";
  caption.textContent = getImageName(fullSrc);

  content.append(fullImage, caption);
  modal.appendChild(content);

  modal.addEventListener("click", () => modal.remove());
  content.addEventListener("click", (event) => event.stopPropagation());

  document.body.appendChild(modal);
}

function initGlobalImageModal() {
  document.addEventListener("click", (event) => {
    const image = event.target.closest("img");
    if (!image || image.closest(".image-modal")) return;
    openImageModal(image.currentSrc || image.src, image.alt || "");
  });
}

function createTopNavButton(target, label, isActive = false) {
  const button = document.createElement("button");
  button.className = `btn btn-pill site-nav-btn${isActive ? " btn-active" : ""}`;
  button.dataset.target = target;
  button.textContent = label;
  return button;
}

function renderTopNavigation(sections) {
  sectionTargets = sections.map((section) => section.key);

  siteNav.querySelectorAll("button.site-nav-btn").forEach((button) => button.remove());

  const loginLink = siteNav.querySelector('a[href="/admin/login"]');
  const nodes = [
    createTopNavButton("home", homeDocument.title, true),
    ...sections.map((section) => createTopNavButton(section.key, section.title)),
    createTopNavButton("lexicon", "Lexicon"),
    createTopNavButton("tools", "Tools"),
  ];

  nodes.forEach((node) => {
    siteNav.insertBefore(node, loginLink || null);
  });
}

function setActiveTopMenu(target) {
  siteNav.querySelectorAll("button.site-nav-btn").forEach((btn) =>
    btn.classList.toggle("btn-active", btn.dataset.target === target)
  );
}

function currentRoute() {
  return window.location.pathname.split("/").filter(Boolean);
}

function navigateTo(path) {
  history.pushState({}, "", path);
  renderRoute();
}

function showOnly(view) {
  sidebar.classList.add("hidden");
  loreView.classList.toggle("hidden", view !== "lore");
  lexiconView.classList.toggle("hidden", view !== "lexicon");
  toolsView.classList.toggle("hidden", view !== "tools");
}

async function renderHome() {
  setActiveTopMenu("home");
  showOnly("lore");
  loreViewController.showSectionMenu("");
  await loreViewController.loadHomeIntro();
}

async function renderLexicon() {
  setActiveTopMenu("lexicon");
  showOnly("lexicon");
}

async function renderTools() {
  setActiveTopMenu("tools");
  showOnly("tools");
}

async function renderSection(section, slug) {
  if (!sectionTargets.includes(section)) {
    renderNotFound();
    return;
  }

  setActiveTopMenu(section);
  showOnly("lore");
  sidebar.classList.remove("hidden");
  loreViewController.showSectionMenu(section);

  if (slug) {
    await loreViewController.loadSectionDocument(section, slug);
  } else {
    await loreViewController.loadSectionRoot(section);
  }
}

function renderNotFound() {
  setActiveTopMenu("");
  showOnly("lore");
  loreContent.innerHTML = "<p>No se encontro la ruta.</p>";
}

async function renderRoute() {
  const parts = currentRoute();

  if (parts.length === 0) {
    await renderHome();
    return;
  }

  const [first, second] = parts;

  if (first === "lexicon") {
    await renderLexicon();
    return;
  }

  if (first === "tools") {
    await renderTools();
    return;
  }

  await renderSection(first, second);
}

function initNavigation() {
  siteNav.addEventListener("click", (event) => {
    const button = event.target.closest("button.site-nav-btn");
    if (!button) return;

    const target = button.dataset.target;
    if (target === "home") navigateTo("/");
    else navigateTo(`/${target}`);
  });

  window.addEventListener("popstate", renderRoute);
}

async function bootstrap() {
  loreViewController = createLoreViewController({ sidebar, loreContent });
  initNavigation();
  initGlobalImageModal();
  loreViewController.interceptMarkdownLinks((type, slug) => navigateTo(`/${type}/${slug}`));

  const loreIndex = await loreViewController.loadLoreIndex();
  homeDocument = loreIndex.home;
  renderTopNavigation(loreIndex.sections);

  const lexiconLanguages = await getLexiconLanguages();
  lexiconViewController = createLexiconViewController(lexiconView, lexiconLanguages);
  toolsViewController = createToolsViewController(toolsView, lexiconLanguages);

  await renderRoute();
}

bootstrap();
