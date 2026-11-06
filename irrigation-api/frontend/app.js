const API_URL = "http://localhost:8001/api/v1";

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");

    if (token && username && !isTokenExpired(token)) {
        showLoggedInView(username);
    } else {
        document.getElementById("login-trigger-section").style.display = "block";
        document.getElementById("user-info").style.display = "none";
    }
    await fetchZones();
});

// for managing the modals (open/close)
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.style.display = show ? "block" : "none";

    if (show) {
        //clear errors on open
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
        errorDiv.style.color = "lightgreen";
        errorDiv.textContent = "Успешна регистрация! Пренасочване към вход...";

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
    document.getElementById("login-trigger-section").style.display = "block";
    document.getElementById("user-info").style.display = "none";
    fetchZones();
}

function showLoggedInView(username) {
    document.getElementById("login-trigger-section").style.display = "none";
    document.getElementById("user-info").style.display = "flex";
    document.getElementById("current-username").textContent = username;
}

async function fetchZones() {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    const isLogged = token && username && !isTokenExpired(token);

    const container = document.getElementById("zones-container");
    container.innerHTML = "";

    if (!isLogged) {
        const dummyZones = [
            { name: "Домати (примерна)", status: "off", watered: "Никога" },
            { name: "Пипер (примерна)", status: "off", watered: "Никога" }
        ];

        dummyZones.forEach(zone => {
            renderZoneCard(zone, container, true); // true за примерна/неактивна карта
        });
        return;
    }

    try {
        const response = await fetch(`${API_URL}/zones`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            if (response.status === 401) {
                logoutUser();
                return;
            }
            throw new Error("Грешка при зареждане");
        }

        const zones = await response.json();
        const zonesArray = Array.isArray(zones) ? zones : Object.entries(zones).map(([id, z]) => ({ id, ...z }));

        zonesArray.forEach(zone => {
            renderZoneCard(zone, container, false);
        });
    } catch (error) {
        console.error("Грешка при зареждане на данните:", error);
    }
}

// Помощна функция за рендване с HTML <template>
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
        cardDiv.style.opacity = "0.75";
        statusEl.className = "status off";
        statusEl.textContent = "СПРЯНО";
        wateredEl.textContent = `Последно: ${zone.watered}`;
        toggleBtn.textContent = "Влез за управление";
        toggleBtn.setAttribute("onclick", "openLoginModal()");
        deleteBtn.style.display = "none"; // Скриваме изтриването за примерните
    } else {
        cardDiv.setAttribute("data-zone-id", zone.id);
        const isWorking = zone.status === "on";
        statusEl.className = isWorking ? "status on" : "status off";
        statusEl.textContent = isWorking ? "РАБОТИ" : "СПРЯНО";

        const lastWatered = zone.last_watered && zone.last_watered !== "Never" ? zone.last_watered : "Никога";
        wateredEl.textContent = `Последно: ${lastWatered}`;

        toggleBtn.setAttribute("onclick", `toggleZone(${zone.id})`);
        deleteBtn.setAttribute("onclick", `deleteZone(${zone.id})`);
    }

    container.appendChild(clone);
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

            if (res.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("username");
                logoutUser();
                alert("Сесията е изтекла или невалиден токен. Моля, влезте отново!");
                openLoginModal();
                return;
            }

            throw new Error(errData.detail || "Грешка при превключване");
        }

        await fetchZones();
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

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expirationTime = payload.exp * 1000;
        return Date.now() >= expirationTime;
    } catch (e) {
        return true;
    }
}

async function addZone() {
    const zoneNameInput = document.getElementById('newZoneName');
    const errorDiv = document.getElementById('add-zone-error');
    const name = zoneNameInput.value.trim();
    if (errorDiv) errorDiv.textContent = "";

    if (!name) {
        if (errorDiv) errorDiv.textContent = "Моля, въведете име на зоната!";
        return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Моля, влезте в системата!");
        openLoginModal();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/zones`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name: name })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Грешка при създаване на зоната");
        }

        zoneNameInput.value = '';
        closeAddZoneModal();
        await fetchZones();
    } catch (err) {
        if (errorDiv) errorDiv.textContent = err.message;
    }
}

async function deleteZone(zoneId) {
    if (!confirm("Сигурни ли сте, че искате да изтриете тази зона?")) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Моля, влезте в системата!");
        openLoginModal();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/zones/${zoneId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error("Грешка при изтриване на зоната");
        }

        await fetchZones();
    } catch (err) {
        alert(err.message);
    }
}