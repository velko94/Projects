const isLocalHost = ["localhost", "127.0.0.1", "0.0.0.0"].includes(window.location.hostname);

window.APP_CONFIG = {
    API_URL: isLocalHost
        ? "http://localhost:8001/api/v1"
        : "https://your-api-id.execute-api.eu-central-1.amazonaws.com/PROD/smart-irrigation-api/api/v1"
};