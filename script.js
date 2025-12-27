// ================= AUDIO =================
const alarm = document.getElementById("alarmSound");
function playAlarm() {
  alarm.currentTime = 0;
  alarm.play().catch(() => {});
}

// ================= DATE RESET =================
let completedToday = Number(localStorage.getItem("completedToday")) || 0;
const todayKey = new Date().toDateString();
if (localStorage.getItem("day") !== todayKey) {
  completedToday = 0;
  localStorage.setItem("completedToday", 0);
  localStorage.setItem("day", todayKey);
}
document.getElementById("headerPomodoros").textContent = completedToday;
document.getElementById("completedTasks").textContent = completedToday;

// ================= PARTICLES =================
const particles = document.getElementById("particles");
for (let i = 0; i < 80; i++) {
  const p = document.createElement("div");
  p.className = "particle";
  const s = Math.random() * 3 + 1;
  p.style.width = s + "px";
  p.style.height = s + "px";
  p.style.left = Math.random() * 100 + "%";
  p.style.top = Math.random() * 100 + "%";
  p.style.opacity = Math.random();
  p.style.animationDuration = (10 + Math.random() * 30) + "s";
  particles.appendChild(p);
}

// ================= TIMER =================
let timer = null;
let secondsLeft = 25 * 60;
let totalSeconds = secondsLeft;
let phase = "work";
let pomodoroCount = Number(localStorage.getItem("totalPomodoros")) || 0;
let streak = Number(localStorage.getItem("streak")) || 0;

document.getElementById("totalPomodoros").textContent = pomodoroCount;
document.getElementById("currentStreak").textContent = streak;

const timerDisplay = document.getElementById("timerDisplay");
const phaseBadge = document.getElementById("phaseBadge");
const timerMega = document.getElementById("timerMega");

function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function updateRing() {
  const deg = 360 * (1 - secondsLeft / totalSeconds);
  timerMega.style.setProperty("--progress", `${deg}deg`);
}

function loadPhase(p) {
  phase = p;
  phaseBadge.textContent = phase.toUpperCase();
  if (phase === "work") totalSeconds = Number(document.getElementById("workTime").value) * 60;
  else if (phase === "short") totalSeconds = Number(document.getElementById("shortBreak").value) * 60;
  else totalSeconds = Number(document.getElementById("longBreak").value) * 60;

  secondsLeft = totalSeconds;
  timerDisplay.textContent = formatTime(secondsLeft);
  updateRing();
}

function startTimer() {
  if (timer) return;
  timer = setInterval(() => {
    secondsLeft--;
    timerDisplay.textContent = formatTime(secondsLeft);
    updateRing();
    if (secondsLeft <= 0) {
      clearInterval(timer);
      timer = null;
      handlePhaseEnd();
    }
  }, 1000);
}

function pauseTimer() { clearInterval(timer); timer = null; }
function resetTimer() { pauseTimer(); loadPhase(phase); }

function handlePhaseEnd() {
  playAlarm();
  if (phase === "work") {
    pomodoroCount++;
    completedToday++;
    streak++;
    localStorage.setItem("totalPomodoros", pomodoroCount);
    localStorage.setItem("completedToday", completedToday);
    localStorage.setItem("streak", streak);
    document.getElementById("headerPomodoros").textContent = completedToday;
    document.getElementById("totalPomodoros").textContent = pomodoroCount;
    document.getElementById("currentStreak").textContent = streak;

    const interval = Number(document.getElementById("longBreakInterval").value);
    loadPhase(pomodoroCount % interval === 0 ? "long" : "short");
  } else {
    loadPhase("work");
  }
  startTimer();
}

// Button Events
document.getElementById("startBtn").onclick = startTimer;
document.getElementById("pauseBtn").onclick = pauseTimer;
document.getElementById("resetBtn").onclick = resetTimer;

// Quick Settings Change
["workTime","shortBreak","longBreak"].forEach(id => {
  document.getElementById(id).onchange = resetTimer;
});

// ================= TASK SYSTEM =================
let tasks = JSON.parse(localStorage.getItem("tasks") || "[]");
const tasksList = document.getElementById("tasksList");
const taskInput = document.getElementById("taskInput");

function saveTasks() {
  localStorage.setItem("tasks", JSON.stringify(tasks));
  document.getElementById("completedTasks").textContent = completedToday;
}

function drawTasks() {
  tasksList.innerHTML = "";
  tasks.forEach((t, i) => {
    const d = document.createElement("div");
    d.className = "task-item" + (t.done ? " completed" : "");

    const c = document.createElement("input");
    c.type = "checkbox";
    c.checked = t.done;
    c.onchange = () => {
      if (!t.done) completedToday++;
      t.done = !t.done;
      localStorage.setItem("completedToday", completedToday);
      saveTasks();
      drawTasks();
    };

    const s = document.createElement("span");
    s.contentEditable = true;
    s.innerText = t.text;
    s.oninput = e => { t.text = e.target.innerText; saveTasks(); };

    const del = document.createElement("button");
    del.className = "delete-btn";
    del.innerHTML = "✕";
    del.onclick = () => { tasks.splice(i,1); saveTasks(); drawTasks(); };

    d.append(c, s, del);
    tasksList.append(d);
  });
}

document.getElementById("addTaskBtn").onclick = () => {
  if (!taskInput.value.trim()) return;
  tasks.push({ text: taskInput.value, done: false });
  taskInput.value = "";
  saveTasks();
  drawTasks();
};

// Initialize
loadPhase("work");
drawTasks();
