# pomo-collab
A web-based Pomodoro timer designed to help users maintain productivity by using the Pomodoro technique. It employs the concept of 25-minute focused work sessions, followed by 5-minute breaks. After four such intervals, a longer break is taken. The application offers the potential for synchronized timer sessions, allowing friends or colleagues to work together in harmony.

## Features:
- Synchronized Timer: Invite friends to the same timer session to keep everyone on the same schedule.
- Pause & Reset: Any party can pause the timer or reset it to start afresh.
- Session Tracker: Keep track of completed work sessions to monitor productivity.
- Alerts: Notifications to inform the user when a session ends and a break begins.

## Technologies Used:
- Frontend: HTML, CSS, and JavaScript.
- Backend: Python (Flask)

## How to Run:
1. Clone the repository:
   - git clone pomo-collab

2. Navigate to the project directory:
   - cd pomo-collab

3. Install required packages:
   - pip install -r requirements.txt
4. Launch the docker containers:
   - docker-compose build
   - docker-compose up

5. Run the application:
   - python app.py

6. Open a web browser and navigate to http://127.0.0.1:5000/ to view the application.
