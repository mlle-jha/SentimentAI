
document.addEventListener("DOMContentLoaded", () => {
    const manualText = document.getElementById("manualText");
    const pdfUpload = document.getElementById("pdfUpload");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const charCounter = document.getElementById("charCounter");
    const selectedFile = document.getElementById("selectedFile");
    const dropZone = document.getElementById("dropZone");

    if (!manualText || !pdfUpload || !analyzeBtn) {
        console.error("SentimentAI: Required HTML elements not found.");
        return;
    }

    // Character counter
    manualText.addEventListener("input", () => {
    if (charCounter) {
        charCounter.textContent = `${manualText.value.length} / 5000`;
    }

    // Typing switches to Text Analysis
    if (manualText.value.trim() && pdfUpload.files.length > 0) {
        pdfUpload.value = "";

        if (selectedFile) {
            selectedFile.textContent = "No document selected";
            selectedFile.classList.remove("has-file");
        }
    }
});

    // Display selected PDF
    pdfUpload.addEventListener("change", () => {
    const file = pdfUpload.files[0];

    if (file) {
        // Selecting a PDF switches to PDF Analysis
        manualText.value = "";

        if (charCounter) {
            charCounter.textContent = "0 / 5000";
        }
    }

    if (selectedFile) {
        selectedFile.textContent = file
            ? `✓ ${file.name}`
            : "No document selected";

        selectedFile.classList.toggle("has-file", !!file);
    }
});

    // Drag and drop PDF support
    if (dropZone) {
        dropZone.addEventListener("dragover", event => {
            event.preventDefault();
            dropZone.classList.add("drag-over");
        });

        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("drag-over");
        });

        dropZone.addEventListener("drop", event => {
            event.preventDefault();
            dropZone.classList.remove("drag-over");

            const file = event.dataTransfer.files[0];

            if (!file) return;

            if (!file.name.toLowerCase().endsWith(".pdf")) {
                alert("Please upload a PDF file.");
                return;
            }

            const transfer = new DataTransfer();
            transfer.items.add(file);
            pdfUpload.files = transfer.files;
            pdfUpload.dispatchEvent(new Event("change"));
        });
    }

    // Main analysis function
    async function analyze() {
        const text = manualText.value.trim();
        const pdf = pdfUpload.files[0];

        if (!text && !pdf) {
            alert("Please enter text or upload a PDF.");
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Processing...";

        try {
            let response;

            if (pdf) {
                const formData = new FormData();
                formData.append("file", pdf);

                response = await fetch("/api/analyze-pdf", {
                    method: "POST",
                    body: formData
                });
            } else {
                response = await fetch("/api/analyze", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ text })
                });
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Unable to process text.");
            }

            // Document statistics
            document.getElementById("totalWords").textContent =
                data.total_words;

            document.getElementById("totalSentences").textContent =
                data.total_sentences;

            document.getElementById("totalChars").textContent =
                Number(data.total_characters).toLocaleString();

            // Keywords
            const keywordsContainer =
                document.getElementById("keywordsContainer");

            keywordsContainer.replaceChildren();

            (data.keywords || []).forEach(item => {
                const keyword = document.createElement("span");
                keyword.className = "keyword-pill";
                keyword.textContent = item.keyword;
                keywordsContainer.appendChild(keyword);
            });

            // Sentiment overview
            const sentiment = data.sentiment;

            if (!sentiment || !sentiment.sentiment_percentages) {
                throw new Error("Sentiment results were not found in the API response.");
            }

            const percentages = sentiment.sentiment_percentages;

            const positive = percentages.POSITIVE || 0;
            const neutral = percentages.NEUTRAL || 0;
            const negative = percentages.NEGATIVE || 0;

            document.getElementById("overallSentiment").textContent =
                sentiment.overall_sentiment;

            document.getElementById("posPercent").textContent =
                positive + "%";

            document.getElementById("neuPercent").textContent =
                neutral + "%";

            document.getElementById("negPercent").textContent =
                negative + "%";

            // Donut chart
            document.getElementById("sentimentChart").style.background =
                `conic-gradient(
                    #f472b6 0% ${positive}%,
                    #93c5fd ${positive}% ${positive + neutral}%,
                    #fda4af ${positive + neutral}% 100%
                )`;

            // AI interpretation
            document.getElementById("aiInsights").textContent =
                sentiment.interpretation;

            console.log("SentimentAI processing results:", data);

        } catch (error) {
            console.error("SentimentAI error:", error);
            alert(error.message);

        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "✦ Analyze Sentiment →";
        }
    }

    // Button click
    analyzeBtn.addEventListener("click", analyze);

    // Enter submits; Shift + Enter inserts a new line
    manualText.addEventListener("keydown", event => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            analyze();
        }
    });
});
