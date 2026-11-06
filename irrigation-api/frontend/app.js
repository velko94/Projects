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
            const cardHTML = `
                <div class="card" style="opacity: 0.75;">
                    <h3 class="zone-name">${zone.name}</h3>
                    <div class="status off">СПРЯНО</div>
                    <p class="zone-watered">Последно: ${zone.watered}</p>
                    <button onclick="openLoginModal()" style="background-color: #555; cursor: pointer;">Влез за управление</button>
                </div>
            `;
            container.innerHTML += cardHTML;
        });
        return;
    }

    try {
        const response = await fetch(`${API_URL}/zones`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("username");
                document.getElementById("login-trigger-section").style.display = "block";
                document.getElementById("user-info").style.display = "none";
                await fetchZones();
                return;
            }
            throw new Error("Грешка при зареждане");
        }

        const zones = await response.json();
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
                    <button onclick="deleteZone(${zone.id})" style="background-color: #d9534f; margin-top: 5px;">Изтрий</button>
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

function openAddZoneModal() {
    const err = document.getElementById("add-zone-error");
    if (err) err.textContent = "";
    document.getElementById("newZoneName").value = "";
    document.getElementById("add-zone-modal").style.display = "block";
}

function closeAddZoneModal() {
    document.getElementById("add-zone-modal").style.display = "none";
}