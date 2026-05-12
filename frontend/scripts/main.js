const logContainer = document.getElementById('log-container');
const startBtn = document.getElementById('start-btn');
const githubInput = document.getElementById('github-url');
const statusBadge = document.getElementById('status-badge');

// Connect to WebSocket
let socket;

function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws/logs`);

    socket.onopen = () => {
        if (statusBadge) {
            statusBadge.innerText = 'Connected';
            statusBadge.style.background = 'rgba(0, 210, 255, 0.2)';
        }
        addLog("WebSocket connection established.", "system");
    };

    socket.onmessage = (event) => {
        try {
            const log = JSON.parse(event.data);
            addLog(log.message, log.agent);
            updateUI(log);
        } catch (e) {
            console.error("Error parsing log:", e);
        }
    };

    socket.onclose = () => {
        if (statusBadge) {
            statusBadge.innerText = 'Offline';
            statusBadge.style.background = 'rgba(255, 0, 0, 0.2)';
        }
        addLog("WebSocket connection closed. Retrying...", "system");
        setTimeout(connectWS, 3000);
    };
}

function addLog(message, agent) {
    if (!logContainer) return;
    const entry = document.createElement('div');
    entry.className = `log-entry ${agent.toLowerCase()}`;
    const time = new Date().toLocaleTimeString([], { hour12: false });
    entry.innerHTML = `<span style="color: #666">[${time}]</span> <span class="agent-name">${agent}:</span> <span class="log-msg">${message}</span>`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function updateUI(log) {
    const msg = log.message.toLowerCase();
    
    if (msg.includes("cloning")) {
        setActiveStep("step-1");
    } else if (msg.includes("indexing")) {
        setActiveStep("step-3");
    } else if (msg.includes("execution attempt")) {
        setActiveStep("step-4");
    } else if (msg.includes("verifying")) {
        setActiveStep("step-5");
    } else if (msg.includes("pr opened")) {
        setActiveStep("step-6");
    }
}

function setActiveStep(id) {
    const target = document.getElementById(id);
    if (!target) return;

    document.querySelectorAll('.step').forEach(s => s.classList.remove('active', 'completed'));
    target.classList.add('active');
    
    // Mark previous steps as completed
    let prev = target.previousElementSibling;
    while (prev) {
        prev.classList.add('completed');
        prev = prev.previousElementSibling;
    }
}

if (startBtn) {
    startBtn.addEventListener('click', async () => {
        const url = githubInput.value.trim();
        if (!url) return alert("Please enter a GitHub Issue URL");

        startBtn.disabled = true;
        startBtn.innerText = "Processing...";
        
        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ issue_url: url })
            });
            await response.json();
            localStorage.setItem('active_url', url);
            window.location.href = 'execution.html';
        } catch (error) {
            alert("Error submitting task: " + error.message);
            startBtn.disabled = false;
            startBtn.innerText = "Start Autonomous Fix";
        }
    });
}

// If we are on the execution page, trigger the start if not already running
if (window.location.pathname.includes('execution.html')) {
    const activeUrl = localStorage.getItem('active_url');
    if (activeUrl) {
        // We don't need to fetch here because dashboard already triggered it
        // and we just want to listen to logs now.
        // But if the user refreshes, we might want to know if it's still running.
    }
}

// Initial connection
connectWS();
