/**
 * AgriVerse AI – Master Frontend Client Script
 * Powers all 14 intelligent smart farming modules.
 */

let currentConversationId = null;
let currentLanguage = localStorage.getItem("agriverse_lang") || "en";

document.addEventListener("DOMContentLoaded", () => {
    initSidebar();
    initGlobalLanguage();
    initHealthCheck();
    loadDashboardStats();
    initViewNavigation();

    // Module-specific initializers based on present DOM elements
    if (document.getElementById("dashboardActivitiesList")) initDashboardActivities();
    if (document.getElementById("chatForm")) initChatInterface();
    if (document.getElementById("leafUploadForm")) initPlantDoctor();
    if (document.getElementById("soilPdfForm")) initSoilLab();
    if (document.getElementById("cropMatchForm")) initCropMatch();
    if (document.getElementById("aquaSmartForm")) initAquaSmart();
    if (document.getElementById("schemeQueryForm")) initSchemeNavigator();
    if (document.getElementById("marketTable")) initAgriMarket();
    if (document.getElementById("twinSimulatorForm")) initVirtualFarmTwin();
    if (document.getElementById("calendarTable")) initFarmingCalendar();
    if (document.getElementById("budgetTable")) initFarmBudget();
    if (document.getElementById("settingsProfileForm")) initSettings();
});

