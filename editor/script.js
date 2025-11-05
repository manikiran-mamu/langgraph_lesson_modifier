// ✅ UPDATED script.js (Fixed-Size Media Inserts)
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("lesson-container");
  const contextMenu = document.getElementById("context-menu");
  const sidePanel = document.getElementById("side-panel");
  const panelContent = document.getElementById("panel-content");

  let contextX = 0;
  let contextY = 0;

  const params = new URLSearchParams(window.location.search);
  const isReadOnly = params.get("readonly") === "true";

  if (isReadOnly) {
    const lessonContainer = document.getElementById("lesson-container");
    lessonContainer.removeAttribute("contenteditable");
  }
  const file = params.get("file");
  if (file) {
    fetch(`/outputs/markdown/${file}`)
      .then(res => res.text())
      .then(data => {
        container.innerHTML = marked.parse(data);
      })
      .catch(err => {
        container.innerText = "Error loading file: " + err.message;
      });
  }

  container.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    contextX = e.pageX;
    contextY = e.pageY;
    contextMenu.style.top = `${e.pageY}px`;
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.display = "block";
  });

  document.addEventListener("click", () => {
    contextMenu.style.display = "none";
  });

  document.getElementById("insert-image").addEventListener("click", () => {
    openPanel(
      "Insert Image",
      `
      <input type="text" id="image-search" placeholder="Search images..." style="width:100%; margin-bottom:10px;">
      <button onclick="searchImage()">Search</button>
      <div id="image-results" style="margin-top:10px;"></div>
      `
    );
    contextMenu.style.display = "none";
  });

  document.getElementById("insert-audio").addEventListener("click", () => {
    openPanel(
      "Insert Audio",
      `
      <textarea id="audio-text" rows="3" style="width:100%; margin-bottom:10px;" placeholder="Enter text for audio..."></textarea>
      <button onclick="generateAudio()">Generate Audio</button>
      `
    );
    contextMenu.style.display = "none";
  });

  document.getElementById("close-panel").addEventListener("click", () => {
    sidePanel.style.right = "-400px";
  });

  window.openPanel = function (title, html) {
    document.getElementById("panel-title").textContent = title;
    panelContent.innerHTML = html;
    sidePanel.style.right = "0px";
  };

  window.searchImage = function () {
    const q = document.getElementById("image-search").value.trim();
    if (!q) return;
    const resultsDiv = document.getElementById("image-results");
    resultsDiv.innerHTML = "<p>Searching...</p>";

    fetch(`/api/search_images?q=${encodeURIComponent(q)}`)
      .then(res => res.json())
      .then(images => {
        resultsDiv.innerHTML = "";
        if (!Array.isArray(images) || images.length === 0) {
          resultsDiv.innerHTML = "<p>No images found.</p>";
          return;
        }

        images.forEach(url => {
          const img = document.createElement("img");
          img.src = url;
          img.style.width = "100%";
          img.style.margin = "5px 0";
          img.style.cursor = "pointer";
          img.onclick = () => {
            insertAtCursor(`<img src="${url}" alt="Lesson Image" class="fixed-media">`);
            sidePanel.style.right = "-400px";
          };
          resultsDiv.appendChild(img);
        });
      })
      .catch(() => {
        resultsDiv.innerHTML = "<p style='color:red;'>Error fetching images.</p>";
      });
  };

  window.generateAudio = function () {
    const text = document.getElementById("audio-text").value.trim();
    if (!text) return;

    fetch("/api/generate_audio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text })
    })
      .then(res => res.json())
      .then(data => {
        const audioHTML = `
          <audio controls class="fixed-media" draggable="true">
            <source src="${data.audio_url}" type="audio/mpeg">
          </audio>
        `;
        insertAtCursor(audioHTML);
        sidePanel.style.right = "-400px";
      })
      .catch(() => {
        alert("Error generating audio.");
      });
  };

  function insertAtCursor(html) {
    const range = document.caretRangeFromPoint
      ? document.caretRangeFromPoint(contextX, contextY)
      : document.caretPositionFromPoint?.(contextX, contextY)?.getRange();
    if (!range) return;
    const frag = range.createContextualFragment(html);
    range.insertNode(frag);
  }

  // === 🧲 Drag and Drop for Audio ===
  container.addEventListener("dragstart", function (e) {
    if (e.target.tagName === "AUDIO") {
      draggedAudio = e.target;
      draggedAudio.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
    }
  });

  container.addEventListener("dragover", function (e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  });

  container.addEventListener("drop", function (e) {
    e.preventDefault();
    if (draggedAudio) {
      draggedAudio.classList.remove("dragging");
      const range = document.caretRangeFromPoint
        ? document.caretRangeFromPoint(e.clientX, e.clientY)
        : document.caretPositionFromPoint?.(e.clientX, e.clientY)?.getRange();
      if (range) {
        range.insertNode(draggedAudio);
      }
      draggedAudio = null;
    }
  });
});