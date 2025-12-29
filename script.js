// ================= TIMER =================
const display = document.getElementById("timerDisplay");
const badge = document.getElementById("phaseBadge");
const ring = document.getElementById("timerMega");
const alarm = document.getElementById("alarmSound");

let seconds = 1500;
let total = 1500;
let timer = null;
let phase = "work";

function format(s){
  return `${Math.floor(s/60)}:${String(s%60).padStart(2,"0")}`;
}

function updateRing(){
  ring.style.setProperty("--progress",`${360*(1-seconds/total)}deg`);
}

function loadPhase(p){
  phase = p;
  badge.textContent = p.toUpperCase();
  total = (p==="work"?25:5)*60;
  seconds = total;
  display.textContent = format(seconds);
  updateRing();
}

function start(){
  if(timer) return;
  timer = setInterval(()=>{
    seconds--;
    display.textContent = format(seconds);
    updateRing();
    if(seconds<=0){
      clearInterval(timer);
      timer=null;
      alarm.play().catch(()=>{});
      loadPhase(phase==="work"?"break":"work");
      start();
    }
  },1000);
}

document.getElementById("startBtn").onclick = start;
document.getElementById("pauseBtn").onclick = ()=>{clearInterval(timer);timer=null};
document.getElementById("resetBtn").onclick = ()=>{clearInterval(timer);timer=null;loadPhase(phase)};

loadPhase("work");

// ================= TASKS =================
const taskInput = document.getElementById("taskInput");
const tasksList = document.getElementById("tasksList");
const popupTasks = document.getElementById("popupTasks");

let tasks = [];

document.getElementById("addTaskBtn").onclick = ()=>{
  if(!taskInput.value.trim()) return;
  tasks.push(taskInput.value);
  taskInput.value="";
  renderTasks();
};

function renderTasks(){
  tasksList.innerHTML="";
  popupTasks.innerHTML="";
  tasks.forEach(t=>{
    const d=document.createElement("div");
    d.className="task-item";
    d.textContent=t;
    tasksList.appendChild(d);

    const p=document.createElement("div");
    p.textContent="• "+t;
    popupTasks.appendChild(p);
  });
}

// ================= LOCK IN MODE =================
const maximizeBtn = document.getElementById("maximizeBtn");
const dashboard = document.getElementById("dashboard");
const taskPopup = document.getElementById("taskPopup");

let locked = false;

maximizeBtn.onclick = ()=>{
  locked=!locked;
  dashboard.classList.toggle("lock-in",locked);
  taskPopup.style.display = locked?"block":"none";
  maximizeBtn.textContent = locked?"✕":"🗖";
};
