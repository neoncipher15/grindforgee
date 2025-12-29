const alarm = document.getElementById("alarmSound");
const timerDisplay = document.getElementById("timerDisplay");
const phaseBadge = document.getElementById("phaseBadge");
const timerMega = document.getElementById("timerMega");

let timer=null, secondsLeft=1500, totalSeconds=1500, phase="work";

function formatTime(s){
  return `${Math.floor(s/60)}:${String(s%60).padStart(2,"0")}`;
}

function updateRing(){
  timerMega.style.setProperty("--progress",`${360*(1-secondsLeft/totalSeconds)}deg`);
}

function loadPhase(p){
  phase=p;
  phaseBadge.textContent=p.toUpperCase();
  totalSeconds=(p==="work"?25:p==="short"?5:15)*60;
  secondsLeft=totalSeconds;
  timerDisplay.textContent=formatTime(secondsLeft);
  updateRing();
}

function startTimer(){
  if(timer) return;
  timer=setInterval(()=>{
    secondsLeft--;
    timerDisplay.textContent=formatTime(secondsLeft);
    updateRing();
    if(secondsLeft<=0){
      clearInterval(timer); timer=null;
      alarm.play().catch(()=>{});
      loadPhase(phase==="work"?"short":"work");
      startTimer();
    }
  },1000);
}

document.getElementById("startBtn").onclick=startTimer;
document.getElementById("pauseBtn").onclick=()=>{clearInterval(timer);timer=null};
document.getElementById("resetBtn").onclick=()=>{clearInterval(timer);timer=null;loadPhase(phase)};

// LOCK IN MODE
const maximizeBtn=document.getElementById("maximizeBtn");
const dashboard=document.querySelector(".dashboard");
const taskPopup=document.getElementById("taskPopup");
const popupTasks=document.getElementById("popupTasks");

let locked=false;
let tasks=[];

maximizeBtn.onclick=()=>{
  locked=!locked;
  dashboard.classList.toggle("lock-in",locked);
  taskPopup.style.display=locked?"block":"none";
  maximizeBtn.textContent=locked?"✕":"🗖";
  renderPopupTasks();
};

function renderPopupTasks(){
  popupTasks.innerHTML="";
  tasks.forEach(t=>{
    const d=document.createElement("div");
    d.textContent=(t.done?"✔ ":"• ")+t.text;
    popupTasks.appendChild(d);
  });
}

loadPhase("work");