// =========================================================================
// 0. SINGLE-PAGE APPLICATION (SPA) TAB NAVIGATION
// =========================================================================
function initViewNavigation() {
    // 1. Sidebar Nav Items
    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", (e) => {
            const targetView = item.getAttribute("data-view") || (item.getAttribute("href") || "").replace(/^#/, "");
            if (targetView) {
                e.preventDefault();
                switchView(targetView);
            }
        });
    });

    // 2. In-page view switch buttons (e.g. on dashboard cards, welcome banner)
    document.querySelectorAll(".btn-view-switch, .service-link[href^='#'], .card-action-btn[href^='#']").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const targetView = btn.getAttribute("data-target") || (btn.getAttribute("href") || "").replace(/^#/, "");
            if (targetView) {
                e.preventDefault();
                switchView(targetView);
            }
        });
    });

    // 3. User profile quick click in header
    document.querySelectorAll(".nav-item-profile").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            switchView("settings");
        });
    });

    // 4. Header Voice toggle button
    const headerVoice = document.getElementById("headerVoiceToggle");
    if (headerVoice) {
        headerVoice.addEventListener("click", () => {
            switchView("chat");
            const btnVoiceInput = document.getElementById("btnVoiceInput");
            if (btnVoiceInput) {
                setTimeout(() => btnVoiceInput.click(), 300);
            }
        });
    }

    // 5. Hash change listener (back/forward in browser history)
    window.addEventListener("hashchange", () => {
        const hash = window.location.hash.replace(/^#/, "");
        if (hash) switchView(hash);
    });

    // 6. Initial view on page load
    let initialView = "dashboard";
    if (window.location.hash) {
        initialView = window.location.hash.replace(/^#/, "");
    } else if (window.SERVER_INITIAL_VIEW) {
        initialView = window.SERVER_INITIAL_VIEW;
    }
    switchView(initialView);
}

function switchView(viewName) {
    if (!viewName) viewName = "dashboard";
    viewName = viewName.replace(/^#/, "").toLowerCase();

    // Map sub-views or aliases
    if (viewName === "chat-history" || viewName === "chatbot") viewName = "chat";
    if (viewName === "risk-radar") viewName = "farm-twin";
    if (viewName === "disease") viewName = "plant-doctor";
    if (viewName === "soil") viewName = "soil-lab";
    if (viewName === "crop") viewName = "crop-match";
    if (viewName === "twin") viewName = "farm-twin";

    const targetEl = document.getElementById(`view-${viewName}`);
    if (!targetEl) {
        viewName = "dashboard";
    }

    // Hide all views and show target
    document.querySelectorAll(".app-view").forEach(v => {
        v.classList.remove("active");
    });
    const finalEl = document.getElementById(`view-${viewName}`);
    if (finalEl) {
        finalEl.classList.add("active");
    }

    // Update active class on sidebar items
    document.querySelectorAll(".nav-item").forEach(item => {
        const itemTarget = item.getAttribute("data-view") || (item.getAttribute("href") || "").replace(/^#/, "");
        item.classList.toggle("active", itemTarget === viewName);
    });

    // Update Header Breadcrumb Title
    const titleMap = {
        "dashboard": "Dashboard",
        "chat": "Agri AI Chat & Consultation",
        "plant-doctor": "Plant Doctor AI – Disease Diagnosis",
        "soil-lab": "Soil Intelligence Lab",
        "crop-match": "CropMatch AI – Recommendation Engine",
        "aquasmart": "AquaSmart – Smart Irrigation Advisor",
        "schemes": "Scheme Navigator – Government Subsidies",
        "market": "AgriMarket Intelligence – Mandi Prices",
        "farm-twin": "Virtual Farm Twin & Risk Radar",
        "calendar": "Smart Farming Calendar",
        "budget": "Farm Budget AI & Cultivation Expenses",
        "settings": "Settings & Farm Profile"
    };
    const headerTitle = document.getElementById("headerTitle");
    if (headerTitle) {
        headerTitle.textContent = titleMap[viewName] || (viewName.charAt(0).toUpperCase() + viewName.slice(1));
    }

    // Close mobile sidebar if open
    const sidebar = document.getElementById("sidebar");
    if (sidebar && window.innerWidth <= 900) {
        sidebar.classList.remove("open");
    }

    // Module-specific on-switch triggers
    if (viewName === "market") {
        const marketTable = document.getElementById("marketTable");
        if (marketTable && (!marketTable.dataset.loaded || marketTable.dataset.loaded === "false")) {
            initAgriMarket();
            marketTable.dataset.loaded = "true";
        }
    } else if (viewName === "calendar") {
        if (typeof loadCalendarActivities === "function") loadCalendarActivities();
    } else if (viewName === "budget") {
        if (typeof loadBudgetLedger === "function") loadBudgetLedger();
    } else if (viewName === "chat") {
        const queryInput = document.getElementById("userQueryInput");
        if (queryInput) setTimeout(() => queryInput.focus(), 200);
    }

    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Update URL hash without pushing unwanted history loops
    if (window.location.hash !== `#${viewName}`) {
        history.replaceState(null, null, `#${viewName}`);
    }
}

// =========================================================================
// 1. GLOBAL UTILITIES & HEALTH
// =========================================================================
function initSidebar() {
    const sidebar = document.getElementById("sidebar");
    const openBtn = document.getElementById("sidebarOpenBtn");
    const closeBtn = document.getElementById("sidebarCloseBtn");
    if (openBtn && sidebar) openBtn.addEventListener("click", () => sidebar.classList.add("open"));
    if (closeBtn && sidebar) closeBtn.addEventListener("click", () => sidebar.classList.remove("open"));
}

function initGlobalLanguage() {
    const langSelect = document.getElementById("languageSelect");
    if (langSelect) {
        langSelect.value = currentLanguage;
        langSelect.addEventListener("change", (e) => {
            currentLanguage = e.target.value;
            localStorage.setItem("agriverse_lang", currentLanguage);
            showToast(`Language set to ${currentLanguage === "ta" ? "தமிழ் (Tamil)" : "English"}`);
        });
    }
}

async function initHealthCheck() {
    const statusBadge = document.getElementById("apiStatusBadge");
    if (!statusBadge) return;
    try {
        const resp = await fetch("/api/health");
        const data = await resp.json();
        if (data.status === "online" && data.gemini_api_configured) {
            statusBadge.innerHTML = `<span class="status-dot pulse-green"></span><span class="status-text">${data.gemini_model} Active</span>`;
        } else {
            statusBadge.innerHTML = `<span class="status-dot" style="background:#f59e0b;"></span><span class="status-text">Local Mode</span>`;
        }
    } catch (e) {
        statusBadge.innerHTML = `<span class="status-dot" style="background:#ef4444;"></span><span class="status-text">Offline</span>`;
    }
}

async function loadDashboardStats() {
    try {
        const resp = await fetch("/api/dashboard/stats");
        const data = await resp.json();
        if (data.success && data.stats) {
            const expEl = document.getElementById("statExpenses");
            const sizeEl = document.getElementById("statFarmSize");
            const cropEl = document.getElementById("statPrimaryCrop");
            const actEl = document.getElementById("statNextActivity");
            if (expEl) expEl.textContent = `₹${data.stats.total_cultivation_cost.toLocaleString("en-IN")}`;
            if (sizeEl) sizeEl.textContent = `${data.stats.farm_size} Acres`;
            if (cropEl) cropEl.textContent = data.stats.primary_crop;
            if (actEl) actEl.textContent = data.stats.next_activity;
        }
    } catch (e) { console.debug("Stats error", e); }
}

function showToast(msg) {
    const old = document.querySelector(".agri-toast");
    if (old) old.remove();
    const t = document.createElement("div");
    t.className = "agri-toast";
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = "0"; setTimeout(() => t.remove(), 300); }, 2500);
}

function formatMarkdownText(text) {
    if (!text) return "";
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    
    // Headers ###
    html = html.replace(/^### (.*$)/gim, '<h4 style="color:var(--forest-800); margin:8px 0 4px;">$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3 style="color:var(--forest-900); margin:12px 0 6px;">$1</h3>');

    // Bullet points
    const lines = html.split("\n");
    let inList = false;
    let result = [];

    for (let line of lines) {
        let trimmed = line.trim();
        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
            if (!inList) {
                result.push("<ul>");
                inList = true;
            }
            result.push(`<li>${trimmed.substring(2)}</li>`);
        } else {
            if (inList) {
                result.push("</ul>");
                inList = false;
            }
            if (trimmed) {
                result.push(`<p>${line}</p>`);
            }
        }
    }
    if (inList) result.push("</ul>");
    return result.join("");
}

// =========================================================================
// 2. DASHBOARD ACTIVITIES & TWIN MODALS
// =========================================================================
function initDashboardActivities() {
    loadDashboardActivitiesList();

    const modalAct = document.getElementById("modalAddActivity");
    const btnOpenAct = document.getElementById("btnOpenAddActivityModal");
    const btnCloseAct = document.getElementById("btnCloseActivityModal");
    const btnCancelAct = document.getElementById("btnCancelActivity");
    const formAct = document.getElementById("formAddActivity");

    if (btnOpenAct && modalAct) btnOpenAct.addEventListener("click", () => {
        document.getElementById("actDate").valueAsDate = new Date();
        modalAct.style.display = "flex";
    });
    if (btnCloseAct) btnCloseAct.addEventListener("click", () => modalAct.style.display = "none");
    if (btnCancelAct) btnCancelAct.addEventListener("click", () => modalAct.style.display = "none");

    if (formAct) {
        formAct.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                crop_name: document.getElementById("actCropName").value,
                activity_name: document.getElementById("actName").value,
                stage: document.getElementById("actStage").value,
                scheduled_date: document.getElementById("actDate").value,
                notes: document.getElementById("actNotes").value
            };
            try {
                const resp = await fetch("/api/calendar/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) {
                    showToast("Activity scheduled successfully!");
                    modalAct.style.display = "none";
                    formAct.reset();
                    loadDashboardActivitiesList();
                    loadDashboardStats();
                }
            } catch (err) { showToast("Failed to schedule activity."); }
        });
    }

    const modalProfile = document.getElementById("modalEditProfile");
    const btnOpenProf = document.getElementById("btnOpenEditProfileModal");
    const btnCloseProf = document.getElementById("btnCloseProfileModal");
    const btnCancelProf = document.getElementById("btnCancelProfile");
    const formProf = document.getElementById("formEditProfile");

    if (btnOpenProf && modalProfile) {
        btnOpenProf.addEventListener("click", async () => {
            try {
                const resp = await fetch("/api/farm-profile");
                const res = await resp.json();
                if (res.success) {
                    const p = res.profile;
                    document.getElementById("editFarmName").value = p.farm_name;
                    document.getElementById("editFarmSize").value = p.farm_size;
                    document.getElementById("editLocation").value = p.location;
                    document.getElementById("editSoilType").value = p.soil_type;
                    document.getElementById("editPrimaryCrop").value = p.primary_crop;
                    document.getElementById("editIrrigation").value = p.irrigation_type;
                    document.getElementById("editWater").value = p.water_availability;
                    modalProfile.style.display = "flex";
                }
            } catch (e) { showToast("Failed to fetch profile"); }
        });
    }
    if (btnCloseProf) btnCloseProf.addEventListener("click", () => modalProfile.style.display = "none");
    if (btnCancelProf) btnCancelProf.addEventListener("click", () => modalProfile.style.display = "none");

    if (formProf) {
        formProf.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                farm_name: document.getElementById("editFarmName").value,
                farm_size: document.getElementById("editFarmSize").value,
                location: document.getElementById("editLocation").value,
                soil_type: document.getElementById("editSoilType").value,
                primary_crop: document.getElementById("editPrimaryCrop").value,
                irrigation_type: document.getElementById("editIrrigation").value,
                water_availability: document.getElementById("editWater").value
            };
            try {
                const resp = await fetch("/api/farm-profile/update", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) {
                    showToast("Farm profile updated!");
                    modalProfile.style.display = "none";
                    updateProfileDOM(res.profile);
                    loadDashboardStats();
                }
            } catch (e) { showToast("Error updating profile"); }
        });
    }
}

