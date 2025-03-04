async function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    displayMessage(userInput, "user-message");
    document.getElementById("user-input").value = "";

    try {
        let response = await fetch("https://resume-chatbot-m3kq.onrender.com/api/gemini", {  
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })  
        });

        if (!response.ok) {
            throw new Error("HTTP error! Status: " + response.status);
        }

        let data = await response.json();
        displayMessage(data.reply, "bot-message");  

    } catch (error) {
        displayMessage("Error: Could not connect to AI. " + error.message, "bot-message");
    }
}

// Function to display messages with dynamic width
function displayMessage(message, className) {
    let chatBox = document.getElementById("chat-box");
    let messageDiv = document.createElement("div");

    // Adjust width based on text length
    let textLength = message.length;
    let maxWidth = "75%";
    let minWidth = "15%";
    let bubbleWidth = Math.min(10 + textLength * 2, 75) + "%"; 

    messageDiv.classList.add("message", className);
    messageDiv.textContent = message;
    messageDiv.style.width = bubbleWidth;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;  
}

// Allow pressing "Enter" to send a message
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
