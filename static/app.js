const listElement = document.querySelector("#conversation-list");
const countElement = document.querySelector("#conversation-count");
const detailElement = document.querySelector("#detail");
const searchInput = document.querySelector("#search-input");
const itemTemplate = document.querySelector("#conversation-item-template");
const turnTemplate = document.querySelector("#turn-template");

let selectedId = null;
let searchTimer = null;

function formatDate(value) {
  if (!value) return "Sin fecha";
  const normalized = value.includes("T") ? value : `${value.replace(" ", "T")}Z`;
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("es", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function titleFor(conversation) {
  return conversation.summary || conversation.repository || "Conversación sin título";
}

async function fetchJson(url) {
  const response = await fetch(url);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "No se pudo cargar la información");
  }
  return payload;
}

function showError(message) {
  detailElement.replaceChildren();
  const state = document.createElement("div");
  state.className = "empty-state error";
  const title = document.createElement("h2");
  title.textContent = "No se pudieron cargar las conversaciones";
  const description = document.createElement("p");
  description.textContent = message;
  state.append(title, description);
  detailElement.append(state);
}

async function loadConversations(query = "") {
  listElement.setAttribute("aria-busy", "true");
  try {
    const payload = await fetchJson(`/api/conversations?q=${encodeURIComponent(query)}`);
    renderConversationList(payload.conversations);
  } catch (error) {
    listElement.replaceChildren();
    countElement.textContent = "No disponible";
    showError(error.message);
  } finally {
    listElement.removeAttribute("aria-busy");
  }
}

function renderConversationList(conversations) {
  listElement.replaceChildren();
  countElement.textContent = `${conversations.length} ${conversations.length === 1 ? "conversación" : "conversaciones"}`;

  if (!conversations.length) {
    const empty = document.createElement("p");
    empty.className = "list-empty";
    empty.textContent = "No hay resultados.";
    listElement.append(empty);
    return;
  }

  for (const conversation of conversations) {
    const item = itemTemplate.content.firstElementChild.cloneNode(true);
    item.dataset.id = conversation.id;
    item.classList.toggle("selected", conversation.id === selectedId);
    item.querySelector(".conversation-title").textContent = titleFor(conversation);
    item.querySelector(".conversation-meta").textContent =
      `${conversation.turn_count} ${conversation.turn_count === 1 ? "turno" : "turnos"} · ${conversation.branch || conversation.host_type || "Local"}`;
    item.querySelector(".conversation-date").textContent = formatDate(
      conversation.updated_at || conversation.created_at,
    );
    item.addEventListener("click", () => loadConversation(conversation.id));
    listElement.append(item);
  }
}

async function loadConversation(id) {
  selectedId = id;
  document.querySelectorAll(".conversation-item").forEach((item) => {
    item.classList.toggle("selected", item.dataset.id === id);
  });
  detailElement.setAttribute("aria-busy", "true");

  try {
    const payload = await fetchJson(`/api/conversations/${encodeURIComponent(id)}`);
    renderConversation(payload.conversation);
  } catch (error) {
    showError(error.message);
  } finally {
    detailElement.removeAttribute("aria-busy");
  }
}

function renderConversation(conversation) {
  detailElement.replaceChildren();

  const header = document.createElement("header");
  header.className = "detail-header";
  const title = document.createElement("h2");
  title.textContent = titleFor(conversation);
  const metadata = document.createElement("p");
  metadata.className = "detail-meta";
  metadata.textContent = [
    conversation.repository,
    conversation.branch,
    formatDate(conversation.updated_at || conversation.created_at),
  ].filter(Boolean).join(" · ");
  header.append(title, metadata);
  detailElement.append(header);

  if (!conversation.turns.length) {
    const empty = document.createElement("p");
    empty.className = "list-empty";
    empty.textContent = "Esta sesión no contiene mensajes guardados.";
    detailElement.append(empty);
    return;
  }

  for (const turn of conversation.turns) {
    const element = turnTemplate.content.firstElementChild.cloneNode(true);
    const userMessage = element.querySelector(".user-message");
    const assistantMessage = element.querySelector(".assistant-message");
    element.querySelector(".user-content").textContent = turn.user_message || "";
    element.querySelector(".assistant-content").textContent = turn.assistant_response || "";
    userMessage.hidden = !turn.user_message;
    assistantMessage.hidden = !turn.assistant_response;
    detailElement.append(element);
  }
}

searchInput.addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => loadConversations(searchInput.value.trim()), 250);
});

loadConversations();