async function loadDashboardActivitiesList() {
    const listEl = document.getElementById("dashboardActivitiesList");
    if (!listEl) return;
    try {
        const resp = await fetch("/api/calendar");
        const res = await resp.json();
        if (res.success && res.activities) {
            listEl.innerHTML = "";
            if (res.activities.length === 0) {
                listEl.innerHTML = `<div style="text-align:center; padding:16px; color:#83968b;">No scheduled activities. Click '+ Add Activity' to schedule.</div>`;
                return;
            }
            res.activities.slice(0, 4).forEach(act => {
                const isDone = act.status === "completed";
                const item = document.createElement("div");
                item.className = "timeline-item";
                item.innerHTML = `
                    <div class="timeline-dot ${isDone ? 'dot-completed' : 'dot-upcoming'}"></div>
                    <div class="timeline-content" style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="timeline-date">${act.scheduled_date} &bull; ${act.stage}</span>
                            <button class="btn btn-sm ${isDone ? 'btn-outline-white' : 'btn-primary'}" style="padding:2px 8px; font-size:0.72rem;" onclick="toggleActivityStatus(${act.id})">
                                ${isDone ? '✓ Completed' : 'Mark Done'}
                            </button>
                        </div>
                        <h4 class="timeline-title" style="${isDone ? 'text-decoration:line-through; color:#83968b;' : ''}">${act.activity_name} (${act.crop_name})</h4>
                        <p class="timeline-desc">${act.notes || 'No extra notes'}</p>
                    </div>
                `;
                listEl.appendChild(item);
            });
        }
    } catch (e) { console.debug("Activities loader error", e); }
}

async function toggleActivityStatus(actId) {
    try {
        const resp = await fetch("/api/calendar/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ activity_id: actId })
        });
        const res = await resp.json();
        if (res.success) {
            showToast(`Activity status changed to ${res.new_status}`);
            loadDashboardActivitiesList();
            loadDashboardStats();
            if (document.getElementById("calendarTable")) initFarmingCalendar();
        }
    } catch (e) { showToast("Failed to toggle activity"); }
}

function updateProfileDOM(p) {
    const elName = document.getElementById("profileFarmName");
    const elLoc = document.getElementById("profileLocation");
    const elSize = document.getElementById("profileSize");
    const elSoil = document.getElementById("profileSoil");
    const elIrr = document.getElementById("profileIrrigation");
    const elWater = document.getElementById("profileWater");
    if (elName) elName.textContent = p.farm_name;
    if (elLoc) elLoc.textContent = p.location;
    if (elSize) elSize.textContent = `${p.farm_size} Acres`;
    if (elSoil) elSoil.textContent = p.soil_type;
    if (elIrr) elIrr.textContent = p.irrigation_type;
    if (elWater) elWater.textContent = p.water_availability;
}

// =========================================================================
// 3. AGRI AI CHATBOT
// =========================================================================
function initChatInterface() {
    const chatForm = document.getElementById("chatForm");
    const queryInput = document.getElementById("userQueryInput");
    const chatFeed = document.getElementById("chatFeed");
    const btnNewChat = document.getElementById("btnNewChat");
    const btnClearCurrentChat = document.getElementById("btnClearCurrentChat");
    const btnVoiceInput = document.getElementById("btnVoiceInput");
    const btnRefreshSessions = document.getElementById("btnRefreshSessions");

    loadChatSessions();

    document.querySelectorAll(".lang-pill").forEach(pill => {
        pill.classList.toggle("active", pill.dataset.lang === currentLanguage);
        pill.addEventListener("click", () => {
            document.querySelectorAll(".lang-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            currentLanguage = pill.dataset.lang;
            localStorage.setItem("agriverse_lang", currentLanguage);
            showToast(`Chat language set to ${currentLanguage === "ta" ? "தமிழ்" : "English"}`);
        });
    });

    queryInput.addEventListener("input", () => {
        queryInput.style.height = "auto";
        queryInput.style.height = Math.min(queryInput.scrollHeight, 120) + "px";
    });

    queryInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = queryInput.value.trim();
        if (!message) return;

        queryInput.value = "";
        queryInput.style.height = "auto";

        appendMessage({
            sender: "user",
            content: message,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });

        const typingIndicator = showTypingIndicator();

        try {
            const resp = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: message,
                    conversation_id: currentConversationId,
                    language: currentLanguage
                })
            });
            const data = await resp.json();
            typingIndicator.remove();

            if (data.success) {
                currentConversationId = data.conversation_id;
                appendMessage({
                    sender: "assistant",
                    content: data.response,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });

                if (data.follow_ups && data.follow_ups.length > 0) {
                    renderQuickChips(data.follow_ups);
                }
                loadChatSessions();
            } else {
                appendErrorMessage(data.error || "Failed to receive response.");
            }
        } catch (err) {
            typingIndicator.remove();
            appendErrorMessage("Network error connecting to AgriVerse AI.");
        }
    });

    const chipsWrapper = document.getElementById("quickChipsWrapper");
    if (chipsWrapper) {
        chipsWrapper.addEventListener("click", (e) => {
            const chip = e.target.closest(".quick-chip");
            if (chip) {
                queryInput.value = chip.dataset.prompt || chip.textContent.trim();
                queryInput.focus();
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
    }

    if (btnNewChat) {
        btnNewChat.addEventListener("click", async () => {
            try {
                const resp = await fetch("/api/chat/new", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ language: currentLanguage })
                });
                const data = await resp.json();
                if (data.success) {
                    currentConversationId = data.conversation.id;
                    clearChatFeed();
                    showToast("Started new consultation session");
                    loadChatSessions();
                }
            } catch (err) { console.error("New chat error", err); }
        });
    }

    if (btnClearCurrentChat) {
        btnClearCurrentChat.addEventListener("click", async () => {
            if (!currentConversationId) {
                clearChatFeed();
                showToast("Chat cleared.");
                return;
            }
            if (confirm("Clear this conversation's messages?")) {
                try {
                    await fetch("/api/chat/clear", {
                        method: "DELETE",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ conversation_id: currentConversationId })
                    });
                    clearChatFeed();
                    showToast("Chat messages cleared.");
                    loadChatSessions();
                } catch (e) { console.error("Clear chat error", e); }
            }
        });
    }

    if (btnRefreshSessions) btnRefreshSessions.addEventListener("click", loadChatSessions);
    initChatVoiceInput(btnVoiceInput, queryInput, chatForm);

    const urlParams = new URLSearchParams(window.location.search);
    const queryParam = urlParams.get("q");
    if (queryParam) {
        queryInput.value = queryParam;
        window.history.replaceState({}, document.title, window.location.pathname);
        setTimeout(() => chatForm.dispatchEvent(new Event("submit")), 400);
    }
}

