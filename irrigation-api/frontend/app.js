/**
 * Frontend application logic for the Smart Irrigation system.
 * Built with Vanilla JavaScript, modular API wrapper, centralized auth handling,
 * and dynamic UI rendering.
 */

const API_URL = "http://localhost:8001/api/v1";

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");

    if (token && username && !isTokenExpired(token)) {
        showLoggedInView(username);
    } else {
        setLoggedOutView();
    }
    await fetchZones();
});

/**
 * Centralized API fetch wrapper.
 * Automatically injects headers, handles authorization, and catches expired sessions.
 */
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        if (isTokenExpired(token)) {
            handleSessionExpiry();
            throw new Error("Session expired. Please log in again.");
        }
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        handleSessionExpiry();
        throw new Error("Unauthorized access. Please log in.");
    }

    return response;
}

/**
 * Handles expired sessions by clearing storage and resetting UI state.
 */
function handleSessionExpiry() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    setLoggedOutView();
    openLoginModal();
}

function setLoggedOutView() {
    const loginTrigger = document.getElementById("login-trigger-section");
    const userInfo = document.getElementById("user-info");
    if (loginTrigger) loginTrigger.style.display = "block";
    if (userInfo) userInfo.style.display = "none";
}

function showLoggedInView(username) {
    const loginTrigger = document.getElementById("login-trigger-section");
    const userInfo = document.getElementById("user-info");
    const currentUsername = document.getElementById("current-username");

    if (loginTrigger) loginTrigger.style.display = "none";
    if (userInfo) userInfo.style.display = "flex";
    if (currentUsername) currentUsername.textContent = username;
}

// Modal Management Utility
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.style.display = show ? "block" : "none";

    if (show) {
        const errorEl = modal.querySelector(".error-msg, [id$='error']");
        if (errorEl) errorEl.textContent = "";

        const inputEl = modal.querySelector("input");
        if (inputEl) inputEl.value = "";
    }
}

function openLoginModal() { toggleModal("login-modal", true); }
function closeLoginModal() { toggleModal("login-modal", false); }

function openRegisterModal() { toggleModal("register-modal", true); }
function closeRegisterModal() { toggleModal("register-modal", false); }

function openAddZoneModal() { toggleModal("add-zone-modal", true); }
function closeAddZoneModal() { toggleModal("add-zone-modal", false); }

async function parseErrorResponse(response) {
    try {
        const errData = await response.json();
        if (typeof errData.detail === "string") {
            return errData.detail;
        } else if (Array.isArray(errData.detail)) {
            return errData.detail.map(e => e.msg || JSON.stringify(e)).join(", ");
        }
        return "An unexpected error occurred.";
    } catch {
        return "Server connection error.";
    }
}

// Authentication Actions
async function registerUser() {
    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;
    const errorDiv = document.getElementById("reg-error");
    errorDiv.textContent = "";

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const errorMsg = await parseErrorResponse(response);
            document.getElementById("reg-password").value = "";
            throw new Error(errorMsg);
        }

        errorDiv.style.color = "lightgreen";
        errorDiv.textContent = "Registration successful! Redirecting to login...";

        setTimeout(() => {
            closeRegisterModal();
            openLoginModal();
            document.getElementById("login-username").value = username;
            errorDiv.style.color = "";
        }, 1500);
    } catch (err) {
        errorDiv.textContent = err.message;
    }
}

async function loginUser() {
    const usernameInput = document.getElementById("login-username").value;
    const passwordInput = document.getElementById("login-password").value;
    const errorDiv = document.getElementById("login-error");
    errorDiv.textContent = "";

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });

        if (!response.ok) {
            const errorMsg = await parseErrorResponse(response);
            document.getElementById("login-password").value = "";
            throw new Error(errorMsg);
        }

        const data = await response.json();
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("username", usernameInput);

        showLoggedInView(usernameInput);
        closeLoginModal();

        document.getElementById("login-username").value = "";
        document.getElementById("login-password").value = "";

        await fetchZones();
    } catch (err) {
        errorDiv.textContent = err.message;
    }
}

