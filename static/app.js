/* NYPD Case File Retrieval System v2.1 — terminal controller
 * Fetches grounded answers from /ask, lists accessed case files,
 * and types the detective response out character-by-character.
 */

const queryInput = document.getElementById("query-input");
const askBtn = document.getElementById("ask-btn");
const sourcesList = document.getElementById("sources-list");
const typedText = document.getElementById("typed-text");
const cursor = document.getElementById("cursor");
const statusDb = document.getElementById("status-db");
const statusClock = document.getElementById("status-clock");

let typingTimer = null;
let busy = false;

/* ---- live system clock in the status bar ---- */
function updateClock() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  statusClock.textContent = `SYS-TIME ${hh}:${mm}:${ss}`;
}
setInterval(updateClock, 1000);
updateClock();

/* ---- UI state helpers ---- */
function setBusy(state) {
  busy = state;
  askBtn.disabled = state;
  queryInput.disabled = state;
  askBtn.textContent = state ? "SEARCHING" : "EXECUTE";
  statusDb.textContent = state ? "DB STATUS: QUERYING" : "DB STATUS: ONLINE";
}

function stopTyping() {
  clearTimeout(typingTimer);
  typingTimer = null;
}

/* ---- render retrieved case files ---- */
function renderSources(sources) {
  sourcesList.innerHTML = "";
  if (!sources || sources.length === 0) {
    const li = document.createElement("li");
    li.textContent = "> NO MATCHING CASE FILES RETRIEVED";
    li.style.color = "var(--amber)";
    sourcesList.appendChild(li);
    return;
  }
  sources.forEach((src, i) => {
    const li = document.createElement("li");
    const pct = Math.round((src.score || 0) * 100);
    li.innerHTML =
      `> ACCESSING FILE: [${src.source}] ` +
      `<span class="match-pct">MATCH ${pct}%</span>`;
    li.style.opacity = "0";
    sourcesList.appendChild(li);
    // staggered "accessing" reveal
    setTimeout(() => {
      li.style.opacity = "1";
    }, 180 * (i + 1));
  });
}

/* ---- typewriter effect ---- */
function typeOut(text) {
  return new Promise((resolve) => {
    stopTyping();
    typedText.textContent = "";
    let i = 0;
    const speed = 16;
    function step() {
      if (i < text.length) {
        typedText.textContent += text.charAt(i);
        i++;
        typingTimer = setTimeout(step, speed);
      } else {
        resolve();
      }
    }
    step();
  });
}

/* ---- main query flow ---- */
async function askQuestion() {
  if (busy) return;
  const question = queryInput.value.trim();
  if (!question) return;

  setBusy(true);
  stopTyping();
  typedText.textContent = "";
  sourcesList.innerHTML = "<li>> ESTABLISHING SECURE UPLINK...</li>";

  try {
    const resp = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!resp.ok) throw new Error("SERVER ERROR " + resp.status);

    const data = await resp.json();

    // Reveal which files were accessed first...
    renderSources(data.sources);
    await wait(450);
    // ...then type out the detective's answer.
    await typeOut(data.answer || "...");
  } catch (err) {
    sourcesList.innerHTML = "";
    await typeOut("CONNECTION TERMINATED: " + (err.message || "unknown error"));
  } finally {
    setBusy(false);
  }
}

function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

/* ---- wire up events ---- */
askBtn.addEventListener("click", askQuestion);
queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    askQuestion();
  }
});