function appendMessage({ sender, content, timestamp }) {
    const chatFeed = document.getElementById("chatFeed");
    if (!chatFeed) return;
    const isBot = sender === "assistant" || sender === "bot";
    const messageEl = document.createElement("div");
    messageEl.className = `chat-message ${isBot ? "bot-message" : "user-message"}`;

    messageEl.innerHTML = `
        <div class="message-avatar"><i class="fa-solid ${isBot ? 'fa-seedling' : 'fa-user'}"></i></div>
        <div class="message-bubble">
            ${isBot ? '<div class="message-sender-name">AgriVerse AI Agronomist</div>' : ''}
            <div class="message-body">${formatMarkdownText(content)}</div>
            <div class="message-tools">
                <span class="message-time">${timestamp || "Just now"}</span>
                ${isBot ? `
                    <button class="tool-btn copy-btn" title="Copy text"><i class="fa-regular fa-copy"></i></button>
                    <button class="tool-btn speak-btn" title="Speak response"><i class="fa-solid fa-volume-high"></i></button>
                ` : ''}
            </div>
        </div>
    `;

    const copyBtn = messageEl.querySelector(".copy-btn");
    if (copyBtn) copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(content).then(() => showToast("Response copied to clipboard!"));
    });

    const speakBtn = messageEl.querySelector(".speak-btn");
    if (speakBtn) speakBtn.addEventListener("click", () => speakText(content, currentLanguage));

    chatFeed.appendChild(messageEl);
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

function showTypingIndicator() {
    const chatFeed = document.getElementById("chatFeed");
    const indicator = document.createElement("div");
    indicator.className = "chat-message bot-message typing-msg";
    indicator.innerHTML = `
        <div class="message-avatar"><i class="fa-solid fa-seedling"></i></div>
        <div class="message-bubble">
            <div class="message-sender-name">AgriVerse AI Thinking...</div>
            <div class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>
        </div>
    `;
    chatFeed.appendChild(indicator);
    chatFeed.scrollTop = chatFeed.scrollHeight;
    return indicator;
}

function renderQuickChips(chips) {
    const container = document.getElementById("chipsContainer");
    if (!container) return;
    container.innerHTML = "";
    chips.forEach(chip => {
        const btn = document.createElement("button");
        btn.className = "quick-chip";
        btn.dataset.prompt = chip;
        btn.textContent = `💡 ${chip}`;
        container.appendChild(btn);
    });
}

