/**
 * VibeCoding Admin Panel
 */
(function () {
  "use strict";

  const API = "/api/admin";
  let token = localStorage.getItem("vc_admin_token");

  // -----------------------------------------------------------------------
  // API helper
  // -----------------------------------------------------------------------
  async function api(path, opts = {}) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${API}${path}`, { ...opts, headers });
    if (res.status === 401) {
      logout();
      throw new Error("Sessao expirada");
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erro ${res.status}`);
    }
    return res.json();
  }

  function toast(msg, isError = false) {
    const el = document.createElement("div");
    el.className = `toast${isError ? " error" : ""}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  // -----------------------------------------------------------------------
  // Auth
  // -----------------------------------------------------------------------
  const loginScreen = document.getElementById("login-screen");
  const adminPanel = document.getElementById("admin-panel");
  const loginForm = document.getElementById("login-form");
  const loginError = document.getElementById("login-error");

  function showPanel() {
    loginScreen.classList.add("hidden");
    adminPanel.classList.remove("hidden");
    loadDashboard();
  }

  function logout() {
    token = null;
    localStorage.removeItem("vc_admin_token");
    localStorage.removeItem("vc_admin_name");
    adminPanel.classList.add("hidden");
    loginScreen.classList.remove("hidden");
  }

  if (token) {
    api("/me").then((data) => {
      document.getElementById("admin-name").textContent = data.display_name;
      showPanel();
    }).catch(() => logout());
  }

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.classList.add("hidden");
    try {
      const data = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: document.getElementById("login-user").value,
          password: document.getElementById("login-pass").value,
        }),
      }).then((r) => { if (!r.ok) throw new Error(); return r.json(); });
      token = data.token;
      localStorage.setItem("vc_admin_token", token);
      localStorage.setItem("vc_admin_name", data.display_name);
      document.getElementById("admin-name").textContent = data.display_name;
      showPanel();
    } catch {
      loginError.textContent = "Usuario ou senha incorretos";
      loginError.classList.remove("hidden");
    }
  });

  document.getElementById("btn-logout").addEventListener("click", logout);

  // -----------------------------------------------------------------------
  // Navigation
  // -----------------------------------------------------------------------
  const sections = { dashboard: "Dashboard", products: "Produtos", skills: "Skills da Bia", prompt: "Personalidade", leads: "Leads" };

  document.querySelectorAll("[data-section]").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const sec = link.dataset.section;
      document.querySelectorAll("[data-section]").forEach((l) => l.classList.remove("active"));
      link.classList.add("active");
      document.querySelectorAll(".section").forEach((s) => s.classList.add("hidden"));
      document.getElementById(`sec-${sec}`).classList.remove("hidden");
      document.getElementById("section-title").textContent = sections[sec];
      if (sec === "dashboard") loadDashboard();
      if (sec === "products") loadProducts();
      if (sec === "skills") loadSkills();
      if (sec === "prompt") loadPromptConfig();
      if (sec === "leads") loadLeads(1);
    });
  });

  // -----------------------------------------------------------------------
  // Dashboard
  // -----------------------------------------------------------------------
  async function loadDashboard() {
    try {
      const data = await api("/stats");
      document.getElementById("stat-sessions").textContent = data.total_sessions;
      document.getElementById("stat-messages").textContent = data.total_messages;
      document.getElementById("stat-leads").textContent = data.total_leads;
      document.getElementById("stat-leads-today").textContent = data.leads_today;
      document.getElementById("stat-leads-week").textContent = data.leads_this_week;
    } catch (e) { toast(e.message, true); }
  }

  // -----------------------------------------------------------------------
  // Products
  // -----------------------------------------------------------------------
  async function loadProducts() {
    try {
      const data = await api("/products");
      const wrap = document.getElementById("products-list");
      if (!data.products.length) { wrap.innerHTML = "<p style='color:var(--text-muted)'>Nenhum produto cadastrado.</p>"; return; }
      wrap.innerHTML = `<table>
        <thead><tr><th>Nome</th><th>Preco</th><th>Publico</th><th>Status</th><th>Acoes</th></tr></thead>
        <tbody>${data.products.map((p) => `<tr>
          <td><strong>${esc(p.name)}</strong><br><small style="color:var(--text-muted)">${esc(p.slug)}</small></td>
          <td>${esc(p.price_display)}</td>
          <td>${esc(p.target_audience || "-")}</td>
          <td><span class="badge ${p.is_active ? "badge-active" : "badge-inactive"}">${p.is_active ? "Ativo" : "Inativo"}</span></td>
          <td class="actions">
            <button class="btn-primary btn-sm" onclick="window._editProduct(${p.id})">Editar</button>
            <button class="btn-danger btn-sm" onclick="window._deleteProduct(${p.id})">Excluir</button>
          </td>
        </tr>`).join("")}</tbody></table>`;
    } catch (e) { toast(e.message, true); }
  }

  const productFormWrap = document.getElementById("product-form-wrap");
  const productForm = document.getElementById("product-form");

  document.getElementById("btn-new-product").addEventListener("click", () => {
    document.getElementById("product-form-title").textContent = "Novo Produto";
    productForm.reset();
    document.getElementById("pf-id").value = "";
    document.getElementById("pf-active").checked = true;
    productFormWrap.classList.remove("hidden");
  });

  document.getElementById("btn-cancel-product").addEventListener("click", () => productFormWrap.classList.add("hidden"));

  productForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("pf-id").value;
    const body = {
      name: document.getElementById("pf-name").value,
      slug: document.getElementById("pf-slug").value,
      price_display: document.getElementById("pf-price").value,
      description: document.getElementById("pf-desc").value,
      target_audience: document.getElementById("pf-audience").value,
      sort_order: parseInt(document.getElementById("pf-order").value) || 0,
      is_active: document.getElementById("pf-active").checked ? 1 : 0,
    };
    try {
      if (id) await api(`/products/${id}`, { method: "PUT", body: JSON.stringify(body) });
      else await api("/products", { method: "POST", body: JSON.stringify(body) });
      toast(id ? "Produto atualizado!" : "Produto criado!");
      productFormWrap.classList.add("hidden");
      loadProducts();
    } catch (e) { toast(e.message, true); }
  });

  window._editProduct = async function (id) {
    const data = await api("/products");
    const p = data.products.find((x) => x.id === id);
    if (!p) return;
    document.getElementById("product-form-title").textContent = "Editar Produto";
    document.getElementById("pf-id").value = p.id;
    document.getElementById("pf-name").value = p.name;
    document.getElementById("pf-slug").value = p.slug;
    document.getElementById("pf-price").value = p.price_display;
    document.getElementById("pf-desc").value = p.description;
    document.getElementById("pf-audience").value = p.target_audience || "";
    document.getElementById("pf-order").value = p.sort_order;
    document.getElementById("pf-active").checked = !!p.is_active;
    productFormWrap.classList.remove("hidden");
  };

  window._deleteProduct = async function (id) {
    if (!confirm("Excluir este produto?")) return;
    try {
      await api(`/products/${id}`, { method: "DELETE" });
      toast("Produto excluido!");
      loadProducts();
    } catch (e) { toast(e.message, true); }
  };

  // -----------------------------------------------------------------------
  // Skills
  // -----------------------------------------------------------------------
  let allSkills = [];
  let skillFilter = "all";

  async function loadSkills() {
    try {
      const data = await api("/skills");
      allSkills = data.skills;
      renderSkills();
    } catch (e) { toast(e.message, true); }
  }

  function renderSkills() {
    const filtered = skillFilter === "all" ? allSkills : allSkills.filter((s) => s.category === skillFilter);
    const wrap = document.getElementById("skills-list");
    if (!filtered.length) { wrap.innerHTML = "<p style='color:var(--text-muted)'>Nenhuma skill nesta categoria.</p>"; return; }
    const catBadge = (c) => `<span class="badge badge-${c}">${c === "objective" ? "Objetivo" : c === "rule" ? "Regra" : "Comportamento"}</span>`;
    wrap.innerHTML = `<table>
      <thead><tr><th>Nome</th><th>Categoria</th><th>Instrucao</th><th>Status</th><th>Acoes</th></tr></thead>
      <tbody>${filtered.map((s) => `<tr>
        <td><strong>${esc(s.name)}</strong></td>
        <td>${catBadge(s.category)}</td>
        <td><small style="color:var(--text-secondary)">${esc(s.prompt_instruction).substring(0, 80)}...</small></td>
        <td>
          <button class="badge ${s.is_active ? "badge-active" : "badge-inactive"}" style="cursor:pointer;border:none"
            onclick="window._toggleSkill(${s.id}, ${s.is_active ? 0 : 1})">${s.is_active ? "Ativa" : "Inativa"}</button>
        </td>
        <td class="actions">
          <button class="btn-primary btn-sm" onclick="window._editSkill(${s.id})">Editar</button>
          <button class="btn-danger btn-sm" onclick="window._deleteSkill(${s.id})">Excluir</button>
        </td>
      </tr>`).join("")}</tbody></table>`;
  }

  document.querySelectorAll(".tab[data-cat]").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab[data-cat]").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      skillFilter = tab.dataset.cat;
      renderSkills();
    });
  });

  const skillFormWrap = document.getElementById("skill-form-wrap");
  const skillForm = document.getElementById("skill-form");

  document.getElementById("btn-new-skill").addEventListener("click", () => {
    document.getElementById("skill-form-title").textContent = "Nova Skill";
    skillForm.reset();
    document.getElementById("sf-id").value = "";
    document.getElementById("sf-active").checked = true;
    skillFormWrap.classList.remove("hidden");
  });

  document.getElementById("btn-cancel-skill").addEventListener("click", () => skillFormWrap.classList.add("hidden"));

  skillForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("sf-id").value;
    const body = {
      name: document.getElementById("sf-name").value,
      slug: document.getElementById("sf-slug").value,
      category: document.getElementById("sf-category").value,
      description: document.getElementById("sf-desc").value,
      prompt_instruction: document.getElementById("sf-instruction").value,
      sort_order: parseInt(document.getElementById("sf-order").value) || 0,
      is_active: document.getElementById("sf-active").checked ? 1 : 0,
    };
    try {
      if (id) await api(`/skills/${id}`, { method: "PUT", body: JSON.stringify(body) });
      else await api("/skills", { method: "POST", body: JSON.stringify(body) });
      toast(id ? "Skill atualizada!" : "Skill criada!");
      skillFormWrap.classList.add("hidden");
      loadSkills();
    } catch (e) { toast(e.message, true); }
  });

  window._editSkill = function (id) {
    const s = allSkills.find((x) => x.id === id);
    if (!s) return;
    document.getElementById("skill-form-title").textContent = "Editar Skill";
    document.getElementById("sf-id").value = s.id;
    document.getElementById("sf-name").value = s.name;
    document.getElementById("sf-slug").value = s.slug;
    document.getElementById("sf-category").value = s.category;
    document.getElementById("sf-desc").value = s.description;
    document.getElementById("sf-instruction").value = s.prompt_instruction;
    document.getElementById("sf-order").value = s.sort_order;
    document.getElementById("sf-active").checked = !!s.is_active;
    skillFormWrap.classList.remove("hidden");
  };

  window._toggleSkill = async function (id, newState) {
    try {
      await api(`/skills/${id}`, { method: "PUT", body: JSON.stringify({ is_active: newState }) });
      toast(newState ? "Skill ativada!" : "Skill desativada!");
      loadSkills();
    } catch (e) { toast(e.message, true); }
  };

  window._deleteSkill = async function (id) {
    if (!confirm("Excluir esta skill?")) return;
    try {
      await api(`/skills/${id}`, { method: "DELETE" });
      toast("Skill excluida!");
      loadSkills();
    } catch (e) { toast(e.message, true); }
  };

  // -----------------------------------------------------------------------
  // Prompt Config
  // -----------------------------------------------------------------------
  async function loadPromptConfig() {
    try {
      const data = await api("/prompt-config");
      const wrap = document.getElementById("prompt-configs");
      wrap.innerHTML = data.configs.map((c) => `
        <div class="config-card" data-key="${esc(c.config_key)}">
          <h4>${esc(c.label)}</h4>
          <p>${esc(c.description || "")}</p>
          <textarea rows="5">${esc(c.config_value)}</textarea>
          <button class="btn-primary btn-sm" onclick="window._saveConfig('${esc(c.config_key)}', this)">Salvar</button>
        </div>
      `).join("");
      document.getElementById("prompt-preview-wrap").classList.add("hidden");
    } catch (e) { toast(e.message, true); }
  }

  window._saveConfig = async function (key, btn) {
    const card = btn.closest(".config-card");
    const value = card.querySelector("textarea").value;
    try {
      await api(`/prompt-config/${key}`, { method: "PUT", body: JSON.stringify({ config_value: value }) });
      toast("Configuracao salva!");
    } catch (e) { toast(e.message, true); }
  };

  document.getElementById("btn-preview-prompt").addEventListener("click", async () => {
    try {
      const data = await api("/prompt-preview");
      document.getElementById("prompt-preview-text").textContent = data.prompt;
      document.getElementById("prompt-chars").textContent = `${data.char_count} chars`;
      document.getElementById("prompt-tokens").textContent = `~${data.token_estimate} tokens`;
      document.getElementById("prompt-preview-wrap").classList.remove("hidden");
    } catch (e) { toast(e.message, true); }
  });

  // -----------------------------------------------------------------------
  // Leads
  // -----------------------------------------------------------------------
  async function loadLeads(page = 1) {
    try {
      const data = await api(`/leads?page=${page}&per_page=15`);
      const wrap = document.getElementById("leads-list");
      if (!data.leads.length) { wrap.innerHTML = "<p style='color:var(--text-muted)'>Nenhum lead capturado ainda.</p>"; return; }
      wrap.innerHTML = `<table>
        <thead><tr><th>Nome</th><th>Email</th><th>WhatsApp</th><th>Produto</th><th>Data</th></tr></thead>
        <tbody>${data.leads.map((l) => `<tr>
          <td>${esc(l.name || "-")}</td>
          <td>${esc(l.email || "-")}</td>
          <td>${esc(l.whatsapp || "-")}</td>
          <td>${esc(l.product_interest || "-")}</td>
          <td><small>${esc(l.created_at || "-")}</small></td>
        </tr>`).join("")}</tbody></table>`;
      // Pagination
      const pagEl = document.getElementById("leads-pagination");
      if (data.pages > 1) {
        let html = "";
        for (let i = 1; i <= data.pages; i++) {
          html += `<button class="${i === page ? "btn-primary" : "btn-secondary"} btn-sm" onclick="window._loadLeadsPage(${i})">${i}</button>`;
        }
        pagEl.innerHTML = html;
      } else { pagEl.innerHTML = ""; }
    } catch (e) { toast(e.message, true); }
  }

  window._loadLeadsPage = loadLeads;

  // -----------------------------------------------------------------------
  // Utils
  // -----------------------------------------------------------------------
  function esc(str) {
    if (str == null) return "";
    const d = document.createElement("div");
    d.textContent = String(str);
    return d.innerHTML;
  }
})();
