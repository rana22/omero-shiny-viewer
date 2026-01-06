console.log("omero.js loaded");

async function getOmeroImage() {
  const url = "https://nife-dev.cancer.gov/webgateway/render_thumbnail/11422/";
  checkThumbnailWithImg(url)
      .then(() => {
          // logged in (or image is publicly accessible)
          showOMEROIframe();
      })
      .catch(() => {
          showLoginButton();
  });
};

function checkThumbnailWithImg(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => resolve(true);   // image returned
    img.onerror = () => reject(new Error("Not an image (likely login/HTML or blocked)"));

    // Cache-bust so you don't get a stale result
    const sep = url.includes("?") ? "&" : "?";
    img.src = url + sep + "cb=" + Date.now();
  });
}

function showOMEROIframe() {
  const container = document.getElementById("omero_container");
  container.innerHTML = "";

  const info = document.createElement("div");
  info.textContent = `Logged in`;
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
  getOmeroImage();
});
