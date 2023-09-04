let isWorkSession = true;
let workSessionCount = 0;
let timeLeft = 25 * 60;  // 25 minutes in seconds
const workDuration = 25 * 60;  // 25 minutes
const shortBreak = 5 * 60;  // 5 minutes
const longBreak = 15 * 60;  // 15 minutes
let timerInterval;


function displayTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function updateTimerDisplay() {
    document.querySelector('.timer-display').textContent = displayTime(timeLeft);
    document.title = `${displayTime(timeLeft)} - Pomodoro Timer`;
}

function handleTimer() {
    timeLeft--;

    if (timeLeft < 0) {
        if (isWorkSession) {
            workSessionCount++;
            if (workSessionCount == 4) {
                timeLeft = longBreak;
                workSessionCount = 0;  // Reset for the next cycle
            } else {
                timeLeft = shortBreak;
            }
        } else {
            timeLeft = workDuration;
        }
        const alertSound = document.getElementById('alertSound');
        alertSound.play();
        isWorkSession = !isWorkSession;  // Toggle between work and break
        pauseTimer();
    }

    updateTimerDisplay();
}

function startTimer() {
    if (!timerInterval) {
        timerInterval = setInterval(handleTimer, 1000);  // Update every second
    }
}

function pauseTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

function resetTimer() {
    pauseTimer();
    isWorkSession = true;
    workSessionCount = 0;
    timeLeft = workDuration;
    updateTimerDisplay();
}

document.getElementById('start').addEventListener('click', startTimer);
document.getElementById('pause').addEventListener('click', pauseTimer);
document.getElementById('reset').addEventListener('click', resetTimer);
