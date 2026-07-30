(() => {
  "use strict";

  const baseDatabase = window.AI_VIDEO_PROMPT_DB;
  if (!baseDatabase || !Array.isArray(baseDatabase.prompts)) {
    document.getElementById("app").style.display = "none";
    document.getElementById("fatal").style.display = "grid";
    return;
  }

  const STORAGE_DB = "ai-video-prompt-library";
  const STORAGE_STORE = "state";
  const STORAGE_KEY = "catalog";
  const FALLBACK_KEY = "ai-video-prompt-library-catalog";
  const ALL = "全部";
  const DEFAULT_COLLECTION = "未归档";
  const MEDIA_ALL = "all";
  const MEDIA_VIDEO = "video";
  const MEDIA_IMAGE = "image";
  const colors = ["violet", "amber", "cyan", "rose"];

  const state = {
    catalog: null,
    query: "",
    category: ALL,
    ratio: ALL,
    collection: ALL,
    mediaType: MEDIA_ALL,
    manageMediaType: MEDIA_VIDEO,
    exportMediaType: MEDIA_VIDEO,
    assignNewCollectionToEditor: false,
    selectedId: null,
    tab: "prompt",
  };

  const el = {
    search: document.getElementById("search"),
    clearSearch: document.getElementById("clearSearch"),
    category: document.getElementById("category"),
    ratio: document.getElementById("ratio"),
    collection: document.getElementById("collection"),
    clearFilters: document.getElementById("clearFilters"),
    resultCount: document.getElementById("resultCount"),
    promptList: document.getElementById("promptList"),
    detail: document.getElementById("detail"),
    topStats: document.getElementById("topStats"),
    toast: document.getElementById("toast"),
    exportButton: document.getElementById("exportButton"),
    openImportButton: document.getElementById("openImportButton"),
    exportImageButton: document.getElementById("exportImageButton"),
    openImageImportButton: document.getElementById("openImageImportButton"),
    mediaFilterButtons: [...document.querySelectorAll("[data-media-filter]")],
    modal: document.getElementById("manageModal"),
    closeModal: document.getElementById("closeModal"),
    importPane: document.getElementById("importPane"),
    editPane: document.getElementById("editPane"),
    fileInput: document.getElementById("fileInput"),
    dropZone: document.getElementById("dropZone"),
    autoClassify: document.getElementById("autoClassify"),
    skipDuplicates: document.getElementById("skipDuplicates"),
    importSummary: document.getElementById("importSummary"),
    promptForm: document.getElementById("promptForm"),
    editId: document.getElementById("editId"),
    editMediaType: document.getElementById("editMediaType"),
    editTitle: document.getElementById("editTitle"),
    editCategory: document.getElementById("editCategory"),
    editCollection: document.getElementById("editCollection"),
    editRatio: document.getElementById("editRatio"),
    editDuration: document.getElementById("editDuration"),
    durationField: document.getElementById("durationField"),
    editTags: document.getElementById("editTags"),
    editPrompt: document.getElementById("editPrompt"),
    editNegative: document.getElementById("editNegative"),
    autoAnalyzeButton: document.getElementById("autoAnalyzeButton"),
    editorHelp: document.getElementById("editorHelp"),
    modalTitle: document.getElementById("modalTitle"),
    modalDescription: document.getElementById("modalDescription"),
    dropTitle: document.getElementById("dropTitle"),
    dropHelp: document.getElementById("dropHelp"),
    categoryOptions: document.getElementById("categoryOptions"),
    openCollectionManager: document.getElementById("openCollectionManager"),
    quickCreateCollection: document.getElementById("quickCreateCollection"),
    collectionModal: document.getElementById("collectionModal"),
    closeCollectionModal: document.getElementById("closeCollectionModal"),
    collectionForm: document.getElementById("collectionForm"),
    collectionName: document.getElementById("collectionName"),
    collectionList: document.getElementById("collectionList"),
    exportModal: document.getElementById("exportModal"),
    exportModalTitle: document.getElementById("exportModalTitle"),
    exportModalDescription: document.getElementById("exportModalDescription"),
    closeExportModal: document.getElementById("closeExportModal"),
    exportMeta: document.getElementById("exportMeta"),
    exportData: document.getElementById("exportData"),
    copyExportButton: document.getElementById("copyExportButton"),
    downloadExportButton: document.getElementById("downloadExportButton"),
  };

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const unique = (values) => [...new Set(values.filter(Boolean))];
  const idEquals = (left, right) => String(left) === String(right);
  const nowIso = () => new Date().toISOString();
  const asText = (value) => value == null ? "" : String(value);
  const asTags = (value) => {
    if (Array.isArray(value)) return unique(value.map(asText).map(v => v.trim()).filter(Boolean));
    return unique(asText(value).split(/[,，、;；|\n]/).map(v => v.trim()).filter(Boolean));
  };
  const slugify = (value) => {
    const slug = asText(value).trim().toLocaleLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-+|-+$/g, "");
    return slug || `prompt-${Date.now()}`;
  };
  const formatDuration = (value) => {
    const number = Number(value);
    if (!Number.isFinite(number) || number <= 0) return "未设置";
    return Number.isInteger(number) ? `${number} 秒` : `${number.toFixed(1)} 秒`;
  };
  const nextUserId = () => `user-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const normalizeText = (value) => asText(value).replace(/\s+/g, " ").trim().toLocaleLowerCase();
  const normalizeCollectionName = (value) => asText(value).replace(/\s+/g, " ").trim().slice(0, 40);

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function normalizeCollectionList(values) {
    const result = [DEFAULT_COLLECTION];
    for (const rawValue of values || []) {
      const value = normalizeCollectionName(rawValue);
      if (!value || result.some(item => normalizeText(item) === normalizeText(value))) continue;
      result.push(value);
    }
    return [
      DEFAULT_COLLECTION,
      ...result.filter(value => value !== DEFAULT_COLLECTION).sort((a, b) => a.localeCompare(b, "zh-CN")),
    ];
  }

  function syncCatalogCollections(catalog = state.catalog) {
    if (!catalog) return [];
    catalog.collections = normalizeCollectionList([
      ...(Array.isArray(catalog.collections) ? catalog.collections : []),
      ...(catalog.prompts || []).map(prompt => prompt.collection),
    ]);
    return catalog.collections;
  }

  function normalizeShot(shot, index) {
    return {
      shot_index: Number(shot?.shot_index) || index + 1,
      start_sec: Number(shot?.start_sec) || 0,
      end_sec: Number(shot?.end_sec) || 0,
      title: asText(shot?.title || `镜头 ${index + 1}`),
      visual_action: asText(shot?.visual_action || shot?.action || shot?.prompt),
      camera: asText(shot?.camera),
      audio: asText(shot?.audio),
      continuity: asText(shot?.continuity),
    };
  }

  function normalizePrompt(prompt, options = {}) {
    const createdAt = prompt?.created_at || options.createdAt || nowIso();
    const title = asText(prompt?.title || options.title || "未命名提示词").trim() || "未命名提示词";
    const duration = Number(prompt?.duration_sec);
    return {
      id: prompt?.id ?? nextUserId(),
      source_id: prompt?.source_id ?? options.sourceId ?? "local-import",
      slug: asText(prompt?.slug || slugify(title)),
      title,
      media_type: [MEDIA_VIDEO, MEDIA_IMAGE].includes(prompt?.media_type)
        ? prompt.media_type
        : ([MEDIA_VIDEO, MEDIA_IMAGE].includes(prompt?.prompt_type) ? prompt.prompt_type : (options.mediaType || MEDIA_VIDEO)),
      category: asText(prompt?.category || "待整理"),
      language: asText(prompt?.language || "zh-CN"),
      aspect_ratio: asText(prompt?.aspect_ratio || "未识别"),
      duration_sec: Number.isFinite(duration) && duration > 0 ? duration : 0,
      resolution: asText(prompt?.resolution || "未识别"),
      style_summary: asText(prompt?.style_summary || prompt?.style || "待补充"),
      scene_summary: asText(prompt?.scene_summary),
      subject_summary: asText(prompt?.subject_summary),
      core_mechanic: asText(prompt?.core_mechanic || "本地提示词，可继续编辑与分类。"),
      camera_language: asText(prompt?.camera_language),
      lighting_color: asText(prompt?.lighting_color),
      audio_design: asText(prompt?.audio_design),
      continuity_rules: asText(prompt?.continuity_rules),
      master_prompt: asText(prompt?.master_prompt || prompt?.prompt || prompt?.content || prompt?.text),
      negative_prompt: asText(prompt?.negative_prompt),
      reference_image_prompt: asText(prompt?.reference_image_prompt),
      recommended_models: asText(prompt?.recommended_models),
      prompt_origin: asText(prompt?.prompt_origin || options.origin || "本地导入"),
      quality_notes: asText(prompt?.quality_notes),
      tags: asTags(prompt?.tags),
      shots: Array.isArray(prompt?.shots) ? prompt.shots.map(normalizeShot) : [],
      collection: asText(prompt?.collection || DEFAULT_COLLECTION),
      user_managed: prompt?.user_managed ?? options.userManaged ?? false,
      created_at: createdAt,
      updated_at: prompt?.updated_at || createdAt,
    };
  }

  function normalizeCatalog(raw) {
    const prompts = Array.isArray(raw?.prompts) ? raw.prompts.map(prompt => normalizePrompt(prompt)) : [];
    return {
      database_name: asText(raw?.database_name || "AI 视频提示词数据库"),
      version: asText(raw?.version || baseDatabase.version || "local"),
      sources: Array.isArray(raw?.sources) ? raw.sources : [],
      prompts,
      collections: normalizeCollectionList([
        ...(Array.isArray(raw?.collections) ? raw.collections : []),
        ...prompts.map(prompt => prompt.collection),
      ]),
      deletedBaseSlugs: Array.isArray(raw?.deletedBaseSlugs) ? raw.deletedBaseSlugs : [],
      saved_at: raw?.saved_at || nowIso(),
    };
  }

  function mergeWithBase(saved) {
    const catalog = saved ? normalizeCatalog(saved) : normalizeCatalog(clone(baseDatabase));
    const deleted = new Set(catalog.deletedBaseSlugs);
    for (const rawPrompt of baseDatabase.prompts) {
      const prompt = normalizePrompt(rawPrompt, { userManaged: false });
      const existingIndex = catalog.prompts.findIndex(item => item.slug === prompt.slug);
      if (existingIndex < 0 && !deleted.has(prompt.slug)) {
        catalog.prompts.push(prompt);
      } else if (existingIndex >= 0 && !catalog.prompts[existingIndex].user_managed) {
        catalog.prompts[existingIndex] = prompt;
      }
    }
    const sourceKeys = new Set(catalog.sources.map(source => `${source.id}|${source.locator || source.title}`));
    for (const source of baseDatabase.sources || []) {
      const key = `${source.id}|${source.locator || source.title}`;
      if (!sourceKeys.has(key)) catalog.sources.push(clone(source));
    }
    catalog.version = baseDatabase.version || catalog.version;
    syncCatalogCollections(catalog);
    return catalog;
  }

  function openStorage() {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) return reject(new Error("IndexedDB unavailable"));
      const request = indexedDB.open(STORAGE_DB, 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORAGE_STORE)) db.createObjectStore(STORAGE_STORE);
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function loadSavedCatalog() {
    try {
      const db = await openStorage();
      const value = await new Promise((resolve, reject) => {
        const request = db.transaction(STORAGE_STORE, "readonly").objectStore(STORAGE_STORE).get(STORAGE_KEY);
        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
      });
      db.close();
      return value;
    } catch {
      try {
        return JSON.parse(localStorage.getItem(FALLBACK_KEY) || "null");
      } catch {
        return null;
      }
    }
  }

  async function saveCatalog() {
    syncCatalogCollections();
    state.catalog.saved_at = nowIso();
    const data = clone(state.catalog);
    try {
      const db = await openStorage();
      await new Promise((resolve, reject) => {
        const request = db.transaction(STORAGE_STORE, "readwrite").objectStore(STORAGE_STORE).put(data, STORAGE_KEY);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
      db.close();
    } catch {
      try {
        localStorage.setItem(FALLBACK_KEY, JSON.stringify(data));
      } catch (error) {
        console.warn("Local persistence is unavailable; changes will last only for this page session.", error);
      }
    }
  }

  function detectRatio(text) {
    const match = asText(text).match(/(?:横屏|竖屏|画幅|比例|aspect\s*ratio)?\s*(21\s*:\s*9|16\s*:\s*9|9\s*:\s*16|4\s*:\s*3|3\s*:\s*4|1\s*:\s*1)/i);
    return match ? match[1].replace(/\s/g, "") : "";
  }

  function detectDuration(text) {
    const source = asText(text);
    const explicit = source.match(/(?:时长|duration|总长)[^\d]{0,10}(\d+(?:\.\d+)?)\s*(?:秒|s\b)/i);
    if (explicit) return Number(explicit[1]);
    const ranges = [...source.matchAll(/\[(\d{1,2}):(\d{2})\s*[-–—~至]\s*(\d{1,2}):(\d{2})\]/g)];
    if (ranges.length) {
      return Math.max(...ranges.map(match => Number(match[3]) * 60 + Number(match[4])));
    }
    const secondRanges = [...source.matchAll(/\[(\d+(?:\.\d+)?)\s*[-–—~至]\s*(\d+(?:\.\d+)?)\s*(?:秒|s)?\]/gi)];
    if (secondRanges.length) return Math.max(...secondRanges.map(match => Number(match[2])));
    const simple = source.match(/(\d+(?:\.\d+)?)\s*(?:秒|s\b)/i);
    return simple ? Number(simple[1]) : 0;
  }

  function detectResolution(text) {
    const match = asText(text).match(/\b(8K|6K|4K|2K|1080P|720P)\b/i);
    return match ? match[1].toUpperCase() : "";
  }

  function detectCategory(text, mediaType = MEDIA_VIDEO) {
    const source = asText(text).toLocaleLowerCase();
    const imageRules = [
      ["人物肖像 / 角色设计", /肖像|人像|角色设定|角色设计|portrait|character\s*(?:design|sheet)/],
      ["产品摄影 / 广告视觉", /产品摄影|商品摄影|广告海报|包装|product\s*(?:photo|shot)|commercial|packshot/],
      ["场景概念 / 环境设计", /场景概念|环境设计|建筑|风景|城市景观|concept\s*art|environment|landscape/],
      ["动漫 / 插画", /动漫|动画|插画|赛璐璐|二次元|anime|illustration|cel[\s-]?shad/],
      ["海报 / 平面设计", /海报|封面|排版|字体设计|poster|cover|graphic\s*design|typography/],
      ["摄影写实", /摄影|写实|镜头|相机|photo(?:graphy)?|photoreal/],
      ["3D / CG", /\b3d\b|cgi|渲染|render/],
    ];
    const videoRules = [
      ["搞笑短视频", /搞笑|喜剧|荒诞|爆笑|恶作剧|comedy|funny/],
      ["美食 / 做饭", /厨房|做饭|烹饪|烧烤|美食|炒菜|锅|cooking|food/],
      ["奇幻动作", /海盗|巨兽|奇幻|boss|魔法|舰队|fantasy/],
      ["概念特效 / VFX", /科幻|vfx|特效|时间冻结|变形|超现实|sci[\s-]?fi/],
      ["Vlog / POV", /\bpov\b|vlog|第一人称/],
      ["广告 / 产品", /广告|产品|商品|commercial|product/],
      ["人物 / 角色", /角色|人物|肖像|portrait|character/],
    ];
    const rules = mediaType === MEDIA_IMAGE ? imageRules : videoRules;
    return rules.find(([, pattern]) => pattern.test(source))?.[0] || "待整理";
  }

  function detectTags(text, mediaType = MEDIA_VIDEO) {
    const source = asText(text);
    const rules = [
      ["搞笑", /搞笑|喜剧|荒诞|爆笑/],
      ["POV", /\bpov\b|第一人称/i],
      ["真人实拍", /真人实拍|live[\s-]?action/i],
      ["2D贴纸", /2d.*贴纸|扁平.*贴纸|die[\s-]?cut/i],
      ["厨房", /厨房|灶台|铁锅/],
      ["美食", /做饭|烹饪|烧烤|美食|炒菜/],
      ["海盗", /海盗|pirate/i],
      ["巨兽", /巨兽|利维坦|leviathan/i],
      ["Boss战", /boss\s*战|boss battle/i],
      ["VFX", /\bvfx\b|视觉特效|时间冻结/i],
      ["时间冻结", /时间冻结|凝固时间/],
      ["角色一致性", /角色.*一致|保持一致|全程.*一致/],
      ["连续镜头", /连续镜头|无硬剪辑|一镜到底/],
      ["手持镜头", /手持|handheld/i],
      ["电影感", /电影级|电影感|cinematic/i],
      ["8K", /\b8k\b/i],
      ["4K", /\b4k\b/i],
      ["16:9", /16\s*:\s*9/],
      ["9:16", /9\s*:\s*16/],
      ["角色设计", /角色设定|角色设计|character\s*(?:design|sheet)/i],
      ["产品摄影", /产品摄影|商品摄影|product\s*(?:photo|shot)/i],
      ["概念艺术", /概念艺术|概念设计|concept\s*art/i],
      ["插画", /插画|illustration/i],
      ["动漫", /动漫|二次元|anime/i],
      ["海报", /海报|poster/i],
      ["摄影写实", /摄影写实|photoreal|photography/i],
    ];
    return unique([
      mediaType === MEDIA_IMAGE ? "图片提示词" : "视频提示词",
      ...rules.filter(([, pattern]) => pattern.test(source)).map(([tag]) => tag),
    ]);
  }

  function parseShots(text) {
    const source = asText(text).replace(/\r\n/g, "\n");
    const marker = /\[(?:(\d{1,2}):(\d{2})|(\d+(?:\.\d+)?))\s*[-–—~至]\s*(?:(\d{1,2}):(\d{2})|(\d+(?:\.\d+)?))\s*(?:秒|s)?\]\s*([^\n]*)/gi;
    const matches = [...source.matchAll(marker)];
    return matches.map((match, index) => {
      const bodyStart = match.index + match[0].length;
      const bodyEnd = matches[index + 1]?.index ?? source.length;
      const body = source.slice(bodyStart, bodyEnd).trim();
      const audioMatch = body.match(/(?:音效|声音|audio)\s*[:：]\s*([^\n]+)/i);
      const cameraMatch = body.match(/(?:镜头|camera)\s*[:：]\s*([^\n]+)/i);
      const cleanTitle = match[7].replace(/^镜头\s*\d+\s*[:：]?\s*/, "").trim();
      const action = body
        .replace(/(?:音效|声音|audio)\s*[:：]\s*[^\n]+/ig, "")
        .replace(/(?:镜头|camera)\s*[:：]\s*[^\n]+/ig, "")
        .trim();
      return {
        shot_index: index + 1,
        start_sec: match[1] != null ? Number(match[1]) * 60 + Number(match[2]) : Number(match[3]),
        end_sec: match[4] != null ? Number(match[4]) * 60 + Number(match[5]) : Number(match[6]),
        title: cleanTitle || `镜头 ${index + 1}`,
        visual_action: action,
        camera: cameraMatch?.[1]?.trim() || "",
        audio: audioMatch?.[1]?.trim() || "",
        continuity: "",
      };
    });
  }

  function analyzePrompt(text, mediaType = MEDIA_VIDEO) {
    return {
      category: detectCategory(text, mediaType),
      aspect_ratio: detectRatio(text) || "未识别",
      duration_sec: mediaType === MEDIA_VIDEO ? detectDuration(text) : 0,
      resolution: detectResolution(text) || "未识别",
      tags: detectTags(text, mediaType),
      shots: mediaType === MEDIA_VIDEO ? parseShots(text) : [],
    };
  }

  function sourceFor(item) {
    return state.catalog.sources.find(source => idEquals(source.id, item.source_id));
  }

  function fillSelect(select, values, current) {
    select.innerHTML = values.map(value =>
      `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
    ).join("");
    select.value = values.includes(current) ? current : ALL;
  }

  function refreshEditorCollectionOptions(current = el.editCollection.value || DEFAULT_COLLECTION) {
    const collections = syncCatalogCollections();
    el.editCollection.innerHTML = collections.map(value =>
      `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
    ).join("");
    el.editCollection.value = collections.includes(current) ? current : DEFAULT_COLLECTION;
  }

  function refreshOptions() {
    const prompts = state.mediaType === MEDIA_ALL
      ? state.catalog.prompts
      : state.catalog.prompts.filter(item => item.media_type === state.mediaType);
    fillSelect(el.category, [ALL, ...unique(prompts.map(item => item.category)).sort()], state.category);
    fillSelect(el.ratio, [ALL, ...unique(prompts.map(item => item.aspect_ratio)).sort()], state.ratio);
    const collections = syncCatalogCollections();
    el.collection.innerHTML = [ALL, ...collections].map(value => {
      const count = value === ALL
        ? prompts.length
        : prompts.filter(prompt => prompt.collection === value).length;
      const label = value === ALL ? `全部合集 · ${count}` : `${value} · ${count}`;
      return `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`;
    }).join("");
    el.collection.value = [ALL, ...collections].includes(state.collection) ? state.collection : ALL;
    const categories = unique(prompts.map(item => item.category)).sort();
    el.categoryOptions.innerHTML = categories.map(value => `<option value="${escapeHtml(value)}"></option>`).join("");
    refreshEditorCollectionOptions();
  }

  function findCollection(name) {
    const normalized = normalizeText(name);
    return (state.catalog.collections || []).find(value => normalizeText(value) === normalized) || "";
  }

  function renderCollectionManager() {
    const collections = syncCatalogCollections();
    el.collectionList.innerHTML = collections.map(name => {
      const count = state.catalog.prompts.filter(prompt => prompt.collection === name).length;
      const isDefault = name === DEFAULT_COLLECTION;
      return `<div class="collection-row">
        <div>
          <strong>${escapeHtml(name)}</strong>
          <small>${count} 条提示词${isDefault ? " · 系统默认合集" : ""}</small>
        </div>
        <div class="collection-row-actions">
          ${isDefault ? "" : `
            <button type="button" data-rename-collection="${escapeHtml(name)}">重命名</button>
            <button class="danger" type="button" data-delete-collection="${escapeHtml(name)}">删除</button>`}
        </div>
      </div>`;
    }).join("");
  }

  function openCollectionDialog(assignToEditor = false) {
    state.assignNewCollectionToEditor = assignToEditor;
    el.collectionName.value = "";
    renderCollectionManager();
    el.collectionModal.classList.add("open");
    document.body.style.overflow = "hidden";
    setTimeout(() => el.collectionName.focus(), 50);
  }

  function closeCollectionDialog() {
    el.collectionModal.classList.remove("open");
    state.assignNewCollectionToEditor = false;
    document.body.style.overflow =
      el.modal.classList.contains("open") || el.exportModal.classList.contains("open") ? "hidden" : "";
  }

  async function createCollection(name) {
    const value = normalizeCollectionName(name);
    if (!value) {
      showToast("请输入合集名称");
      return;
    }
    const existing = findCollection(value);
    if (existing) {
      if (state.assignNewCollectionToEditor) {
        refreshEditorCollectionOptions(existing);
        closeCollectionDialog();
      }
      showToast("该合集已经存在");
      return;
    }
    state.catalog.collections.push(value);
    await saveCatalog();
    refreshOptions();
    renderCollectionManager();
    if (state.assignNewCollectionToEditor) {
      refreshEditorCollectionOptions(value);
      closeCollectionDialog();
    } else {
      el.collectionName.value = "";
      el.collectionName.focus();
    }
    showToast(`合集“${value}”已建立并自动保存`);
  }

  async function renameCollection(oldName) {
    const proposed = window.prompt(`将合集“${oldName}”重命名为：`, oldName);
    if (proposed == null) return;
    const newName = normalizeCollectionName(proposed);
    if (!newName || newName === oldName) return;
    const existing = findCollection(newName);
    if (existing && existing !== oldName) {
      showToast("同名合集已经存在");
      return;
    }
    const editorUsesRenamedCollection = el.editCollection.value === oldName;
    state.catalog.collections = state.catalog.collections.map(name => name === oldName ? newName : name);
    state.catalog.prompts.forEach(prompt => {
      if (prompt.collection === oldName) prompt.collection = newName;
    });
    if (state.collection === oldName) state.collection = newName;
    await saveCatalog();
    render();
    if (editorUsesRenamedCollection) refreshEditorCollectionOptions(newName);
    renderCollectionManager();
    showToast(`合集已重命名为“${newName}”`);
  }

  async function deleteCollection(name) {
    if (name === DEFAULT_COLLECTION) return;
    const count = state.catalog.prompts.filter(prompt => prompt.collection === name).length;
    if (!window.confirm(`确定删除合集“${name}”吗？\n\n其中 ${count} 条提示词会移入“${DEFAULT_COLLECTION}”，提示词本身不会被删除。`)) return;
    const editorUsesDeletedCollection = el.editCollection.value === name;
    state.catalog.prompts.forEach(prompt => {
      if (prompt.collection === name) prompt.collection = DEFAULT_COLLECTION;
    });
    state.catalog.collections = state.catalog.collections.filter(value => value !== name);
    if (state.collection === name) state.collection = ALL;
    await saveCatalog();
    render();
    if (editorUsesDeletedCollection) refreshEditorCollectionOptions(DEFAULT_COLLECTION);
    renderCollectionManager();
    showToast(`合集“${name}”已删除，提示词已移入“${DEFAULT_COLLECTION}”`);
  }

  function filteredPrompts() {
    const query = state.query.trim().toLocaleLowerCase();
    return state.catalog.prompts
      .filter(item => {
        const mediaOk = state.mediaType === MEDIA_ALL || item.media_type === state.mediaType;
        const categoryOk = state.category === ALL || item.category === state.category;
        const ratioOk = state.ratio === ALL || item.aspect_ratio === state.ratio;
        const collectionOk = state.collection === ALL || item.collection === state.collection;
        const haystack = [
          item.title, item.category, item.collection, item.style_summary, item.scene_summary,
          item.subject_summary, item.core_mechanic, item.master_prompt, ...(item.tags || []),
        ].join(" ").toLocaleLowerCase();
        return mediaOk && categoryOk && ratioOk && collectionOk && (!query || haystack.includes(query));
      })
      .sort((a, b) => {
        if (a.user_managed !== b.user_managed) return a.user_managed ? -1 : 1;
        return asText(b.updated_at).localeCompare(asText(a.updated_at));
      });
  }

  function updateStats() {
    const videoCount = state.catalog.prompts.filter(item => item.media_type === MEDIA_VIDEO).length;
    const imageCount = state.catalog.prompts.filter(item => item.media_type === MEDIA_IMAGE).length;
    const shotCount = state.catalog.prompts.reduce((sum, item) => sum + item.shots.length, 0);
    const collectionCount = syncCatalogCollections()
      .filter(name => name !== DEFAULT_COLLECTION)
      .filter(name => state.catalog.prompts.some(item => item.collection === name))
      .length;
    el.topStats.innerHTML = `
      <span><strong>${videoCount}</strong> 视频</span>
      <i></i><span><strong>${imageCount}</strong> 图片</span>
      <i></i><span><strong>${collectionCount}</strong> 合集</span>
      <i></i><span><strong>${shotCount}</strong> 分镜</span>`;
  }

  function renderList() {
    const items = filteredPrompts();
    if (items.length && !items.some(item => idEquals(item.id, state.selectedId))) {
      state.selectedId = items[0].id;
      state.tab = "prompt";
    }
    el.resultCount.textContent = `${items.length} 个结果`;
    el.clearSearch.style.display = state.query ? "block" : "none";
    el.clearFilters.style.display =
      state.mediaType !== MEDIA_ALL || state.category !== ALL || state.ratio !== ALL || state.collection !== ALL ? "block" : "none";
    el.mediaFilterButtons.forEach(button =>
      button.classList.toggle("active", button.dataset.mediaFilter === state.mediaType));
    if (!items.length) {
      el.promptList.innerHTML = `
        <div class="empty"><div class="empty-glyph">⌕</div>
        <h2>没有匹配的提示词</h2><p>试试缩短关键词或清除筛选条件。</p></div>`;
      el.detail.innerHTML = "";
      return;
    }
    el.promptList.innerHTML = items.map((item, index) => `
      <button class="prompt-card ${idEquals(item.id, state.selectedId) ? "selected" : ""}"
              type="button" data-prompt-id="${escapeHtml(item.id)}">
        <span class="card-index ${colors[index % colors.length]}">${String(index + 1).padStart(2, "0")}</span>
        <span class="card-content">
          <span class="card-topline">
            <strong class="card-title">${escapeHtml(item.title)}</strong>
            <span class="media-badge ${item.media_type === MEDIA_IMAGE ? "image" : ""}">
              ${item.media_type === MEDIA_IMAGE ? "图片" : "视频"}
            </span>
          </span>
          <span class="card-collection">${escapeHtml(item.collection)}</span>
          <span class="card-description">${escapeHtml(item.style_summary || item.category)}</span>
          <span class="tag-row">
            ${(item.tags || []).slice(0, 3).map(tag => `<em class="tag">${escapeHtml(tag)}</em>`).join("")}
            <small class="duration">${escapeHtml(item.aspect_ratio)}${item.media_type === MEDIA_VIDEO ? ` · ${formatDuration(item.duration_sec)}` : ""}</small>
          </span>
        </span>
      </button>`).join("");
    el.promptList.querySelectorAll("[data-prompt-id]").forEach(button => {
      button.addEventListener("click", () => {
        state.selectedId = button.dataset.promptId;
        state.tab = "prompt";
        render();
      });
    });
  }

  function copyButton(text, label, compact = true) {
    return `<button class="copy-button ${compact ? "compact" : ""}" type="button"
      data-copy="${encodeURIComponent(text || "")}"><span aria-hidden="true">⧉</span>${escapeHtml(label)}</button>`;
  }

  function promptTab(item) {
    return `<div class="content-width">
      <section class="content-card">
        <div class="section-title">
          <div><p class="eyebrow">MASTER PROMPT</p><h3>完整提示词</h3></div>
          ${copyButton(item.master_prompt, "复制")}
        </div>
        <div class="prompt-text">${escapeHtml(item.master_prompt)}</div>
      </section>
      <section class="content-card negative-card">
        <div class="section-title">
          <div><p class="eyebrow">NEGATIVE CONSTRAINTS</p><h3>负面提示词</h3></div>
          ${copyButton(item.negative_prompt, "复制")}
        </div>
        <p class="negative-text">${escapeHtml(item.negative_prompt || "尚未填写")}</p>
      </section>
      ${item.reference_image_prompt ? `<section class="content-card">
        <div class="section-title">
          <div><p class="eyebrow">REFERENCE IMAGE</p><h3>参考图提示词</h3></div>
          ${copyButton(item.reference_image_prompt, "复制")}
        </div><div class="prompt-text">${escapeHtml(item.reference_image_prompt)}</div>
      </section>` : ""}
    </div>`;
  }

  function shotsTab(item) {
    if (!item.shots.length) {
      return `<div class="content-width"><div class="empty">
        <div class="empty-glyph">◷</div><h2>还没有分镜</h2>
        <p>编辑这条提示词并点击“自动分析”，可从时间码中提取分镜。</p></div></div>`;
    }
    return `<div class="content-width timeline">${item.shots.map(shot => {
      const combined = [
        item.continuity_rules, shot.visual_action,
        shot.camera ? `镜头：${shot.camera}` : "",
        shot.audio ? `音效：${shot.audio}` : "",
        shot.continuity ? `连续性：${shot.continuity}` : "",
        item.negative_prompt ? `禁止：${item.negative_prompt}` : "",
      ].filter(Boolean).join("\n\n");
      return `<article class="shot-card">
        <div class="shot-rail"><span>${String(shot.shot_index).padStart(2, "0")}</span><i></i></div>
        <div class="shot-body">
          <div class="shot-heading"><div>
            <time class="shot-time">${Number(shot.start_sec).toFixed(1).replace(".0", "")}s — ${Number(shot.end_sec).toFixed(1).replace(".0", "")}s</time>
            <h3>${escapeHtml(shot.title)}</h3>
          </div>${copyButton(combined, "复制本镜头")}</div>
          <p class="shot-action">${escapeHtml(shot.visual_action)}</p>
          <dl>
            ${shot.camera ? `<div><dt>镜头</dt><dd>${escapeHtml(shot.camera)}</dd></div>` : ""}
            ${shot.audio ? `<div><dt>声音</dt><dd>${escapeHtml(shot.audio)}</dd></div>` : ""}
            ${shot.continuity ? `<div><dt>连续性</dt><dd>${escapeHtml(shot.continuity)}</dd></div>` : ""}
          </dl>
        </div>
      </article>`;
    }).join("")}</div>`;
  }

  function specTab(item) {
    const specs = item.media_type === MEDIA_IMAGE
      ? [
          ["视觉风格", item.style_summary], ["场景", item.scene_summary],
          ["主体", item.subject_summary], ["构图与视角", item.camera_language],
          ["灯光与色彩", item.lighting_color], ["画面约束", item.continuity_rules],
          ["推荐模型", item.recommended_models],
        ]
      : [
          ["视觉风格", item.style_summary], ["场景", item.scene_summary],
          ["主体", item.subject_summary], ["镜头语言", item.camera_language],
          ["灯光与色彩", item.lighting_color], ["音效设计", item.audio_design],
          ["连续性规则", item.continuity_rules], ["推荐模型", item.recommended_models],
        ];
    return `<div class="content-width spec-grid">
      ${specs.map(([label, value]) => `<section class="content-card spec-card">
        <p class="eyebrow">${escapeHtml(label)}</p>
        <p class="spec-value">${escapeHtml(value || "尚未填写")}</p>
      </section>`).join("")}
      <section class="content-card spec-card full">
        <p class="eyebrow">标签</p>
        <div class="large-tags">${(item.tags || []).map(tag =>
          `<span class="large-tag">${escapeHtml(tag)}</span>`).join("") || "尚未添加标签"}</div>
      </section>
    </div>`;
  }

  function sourceTab(item) {
    const source = sourceFor(item);
    return `<div class="content-width source-grid">
      <section class="content-card">
        <p class="eyebrow">DATA PROVENANCE</p>
        <h3 class="source-title">${escapeHtml(source?.title || "本地导入")}</h3>
        <dl>
          <div><dt>来源类型</dt><dd>${escapeHtml(source?.source_type || item.prompt_origin)}</dd></div>
          <div><dt>来源位置</dt><dd>${escapeHtml(source?.locator || "浏览器本地数据库")}</dd></div>
          <div><dt>提示词性质</dt><dd>${escapeHtml(item.prompt_origin)}</dd></div>
          <div><dt>更新时间</dt><dd>${escapeHtml(new Date(item.updated_at).toLocaleString("zh-CN"))}</dd></div>
        </dl>
      </section>
      <section class="content-card note-card">
        <p class="eyebrow">QUALITY NOTES</p>
        <h3 class="source-title">数据质量说明</h3>
        <p>${escapeHtml(item.quality_notes || "这是可编辑的本地记录。")}</p>
        ${source?.notes ? `<p>${escapeHtml(source.notes)}</p>` : ""}
      </section>
    </div>`;
  }

  function renderDetail() {
    const item = state.catalog.prompts.find(prompt => idEquals(prompt.id, state.selectedId));
    if (!item) return;
    if (item.media_type === MEDIA_IMAGE && state.tab === "shots") state.tab = "prompt";
    const tabs = [
      ["prompt", "完整提示词"],
      ...(item.media_type === MEDIA_VIDEO ? [["shots", `分镜 · ${item.shots.length}`]] : []),
      ["spec", "创作规格"], ["source", "来源说明"],
    ];
    const tabContent = {
      prompt: promptTab(item), shots: shotsTab(item),
      spec: specTab(item), source: sourceTab(item),
    }[state.tab];
    el.detail.innerHTML = `
      <div class="detail-hero">
        <div class="detail-heading">
          <p class="eyebrow">${item.media_type === MEDIA_IMAGE ? "IMAGE PROMPT" : "VIDEO PROMPT"} · ${item.user_managed ? "LOCAL" : "DATABASE"}</p>
          <h2>${escapeHtml(item.title)}</h2>
          <p class="detail-lead">${escapeHtml(item.core_mechanic)}</p>
        </div>
        <div class="detail-actions">${copyButton(item.master_prompt, "复制完整提示词", false)}</div>
        <div class="detail-facts">
          <span><small>画幅</small>${escapeHtml(item.aspect_ratio)}</span>
          <span><small>分辨率</small>${escapeHtml(item.resolution)}</span>
          ${item.media_type === MEDIA_VIDEO
            ? `<span><small>时长</small>${formatDuration(item.duration_sec)}</span>
               <span><small>分镜</small>${item.shots.length} 段</span>`
            : `<span><small>类型</small>图片提示词</span>
               <span><small>标签</small>${item.tags.length} 个</span>`}
        </div>
      </div>
      <div class="management-strip">
        <div>
          <span class="media-badge ${item.media_type === MEDIA_IMAGE ? "image" : ""}">
            ${item.media_type === MEDIA_IMAGE ? "▧ 图片提示词" : "🎬 视频提示词"}
          </span>
          <span class="collection-chip">合集 · ${escapeHtml(item.collection)}</span>
          ${item.user_managed ? `<span class="local-badge">本地导入 / 编辑</span>` : ""}
        </div>
        <div class="management-actions">
          <button class="toolbar-button" type="button" data-edit-prompt>编辑与分类</button>
          <button class="toolbar-button danger" type="button" data-delete-prompt>删除</button>
        </div>
      </div>
      <nav class="detail-tabs" aria-label="提示词详情">
        ${tabs.map(([key, label]) =>
          `<button type="button" data-tab="${key}" class="${state.tab === key ? "active" : ""}">${label}</button>`
        ).join("")}
      </nav>
      <div class="detail-scroll">${tabContent}</div>`;
    bindDetailEvents();
  }

  function bindDetailEvents() {
    el.detail.querySelectorAll("[data-tab]").forEach(button => {
      button.addEventListener("click", () => {
        state.tab = button.dataset.tab;
        renderDetail();
      });
    });
    el.detail.querySelectorAll("[data-copy]").forEach(button => {
      button.addEventListener("click", () => copyText(decodeURIComponent(button.dataset.copy)));
    });
    el.detail.querySelector("[data-edit-prompt]")?.addEventListener("click", () => {
      const item = state.catalog.prompts.find(prompt => idEquals(prompt.id, state.selectedId));
      if (item) openEditor(item);
    });
    el.detail.querySelector("[data-delete-prompt]")?.addEventListener("click", deleteSelected);
  }

  function render() {
    refreshOptions();
    updateStats();
    renderList();
    if (filteredPrompts().length) renderDetail();
  }

  let toastTimer;
  function showToast(message) {
    clearTimeout(toastTimer);
    el.toast.textContent = message;
    el.toast.classList.add("show");
    toastTimer = setTimeout(() => el.toast.classList.remove("show"), 1800);
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const area = document.createElement("textarea");
      area.value = text;
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
    showToast("已复制到剪贴板");
  }

  function setModalTab(tab) {
    document.querySelectorAll("[data-modal-tab]").forEach(button =>
      button.classList.toggle("active", button.dataset.modalTab === tab));
    el.importPane.classList.toggle("active", tab === "import");
    el.editPane.classList.toggle("active", tab === "edit");
    const typeLabel = state.manageMediaType === MEDIA_IMAGE ? "图片提示词" : "视频提示词";
    el.modalTitle.textContent = tab === "edit"
      ? `${el.editId.value ? "编辑" : "新增"}${typeLabel}`
      : `导入${typeLabel}`;
  }

  function openModal(tab = "import") {
    setModalTab(tab);
    el.modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    el.modal.classList.remove("open");
    document.body.style.overflow = "";
  }

  function updateManagerCopy(mediaType) {
    const isImage = mediaType === MEDIA_IMAGE;
    el.modalTitle.textContent = isImage ? "导入图片提示词" : "导入视频提示词";
    el.modalDescription.textContent = isImage
      ? "导入用于文生图、参考图或视觉设计的提示词，并继续编辑分类、合集与标签。"
      : "导入用于文生视频、图生视频或视频编辑的提示词，并自动整理时长与分镜。";
    el.dropTitle.textContent = isImage
      ? "拖入图片提示词文件，或点击选择"
      : "拖入视频提示词文件，或点击选择";
    el.dropHelp.innerHTML = isImage
      ? "TXT / Markdown：每个文件创建一条图片提示词<br>JSON：支持图片提示词备份、数组或单条记录"
      : "TXT / Markdown：每个文件创建一条视频提示词<br>JSON：支持视频提示词备份、数组或单条记录";
  }

  function updateEditorMode(mediaType) {
    const isImage = mediaType === MEDIA_IMAGE;
    el.editMediaType.value = mediaType;
    el.durationField.style.display = isImage ? "none" : "flex";
    el.editorHelp.textContent = isImage
      ? "自动分析会识别图片分类、标签、画幅和分辨率。"
      : "自动分析会识别视频分类、标签、画幅、时长和时间码分镜。";
  }

  function openManager(mediaType, tab = "import") {
    state.manageMediaType = mediaType;
    updateManagerCopy(mediaType);
    el.importSummary.classList.remove("show");
    openModal(tab);
  }

  function clearEditor(mediaType = state.manageMediaType) {
    el.promptForm.reset();
    el.editId.value = "";
    refreshEditorCollectionOptions(DEFAULT_COLLECTION);
    el.editRatio.value = "";
    el.editDuration.value = "";
    el.editCategory.value = "";
    updateEditorMode(mediaType);
  }

  function openEditor(item = null) {
    const mediaType = item?.media_type || state.manageMediaType;
    state.manageMediaType = mediaType;
    updateManagerCopy(mediaType);
    clearEditor(mediaType);
    if (item) {
      el.editId.value = item.id;
      el.editMediaType.value = item.media_type;
      el.editTitle.value = item.title;
      el.editCategory.value = item.category;
      refreshEditorCollectionOptions(item.collection);
      el.editRatio.value = item.aspect_ratio === "未识别" ? "" : item.aspect_ratio;
      el.editDuration.value = item.duration_sec || "";
      el.editTags.value = item.tags.join(", ");
      el.editPrompt.value = item.master_prompt;
      el.editNegative.value = item.negative_prompt;
    }
    openModal("edit");
    setTimeout(() => el.editTitle.focus(), 50);
  }

  function applyAnalysisToEditor() {
    const mediaType = el.editMediaType.value;
    const analysis = analyzePrompt(el.editPrompt.value, mediaType);
    if (!el.editCategory.value || el.editCategory.value === "待整理") el.editCategory.value = analysis.category;
    if (!el.editRatio.value) el.editRatio.value = analysis.aspect_ratio === "未识别" ? "" : analysis.aspect_ratio;
    if (!el.editDuration.value && analysis.duration_sec) el.editDuration.value = analysis.duration_sec;
    const combinedTags = unique([...asTags(el.editTags.value), ...analysis.tags]);
    el.editTags.value = combinedTags.join(", ");
    showToast(mediaType === MEDIA_IMAGE
      ? `图片提示词分析完成：识别到 ${analysis.tags.length} 个标签`
      : `视频提示词分析完成：识别到 ${analysis.shots.length} 个分镜`);
  }

  async function saveEditor(event) {
    event.preventDefault();
    const existing = state.catalog.prompts.find(prompt => idEquals(prompt.id, el.editId.value));
    const mediaType = el.editMediaType.value;
    const analysis = analyzePrompt(el.editPrompt.value, mediaType);
    const timestamp = nowIso();
    if (existing) {
      Object.assign(existing, {
        media_type: mediaType,
        title: el.editTitle.value.trim(),
        slug: existing.slug || slugify(el.editTitle.value),
        category: el.editCategory.value.trim() || analysis.category,
        collection: normalizeCollectionName(el.editCollection.value) || DEFAULT_COLLECTION,
        aspect_ratio: el.editRatio.value.trim() || analysis.aspect_ratio,
        duration_sec: mediaType === MEDIA_VIDEO ? (Number(el.editDuration.value) || analysis.duration_sec) : 0,
        resolution: existing.resolution === "未识别" ? analysis.resolution : existing.resolution,
        tags: asTags(el.editTags.value).length ? asTags(el.editTags.value) : analysis.tags,
        master_prompt: el.editPrompt.value.trim(),
        negative_prompt: el.editNegative.value.trim(),
        shots: mediaType === MEDIA_VIDEO
          ? (analysis.shots.length ? analysis.shots : existing.shots)
          : [],
        user_managed: true,
        updated_at: timestamp,
      });
      state.selectedId = existing.id;
    } else {
      const prompt = normalizePrompt({
        id: nextUserId(),
        media_type: mediaType,
        title: el.editTitle.value.trim(),
        category: el.editCategory.value.trim() || analysis.category,
        collection: normalizeCollectionName(el.editCollection.value) || DEFAULT_COLLECTION,
        aspect_ratio: el.editRatio.value.trim() || analysis.aspect_ratio,
        duration_sec: mediaType === MEDIA_VIDEO ? (Number(el.editDuration.value) || analysis.duration_sec) : 0,
        resolution: analysis.resolution,
        tags: asTags(el.editTags.value).length ? asTags(el.editTags.value) : analysis.tags,
        master_prompt: el.editPrompt.value.trim(),
        negative_prompt: el.editNegative.value.trim(),
        shots: mediaType === MEDIA_VIDEO ? analysis.shots : [],
        user_managed: true,
        created_at: timestamp,
        updated_at: timestamp,
      }, { userManaged: true, origin: "手动新增", mediaType });
      state.catalog.prompts.push(prompt);
      state.selectedId = prompt.id;
    }
    await saveCatalog();
    state.category = ALL;
    state.ratio = ALL;
    state.collection = ALL;
    state.mediaType = mediaType;
    closeModal();
    render();
    showToast(existing ? "提示词已更新并自动保存" : "提示词已新增并自动保存");
  }

  async function deleteSelected() {
    const index = state.catalog.prompts.findIndex(prompt => idEquals(prompt.id, state.selectedId));
    if (index < 0) return;
    const item = state.catalog.prompts[index];
    if (!window.confirm(`确定删除“${item.title}”吗？\n\n可通过之前导出的 JSON 备份恢复。`)) return;
    if (!item.user_managed && item.slug && !state.catalog.deletedBaseSlugs.includes(item.slug)) {
      state.catalog.deletedBaseSlugs.push(item.slug);
    }
    state.catalog.prompts.splice(index, 1);
    state.selectedId = state.catalog.prompts[0]?.id ?? null;
    await saveCatalog();
    render();
    showToast("提示词已从本地数据库删除");
  }

  function isDuplicate(candidate) {
    const title = normalizeText(candidate.title);
    const prompt = normalizeText(candidate.master_prompt);
    return state.catalog.prompts.some(item =>
      item.media_type === candidate.media_type &&
      normalizeText(item.title) === title &&
      normalizeText(item.master_prompt) === prompt);
  }

  function promptFromRaw(raw, filename, useAnalysis, importMediaType) {
    const isString = typeof raw === "string";
    const content = isString ? raw : asText(raw.master_prompt || raw.prompt || raw.content || raw.text);
    const titleFromFile = filename.replace(/\.(txt|md|markdown|json)$/i, "");
    const rawObject = isString ? {} : raw;
    const mediaType = [MEDIA_VIDEO, MEDIA_IMAGE].includes(rawObject.media_type)
      ? rawObject.media_type
      : importMediaType;
    const analysis = useAnalysis ? analyzePrompt(content, mediaType) : {
      category: "待整理", aspect_ratio: "未识别", duration_sec: 0,
      resolution: "未识别", tags: [], shots: [],
    };
    return normalizePrompt({
      ...rawObject,
      id: nextUserId(),
      media_type: mediaType,
      source_id: "local-import",
      slug: `${slugify(rawObject.title || titleFromFile)}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      title: rawObject.title || titleFromFile,
      category: rawObject.category || analysis.category,
      aspect_ratio: rawObject.aspect_ratio || analysis.aspect_ratio,
      duration_sec: mediaType === MEDIA_VIDEO ? (rawObject.duration_sec || analysis.duration_sec) : 0,
      resolution: rawObject.resolution || analysis.resolution,
      master_prompt: content,
      tags: asTags(rawObject.tags).length ? asTags(rawObject.tags) : analysis.tags,
      shots: mediaType === MEDIA_VIDEO
        ? (Array.isArray(rawObject.shots) && rawObject.shots.length ? rawObject.shots : analysis.shots)
        : [],
      collection: normalizeCollectionName(rawObject.collection) || DEFAULT_COLLECTION,
      prompt_origin: `本地导入：${filename}`,
      user_managed: true,
      created_at: nowIso(),
      updated_at: nowIso(),
    }, { userManaged: true, origin: `本地导入：${filename}`, mediaType });
  }

  async function importFiles(fileList) {
    const files = [...fileList];
    if (!files.length) return;
    let imported = 0;
    let importedCollections = 0;
    let skipped = 0;
    const errors = [];
    for (const file of files) {
      try {
        const text = await file.text();
        let records;
        if (/\.json$/i.test(file.name) || file.type.includes("json")) {
          const parsed = JSON.parse(text);
          if (Array.isArray(parsed?.collections)) {
            for (const rawCollection of parsed.collections) {
              const collection = normalizeCollectionName(rawCollection);
              if (collection && !findCollection(collection)) {
                state.catalog.collections.push(collection);
                importedCollections += 1;
              }
            }
          }
          records = Array.isArray(parsed) ? parsed : Array.isArray(parsed?.prompts) ? parsed.prompts : [parsed];
        } else {
          records = [text];
        }
        for (const record of records) {
          const candidate = promptFromRaw(record, file.name, el.autoClassify.checked, state.manageMediaType);
          if (!candidate.master_prompt.trim()) {
            skipped += 1;
            continue;
          }
          if (el.skipDuplicates.checked && isDuplicate(candidate)) {
            skipped += 1;
            continue;
          }
          state.catalog.prompts.push(candidate);
          state.selectedId = candidate.id;
          imported += 1;
        }
      } catch (error) {
        errors.push(`${file.name}：${error.message}`);
      }
    }
    if (imported || importedCollections) {
      await saveCatalog();
      state.category = ALL;
      state.ratio = ALL;
      state.collection = ALL;
      state.mediaType = state.manageMediaType;
      render();
    }
    el.importSummary.classList.add("show");
    el.importSummary.innerHTML = `
      <strong>${state.manageMediaType === MEDIA_IMAGE ? "图片" : "视频"}提示词导入完成：新增 ${imported} 条，新增合集 ${importedCollections} 个，跳过 ${skipped} 条。</strong>
      ${errors.length ? `<p>${errors.map(escapeHtml).join("<br>")}</p>` : "<p>新记录已保存到当前浏览器数据库。</p>"}`;
    el.fileInput.value = "";
  }

  function createExportPayload(mediaType = state.exportMediaType) {
    const prompts = state.catalog.prompts.filter(item => item.media_type === mediaType);
    const sourceIds = new Set(prompts.map(item => String(item.source_id)));
    return {
      ...clone(state.catalog),
      database_name: mediaType === MEDIA_IMAGE ? "AI 图片提示词数据库" : "AI 视频提示词数据库",
      sources: clone(state.catalog.sources.filter(source => sourceIds.has(String(source.id)))),
      prompts: clone(prompts),
      export_scope: mediaType,
      export_format: mediaType === MEDIA_IMAGE
        ? "AI Image Prompt Atlas local backup"
        : "AI Video Prompt Atlas local backup",
      exported_at: nowIso(),
    };
  }

  function openExportModal(mediaType) {
    state.exportMediaType = mediaType;
    const isImage = mediaType === MEDIA_IMAGE;
    const payload = createExportPayload(mediaType);
    const json = JSON.stringify(payload, null, 2);
    const shotCount = payload.prompts.reduce((sum, item) => sum + (item.shots?.length || 0), 0);
    el.exportModalTitle.textContent = isImage ? "导出图片提示词" : "导出视频提示词";
    el.exportModalDescription.textContent = isImage
      ? "导出仅包含图片提示词的 JSON 备份，可在其他设备或浏览器重新导入。"
      : "导出仅包含视频提示词及分镜的 JSON 备份，可在其他设备或浏览器重新导入。";
    el.exportData.value = json;
    el.exportMeta.textContent =
      isImage
        ? `图片备份已生成：${payload.prompts.length} 条图片提示词，${new Blob([json]).size} 字节。`
        : `视频备份已生成：${payload.prompts.length} 条视频提示词，${shotCount} 个分镜，${new Blob([json]).size} 字节。`;
    el.exportModal.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeExportModal() {
    el.exportModal.classList.remove("open");
    document.body.style.overflow = "";
  }

  function downloadExportBackup() {
    const json = el.exportData.value || JSON.stringify(createExportPayload(state.exportMediaType), null, 2);
    const blob = new Blob([json], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    const prefix = state.exportMediaType === MEDIA_IMAGE ? "AI图片提示词数据库" : "AI视频提示词数据库";
    anchor.download = `${prefix}_备份_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast("JSON 备份下载已开始");
  }

  function bindGlobalEvents() {
    el.search.addEventListener("input", event => {
      state.query = event.target.value;
      render();
    });
    el.clearSearch.addEventListener("click", () => {
      state.query = "";
      el.search.value = "";
      el.search.focus();
      render();
    });
    el.category.addEventListener("change", event => {
      state.category = event.target.value;
      render();
    });
    el.ratio.addEventListener("change", event => {
      state.ratio = event.target.value;
      render();
    });
    el.collection.addEventListener("change", event => {
      state.collection = event.target.value;
      render();
    });
    el.openCollectionManager.addEventListener("click", () => openCollectionDialog(false));
    el.quickCreateCollection.addEventListener("click", () => openCollectionDialog(true));
    el.closeCollectionModal.addEventListener("click", closeCollectionDialog);
    el.collectionModal.addEventListener("click", event => {
      if (event.target === el.collectionModal) closeCollectionDialog();
    });
    el.collectionForm.addEventListener("submit", event => {
      event.preventDefault();
      createCollection(el.collectionName.value);
    });
    el.collectionList.addEventListener("click", event => {
      const renameButton = event.target.closest("[data-rename-collection]");
      if (renameButton) {
        renameCollection(renameButton.dataset.renameCollection);
        return;
      }
      const deleteButton = event.target.closest("[data-delete-collection]");
      if (deleteButton) deleteCollection(deleteButton.dataset.deleteCollection);
    });
    el.mediaFilterButtons.forEach(button => {
      button.addEventListener("click", () => {
        state.mediaType = button.dataset.mediaFilter;
        state.category = ALL;
        state.ratio = ALL;
        state.collection = ALL;
        state.tab = "prompt";
        render();
      });
    });
    el.clearFilters.addEventListener("click", () => {
      state.mediaType = MEDIA_ALL;
      state.category = ALL;
      state.ratio = ALL;
      state.collection = ALL;
      el.search.value = "";
      state.query = "";
      render();
    });
    el.openImportButton.addEventListener("click", () => {
      openManager(MEDIA_VIDEO, "import");
    });
    el.openImageImportButton.addEventListener("click", () => {
      openManager(MEDIA_IMAGE, "import");
    });
    el.exportButton.addEventListener("click", () => openExportModal(MEDIA_VIDEO));
    el.exportImageButton.addEventListener("click", () => openExportModal(MEDIA_IMAGE));
    el.closeExportModal.addEventListener("click", closeExportModal);
    el.exportModal.addEventListener("click", event => {
      if (event.target === el.exportModal) closeExportModal();
    });
    el.copyExportButton.addEventListener("click", () => copyText(el.exportData.value));
    el.downloadExportButton.addEventListener("click", downloadExportBackup);
    el.closeModal.addEventListener("click", closeModal);
    el.modal.addEventListener("click", event => {
      if (event.target === el.modal) closeModal();
    });
    document.querySelectorAll("[data-modal-tab]").forEach(button => {
      button.addEventListener("click", () => {
        if (button.dataset.modalTab === "edit") clearEditor(state.manageMediaType);
        setModalTab(button.dataset.modalTab);
      });
    });
    el.dropZone.addEventListener("click", () => el.fileInput.click());
    el.dropZone.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        el.fileInput.click();
      }
    });
    ["dragenter", "dragover"].forEach(name => el.dropZone.addEventListener(name, event => {
      event.preventDefault();
      el.dropZone.classList.add("dragging");
    }));
    ["dragleave", "drop"].forEach(name => el.dropZone.addEventListener(name, event => {
      event.preventDefault();
      el.dropZone.classList.remove("dragging");
    }));
    el.dropZone.addEventListener("drop", event => importFiles(event.dataTransfer.files));
    el.fileInput.addEventListener("change", event => importFiles(event.target.files));
    el.editMediaType.addEventListener("change", event => {
      state.manageMediaType = event.target.value;
      updateManagerCopy(state.manageMediaType);
      updateEditorMode(state.manageMediaType);
    });
    el.autoAnalyzeButton.addEventListener("click", applyAnalysisToEditor);
    el.promptForm.addEventListener("submit", saveEditor);
    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && el.collectionModal.classList.contains("open")) {
        closeCollectionDialog();
        return;
      }
      if (event.key === "Escape" && el.exportModal.classList.contains("open")) {
        closeExportModal();
        return;
      }
      if (event.key === "Escape" && el.modal.classList.contains("open")) {
        closeModal();
        return;
      }
      if (event.key === "/" && document.activeElement !== el.search &&
          !el.modal.classList.contains("open") && !el.collectionModal.classList.contains("open")) {
        event.preventDefault();
        el.search.focus();
      }
    });
  }

  async function start() {
    const saved = await loadSavedCatalog();
    state.catalog = mergeWithBase(saved);
    state.selectedId = state.catalog.prompts[0]?.id ?? null;
    await saveCatalog();
    bindGlobalEvents();
    render();
  }

  start().catch(error => {
    console.error(error);
    document.getElementById("app").style.display = "none";
    document.getElementById("fatal").style.display = "grid";
    document.querySelector("#fatal p").textContent = `本地数据库初始化失败：${error.message}`;
  });
})();
