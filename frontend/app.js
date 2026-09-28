const API_BASE = window.location.origin;

function scrollToAI() {
    document.getElementById("ai").scrollIntoView({
        behavior: "smooth"
    });
}

function scrollToIntelligence() {
    document.getElementById("intelligence").scrollIntoView({
        behavior: "smooth"
    });
}

function setQuestion(question) {
    document.getElementById("questionInput").value = question;
    scrollToAI();
}

function handleEnter(event) {
    if (event.key === "Enter") {
        askGridMind();
    }
}

async function askGridMind() {

    const input = document.getElementById("questionInput");
    const responseBox = document.getElementById("responseBox");

    const question = input.value.trim();

    if (!question) {
        return;
    }

    responseBox.innerHTML = `
        <div class="ai-answer">
            <div class="answer-question">
                QUERY / ${escapeHtml(question)}
            </div>

            <div class="answer-text">
                Analyzing grid intelligence...
            </div>

            <div class="answer-type">
                GRIDMIND AI ENGINE
            </div>
        </div>
    `;

    try {

        const response = await fetch(`${API_BASE}/ai/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const data = await response.json();

        responseBox.innerHTML = `
            <div class="ai-answer">

                <div class="answer-question">
                    QUERY / ${escapeHtml(data.question || question)}
                </div>

                <div class="answer-text">
                    ${escapeHtml(data.answer)}
                </div>

                <div class="answer-type">
                    ${escapeHtml(
                        (data.type || "GRID INTELLIGENCE")
                        .replaceAll("_", " ")
                        .toUpperCase()
                    )}
                </div>

            </div>
        `;

    } catch (error) {

        responseBox.innerHTML = `
            <div class="ai-answer">

                <div class="answer-question">
                    SYSTEM / CONNECTION ERROR
                </div>

                <div class="answer-text">
                    GridMind AI Analyst could not be reached.
                </div>

                <div class="answer-type">
                    CHECK API SERVICE
                </div>

            </div>
        `;

        console.error(error);
    }
}


function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}