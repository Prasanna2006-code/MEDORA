const API_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {

// =========================
// PAGE NAVIGATION
// =========================

const pageLinks = {
    dashboard: "dashboard.html",
    triage: "emergency-triage.html",
    queue: "priority-queue.html",
    patients: "patients.html",
    reassessment: "reassessment.html",
    history: "history.html",
    unidentified: "unidentified-patient.html",
    settings: "settings.html"
};

function navigateTo(page) {
    if (pageLinks[page]) {
        window.location.href = pageLinks[page];
    }
}

// =========================
// NAVBAR BUTTONS
// =========================

const navButtons = document.querySelectorAll("[data-page]");

navButtons.forEach(button => {
    button.addEventListener("click", () => {
        const page = button.dataset.page;
        navigateTo(page);
    });
});

// Support common IDs if data-page is not used
const navigationMap = {
    dashboardBtn: "dashboard",
    triageBtn: "triage",
    queueBtn: "queue",
    patientsBtn: "patients",
    reassessmentBtn: "reassessment",
    historyBtn: "history",
    unidentifiedBtn: "unidentified",
    settingsBtn: "settings"
};

Object.entries(navigationMap).forEach(([id, page]) => {
    const button = document.getElementById(id);

    if (button) {
        button.addEventListener("click", () => {
            navigateTo(page);
        });
    }
});

// =========================
// LOGO / HOME
// =========================

const logo = document.querySelector(".brand");

if (logo) {
    logo.style.cursor = "pointer";

    logo.addEventListener("click", () => {
        navigateTo("dashboard");
    });
}

// =========================
// BACK BUTTONS
// =========================

const backButtons = document.querySelectorAll("[data-back]");

backButtons.forEach(button => {
    button.addEventListener("click", () => {
        window.history.back();
    });
});

// =========================
// PAGE-SPECIFIC BUTTONS
// =========================

const addPatientBtn = document.getElementById("addPatientBtn");

if (addPatientBtn) {
    addPatientBtn.addEventListener("click", () => {
        navigateTo("triage");
    });
}

const viewQueueBtn = document.getElementById("viewQueueBtn");

if (viewQueueBtn) {
    viewQueueBtn.addEventListener("click", () => {
        navigateTo("queue");
    });
}

const resultAddPatientBtn = document.getElementById("resultAddPatientBtn");

if (resultAddPatientBtn) {
    resultAddPatientBtn.addEventListener("click", () => {
        navigateTo("triage");
    });
}

// =========================
// ACTIVE NAVIGATION
// =========================

const currentPage = window.location.pathname
    .split("/")
    .pop()
    .toLowerCase();

const activePageMap = {
    "index.html": "dashboard",
    "": "dashboard",
    "dashboard.html": "dashboard",
    "emergency-triage.html": "triage",
    "priority-queue.html": "queue",
    "patients.html": "patients",
    "reassessment.html": "reassessment",
    "history.html": "history",
    "unidentified-patient.html": "unidentified",
    "settings.html": "settings"
};

const activePage = activePageMap[currentPage];

if (activePage) {
    document.querySelectorAll("[data-page]").forEach(button => {
        if (button.dataset.page === activePage) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }
    });
}

// =========================
// BACKEND CONNECTION STATUS
// =========================

const systemStatus = document.getElementById("systemStatus");

async function checkBackend() {
    if (!systemStatus) return;

    try {
        const response = await fetch(`${API_URL}/health`);

        if (response.ok) {
            systemStatus.textContent = "System Online";
            systemStatus.classList.add("online");
            systemStatus.classList.remove("offline");
        } else {
            throw new Error("Backend unavailable");
        }

    } catch (error) {
        systemStatus.textContent = "System Offline";
        systemStatus.classList.add("offline");
        systemStatus.classList.remove("online");

        console.error("Backend connection error:", error);
    }
}

checkBackend();

// =========================
// GLOBAL API HELPER
// =========================

window.MEDORA = {
    API_URL,

    navigateTo,

    async get(endpoint) {
        const response = await fetch(`${API_URL}${endpoint}`);

        if (!response.ok) {
            throw new Error(`GET ${endpoint} failed: ${response.status}`);
        }

        return await response.json();
    },

    async post(endpoint, data) {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`POST ${endpoint} failed: ${response.status}`);
        }

        return await response.json();
    },

    async put(endpoint, data) {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`PUT ${endpoint} failed: ${response.status}`);
        }

        return await response.json();
    },

    async delete(endpoint) {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error(`DELETE ${endpoint} failed: ${response.status}`);
        }

        return await response.json();
    }
};

console.log("MEDORA script.js loaded");
console.log("Current page:", currentPage);
console.log("API:", API_URL);

});