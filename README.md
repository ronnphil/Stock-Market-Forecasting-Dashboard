## Overview

- Built a full-stack web app displaying real-time S&P 500 stock data with AI-powered market trend forecasting
- Key focus: making complex AI output readable and actionable for a non-technical user
- Stack: **Python, Streamlit, Node.js, SQL, LSTM neural network**
<img width="1889" height="982" alt="image" src="https://github.com/user-attachments/assets/4863135a-40b0-49f9-a83c-30d71443869a" />

---

## 📚 Skills

**💻 Software**

- 🐍 Python + Streamlit: Built and styled the interactive dashboard UI
- 🔄 Node.js: Data pipeline to fetch and structure live market data
- 🗄️ SQL: Scripts to store and retrieve historical stock data
- 🤖 LSTM Neural Network: Time-series model for market trend prediction

---

## ⭐ Highlights

**UI — Streamlit Dashboard**

- **Goal:** Display live stock data and AI predictions in a way a normal user could actually understand
- **UX Decisions:** Chose chart types based on readability, structured layout around user flow (overview → detail → forecast), used color contrast to distinguish historical vs predicted data
- **Result:** AI output surfaced directly on the dashboard — no data science background needed to interpret it

**Backend — Node.js Data Pipeline**

- Built a pipeline to fetch and structure live market data, feeding real-time updates directly to the front end
- Wrote SQL scripts to store and retrieve 5-year historical S&P 500 data for the LSTM model

**AI — LSTM Forecasting Model**

- Trained an LSTM neural network on 5-year S&P 500 data to predict market volatility
- Integrated predictions directly into the dashboard UI so results were immediately visible to the user

---

## 🚫 Key Constraints

- **Latency:** Live stock data had to update in real time without lag
- **Readability:** AI forecasts had to be interpretable by a non-technical user
- **Accuracy:** LSTM model needed sufficient historical data to produce meaningful predictions

---

## 🎯 Key Takeaway

Building the AI model was the straightforward part. The real challenge was designing the dashboard so the predictions were actually interpretable — choosing the right chart, the right labels, and the right layout so a user didn't need a data science background to understand what the model was telling them. This project taught me that the UI layer is what makes or breaks whether AI output is actually useful.