function appendErrorMessage(errText) {
    const chatFeed = document.getElementById("chatFeed");
    if (!chatFeed) return;
    const errEl = document.createElement("div");
    errEl.className = "chat-message bot-message";
    errEl.innerHTML = `
        <div class="message-avatar" style="background:#fee2e2; color:#d32f2f;"><i class="fa-solid fa-triangle-exclamation"></i></div>
        <div class="message-bubble" style="border-color:#fca5a5; background:#fff5f5;">
            <div class="message-sender-name" style="color:#d32f2f;">System Notice</div>
            <div class="message-body" style="color:#b91c1c;">${errText}</div>
        </div>
    `;
    chatFeed.appendChild(errEl);
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

function clearChatFeed() {
    const chatFeed = document.getElementById("chatFeed");
    if (!chatFeed) return;
    chatFeed.innerHTML = `
        <div class="chat-message bot-message" data-id="welcome">
            <div class="message-avatar"><i class="fa-solid fa-seedling"></i></div>
            <div class="message-bubble">
                <div class="message-sender-name">AgriVerse AI Companion</div>
                <div class="message-body">
                    <p><strong>Vanakkam & Welcome to a New Consultation! 🌾</strong></p>
                    <p>How can I assist you with your crops, soil, water management, or pest prevention today?</p>
                </div>
                <div class="message-tools"><span class="message-time">Just now</span></div>
            </div>
        </div>
    `;
}

async function loadChatSessions() {
    const listEl = document.getElementById("sessionsList");
    if (!listEl) return;
    try {
        const resp = await fetch("/api/chat/history");
        const data = await resp.json();
        if (data.success && data.conversations) {
            listEl.innerHTML = "";
            if (data.conversations.length === 0) {
                listEl.innerHTML = `<div style="font-size:0.75rem; color:#83968b; padding:10px;">No prior consultations yet.</div>`;
                return;
            }
            data.conversations.forEach(conv => {
                const item = document.createElement("div");
                item.className = `session-item ${conv.id === currentConversationId ? 'active' : ''}`;
                item.innerHTML = `
                    <i class="fa-regular fa-message"></i>
                    <div class="session-info">
                        <span class="session-title">${conv.title || "Agricultural Consultation"}</span>
                        <span class="session-time">${conv.message_count || 0} messages</span>
                    </div>
                `;
                item.addEventListener("click", () => switchConversation(conv.id));
                listEl.appendChild(item);
            });
        }
    } catch (e) { console.debug("Session loader error", e); }
}

async function switchConversation(convId) {
    currentConversationId = convId;
    loadChatSessions();
    try {
        const resp = await fetch(`/api/chat/history?conversation_id=${convId}`);
        const data = await resp.json();
        if (data.success && data.messages) {
            const chatFeed = document.getElementById("chatFeed");
            chatFeed.innerHTML = "";
            data.messages.forEach(msg => {
                appendMessage({
                    sender: msg.sender,
                    content: msg.content,
                    timestamp: new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });
            });
            showToast("Conversation loaded");
        }
    } catch (e) { console.error("Load messages error", e); }
}

function speakText(text, lang = "en") {
    if (!("speechSynthesis" in window)) {
        showToast("Text-to-speech not supported in this browser.");
        return;
    }
    window.speechSynthesis.cancel();
    const clean = text.replace(/[*_#`\-]/g, "");
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = lang === "ta" ? "ta-IN" : "en-IN";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
    showToast("Speaking response...");
}

function initChatVoiceInput(btn, input, form) {
    if (!btn || !input) return;
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) return;
    const rec = new SpeechRec();
    rec.continuous = false;
    let recActive = false;

    btn.addEventListener("click", () => {
        rec.lang = currentLanguage === "ta" ? "ta-IN" : "en-IN";
        if (!recActive) {
            rec.start();
            btn.classList.add("recording");
            recActive = true;
        } else {
            rec.stop();
            btn.classList.remove("recording");
            recActive = false;
        }
    });

    rec.onresult = (e) => {
        input.value = e.results[0][0].transcript;
        btn.classList.remove("recording");
        recActive = false;
        showToast(`Recognized voice query`);
        setTimeout(() => form.dispatchEvent(new Event("submit")), 400);
    };
    rec.onerror = () => { btn.classList.remove("recording"); recActive = false; };
}

// =========================================================================
// 4. PLANT DOCTOR AI
// =========================================================================
function initPlantDoctor() {
    const dropzone = document.getElementById("leafDropzone");
    const fileInput = document.getElementById("leafFileInput");
    const promptBox = document.getElementById("dropzonePrompt");
    const previewBox = document.getElementById("imagePreviewContainer");
    const previewImg = document.getElementById("imagePreview");
    const btnRemove = document.getElementById("btnRemoveImage");
    const btnAnalyze = document.getElementById("btnAnalyzeLeaf");
    const form = document.getElementById("leafUploadForm");
    const analysisBody = document.getElementById("analysisBody");
    const statusBadge = document.getElementById("analysisStatusBadge");
    const followUpSec = document.getElementById("followUpSection");

    if (!dropzone || !fileInput) return;
    dropzone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            const r = new FileReader();
            r.onload = (ev) => {
                previewImg.src = ev.target.result;
                promptBox.style.display = "none";
                previewBox.style.display = "block";
                btnAnalyze.disabled = false;
            };
            r.readAsDataURL(e.target.files[0]);
        }
    });
    if (btnRemove) {
        btnRemove.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            previewBox.style.display = "none";
            promptBox.style.display = "block";
            btnAnalyze.disabled = true;
        });
    }

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;
            const formData = new FormData();
            formData.append("leaf_image", fileInput.files[0]);
            formData.append("crop_notes", document.getElementById("cropNotes").value);
            formData.append("language", document.getElementById("doctorLanguage").value);

            statusBadge.textContent = "Inspecting with Gemini...";
            btnAnalyze.disabled = true;
            analysisBody.innerHTML = `
                <div style="text-align:center; padding:40px;">
                    <i class="fa-solid fa-microscope fa-spin" style="font-size:3rem; color:var(--emerald-500);"></i>
                    <h4 style="margin-top:14px;">Analyzing Visible Symptoms...</h4>
                </div>
            `;

            try {
                const resp = await fetch("/api/plant-doctor/analyze", { method: "POST", body: formData });
                const data = await resp.json();
                btnAnalyze.disabled = false;
                if (data.success) {
                    statusBadge.textContent = "Diagnostic Complete";
                    analysisBody.innerHTML = `
                        <div style="font-size:0.92rem; line-height:1.7;">${formatMarkdownText(data.analysis)}</div>
                        <div class="card-alert alert-info" style="margin-top:16px;">
                            <i class="fa-solid fa-circle-exclamation"></i>
                            <span>${data.disclaimer}</span>
                        </div>
                    `;
                    if (followUpSec) followUpSec.style.display = "block";
                } else {
                    statusBadge.textContent = "Error";
                    analysisBody.innerHTML = `<div class="card-alert" style="background:#fee2e2; color:#d32f2f;">${data.error}</div>`;
                }
            } catch (err) {
                btnAnalyze.disabled = false;
                statusBadge.textContent = "Connection Error";
                analysisBody.innerHTML = `<div class="card-alert" style="background:#fee2e2; color:#d32f2f;">Network failure reaching Gemini vision API.</div>`;
            }
        });
    }

    const btnFollowUp = document.getElementById("btnSendDoctorFollowUp");
    const inputFollowUp = document.getElementById("doctorFollowUpInput");
    if (btnFollowUp && inputFollowUp) {
        btnFollowUp.addEventListener("click", () => {
            const q = inputFollowUp.value.trim();
            if (!q) return;
            window.location.href = `/chat?q=${encodeURIComponent("Plant Health Follow-up: " + q)}`;
        });
    }
}

// =========================================================================
// 5. SOIL INTELLIGENCE LAB
// =========================================================================
let npkChartInstance = null;

function initSoilLab() {
    const tabPdf = document.getElementById("tabUploadPdf");
    const tabManual = document.getElementById("tabManualInput");
    const formPdf = document.getElementById("soilPdfForm");
    const formManual = document.getElementById("soilManualForm");

    const dropzone = document.getElementById("soilDropzone");
    const fileInput = document.getElementById("soilFileInput");
    const promptBox = document.getElementById("soilDropzonePrompt");
    const infoBox = document.getElementById("pdfSelectedInfo");
    const nameLabel = document.getElementById("selectedPdfName");
    const btnRemove = document.getElementById("btnRemovePdf");
    const btnAnalyze = document.getElementById("btnAnalyzeSoilPdf");

    if (tabPdf && tabManual) {
        tabPdf.addEventListener("click", () => {
            tabPdf.classList.add("active");
            tabManual.classList.remove("active");
            formPdf.style.display = "block";
            formManual.style.display = "none";
        });
        tabManual.addEventListener("click", () => {
            tabManual.classList.add("active");
            tabPdf.classList.remove("active");
            formPdf.style.display = "none";
            formManual.style.display = "block";
        });
    }

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                nameLabel.textContent = e.target.files[0].name;
                promptBox.style.display = "none";
                infoBox.style.display = "block";
                btnAnalyze.disabled = false;
            }
        });
        if (btnRemove) {
            btnRemove.addEventListener("click", (e) => {
                e.stopPropagation();
                fileInput.value = "";
                infoBox.style.display = "none";
                promptBox.style.display = "block";
                btnAnalyze.disabled = true;
            });
        }
    }

    if (formPdf) {
        formPdf.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;
            const formData = new FormData();
            formData.append("soil_pdf", fileInput.files[0]);
            formData.append("crop_name", document.getElementById("soilCropName").value);
            formData.append("language", document.getElementById("soilLanguage").value);

            showToast("Extracting parameters via PyMuPDF...");
            try {
                const resp = await fetch("/api/soil-lab/upload", { method: "POST", body: formData });
                const res = await resp.json();
                if (res.success) renderSoilResults(res);
                else showToast(res.error || "Analysis failed");
            } catch (err) { showToast("Error uploading soil card"); }
        });
    }

    if (formManual) {
        formManual.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                ph: document.getElementById("mPh").value,
                electrical_conductivity: document.getElementById("mEc").value,
                organic_carbon: document.getElementById("mOc").value,
                nitrogen: document.getElementById("mN").value,
                phosphorus: document.getElementById("mP").value,
                potassium: document.getElementById("mK").value,
                crop_name: "Paddy / Rice",
                language: currentLanguage
            };
            try {
                const resp = await fetch("/api/soil-lab/evaluate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) renderSoilResults(res);
            } catch (err) { showToast("Evaluation error"); }
        });
    }

    renderNPKChart(240, 18.5, 210);
}

