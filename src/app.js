// Orchestration
document.addEventListener('DOMContentLoaded', async () => {
    const input = document.getElementById('foodInput');
    const btn = document.getElementById('analyzeBtn');
    const loader = document.getElementById('btnLoader');
    const resultsList = document.getElementById('results');
    const feedbackArea = document.getElementById('coachFeedback');

    btn.addEventListener('click', async () => {
        const text = input.value.trim();
        if (!text) return;

        // UI Loading State
        btn.disabled = true;
        loader.style.display = 'inline-block';
        resultsList.innerHTML = '';
        feedbackArea.innerText = 'Analyzing...';

        try {
            // Call FastAPI Backend
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error("API call failed");
            }

            const data = await response.json();

            // UI Update: Show parsed items (Agent A)
            data.parsed_items.forEach(item => {
                const li = document.createElement('li');
                li.className = 'result-item';
                li.innerHTML = `<span>${item.name}</span> <span>${item.amount}g</span>`;
                resultsList.appendChild(li);
            });

            // UI Update: Stats (Agent B)
            document.getElementById('stat-calories').innerText = Math.round(data.total.calories);
            document.getElementById('stat-protein').innerText = Math.round(data.total.protein) + 'g';
            document.getElementById('stat-carbs').innerText = Math.round(data.total.carbs) + 'g';
            document.getElementById('stat-fat').innerText = Math.round(data.total.fat) + 'g';

            // UI Update: Feedback (Agent C)
            feedbackArea.innerText = data.feedback;

        } catch (err) {
            console.error(err);
            feedbackArea.innerText = "Error during analysis. Please try again.";
        } finally {
            btn.disabled = false;
            loader.style.display = 'none';
        }
    });
});
