const API_URL = "http://localhost:8001/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");

    if (token && username) {
        showLoggedInView(username);
    } else {
        logoutUser();
    }
    fetchZones();
});

function openLoginModal() {
    document.getElementById("login-error").textContent = "";
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("login-modal").style.display = "block";
}

function closeLoginModal() {
    document.getElementById("login-modal").style.display = "none";
}

function openRegisterModal() {
    document.getElementById("reg-error").textContent = "";
    document.getElementById("reg-username").value = "";
    document.getElementById("reg-password").value = "";
    document.getElementById("register-modal").style.display = "block";
}

function closeRegisterModal() {
    document.getElementById("register-modal").style.display = "none";
}

/// Четем грешките директно от бЕкенд Pydantic отговора (включително regex валидациите за специални символи)
async function parseErrorResponse(response) {
    try {
        const errData = await response.json();
        if (typeof errData.detail === "string") {
            return errData.detail;
        } else if (Array.isArray(errData.detail)) {
            // Тук хващаме грешките от Pydantic рутера (като regex несъответствията) и ги обединяваме
            return errData.detail.map(e => e.msg || JSON.stringify(e)).join(", ");
        }
        return "Възникна грешка.";
    } catch {
        return "Грешка при връзка със сървъра.";
    }
}

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

        closeRegisterModal();
        openLoginModal();
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
    } catch (err) {
        errorDiv.textContent = err.message;
    }
}

function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    document.getElementById("login-trigger-section").style.display = "block";
    document.getElementById("user-info").style.display = "none";
}

function showLoggedInView(username) {
    document.getElementById("login-trigger-section").style.display = "none";
    document.getElementById("user-info").style.display = "flex";
    document.getElementById("current-username").textContent = username;
}

async function fetchZones() {
    try {
        const response = await fetch(`${API_URL}/zones`);
        const zonesData = await response.json();

        for (const [id, zone] of Object.entries(zonesData)) {
            const card = document.querySelector(`.card[data-zone-id="${id}"]`);
            if (!card) continue;

            const nameEl = card.querySelector(".zone-name");
            const statusEl = card.querySelector(".status");
            const wateredEl = card.querySelector(".zone-watered");

            if (nameEl) nameEl.textContent = zone.name;

            const lastWateredText = zone.last_watered && zone.last_watered !== "Never"
                ? zone.last_watered
                : "Никога";
            if (wateredEl) wateredEl.textContent = `Последно: ${lastWateredText}`;

            if (statusEl) {
                if (zone.status === "on") {
                    statusEl.className = "status on";
                    statusEl.textContent = "РАБОТИ";
                } else {
                    statusEl.className = "status off";
                    statusEl.textContent = "СПРЯНО";
                }
            }
        }
    } catch (error) {
        console.error("Грешка при зареждане на данните:", error);
    }
}

async function toggleZone(zoneId) {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Моля, влезте в системата, за да управлявате зоните!");
        openLoginModal();
        return;
    }

    const headers = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
        "X-API-KEY": "SuperSecretKey123"
    };

    try {
        const res = await fetch(`${API_URL}/zones/${zoneId}/toggle`, {
            method: "POST",
            headers: headers
        });

        if (res.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("username");
            logoutUser();
            alert("Сесията е изтекла или невалиден токен. Моля, влезте отново!");
            openLoginModal();
            return;
        }

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Грешка при превключване");
        }

        fetchZones();
    } catch (err) {
        alert(err.message);
    }
}

function togglePasswordVisibility(fieldId) {
    const passwordInput = document.getElementById(fieldId);
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
}