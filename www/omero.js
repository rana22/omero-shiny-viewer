console.log("omero.js loaded");

function checkThumbnailWithImg(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => resolve(true);   // image returned
    img.onerror = () => reject(new Error("Not an image (likely login/HTML or blocked)"));

    // Cache-bust so you don't get a stale result
    const sep = url.includes("?") ? "&" : "?";
    img.src = url + sep + "cb=" + Date.now();
  });
};

const OMERO_BASE = 'https://nife-dev.cancer.gov';
const OMERO_WEBCLIENT_BASE = "https://nife-dev.cancer.gov/webclient"; // webclient base
// Common OMERO.webclient pattern:
function buildOmeroViewerUrl(imageId) {
  // If your OMERO expects a different pattern, change this line only.
  return `${OMERO_WEBCLIENT_BASE}/render_thumbnail/${imageId}`;
}

// --- 404 image (inline SVG data URI) ---
function get404DataUri(message) {
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" width="900" height="260">
    <rect width="100%" height="100%" fill="#f8d7da"/>
    <rect x="18" y="18" width="864" height="224" rx="12" fill="#ffffff" stroke="#f5c2c7"/>
    <text x="60" y="110" font-family="system-ui, -apple-system, Segoe UI, Roboto, Arial" font-size="72" font-weight="800" fill="#842029">404</text>
    <text x="60" y="160" font-family="system-ui, -apple-system, Segoe UI, Roboto, Arial" font-size="22" fill="#842029">${message}</text>
    <text x="60" y="200" font-family="system-ui, -apple-system, Segoe UI, Roboto, Arial" font-size="16" fill="#842029">Enter a valid Image ID and try again.</text>
  </svg>`;
  return "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg.trim());
}

// function showNotFound(container, reasonText = "Image ID not found") {
//   // Clear viewer area and show a 404-style image + text
//   const viewerArea = container.querySelector("#omero_viewer_area");
//   viewerArea.innerHTML = "";

//   const img = document.createElement("img");
// //   img.src = get404DataUri(reasonText);
//   img.alt = reasonText;
//   img.style.width = "100%";
//   img.style.maxWidth = "900px";
//   img.style.display = "block";
//   img.style.borderRadius = "8px";
//   img.style.border = "1px solid #f5c2c7";

//   const wrap = document.createElement("div");
//   wrap.style.display = "flex";
//   wrap.style.justifyContent = "center";
//   wrap.appendChild(img);

//   viewerArea.appendChild(wrap);
// }

function displayImage (container, url) {
    const viewerArea = container.querySelector("#omero_viewer_area");
    viewerArea.innerHTML = "";

    const iframe = document.createElement("iframe");
    iframe.src = url;
    iframe.style.width = "100%";
    iframe.style.height = "80px";
    iframe.style.border = "0";

    viewerArea.appendChild(iframe);
};

function displayIviewer(container, imageId) {
    console.log('display iviewer');
    const iviewerArea = container.querySelector("#omero_iviewer_area");
    iviewerArea.innerHTML = "";
    const url = `${OMERO_BASE}/iviewer/?images=${imageId}`;
    const iviewerframe = document.createElement("iframe");
    iviewerframe.src = url;
    iviewerframe.style.width = "100%";
    iviewerframe.style.height = "900px";
    iviewerframe.style.border = "0";

    iviewerArea.appendChild(iviewerframe);
}

function loadImageIntoIframe(container, imageId) {
  const url = buildOmeroViewerUrl(imageId)
  checkThumbnailWithImg(url)
    .then(() => {
      displayImage(container, url);
      displayIviewer(container, imageId);
    })
    .catch(err => {
      console.log(imageId);
      // showNotFound(container);
      const viewerArea = container.querySelector("#omero_viewer_area");
      viewerArea.innerHTML = "";
      const iviewerArea = container.querySelector("#omero_iviewer_area");
      iviewerArea.innerHTML = "";
      showErrorContent(viewerArea);
  })
}

/**
 * showOMEROIframe(username)
 * Renders:
 * - header "Logged in as ..."
 * - input + button to choose Image ID
 * - iframe viewer area
 * If Image ID is missing/invalid => shows 404 image
 */
function showOMEROIframe() {
  const container = document.getElementById("omero_container");
  if (!container) {
    console.error("Missing #omero_container in DOM");
    return;
  }
  container.innerHTML = "";

  // Header line
  const info = document.createElement("div");
  info.textContent = "Provide valid image id to view images from OMERO";
  info.style.margin = "0 0 10px 0";
  info.style.fontSize = "20px";

  // Control panel
  const controls = document.createElement("div");
  controls.style.display = "flex";
  controls.style.gap = "10px";
  controls.style.alignItems = "center";
  controls.style.marginBottom = "12px";

  const label = document.createElement("span");
  label.textContent = "Image ID:";
  label.style.fontSize = "14px";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "e.g., 11422";
  input.inputMode = "numeric";
  input.style.padding = "8px 10px";
  input.style.border = "1px solid #ccc";
  input.style.borderRadius = "6px";
  input.style.width = "180px";

  const btn = document.createElement("button");
  btn.textContent = "View Image";
  btn.className = "btn btn-primary";

  // Viewer area
  const viewerArea = document.createElement("div");
  viewerArea.id = "omero_viewer_area";

  const iviewerArea = document.createElement("div");
  iviewerArea.id = "omero_iviewer_area";

  // Helper: validate and load
  const onView = () => {
    const raw = (input.value || "").trim();
    // If empty => 404 image
    if (!raw) {
    //   showNotFound(container, "Provide Image ID");
      viewerArea.innerHTML = "";
      iviewerArea.innerHTML = "";
      showErrorContent(viewerArea);
      return;
    }

    // Numeric check (OMERO image IDs are typically integers)
    const imageId = Number(raw);
    if (!Number.isInteger(imageId) || imageId <= 0) {
    //   showNotFound(container, `Image ID not found (${raw})`);
      viewerArea.innerHTML = "";
      iviewerArea.innerHTML = "";
      showErrorContent(viewerArea);
      return;
    }

    // Load iframe viewer
    loadImageIntoIframe(container, imageId);
  };

  btn.addEventListener("click", onView);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") onView();
  });

  controls.appendChild(label);
  controls.appendChild(input);
  controls.appendChild(btn);

  container.appendChild(info);
  container.appendChild(controls);
  container.appendChild(viewerArea);
  container.appendChild(iviewerArea);

  // Initial state: show 404-style prompt until user enters an ID
//   showNotFound(container, "Image ID not found (enter an ID)");
}

function showErrorContent(viewerArea) {
//   const container = document.getElementById("omero_container");
//   container.innerHTML = "";

  // Notification message
  const messageContainer = document.createElement("div");
  //   message.textContent =
  //     `Image with id Not found OR \n` +
  //     "You are not logged in to OMERO. Please log in using the button below. " +
  //     "If you have already logged provide valid image id and click “View Image”.";
  const message = document.createElement("ul");
  message.style.marginBottom = "12px";
  message.style.paddingLeft = "20px";  

  const li1 = document.createElement("li");
  li1.textContent = "Image with the specified ID was not found.";  

  const li2 = document.createElement("li");
  li2.textContent =
    "You are not logged in to OMERO. Please log in using the button below.";  

  const li3 = document.createElement("li");
  li3.textContent =
  "If you are already logged in, provide a valid Image ID and click “View Image”.";

  message.appendChild(li1);
  message.appendChild(li2);
  message.appendChild(li3);
  messageContainer.style.padding = "12px 16px";
  messageContainer.style.marginBottom = "16px";
  messageContainer.style.borderRadius = "6px";
  messageContainer.style.backgroundColor = "#e1b4c0ff";   // soft warning yellow
  messageContainer.style.border = "1px solid #86424bff";
  messageContainer.style.color = "#050505ff";
  messageContainer.style.fontSize = "16px";
  messageContainer.style.lineHeight = "1.5";
  messageContainer.append(message);
  viewerArea.appendChild(messageContainer);

  // Button container
  const wrapper = document.createElement("div");
  wrapper.style.display = "flex";
  wrapper.style.gap = "12px";
  wrapper.style.alignItems = "center";

  // Login button
  const loginBtn = document.createElement("a");
  loginBtn.textContent = "Log in to OMERO";
  loginBtn.href = "https://nife-dev.cancer.gov/omero_plus/login/?url=%2Fwebclient%2F";
  loginBtn.target = "_blank";
  loginBtn.className = "btn btn-primary";

  viewerArea.appendChild(loginBtn);
}

document.addEventListener("DOMContentLoaded", () => {
  showOMEROIframe();
});