function renderSoilResults(res) {
    const m = res.metrics;
    document.getElementById("cardPhVal").textContent = m.ph.value;
    document.getElementById("cardPhStatus").textContent = m.ph.status;
    document.getElementById("cardNVal").textContent = `${m.nitrogen.value} kg/ha`;
    document.getElementById("cardNStatus").textContent = m.nitrogen.status;
    document.getElementById("cardPVal").textContent = `${m.phosphorus.value} kg/ha`;
    document.getElementById("cardPStatus").textContent = m.phosphorus.status;

    document.getElementById("soilRecommendationText").innerHTML = formatMarkdownText(res.recommendation);
    renderNPKChart(m.nitrogen.value, m.phosphorus.value, m.potassium.value);
    showToast("Soil analysis updated!");
}

function renderNPKChart(n, p, k) {
    const ctx = document.getElementById("soilNpkChart");
    if (!ctx) return;
    if (npkChartInstance) npkChartInstance.destroy();

    npkChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
            datasets: [
                {
                    label: 'Sample Measurement (kg/ha)',
                    data: [n, p, k],
                    backgroundColor: ['#40916c', '#52b788', '#74c69d'],
                    borderRadius: 6
                },
                {
                    label: 'ICAR Optimal Baseline (kg/ha)',
                    data: [350, 20, 200],
                    backgroundColor: '#e2ece5',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// =========================================================================
// 6. CROPMATCH AI
// =========================================================================
function initCropMatch() {
    const form = document.getElementById("cropMatchForm");
    const outputBox = document.getElementById("cropRecommendationOutput");
    const badge = document.getElementById("cropResultBadge");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            badge.textContent = "Matching...";
            outputBox.innerHTML = `
                <div style="text-align:center; padding:40px;">
                    <i class="fa-solid fa-wheat-awn fa-spin" style="font-size:3rem; color:var(--emerald-500);"></i>
                    <h4 style="margin-top:14px;">Evaluating Agronomic Fit...</h4>
                </div>
            `;

            const payload = {
                location: document.getElementById("cropLocation").value,
                soil_type: document.getElementById("cropSoilType").value,
                ph: document.getElementById("cropPh").value,
                season: document.getElementById("cropSeason").value,
                water: document.getElementById("cropWater").value,
                previous_crop: document.getElementById("cropPrevCrop").value,
                language: document.getElementById("cropLang").value
            };

            try {
                const resp = await fetch("/api/crop-match/recommend", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) {
                    badge.textContent = "Matched";
                    outputBox.innerHTML = `<div style="font-size:0.92rem; line-height:1.7;">${formatMarkdownText(res.recommendations)}</div>`;
                } else {
                    badge.textContent = "Error";
                    outputBox.innerHTML = `<div class="card-alert" style="background:#fee2e2; color:#d32f2f;">${res.error}</div>`;
                }
            } catch (err) {
                badge.textContent = "Connection Error";
                outputBox.innerHTML = `<div class="card-alert" style="background:#fee2e2; color:#d32f2f;">Network error reaching recommendation engine.</div>`;
            }
        });
    }
}

// =========================================================================
// 7. AQUASMART IRRIGATOR
// =========================================================================
function initAquaSmart() {
    const form = document.getElementById("aquaSmartForm");
    const output = document.getElementById("aquaResultBody");
    const badge = document.getElementById("aquaStatusBadge");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            badge.textContent = "Calculating...";
            output.innerHTML = `
                <div style="text-align:center; padding:40px;">
                    <i class="fa-solid fa-droplet fa-spin" style="font-size:3rem; color:var(--emerald-500);"></i>
                    <h4 style="margin-top:14px;">Optimizing Water Guidance...</h4>
                </div>
            `;

            const payload = {
                crop: document.getElementById("aquaCrop").value,
                stage: document.getElementById("aquaStage").value,
                soil: document.getElementById("aquaSoil").value,
                system: document.getElementById("aquaSystem").value,
                language: document.getElementById("aquaLang").value
            };

            try {
                const resp = await fetch("/api/aquasmart/guidance", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) {
                    badge.textContent = "Guidance Ready";
                    output.innerHTML = `<div style="font-size:0.92rem; line-height:1.7;">${formatMarkdownText(res.guidance)}</div>`;
                }
            } catch (err) { showToast("Error calculating water guidance"); }
        });
    }
}

// =========================================================================
// 8. SCHEME NAVIGATOR RAG
// =========================================================================
function initSchemeNavigator() {
    const formQuery = document.getElementById("schemeQueryForm");
    const formUpload = document.getElementById("schemeUploadForm");
    const answerBox = document.getElementById("schemeAnswerBody");
    const citationsBox = document.getElementById("schemeCitationsBox");
    const citationsList = document.getElementById("citationsList");
    const badge = document.getElementById("ragStatusBadge");

    if (formUpload) {
        formUpload.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById("schemePdfFile");
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append("scheme_pdf", fileInput.files[0]);

            showToast("Indexing PDF into FAISS vector store...");
            try {
                const resp = await fetch("/api/schemes/upload", { method: "POST", body: formData });
                const res = await resp.json();
                if (res.success) {
                    showToast(res.message);
                    document.getElementById("uploadStatusMsg").textContent = res.message;
                    formUpload.reset();
                }
            } catch (err) { showToast("Failed to index PDF"); }
        });
    }

    if (formQuery) {
        formQuery.addEventListener("submit", async (e) => {
            e.preventDefault();
            const q = document.getElementById("schemeQuestionInput").value.trim();
            if (!q) return;

            badge.textContent = "FAISS Searching...";
            answerBox.innerHTML = `
                <div style="text-align:center; padding:30px;">
                    <i class="fa-solid fa-file-shield fa-spin" style="font-size:2.8rem; color:var(--emerald-500);"></i>
                    <h4 style="margin-top:12px;">Retrieving Document Context...</h4>
                </div>
            `;
            if (citationsBox) citationsBox.style.display = "none";

            try {
                const resp = await fetch("/api/schemes/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: q, language: document.getElementById("schemeLang").value })
                });
                const res = await resp.json();
                if (res.success) {
                    badge.textContent = "Grounded Answer";
                    answerBox.innerHTML = `<div style="font-size:0.92rem; line-height:1.7;">${formatMarkdownText(res.answer)}</div>`;
                    
                    if (res.citations && res.citations.length > 0 && citationsBox && citationsList) {
                        citationsList.innerHTML = "";
                        res.citations.forEach(c => {
                            const item = document.createElement("div");
                            item.innerHTML = `<strong>📄 ${c.document} (Page ${c.page}):</strong> <em>"${c.text_snippet}..."</em>`;
                            citationsList.appendChild(item);
                        });
                        citationsBox.style.display = "block";
                    }
                } else {
                    answerBox.innerHTML = `<div class="card-alert" style="background:#fee2e2; color:#d32f2f;">${res.error}</div>`;
                }
            } catch (err) { showToast("RAG query failed"); }
        });
    }

    document.querySelectorAll(".quick-chip[data-prompt]").forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.dataset.prompt;
            const input = document.getElementById("schemeQuestionInput");
            if (input) {
                input.value = prompt;
                if (formQuery) formQuery.dispatchEvent(new Event("submit"));
            }
        });
    });
}

