let isWorkSession = true;
let workSessionCount = 0;
let timeLeft = 25 * 60;  // 25 minutes in seconds
const workDuration = 25 * 60;  // 25 minutes
const shortBreak = 5 * 60;  // 5 minutes
const longBreak = 15 * 60;  // 15 minutes
let timerInterval;
const socket = io.connect('http://localhost:5000'); // Adjust the URL accordingly.
let currentSessionID = null;



function displayTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function updateTimerDisplay() {
    document.querySelector('.timer-display').textContent = displayTime(timeLeft);
    document.title = `${displayTime(timeLeft)} - Pomo-collab Timer`;
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
        const alertSound = document.getElementById('alertSound'); // Play the alert sound
        alertSound.play();

        if (Notification.permission === 'granted') { // Show the notification
            new Notification('Pomodoro Timer Alert!', {
                body: isWorkSession ? 'Take a break!' : 'Time to work!',
            });
        }


        isWorkSession = !isWorkSession;  // Toggle between work and break


        pauseTimer();
    }

    updateTimerDisplay();
    if (document.getElementById('onlineModeSwitch').checked) {
        socket.emit('timer_update', { session_id: currentSessionID, time_left: timeLeft });  // Emit timer update to the server
    }
}

function startTimer() {
    if (!timerInterval) {
        timerInterval = setInterval(handleTimer, 1000);  // Update every second
        if (document.getElementById('onlineModeSwitch').checked) {
            socket.emit('action_update', { session_id: currentSessionID, action: 'start' });  // Emit start action to the server
        }
    }
}

function pauseTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    if (document.getElementById('onlineModeSwitch').checked) {
        socket.emit('action_update', { session_id: currentSessionID, action: 'pause' });  // Emit pause action to the server
    }
}

function resetTimer() {
    pauseTimer();
    isWorkSession = true;
    workSessionCount = 0;
    timeLeft = workDuration;
    updateTimerDisplay();
    if (document.getElementById('onlineModeSwitch').checked) {
        socket.emit('action_update', { session_id: currentSessionID, action: 'reset' });  // Emit reset action to the server
    }
}

// Event Listeners-------------------------------------------------------------------------------------------------------------------

// Timer controls
document.getElementById('start').addEventListener('click', startTimer);
document.getElementById('pause').addEventListener('click', pauseTimer);
document.getElementById('reset').addEventListener('click', resetTimer);

// Session creation and joining
document.getElementById('createSession').addEventListener('click', function () {
    // Emit the 'create_session' event to the server
    if (document.getElementById('onlineModeSwitch').checked) {
        socket.emit('create_session');
    }
});
document.getElementById('joinSession').addEventListener('click', function () {
    const sessionID = document.getElementById('sessionIDInput').value;
    if (sessionID) {
        // Emit the 'join_session' event with the session ID
        if (document.getElementById('onlineModeSwitch').checked) {
            socket.emit('join_session', sessionID);
        }
    } else {
        alert("Please enter a valid Session ID.");
    }
});

// Request notification permission
document.addEventListener('DOMContentLoaded', function () {
    Notification.requestPermission().then(function (result) {
        if (result === 'granted') {
            console.log('User granted notification permission');
        }
    });
});





// Socket.io event handlers------------------------------------------------------------------------------------------------------------
socket.on('session_created', (data) => {
    console.log('Session created with ID:', data.session_id);
    // Here you can update the UI or store the session ID locally.
    currentSessionID = data.session_id;
    // Notify the user
    alert(`Session created! Share this session ID with others: ${data.session_id}`); // or use a more elegant notification method
});

socket.on('timer_updated', (data) => {
    timeLeft = data.time_left;
    // Update your frontend timer display
    updateTimerDisplay();
});


socket.on('session_joined', (data) => {
    currentSessionID = data.session_id;
    // Notify the user
    alert("Successfully joined the session!"); // or use a more elegant notification method

    // Update the timer display
    timeLeft = data.time_left;
    updateTimerDisplay();

    // Potentially update other UI elements based on the session's current state
    if (data.status === 'running') {
        // If the session was already running, start the timer on this client's side as well
        startTimer();
    }
});

socket.on('action_updated', (data) => {
    timeLeft = data.time_left;

    switch (data.status) {
        case 'running':
            startTimer();
            break;
        case 'paused':
            pauseTimer();
            break;
        default:
            console.warn("Received unknown status:", data.status);
            break;
    }

    // Update the timer display
    updateTimerDisplay();
});

socket.on('error', (data) => {
    alert(data.message);
});




