let collectDetails = false;

const suggestedQuestions = [
    "What is your website about?",
    "How can I contact support?",
    "What are your hours?"
];

document.addEventListener('DOMContentLoaded', () => {
    const questionList = document.getElementById('question-list');
    suggestedQuestions.forEach(question => {
        const li = document.createElement('li');
        li.textContent = question;
        li.onclick = () => sendSuggestedQuestion(question);
        questionList.appendChild(li);
    });

    document.getElementById('user-input').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

function showTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span> Bot is typing...';
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return typingDiv;
}

function hideTypingIndicator(typingDiv) {
    if (typingDiv) {
        typingDiv.remove();
    }
}

function sendSuggestedQuestion(question) {
    appendMessage('You', question);
    const typingDiv = showTypingIndicator();
    setTimeout(() => {
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: question })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator(typingDiv);
            appendMessage('Bot', data.response);
            if (data.collect_details) {
                collectDetails = true;
                const form = document.getElementById('details-form');
                form.style.display = 'block';
                setTimeout(() => form.classList.add('active'), 10);
            }
        });
    }, 1000);
}

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    appendMessage('You', message);
    input.value = '';

    const typingDiv = showTypingIndicator();
    setTimeout(() => {
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator(typingDiv);
            appendMessage('Bot', data.response);
            if (data.collect_details) {
                collectDetails = true;
                const form = document.getElementById('details-form');
                form.style.display = 'block';
                setTimeout(() => form.classList.add('active'), 10);
            }
        });
    }, 1000);
}

function submitDetails() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const number = document.getElementById('number').value;
    const issue = document.getElementById('issue').value;

    if (!name || !email || !issue) {
        appendMessage('Bot', 'Please fill in all required fields: name, email, and issue.');
        return;
    }

    fetch('/submit_details', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, number, issue })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage('Bot', data.response);
        const form = document.getElementById('details-form');
        form.classList.remove('active');
        setTimeout(() => form.style.display = 'none', 500);
        collectDetails = false;
    });
}

function appendMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.textContent = `${sender}: ${text}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}