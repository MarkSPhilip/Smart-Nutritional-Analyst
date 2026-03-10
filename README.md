# Smart Nutritional Analyst 🍏

A multi-agent system designed to parse natural language food logs, calculate precise macronutrients using real-time API data, and provide behavioral coaching feedback.

## 🚀 Key Features

-   **Agent A (The Parser)**: Dynamic food extraction from natural language. Handles quantities (e.g., "two eggs"), volumes (e.g., "300ml juice"), and specialized weights (e.g., "chicken200g").
-   **Agent B (The Calculator)**: Powered by the **OpenFoodFacts API**. It fetches live nutritional data with a robust multi-product fallback system to ensure data accuracy.
-   **Agent C (The Coach)**: Provides instant, actionable feedback based on your meal's macronutrient profile.
-   **Premium Dashboard**: A sleek, dark-mode interface with glassmorphism effects and micro-animations.

## 🛠️ Tech Stack

-   **Backend**: FastAPI (Python)
-   **Agents**: Python-based logic with Regex and `requests`
-   **Nutritional Data**: OpenFoodFacts API
-   **Frontend**: Vanilla HTML5, CSS3, and JavaScript

## 📦 Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd "Smart Nutritional Analyst"
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    python main.py
    ```

4.  **Access the Dashboard**:
    Open `http://127.0.0.1:8000` in your browser.

## 📁 Project Structure

-   `main.py`: FastAPI server and agent orchestration.
-   `agents.py`: core logic for Parser, Calculator, and Coach agents.
-   `index.html`: Main dashboard interface.
-   `src/`: Frontend assets (CSS and JS).
-   `requirements.txt`: Python package dependencies.

## 🌐 Deployment

This project is cloud-ready and can be deployed for free on platforms like **Render** or **Hugging Face Spaces**. See `deployment_guide.md` for detailed instructions.

---
Created with ❤️ for better nutrition tracking.
