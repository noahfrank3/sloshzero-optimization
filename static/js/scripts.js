import { config } from "config.js";

async function sendHttpRequest(endpoint, method, headers = {}, body = null) {
    try {
        const options = { method, headers };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${config.URL}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error making HTTP request:", error);
        throw error;
    }
}

window.getTrialData = async function(APIKey) {
    const response = await sendHttpRequest(
        "/user/get-trial-data",
        "GET",
        {"api-key": APIKey}
    );
    document.getElementById("trial-data-text").textContent = response.params;
}

window.sendAPIKey = async function() {
    const APIKey = document.getElementById("api-key").value;
    await sendHttpRequest("/user/check-api-key", "GET", {"api-key": APIKey});

    await window.getTrialData(APIKey);

    document.getElementById("trial-data").style.display = "flex";
    document.getElementById("objectives").style.display = "flex";
    document.getElementById("user-buttons").style.display = "flex";

    document.getElementById("api-key").readOnly = true;
}

window.sendObjectives = async function() {
    const APIKey = document.getElementById("api-key").value;
    const objectives = document.getElementById("objectives-input").value;

    await sendHttpRequest(
        "/user/complete-trial",
        "POST",
        {"api-key": APIKey},
        {"objectives": objectives}
    );

    document.getElementById("objectives-input").value = "";
    await window.getTrialData(APIKey);
}

window.sendHeadAPIKey = async function() {
    const APIKey = document.getElementById("head-api-key").value;
    await sendHttpRequest("/admin/check-api-key", "GET", {"api-key": APIKey})

    document.getElementById("add-trials").style.display = "flex";
    document.getElementById("user-operations").style.display = "flex";
    document.getElementById("admin-buttons").style.display = "flex";
    document.getElementById("logs").style.display = "flex";

    document.getElementById("head-api-key").readOnly = true;
}

window.addTrials = async function() {
    const APIKey = document.getElementById("head-api-key").value;
    const numTrials = document.getElementById("num-trials").value;

    await sendHttpRequest(
        "/admin/add-trials",
        "POST",
        {"api-key": APIKey},
        {"numTrials": numTrials}
    );

    document.getElementById("num-trials").value = "";
}

window.createUser = async function() {
    const APIKey = document.getElementById("head-api-key").value;
    const name = document.getElementById("create-user-name").value;

    await sendHttpRequest(
        "/admin/create-user",
        "POST",
        {"api-key": APIKey},
        {"name": name}
    );

    document.getElementById("create-user-name").value = "";
}

window.deleteUser = async function() {
    const APIKey = document.getElementById("head-api-key").value;
    const name = document.getElementById("delete-user-name").value;

    await sendHttpRequest(
        "/admin/delete-user",
        "POST",
        {"api-key": APIKey},
        {"name": name}
    );

    document.getElementById("delete-user-name").value = "";
}

window.getAPIKey = async function() {
    const APIKey = document.getElementById("head-api-key").value;
    const name = document.getElementById("get-api-key-name").value;

    const response = await sendHttpRequest(
        "/admin/get-api-key",
        "POST",
        {"api-key": APIKey},
        {"name": name}
    );

    document.getElementById("get-api-key-name").value = "";
    document.getElementById("log-text").value = response.APIKey;
}

window.downloadResults = async function() {
    const response = await sendHttpRequest("/public/download-results", "GET");
    const blob = await response.blob();
    const downloadURL = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadURL;
    a.download = "results.json";
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
}

window.pauseExperiment = async function() {
    const APIKey = document.getElementById("head-api-key")?.value || document.getElementById("api-key").value;
    await sendHttpRequest("/shared/pause-experiment", "GET", {"api-key": APIKey});
}

window.resetExperiment = async function() {
    const APIKey = document.getElementById("head-api-key")?.value || document.getElementById("api-key").value;
    await sendHttpRequest("/shared/reset-experiment", "GET", {"api-key": APIKey});
}
