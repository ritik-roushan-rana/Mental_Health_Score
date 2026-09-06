const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("submit-btn");
const loadingEl = document.getElementById("state-loading");
const errorEl = document.getElementById("state-error");
const gaugeFill = document.getElementById("gauge-fill");
const gaugeNumber = document.getElementById("gauge-number");
const gaugeLabel = document.getElementById("gauge-label");

const GAUGE_ARC_LENGTH = 251.3; // path length of the semicircle
const countries = ["Canada", "France", "Germany", "India", "Mexico", "Turkey", "UK", "USA", "Other"];

function setGauge(score) {
  const clamped = Math.max(0, Math.min(10, score));
  const fraction = clamped / 10;
  const offset = GAUGE_ARC_LENGTH * (1 - fraction);
  gaugeFill.style.strokeDashoffset = offset;

  let color, label;
  if (clamped < 4) {
    color = "var(--brick)";
    label = "Lower than average — worth a closer look";
  } else if (clamped < 6) {
    color = "var(--amber)";
    label = "Below average";
  } else if (clamped < 8) {
    color = "var(--teal)";
    label = "Solid, typical range";
  } else {
    color = "var(--teal-deep)";
    label = "Strong wellbeing signal";
  }
  gaugeFill.style.stroke = color;
  gaugeNumber.textContent = clamped.toFixed(1);
  gaugeLabel.textContent = label;
}

function resetGauge() {
  gaugeFill.style.strokeDashoffset = GAUGE_ARC_LENGTH;
  gaugeNumber.textContent = "—";
  gaugeLabel.textContent = "Fill in the form to get your reading";
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();
  loadingEl.classList.remove("hidden");
  submitBtn.disabled = true;
  submitBtn.textContent = "Calculating…";

  const formData = new FormData(form);
  const selectedCountry = formData.get("Country");

  const payload = {
    Age: Number(formData.get("Age")),
    Gender: formData.get("Gender"),
    Academic_Level: formData.get("Academic_Level"),
    Most_Used_Platform: formData.get("Most_Used_Platform"),
    Purpose_Of_Use: formData.get("Purpose_Of_Use"),
    Avg_Daily_Usage_Hours: Number(formData.get("Avg_Daily_Usage_Hours")),
    Study_Hours: Number(formData.get("Study_Hours")),
    Physical_Activity_Hours: Number(formData.get("Physical_Activity_Hours")),
    Sleep_Hours_Per_Night: Number(formData.get("Sleep_Hours_Per_Night")),
    Stress_Level: formData.get("Stress_Level"),
  };

  countries.forEach((c) => {
    payload[`Country_grouped_${c}`] = c === selectedCountry;
  });

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => null);
      const detail = errData && errData.detail
        ? (Array.isArray(errData.detail) ? errData.detail.map(d => d.msg).join("; ") : errData.detail)
        : `Request failed (${response.status})`;
      showError(detail);
      resetGauge();
      return;
    }

    const data = await response.json();
    setGauge(data.predicted_mental_health_score);

  } catch (err) {
    showError("Couldn't reach the server. Check that it's running and try again.");
    resetGauge();
  } finally {
    loadingEl.classList.add("hidden");
    submitBtn.disabled = false;
    submitBtn.textContent = "Calculate my score";
  }
});