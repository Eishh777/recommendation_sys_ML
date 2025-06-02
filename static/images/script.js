function sendMessage(event) {
    if (event.key === "Enter") {
        let input = document.getElementById("userInput");
        let message = input.value.trim();
        let chatbox = document.getElementById("messages");

        if (message === "") return;

        // Display user message
        chatbox.innerHTML += `<div class="user-message">User: ${message}</div>`;
        input.value = "";

        // Send message to backend
        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        })
        .then(response => response.json())
        .then(data => {
            chatbox.innerHTML += `<div class="bot-message">Bot: ${data.response}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        })
        .catch(error => {
            console.error("Error:", error);
            chatbox.innerHTML += `<div class="bot-message error">Error: Could not get a response.</div>`;
        });
    }
}

// Function to toggle chatbot visibility
function toggleChatbot() {
    const chatbotBody = document.querySelector(".chatbot-body");
    chatbotBody.style.display = chatbotBody.style.display === "flex" ? "none" : "flex";
}
