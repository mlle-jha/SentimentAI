document.addEventListener("DOMContentLoaded", () => {
  const manualText = document.getElementById("manualText");
  const pdfUpload = document.getElementById("pdfUpload");
  const analyzeBtn = document.getElementById("analyzeBtn");

  if (!manualText || !pdfUpload || !analyzeBtn) {
    console.error("SentimentAI: Required HTML elements not found.");
    return;
  }

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

      if (pdf) {
        const formData = new FormData();
        formData.append("file", pdf);

        response = await fetch("/api/analyze-pdf", {
          method: "POST",
          body: formData,
        });
      } else {
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

      // Update processing insights
      const insights = document.getElementById("aiInsights");

      if (insights) {
        insights.textContent =
          "Text processing completed successfully. " +
          "Your document is ready for sentiment classification.";
      }

      // SAVE ANALYSIS TO HISTORY
      const history = JSON.parse(
        localStorage.getItem("sentimentHistory") || "[]",
      );

      const historyEntry = {
        date: new Date().toISOString(),
        inputType: pdf ? "PDF Upload" : "Manual Text",
        sourceName: pdf ? pdf.name : "Pasted Text",
        total_words: data.total_words,
        total_sentences: data.total_sentences,
        total_characters: data.total_characters,
        keywords: data.keywords || [],
      };

      history.unshift(historyEntry);

      localStorage.setItem("sentimentHistory", JSON.stringify(history));

      console.log("SentimentAI processing results:", data);

      alert("Text processing completed successfully!");
    } catch (error) {
      console.error("SentimentAI error:", error);
      alert(error.message);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "✦ Analyze Sentiment ›";
    }
  });
});
