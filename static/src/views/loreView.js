import { fetchText, getLoreDocument, getLoreIndex, normalizeLoreHtml } from "../service.js";

export function createLoreViewController({
  sidebar,
  loreContent,
}) {
  let currentLoreType = null;
  let sectionMeta = [];
  let sectionMenus = new Map();
  let homeDocument = null;

  function validateHomeDocument(index) {
    if (!Array.isArray(index?.documents) || index.documents.length === 0) {
      throw new Error("Contrato invalido: lore/index.documents debe ser una lista no vacia");
    }

    const [first] = index.documents;
    if (!first || typeof first.slug !== "string" || !first.slug) {
      throw new Error("Contrato invalido: documents[0].slug es obligatorio");
    }

    if (typeof first.title !== "string" || !first.title) {
      throw new Error("Contrato invalido: documents[0].title es obligatorio");
    }

    return {
      slug: first.slug,
      title: first.title,
    };
  }

  function normalizeSections(index) {
    const sections = index?.sections;

    if (!sections || typeof sections !== "object") {
      throw new Error("Contrato invalido: lore/index.sections es obligatorio");
    }

    const normalized = Object.entries(sections).map(([key, value]) => {
      if (!Array.isArray(value) || value.length === 0) {
        throw new Error(`Contrato invalido: sections.${key} debe ser una lista no vacia`);
      }

      const documents = value.filter((item) => item && typeof item.slug === "string");
      if (documents.length !== value.length) {
        throw new Error(`Contrato invalido: sections.${key} contiene documentos sin slug`);
      }

      for (const item of documents) {
        if (typeof item.title !== "string" || !item.title) {
          throw new Error(`Contrato invalido: sections.${key} contiene documentos sin title`);
        }
      }

      const root = documents.find((item) => item.slug === key);
      if (!root) {
        throw new Error(`Contrato invalido: falta documento raiz ${key}.md en sections.${key}`);
      }

      if (!root.title || typeof root.title !== "string") {
        throw new Error(`Contrato invalido: falta title para sections.${key} (documento raiz)`);
      }

      return {
        key,
        title: root.title,
        rootSlug: root.slug,
        documents,
      };
    });

    if (!normalized.length) {
      throw new Error("Contrato invalido: sections no contiene secciones");
    }

    return normalized;
  }

  function createLoreMenuItem({ slug, title }, type) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "btn-ghost";
    btn.textContent = title;
    btn.addEventListener("click", () => {
      loadLoreDocument(type, slug, title);
    });
    li.appendChild(btn);
    return li;
  }

  function renderSidebar() {
    sidebar.innerHTML = "";
    sectionMenus = new Map();

    sectionMeta.forEach((section) => {
      const sectionNode = document.createElement("section");
      sectionNode.id = `${section.key}-menu`;
      sectionNode.className = "menu-section hidden";

      const heading = document.createElement("h3");
      const headingButton = document.createElement("button");
      headingButton.className = "btn-ghost";
      headingButton.textContent = section.title;
      headingButton.addEventListener("click", () => {
        loadLoreDocument(section.key, section.rootSlug, section.title);
      });
      heading.appendChild(headingButton);

      const list = document.createElement("ul");
      section.documents
        .filter((item) => item.slug !== section.rootSlug)
        .forEach((item) => {
          list.appendChild(createLoreMenuItem(item, section.key));
        });

      sectionNode.append(heading, list);
      sidebar.appendChild(sectionNode);
      sectionMenus.set(section.key, sectionNode);
    });
  }

  async function loadLoreIndex() {
    try {
      const index = await getLoreIndex();
      sectionMeta = normalizeSections(index);
      homeDocument = validateHomeDocument(index);
      renderSidebar();

      return {
        index,
        home: homeDocument,
        sections: sectionMeta.map((section) => ({
          key: section.key,
          title: section.title,
          rootSlug: section.rootSlug,
        })),
      };
    } catch (error) {
      sidebar.innerHTML = `<p>${error.message}</p>`;
      loreContent.innerHTML = `<p>${error.message}</p>`;
      throw error;
    }
  }

  function showSectionMenu(sectionKey) {
    let exists = false;
    sectionMenus.forEach((menu, key) => {
      const isCurrent = key === sectionKey;
      menu.classList.toggle("hidden", !isCurrent);
      exists = exists || isCurrent;
    });
    return exists;
  }

  async function loadSectionRoot(sectionKey) {
    const section = sectionMeta.find((item) => item.key === sectionKey);
    if (!section) {
      throw new Error(`Contrato invalido: seccion no registrada ${sectionKey}`);
    }
    await loadLoreDocument(section.key, section.rootSlug, section.title);
  }

  async function loadSectionDocument(sectionKey, slug) {
    const section = sectionMeta.find((item) => item.key === sectionKey);
    if (!section) {
      throw new Error(`Contrato invalido: seccion no registrada ${sectionKey}`);
    }
    const document = section.documents.find((item) => item.slug === slug);
    if (!document) {
      throw new Error(`Contrato invalido: documento no encontrado ${sectionKey}/${slug}`);
    }
    await loadLoreDocument(section.key, slug, document.title);
  }

  async function loadHomeIntro() {
    currentLoreType = null;
    loreContent.innerHTML = "<p>Cargando documento...</p>";

    try {
      if (!homeDocument) {
        throw new Error("Contrato invalido: documento home no cargado");
      }

      const html = await fetchText(`/lore/${homeDocument.slug}`);
      loreContent.innerHTML = normalizeLoreHtml(html);
      document.title = `Koten | ${homeDocument.title}`;
    } catch (error) {
      loreContent.innerHTML = `<p>${error.message}</p>`;
    }
  }

  async function loadLoreDocument(type, slug, title) {
    try {
      currentLoreType = type;
      loreContent.innerHTML = "<p>Cargando documento...</p>";
      const html = await getLoreDocument(type, slug);
      loreContent.innerHTML = normalizeLoreHtml(html);
      document.title = `Koten | ${title}`;
    } catch (error) {
      loreContent.innerHTML = `<p>${error.message}</p>`;
    }
  }

  function findLoreDocumentByTypeAndSlug(type, slug) {
    if (!type) return null;
    const section = sectionMeta.find((item) => item.key === type);
    if (!section) return null;
    const match = section.documents.find((item) => item.slug === slug);
    if (!match) return null;
    return { type: section.key, title: match.title, slug };
  }

  function parseMarkdownLink(href) {
    const cleanHref = href.split("#")[0].split("?")[0].trim();
    if (!cleanHref || !cleanHref.endsWith(".md")) return null;

    const parts = cleanHref.split("/").filter(Boolean);
    const file = parts[parts.length - 1];
    const slug = file.replace(/\.md$/i, "");
    if (!slug) return null;

    if (parts.length > 1) {
      return { type: parts[0], slug };
    }

    if (!currentLoreType) {
      return null;
    }

    return { type: currentLoreType, slug };
  }

  function interceptMarkdownLinks(onNavigate) {
    loreContent.addEventListener("click", async (event) => {
      const link = event.target.closest("a");

      if (!link) {
        return;
      }

      const href = link.getAttribute("href") || "";
      const target = parseMarkdownLink(href);

      if (!target) {
        return;
      }

      event.preventDefault();

      if (onNavigate) {
        onNavigate(target.type, target.slug);
        return;
      }

      const fromIndex = findLoreDocumentByTypeAndSlug(target.type, target.slug);
      if (!fromIndex) {
        loreContent.innerHTML = `<p>No se pudo resolver el enlace: ${href}</p>`;
        return;
      }

      await loadLoreDocument(fromIndex.type, target.slug, fromIndex.title);
    });
  }

  return {
    loadLoreIndex,
    loadHomeIntro,
    loadLoreDocument,
    loadSectionRoot,
    loadSectionDocument,
    showSectionMenu,
    interceptMarkdownLinks,
  };
}
