// Pomodoro Timer App

class PomodoroTimer {
    constructor() {
        // Timer settings (seconds)
        this.workTime = 25 * 60;
        this.shortBreak = 5 * 60;
        this.longBreak = 15 * 60;

        // State
        this.timeLeft = this.workTime;
        this.isRunning = false;
        this.isWorkSession = true;
        this.sessionsCompleted = 0;
        this.timerInterval = null;

        // DOM Elements
        this.timerDisplay = document.getElementById('timer');
        this.statusDisplay = document.getElementById('status');
        this.sessionsDisplay = document.getElementById('sessions');
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.skipBtn = document.getElementById('skipBtn');
        this.workTimeInput = document.getElementById('workTime');
        this.shortBreakInput = document.getElementById('shortBreak');
        this.longBreakInput = document.getElementById('longBreak');
        this.modal = document.getElementById('modal');
        this.modalIcon = document.getElementById('modalIcon');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalMessage = document.getElementById('modalMessage');
        this.modalBtn = document.getElementById('modalBtn');

        this.init();
    }

    init() {
        // Event listeners
        this.startBtn.addEventListener('click', () => this.toggleTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        this.skipBtn.addEventListener('click', () => this.skipSession());
        this.modalBtn.addEventListener('click', () => this.closeModal());

        // Settings listeners
        this.workTimeInput.addEventListener('change', () => this.updateSettings());
        this.shortBreakInput.addEventListener('change', () => this.updateSettings());
        this.longBreakInput.addEventListener('change', () => this.updateSettings());

        // Initial display
        this.updateDisplay();

        // Request notification permission
        if ('Notification' in window) {
            Notification.requestPermission();
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    updateDisplay() {
        this.timerDisplay.textContent = this.formatTime(this.timeLeft);
        this.sessionsDisplay.textContent = this.sessionsCompleted;

        if (this.isWorkSession) {
            this.timerDisplay.classList.remove('break');
            this.statusDisplay.classList.remove('break');
            this.statusDisplay.classList.add('work');
            this.statusDisplay.textContent = '🔴 作業時間';
        } else {
            this.timerDisplay.classList.add('break');
            this.statusDisplay.classList.add('break');
            this.statusDisplay.classList.remove('work');
            if (this.sessionsCompleted % 4 === 0 && this.sessionsCompleted > 0) {
                this.statusDisplay.textContent = '🟢 長い休憩';
            } else {
                this.statusDisplay.textContent = '🟢 休憩時間';
            }
        }

        // Update page title
        document.title = `${this.formatTime(this.timeLeft)} - Pomodoro Timer`;
    }

    updateSettings() {
        if (!this.isRunning) {
            this.workTime = parseInt(this.workTimeInput.value) * 60 || 25 * 60;
            this.shortBreak = parseInt(this.shortBreakInput.value) * 60 || 5 * 60;
            this.longBreak = parseInt(this.longBreakInput.value) * 60 || 15 * 60;

            if (this.isWorkSession) {
                this.timeLeft = this.workTime;
                this.updateDisplay();
            }
        }
    }

    toggleTimer() {
        if (this.isRunning) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    }

    startTimer() {
        this.isRunning = true;
        this.startBtn.textContent = '⏸ 一時停止';

        this.timerInterval = setInterval(() => {
            if (this.timeLeft > 0) {
                this.timeLeft--;
                this.updateDisplay();
            } else {
                this.timerFinished();
            }
        }, 1000);
    }

    pauseTimer() {
        this.isRunning = false;
        this.startBtn.textContent = '▶ スタート';
        clearInterval(this.timerInterval);
    }

    resetTimer() {
        this.pauseTimer();

        if (this.isWorkSession) {
            this.timeLeft = this.workTime;
        } else {
            if (this.sessionsCompleted % 4 === 0 && this.sessionsCompleted > 0) {
                this.timeLeft = this.longBreak;
            } else {
                this.timeLeft = this.shortBreak;
            }
        }

        this.updateDisplay();
    }

    skipSession() {
        this.pauseTimer();
        this.timerFinished();
    }

    timerFinished() {
        this.pauseTimer();

        if (this.isWorkSession) {
            this.sessionsCompleted++;
            if (this.sessionsCompleted % 4 === 0) {
                this.timeLeft = this.longBreak;
                this.showModal('🎉', 'お疲れさま！', '4セッション完了！\n長い休憩を取りましょう。');
            } else {
                this.timeLeft = this.shortBreak;
                this.showModal('✅', '完了', '作業セッション完了！\n短い休憩を取りましょう。');
            }
            this.isWorkSession = false;
        } else {
            this.timeLeft = this.workTime;
            this.showModal('💪', '準備OK', '休憩終了！\n次の作業セッションを始めましょう。');
            this.isWorkSession = true;
        }

        this.updateDisplay();
        this.sendNotification();
    }

    showModal(icon, title, message) {
        this.modalIcon.textContent = icon;
        this.modalTitle.textContent = title;
        this.modalMessage.textContent = message;
        this.modal.classList.add('show');
    }

    closeModal() {
        this.modal.classList.remove('show');
    }

    sendNotification() {
        if ('Notification' in window && Notification.permission === 'granted') {
            const title = this.isWorkSession ? '💪 作業開始' : '☕ 休憩開始';
            const body = this.isWorkSession
                ? '次の作業セッションを始めましょう！'
                : '休憩を取りましょう！';

            new Notification(title, { body, icon: '🍅' });
        }
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});
