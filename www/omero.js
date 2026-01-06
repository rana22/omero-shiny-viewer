console.log("omero.js loaded");

console.log("omero.js loaded");

async function verifyOMEROLogin() {
  try {
    showOMEROIframe("data.username");
    const response = await fetch("https://nife-dev.cancer.gov/metadata/api/verify", {
      method: "GET",
      credentials: "include",
      headers: { "Accept": "application/json" }
    });

    // if (!response.ok) {
    //   throw new Error(`HTTP ${response.status}`);
    // }

    // const data = await response.json();
    // console.log("verify_login response:", data);

    // if (data.isLoggedIn) {
    //   showOMEROIframe(data.username);
    // } else {
    //   showLoginButton();
    // }

  } catch (err) {
    console.error("Login verification failed:", err);
    showLoginButton();
  }
}

function showOMEROIframe(username) {
  const container = document.getElementById("omero_container");
  container.innerHTML = "";

  const info = document.createElement("div");
  info.textContent = `Logged in as ${username}`;
  info.style.marginBottom = "8px";

  const iframe = document.createElement("iframe");
  iframe.src = "https://nife-dev.cancer.gov/webgateway/render_thumbnail/11422";
  iframe.style.width = "100%";
  iframe.style.height = "800px";
  iframe.style.border = "0";

  container.appendChild(info);
  container.appendChild(iframe);
}

function showLoginButton() {
  const container = document.getElementById("omero_container");
  container.innerHTML = "";

  const btn = document.createElement("a");
  btn.textContent = "Log in to OMERO";
  btn.href = "https://nife-dev.cancer.gov/omero_plus/login/?url=%2Fwebclient%2F";
  btn.target = "_blank";
  btn.className = "btn btn-primary";

  container.appendChild(btn);
}

document.addEventListener("DOMContentLoaded", () => {
  verifyOMEROLogin();
});