// =========================================================================
// 9. AGRIMARKET INTELLIGENCE
// =========================================================================
let marketChartInstance = null;

function initAgriMarket() {
    loadMarketPrices();

    const btnFilter = document.getElementById("btnFilterMarket");
    const inputSearch = document.getElementById("marketSearchInput");
    const selectState = document.getElementById("marketStateFilter");

    if (btnFilter) {
        btnFilter.addEventListener("click", () => {
            loadMarketPrices(inputSearch.value, selectState.value);
        });
    }

    loadHistoricalChart("Paddy (Common)");
}

async function loadMarketPrices(query = "", state = "") {
    const tbody = document.getElementById("marketTableBody");
    if (!tbody) return;

    try {
        const resp = await fetch(`/api/market/search?query=${encodeURIComponent(query)}&state=${encodeURIComponent(state)}`);
        const res = await resp.json();
        if (res.success && res.prices) {
            tbody.innerHTML = "";
            res.prices.forEach(p => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${p.commodity}</strong><br><small style="color:#83968b;">${p.category}</small></td>
                    <td>${p.mandi}<br><small style="color:#83968b;">${p.state}</small></td>
                    <td><strong style="color:var(--forest-800); font-size:1.05rem;">₹${p.modal_price.toLocaleString("en-IN")}</strong> / Qtl</td>
                    <td><small>₹${p.min_price} - ₹${p.max_price}</small></td>
                    <td><button class="btn btn-sm btn-outline-white" style="color:var(--forest-800); border-color:var(--border-color);" onclick="loadHistoricalChart('${p.commodity}')"><i class="fa-solid fa-chart-line"></i> Trend</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) { console.debug("Market load error", e); }
}

async function loadHistoricalChart(commodity) {
    const label = document.getElementById("chartCommodityLabel");
    if (label) label.textContent = commodity;

    try {
        const resp = await fetch(`/api/market/trend?commodity=${encodeURIComponent(commodity)}`);
        const res = await resp.json();
        if (res.success && res.chart_data) {
            const ctx = document.getElementById("marketTrendChart");
            if (!ctx) return;
            if (marketChartInstance) marketChartInstance.destroy();

            marketChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: res.chart_data.labels,
                    datasets: [{
                        label: `${commodity} (₹/Quintal)`,
                        data: res.chart_data.prices,
                        borderColor: '#2d6a4f',
                        backgroundColor: 'rgba(82, 183, 136, 0.15)',
                        fill: true,
                        tension: 0.3,
                        pointBackgroundColor: '#40916c'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: false } }
                }
            });
        }
    } catch (e) { console.debug("Chart error", e); }
}

// =========================================================================
// 10. VIRTUAL FARM TWIN & RISK RADAR
// =========================================================================
function initVirtualFarmTwin() {
    const form = document.getElementById("twinSimulatorForm");
    const outputBox = document.getElementById("simulationOutputBox");
    const outputText = document.getElementById("simulationResultText");
    const btnRun = document.getElementById("btnRunSimulation");

    document.querySelectorAll(".quick-chip[data-scenario]").forEach(chip => {
        chip.addEventListener("click", () => {
            document.getElementById("scenarioInput").value = chip.dataset.scenario;
            if (form) form.dispatchEvent(new Event("submit"));
        });
    });

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const scenario = document.getElementById("scenarioInput").value.trim();
            if (!scenario) return;

            btnRun.disabled = true;
            btnRun.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Simulating...`;
            outputBox.style.display = "block";
            outputText.innerHTML = `<p style="color:var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Projecting agronomic stress, soil moisture depletion, and yield risk...</p>`;

            try {
                const resp = await fetch("/api/twin/simulate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ scenario: scenario, language: document.getElementById("simLanguage").value })
                });
                const res = await resp.json();
                btnRun.disabled = false;
                btnRun.innerHTML = `<i class="fa-solid fa-play"></i> Run Simulation`;
                if (res.success) {
                    outputText.innerHTML = formatMarkdownText(res.simulation);
                    showToast("Twin simulation completed!");
                }
            } catch (err) {
                btnRun.disabled = false;
                btnRun.innerHTML = `<i class="fa-solid fa-play"></i> Run Simulation`;
                showToast("Simulation error");
            }
        });
    }
}

// =========================================================================
// 11. FARMING CALENDAR
// =========================================================================
function initFarmingCalendar() {
    loadCalendarTable();
    const form = document.getElementById("calendarAddForm");
    if (form) {
        document.getElementById("calDate").valueAsDate = new Date();
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                crop_name: document.getElementById("calCrop").value,
                activity_name: document.getElementById("calActivity").value,
                stage: document.getElementById("calStage").value,
                scheduled_date: document.getElementById("calDate").value,
                notes: document.getElementById("calNotes").value
            };
            try {
                const resp = await fetch("/api/calendar/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) {
                    showToast("Activity added to calendar!");
                    form.reset();
                    document.getElementById("calDate").valueAsDate = new Date();
                    loadCalendarTable();
                }
            } catch (err) { showToast("Error scheduling activity"); }
        });
    }
}