function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    setLoggedOutView();
    fetchZones();
}

// Zone Operations
async function fetchZones() {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    const isLogged = token && username && !isTokenExpired(token);

    const container = document.getElementById("zones-container");
    container.innerHTML = "";

    if (!isLogged) {
        const dummyZones = [
            { name: "Tomatoes (Sample)", status: "off", watered: "Never" },
            { name: "Peppers (Sample)", status: "off", watered: "Never" }
        ];

        dummyZones.forEach(zone => renderZoneCard(zone, container, true));
        return;
    }

    try {
        const response = await apiFetch("/zones", { method: "GET" });
        const zones = await response.json();
        const zonesArray = Array.isArray(zones) ? zones : Object.entries(zones).map(([id, z]) => ({ id, ...z }));

        zonesArray.forEach(zone => renderZoneCard(zone, container, false));
    } catch (error) {
        console.error("Error fetching zones:", error);
    }
}

function renderZoneCard(zone, container, isDummy = false) {
    const template = document.getElementById("zone-card-template");
    const clone = template.content.cloneNode(true);

    const cardDiv = clone.querySelector(".card");
    const nameEl = clone.querySelector(".zone-name");
    const statusEl = clone.querySelector(".zone-status");
    const wateredEl = clone.querySelector(".zone-watered");
    const toggleBtn = clone.querySelector(".btn-toggle");
    const deleteBtn = clone.querySelector(".btn-delete");

    nameEl.textContent = zone.name;

    if (isDummy) {
        cardDiv.classList.add("sample-card"); // Използваме CSS клас вместо inline стил
        statusEl.className = "status off";
        statusEl.textContent = "OFF";
        wateredEl.textContent = `Last watered: ${zone.watered}`;
        toggleBtn.textContent = "Login to control";
        toggleBtn.setAttribute("onclick", "openLoginModal()");
        deleteBtn.style.display = "none";
    } else {
        cardDiv.setAttribute("data-zone-id", zone.id);
        const isWorking = zone.status === "on";
        statusEl.className = isWorking ? "status on" : "status off";
        statusEl.textContent = isWorking ? "RUNNING" : "OFF";

        const lastWatered = zone.last_watered && zone.last_watered !== "Never" ? zone.last_watered : "Never";
        wateredEl.textContent = `Last watered: ${lastWatered}`;

        toggleBtn.setAttribute("onclick", `toggleZone(${zone.id})`);
        deleteBtn.setAttribute("onclick", `deleteZone(${zone.id})`);
    }

    container.appendChild(clone);
}

async function toggleZone(zoneId) {
    try {
        await apiFetch(`/zones/${zoneId}/toggle`, { method: "POST" });
        await fetchZones();
    } catch (err) {
        alert(err.message);
    }
}

async function addZone() {
    const zoneNameInput = document.getElementById('newZoneName');
    const errorDiv = document.getElementById('add-zone-error');
    const name = zoneNameInput.value.trim();
    if (errorDiv) errorDiv.textContent = "";

    if (!name) {
        if (errorDiv) errorDiv.textContent = "Please enter a zone name!";
        return;
    }

    try {
        const response = await apiFetch("/zones", {
            method: 'POST',
            body: JSON.stringify({ name: name })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Failed to create zone.");
        }

        zoneNameInput.value = '';
        closeAddZoneModal();
        await fetchZones();
    } catch (err) {
        if (errorDiv) errorDiv.textContent = err.message;
    }
}

async function deleteZone(zoneId) {
    if (!confirm("Are you sure you want to delete this zone?")) return;

    try {
        const response = await apiFetch(`/zones/${zoneId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error("Failed to delete zone.");
        }

        await fetchZones();
    } catch (err) {
        alert(err.message);
    }
}

// Helpers
function togglePasswordVisibility(fieldId) {
    const passwordInput = document.getElementById(fieldId);
    if (!passwordInput) return;
    passwordInput.type = passwordInput.type === "password" ? "text" : "password";
}

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expirationTime = payload.exp * 1000;
        return Date.now() >= expirationTime;
    } catch (e) {
        return true;
    }
}