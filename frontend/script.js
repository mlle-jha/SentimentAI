
document.addEventListener("DOMContentLoaded", () => {
  const manualText = document.getElementById("manualText");
  const pdfUpload = document.getElementById("pdfUpload");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const selectedFileName = document.getElementById("selectedFileName");
  const charCount = document.getElementById("charCount");

  if (!manualText || !pdfUpload || !analyzeBtn) {
    console.error("SentimentAI: Required HTML elements not found.");
    return;
  }

  // Handle PDF selection
  pdfUpload.addEventListener("change", () => {
    const file = pdfUpload.files[0];

    if (file) {
      // Clear manual text when a PDF is selected
      manualText.value = "";

      if (charCount) {
        charCount.textContent = "0";
      }

      selectedFileName.textContent = `Selected: ${file.name}`;
    } else {
      selectedFileName.textContent = "PDF files only";
    }
  });

  // Handle manual text input
  manualText.addEventListener("input", () => {
    // Update character counter
    if (charCount) {
      charCount.textContent = manualText.value.length;
    }

    // Clear PDF selection when user starts typing
    if (manualText.value.trim() && pdfUpload.files.length > 0) {
      pdfUpload.value = "";
      selectedFileName.textContent = "PDF files only";
    }
  });

  // Analyze button
  analyzeBtn.addEventListener("click", async () => {
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

      // Analyze PDF
      if (pdf) {
        const formData = new FormData();
        formData.append("file", pdf);

        response = await fetch("/api/analyze-pdf", {
          method: "POST",
          body: formData,
        });
      } else {
        // Analyze manual text
        response = await fetch("/api/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text }),
        });
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to process text.");
      }

      // Update document statistics
      document.getElementById("totalWords").textContent = data.total_words;

      document.getElementById("totalSentences").textContent =
        data.total_sentences;

      document.getElementById("totalChars").textContent =
        data.total_characters.toLocaleString();

      // Update keywords
      const keywordsContainer = document.getElementById("keywordsContainer");

      keywordsContainer.replaceChildren();

      (data.keywords || []).forEach((item) => {
        const keyword = document.createElement("span");
        keyword.className = "keyword-pill";
        keyword.textContent = item.keyword;
        keywordsContainer.appendChild(keyword);
      });

      // Update sentiment overview
      const percentages = data.sentiment_percentages;

      if (!percentages || !data.overall_sentiment) {
        throw new Error(
          "Sentiment results are missing. Please check the backend response."
        );
      }

      const positive = Number(percentages.POSITIVE || 0);
      const neutral = Number(percentages.NEUTRAL || 0);
      const negative = Number(percentages.NEGATIVE || 0);

      document.getElementById("overallSentiment").textContent =
        data.overall_sentiment;

      document.getElementById("posPercent").textContent =
        `${positive.toFixed(2)}%`;

      document.getElementById("neuPercent").textContent =
        `${neutral.toFixed(2)}%`;

      document.getElementById("negPercent").textContent =
        `${negative.toFixed(2)}%`;

      // Update donut chart using existing CSS colors
      const sentimentChart = document.getElementById("sentimentChart");

      const lime = getComputedStyle(document.documentElement)
        .getPropertyValue("--lime")
        .trim();

      const pink = getComputedStyle(document.documentElement)
        .getPropertyValue("--pink")
        .trim();

      sentimentChart.style.background = `conic-gradient(
        ${lime} 0% ${positive}%,
        #d7c8db ${positive}% ${positive + neutral}%,
        ${pink} ${positive + neutral}% 100%
      )`;

      // Update AI insights
      const insights = document.getElementById("aiInsights");

      if (insights) {
        insights.textContent =
          data.interpretation ||
          "Sentiment analysis completed successfully.";
      }

      // Save analysis to history
      const history = JSON.parse(
        localStorage.getItem("sentimentHistory") || "[]"
      );

      const historyEntry = {
        date: new Date().toISOString(),
        inputType: pdf ? "PDF Upload" : "Manual Text",
        sourceName: pdf ? pdf.name : "Pasted Text",
        total_words: data.total_words,
        total_sentences: data.total_sentences,
        total_characters: data.total_characters,
        keywords: data.keywords || [],
        overall_sentiment: data.overall_sentiment,
        sentiment_percentages: data.sentiment_percentages,
      };

      history.unshift(historyEntry);

      localStorage.setItem(
        "sentimentHistory",
        JSON.stringify(history)
      );

      console.log("SentimentAI processing results:", data);

      alert("Sentiment analysis completed successfully!");

    } catch (error) {
      console.error("SentimentAI error:", error);
      alert(error.message);

    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "✦ Analyze Sentiment ›";
    }
  });
});