async function loadCalendarTable() {
    const tbody = document.getElementById("calendarTableBody");
    const badge = document.getElementById("activityCountBadge");
    if (!tbody) return;

    try {
        const resp = await fetch("/api/calendar");
        const res = await resp.json();
        if (res.success && res.activities) {
            tbody.innerHTML = "";
            if (badge) badge.textContent = `${res.activities.length} Activities`;
            if (res.activities.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px; color:#83968b;">No activities logged.</td></tr>`;
                return;
            }
            res.activities.forEach(act => {
                const isDone = act.status === "completed";
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${act.crop_name}</strong><br><small style="color:#83968b;">${act.stage}</small></td>
                    <td><strong>${act.activity_name}</strong><br><small style="color:#83968b;">${act.notes || ''}</small></td>
                    <td>${act.scheduled_date}</td>
                    <td><span class="badge-status ${isDone ? 'badge-verified' : ''}" style="${!isDone ? 'background:#fef3c7; color:#d97706;' : ''}">${isDone ? '✓ Completed' : 'Pending'}</span></td>
                    <td>
                        <button class="btn btn-sm ${isDone ? 'btn-outline-white' : 'btn-primary'}" style="padding:3px 8px; font-size:0.75rem;" onclick="toggleActivityStatus(${act.id})">${isDone ? 'Undo' : 'Complete'}</button>
                        <button class="btn btn-sm btn-outline-danger" style="padding:3px 8px; font-size:0.75rem;" onclick="deleteActivity(${act.id})"><i class="fa-solid fa-trash-can"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) { console.debug("Calendar load error", e); }
}

async function deleteActivity(actId) {
    if (confirm("Delete this activity?")) {
        try {
            await fetch("/api/calendar/delete", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ activity_id: actId })
            });
            showToast("Activity deleted");
            loadCalendarTable();
            loadDashboardStats();
        } catch (e) { showToast("Error deleting"); }
    }
}

// =========================================================================
// 12. FARM BUDGET AI
// =========================================================================
let budgetDonutInstance = null;

function initFarmBudget() {
    loadBudgetLedger();
    const form = document.getElementById("budgetAddForm");
    if (form) {
        document.getElementById("expDate").valueAsDate = new Date();
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                category: document.getElementById("expCategory").value,
                item_name: document.getElementById("expItem").value,
                amount: document.getElementById("expAmount").value,
                expense_date: document.getElementById("expDate").value,
                notes: document.getElementById("expNotes").value
            };
            try {
                const resp = await fetch("/api/budget/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.success) {
                    showToast("Expense recorded!");
                    form.reset();
                    document.getElementById("expDate").valueAsDate = new Date();
                    loadBudgetLedger();
                    loadDashboardStats();
                }
            } catch (err) { showToast("Error saving expense"); }
        });
    }

    const btnExport = document.getElementById("btnExportCsv");
    if (btnExport) {
        btnExport.addEventListener("click", exportBudgetCsv);
    }
}

async function loadBudgetLedger() {
    const tbody = document.getElementById("budgetTableBody");
    if (!tbody) return;

    try {
        const resp = await fetch("/api/budget");
        const res = await resp.json();
        if (res.success && res.budget) {
            const b = res.budget;
            document.getElementById("budTotal").textContent = `₹${b.total_expenses.toLocaleString("en-IN")}`;
            document.getElementById("budCostPerAcre").textContent = `₹${b.cost_per_acre.toLocaleString("en-IN")}`;
            document.getElementById("budAcreLabel").textContent = `Based on ${b.farm_size} Acres`;
            document.getElementById("budItemCount").textContent = `${b.records.length} entries`;

            tbody.innerHTML = "";
            if (b.records.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#83968b;">No expenses logged.</td></tr>`;
                return;
            }

            b.records.forEach(r => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${r.expense_date}</td>
                    <td><span class="badge-status badge-verified">${r.category}</span></td>
                    <td><strong>${r.item_name}</strong></td>
                    <td><strong style="color:var(--forest-800);">₹${r.amount.toLocaleString("en-IN")}</strong></td>
                    <td><small style="color:#83968b;">${r.notes || '-'}</small></td>
                    <td><button class="btn btn-sm btn-outline-danger" style="padding:2px 8px; font-size:0.75rem;" onclick="deleteExpense(${r.id})"><i class="fa-solid fa-trash-can"></i></button></td>
                `;
                tbody.appendChild(tr);
            });

            renderBudgetChart(b.category_breakdown);
        }
    } catch (e) { console.debug("Budget error", e); }
}

function renderBudgetChart(catMap) {
    const ctx = document.getElementById("budgetDonutChart");
    if (!ctx) return;
    if (budgetDonutInstance) budgetDonutInstance.destroy();

    const labels = Object.keys(catMap);
    const data = Object.values(catMap);

    budgetDonutInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#1b4332', '#2d6a4f', '#40916c', '#52b788', '#74c69d', '#b7e4c7', '#d8f3dc']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right' } }
        }
    });
}

async function deleteExpense(expId) {
    if (confirm("Delete this expense record?")) {
        try {
            await fetch("/api/budget/delete", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ expense_id: expId })
            });
            showToast("Expense removed");
            loadBudgetLedger();
            loadDashboardStats();
        } catch (e) { showToast("Error deleting expense"); }
    }
}

async function exportBudgetCsv() {
    try {
        const resp = await fetch("/api/budget");
        const res = await resp.json();
        if (res.success && res.budget.records) {
            let csv = "ID,Date,Category,Item,Amount,Notes\n";
            res.budget.records.forEach(r => {
                csv += `"${r.id}","${r.expense_date}","${r.category}","${r.item_name}","${r.amount}","${r.notes || ''}"\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `agriverse_farm_expenses_${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            showToast("Expense report downloaded!");
        }
    } catch (e) { showToast("Export failed"); }
}

// =========================================================================
// 13. SETTINGS
// =========================================================================
function initSettings() {
    const form = document.getElementById("settingsProfileForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const name = document.getElementById("setFarmerName").value;
            const loc = document.getElementById("setFarmerLocation").value;
            const lang = document.getElementById("setDefaultLang").value;
            
            const navName = document.getElementById("navUserName");
            const navLoc = document.getElementById("navUserLocation");
            if (navName) navName.textContent = name;
            if (navLoc) navLoc.textContent = loc;
            
            localStorage.setItem("agriverse_lang", lang);
            showToast("Settings saved successfully!");
        });
    }
}

// Expose functions called by inline HTML event attributes
window.switchView = switchView;
window.toggleActivityStatus = toggleActivityStatus;
window.deleteActivity = deleteActivity;
window.deleteExpense = deleteExpense;
window.loadHistoricalChart = loadHistoricalChart;
