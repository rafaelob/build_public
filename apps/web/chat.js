/**
 * VibeCoding Chat — Frontend logic
 */
(function () {
  "use strict";

  const API_URL = "/api/chat";

  // --- DOM refs ---
  const toggle = document.getElementById("chat-toggle");
  const window_ = document.getElementById("chat-window");
  const closeBtn = document.getElementById("chat-close");
  const messagesEl = document.getElementById("chat-messages");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");

  let sessionId = localStorage.getItem("vc_session") || null;
  let isWaiting = false;

  // --- Helpers ---
  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addMessage(text, role) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
  }

  function setWaiting(state) {
    isWaiting = state;
    sendBtn.disabled = state;
    input.disabled = state;
  }

  // --- Chat open/close ---
  let hasOpened = false;

  toggle.addEventListener("click", () => {
    window_.classList.toggle("hidden");
    if (!hasOpened) {
      hasOpened = true;
      addMessage(
        "Oi! Eu sou a Bia, atendente virtual da VibeCoding! \u{1F44B}\n\nQuer aprender a construir software com IA? Me conta: o que te trouxe aqui hoje?",
        "bot"
      );
    }
    if (!window_.classList.contains("hidden")) {
      input.focus();
    }
  });

  closeBtn.addEventListener("click", () => {
    window_.classList.add("hidden");
  });

  // --- Send message ---
  async function sendMessage() {
    const text = input.value.trim();
    if (!text || isWaiting) return;

    input.value = "";
    addMessage(text, "user");
    setWaiting(true);

    const typingEl = addMessage("Digitando...", "bot typing");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: text,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();

      // Salva session
      sessionId = data.session_id;
      localStorage.setItem("vc_session", sessionId);

      // Remove typing, mostra resposta
      typingEl.remove();
      addMessage(data.response, "bot");
    } catch (err) {
      console.error("Chat error:", err);
      typingEl.remove();
      addMessage(
        "Ops, tive um problema de conexao. Tenta de novo em alguns segundos?",
        "bot"
      );
    } finally {
      setWaiting(false);
      input.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
})();
