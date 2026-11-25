
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
      manualText.value = "";

      if (charCount) {
        charCount.textContent = "0";
      }

      if (selectedFileName) {
        selectedFileName.textContent = `Selected: ${file.name}`;
      }
    } else if (selectedFileName) {
      selectedFileName.textContent = "PDF files only";
    }
  });

  // Handle manual text input
  manualText.addEventListener("input", () => {
    if (charCount) {
      charCount.textContent = manualText.value.length;
    }

    // Clear PDF selection when user starts typing
    if (manualText.value.trim() && pdfUpload.files.length > 0) {
      pdfUpload.value = "";

      if (selectedFileName) {
        selectedFileName.textContent = "PDF files only";
      }
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

      // =====================================
      // UPDATE KEY STATISTICS
      // =====================================

      const statistics = {
        totalWords: data.total_words ?? 0,
        stopWords: data.total_stop_words ?? 0,
        meaningfulWords: data.total_meaningful_words ?? 0,
        totalSentences: data.total_sentences ?? 0,
        totalChars: Number(data.total_characters || 0).toLocaleString(),
      };

      Object.entries(statistics).forEach(([id, value]) => {
        const element = document.getElementById(id);

        if (element) {
          element.textContent = value;
        }
      });

      // =====================================
      // UPDATE TEXT SUMMARY
      // =====================================

      const summaryElement = document.getElementById("textSummary");

      if (summaryElement) {
        summaryElement.textContent =
          data.summary ||
          "A summary could not be generated for this document.";
      }

      // =====================================
      // UPDATE KEYWORDS
      // =====================================

      const keywordsContainer = document.getElementById("keywordsContainer");

      if (keywordsContainer) {
        keywordsContainer.replaceChildren();

        (data.keywords || []).forEach((item) => {
          const keyword = document.createElement("span");
          keyword.className = "keyword-pill";
          keyword.textContent = item.keyword;
          keywordsContainer.appendChild(keyword);
        });
      }

      // =====================================
      // UPDATE SENTIMENT OVERVIEW
      // =====================================

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

      // Update donut chart
      const sentimentChart = document.getElementById("sentimentChart");

      if (sentimentChart) {
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
      }

      // =====================================
      // UPDATE AI INSIGHTS
      // =====================================

      const insights = document.getElementById("aiInsights");

      if (insights) {
        insights.textContent =
          data.interpretation ||
          "Sentiment analysis completed successfully.";
      }

      // =====================================
      // SAVE ANALYSIS TO HISTORY
      // =====================================

      const history = JSON.parse(
        localStorage.getItem("sentimentHistory") || "[]"
      );

      const historyEntry = {
        date: new Date().toISOString(),
        inputType: pdf ? "PDF Upload" : "Manual Text",
        sourceName: pdf ? pdf.name : "Pasted Text",
        total_words: data.total_words,
        total_stop_words: data.total_stop_words ?? 0,
        total_meaningful_words: data.total_meaningful_words ?? 0,
        total_sentences: data.total_sentences,
        total_characters: data.total_characters,
        summary: data.summary || "",
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
