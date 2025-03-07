document.addEventListener("DOMContentLoaded", function () {
    const startButton = document.getElementById("start-btn");
    const stopButton = document.getElementById("stop-btn");
    const exitButton = document.getElementById("exit-btn");
    const liveTranscription = document.getElementById("live-transcription");
    const finalTranscription = document.getElementById("final-transcription");
    const grammarErrors = document.getElementById("grammar-errors");
    const accuracyScore = document.getElementById("accuracy-score");

    let eventSource;

    // Function to send requests to the backend
    async function sendRequest(endpoint) {
        try {
            console.log(`Sending request to ${endpoint}`);
            disableButtons(true);

            const response = await fetch(endpoint);
            if (!response.ok) {
                throw new Error(`Request failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`Response from ${endpoint}:`, data);
        } catch (error) {
            console.error(`Error with ${endpoint}:`, error);
            alert(`Error: ${error.message}`);
        } finally {
            disableButtons(false);
        }
    }

    // Function to enable/disable buttons
    function disableButtons(disabled) {
        startButton.disabled = disabled;
        stopButton.disabled = disabled;
        exitButton.disabled = disabled;
    }

    // Start transcription
    startButton.addEventListener("click", () => {
        // Reset UI before starting
        liveTranscription.textContent = "Waiting for speech...";
        finalTranscription.textContent = "";
        grammarErrors.innerHTML = "";
        accuracyScore.textContent = "Waiting for analysis...";
        
        sendRequest("/start");
        initializeEventSource();
    });

    // Stop transcription
    stopButton.addEventListener("click", () => {
        sendRequest("/stop");
        // We'll keep the event source open to receive final results
    });

    // Exit application
    exitButton.addEventListener("click", () => {
        const confirmExit = confirm("Are you sure you want to exit?");
        if (confirmExit) {
            sendRequest("/exit").then(() => {
                if (eventSource) {
                    eventSource.close();
                }
                // Attempt to close the tab
                window.close();
            });
        }
    });

    // Initialize EventSource for live transcription updates
    function initializeEventSource() {
        if (eventSource) {
            eventSource.close();
        }

        eventSource = new EventSource("/transcription");

        eventSource.onmessage = function (event) {
            const message = event.data;
            console.log("Received event data:", message);

            if (message.startsWith("LIVE::")) {
                const text = message.replace("LIVE::", "");
                console.log("Live text to display:", text);
                liveTranscription.textContent = text;
            } 
            else if (message.startsWith("FULL_TRANSCRIPTION::")) {
                const text = message.replace("FULL_TRANSCRIPTION::", "");
                console.log("Final text to display:", text);
                finalTranscription.textContent = text;
            } 
            else if (message.startsWith("GRAMMAR_ERRORS::")) {
                try {
                    const errorsJson = message.replace("GRAMMAR_ERRORS::", "");
                    console.log("Grammar errors JSON:", errorsJson);
                    const errors = JSON.parse(errorsJson);
                    updateGrammarErrorsTable(errors);
                } catch (err) {
                    console.error("Error parsing grammar errors:", err);
                    grammarErrors.innerHTML = "<tr><td colspan='3'>No grammar errors found.</td></tr>";
                }
            } 
            else if (message.startsWith("ACCURACY::")) {
                const accuracy = message.replace("ACCURACY::", "");
                console.log("Accuracy to display:", accuracy);
                accuracyScore.textContent = accuracy;

                // Close the EventSource after receiving the final data
                if (eventSource) {
                    eventSource.close();
                }
            }
        };

        eventSource.onerror = function (event) {
            console.error("EventSource error:", event);
            if (event.eventPhase === EventSource.CLOSED) {
                console.log("EventSource was closed");
            }
        };
    }

    // Function to update the grammar errors table
    function updateGrammarErrorsTable(errors) {
        grammarErrors.innerHTML = "";

        if (!errors || errors.length === 0) {
            grammarErrors.innerHTML = "<tr><td colspan='3'>No grammar errors found.</td></tr>";
            return;
        }

        errors.forEach(error => {
            const row = document.createElement("tr");
            row.className = "border-b border-gray-700";

            const sentenceCell = document.createElement("td");
            sentenceCell.className = "p-3 text-left";
            sentenceCell.textContent = error.sentence || "N/A";
            row.appendChild(sentenceCell);

            const errorCell = document.createElement("td");
            errorCell.className = "p-3";
            errorCell.textContent = error.error || "N/A";
            row.appendChild(errorCell);

            const correctionCell = document.createElement("td");
            correctionCell.className = "p-3";
            
            // Handle the correction, which might be in 'suggestion' field
            let correction = "N/A";
            if (error.suggestion && Array.isArray(error.suggestion) && error.suggestion.length > 0) {
                correction = error.suggestion.join(", ");
            }
            
            correctionCell.textContent = correction;
            row.appendChild(correctionCell);

            grammarErrors.appendChild(row);
        });
    }
});