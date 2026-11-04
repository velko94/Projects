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
        const zones = await response.json();

        const container = document.getElementById("zones-container");
        container.innerHTML = ""; // Изчистваме старите статични карти

        // Ако бекендът връща обект или масив, го адаптираме:
        const zonesArray = Array.isArray(zones) ? zones : Object.entries(zones).map(([id, z]) => ({ id, ...z }));

        zonesArray.forEach(zone => {
            const isWorking = zone.status === "on";
            const statusClass = isWorking ? "status on" : "status off";
            const statusText = isWorking ? "РАБОТИ" : "СПРЯНО";
            const lastWatered = zone.last_watered && zone.last_watered !== "Never"
                ? zone.last_watered
                : "Никога";

            const cardHTML = `
                <div class="card" data-zone-id="${zone.id}">
                    <h3 class="zone-name">${zone.name}</h3>
                    <div class="${statusClass}">${statusText}</div>
                    <p class="zone-watered">Последно: ${lastWatered}</p>
                    <button onclick="toggleZone(${zone.id})">Пусни / Спри</button>
                </div>
            `;
            container.innerHTML += cardHTML;
        });
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
    };

    try {
        const res = await fetch(`${API_URL}/zones/${zoneId}/toggle`, {
            method: "POST",
            headers: headers
        });

        if (!res.ok) {
            const errData = await res.json();

            // Ако грешката е свързана с JWT токена (изтекъл или невалиден), тогава трием сесията
            if (res.status === 401 && errData.detail !== "Wrong api key") {
                localStorage.removeItem("access_token");
                localStorage.removeItem("username");
                logoutUser();
                alert("Сесията е изтекла или невалиден токен. Моля, влезте отново!");
                openLoginModal();
                return;
            }

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