[README.md](https://github.com/user-attachments/files/23784301/README.md)
# 🚀 GitHub Mermaid Diagram Generator

Transform any GitHub repository into beautiful, detailed **Mermaid
diagrams** using AI.\
Analyze codebases, visualize architecture, and understand project
structure through interactive diagrams.

------------------------------------------------------------------------

## ✨ Features

### 🎨 Supported Diagram Types

-   **Sequence Diagrams**
-   **Component Diagrams**
-   **ER / Database Diagrams**
-   **Flowcharts**
-   **Class Diagrams**
-   **State Diagrams**
-   **User Journey Maps**
-   **Gantt Charts**
-   **Mindmaps**

------------------------------------------------------------------------

## 💬 Intelligent Chat Interface

-   Ask natural language questions about any GitHub Repo\
-   Generate diagrams on-demand\
-   Explain architecture with visuals

------------------------------------------------------------------------

## 🎯 Smart Capabilities

-   Deep repository scanning\
-   Accurate diagram generation using GPT-4o\
-   Real‑time Mermaid rendering\
-   Dark/Light themes\
-   Diagram history + downloads

------------------------------------------------------------------------

# 📋 Prerequisites

-   Python 3.8+
-   OpenAI API Key\
-   GitHub Token (optional but recommended)

------------------------------------------------------------------------

# 🚀 Quick Start

## 1️⃣ Clone Repo

``` bash
git clone https://github.com/yourusername/github-mermaid-generator.git
cd github-mermaid-generator
```

## 2️⃣ Backend Setup

``` bash
cd backend
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

# Create .env
OPENAI_API_KEY=your_key
GITHUB_TOKEN=your_token
```

## 3️⃣ Frontend Setup

``` bash
cd ../frontend
pip install -r requirements.txt
```

## 4️⃣ Run System

### Backend:

``` bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend:

``` bash
streamlit run app.py
```

Open:\
- Frontend → http://localhost:8501\
- Backend → http://localhost:8000\
- Docs → http://localhost:8000/docs

------------------------------------------------------------------------

# 📁 Project Structure

    github-mermaid-generator/
    │
    ├── backend/
    │   ├── main.py
    │   ├── models.py
    │   ├── routes/
    │   ├── services/
    │
    ├── frontend/
    │   ├── app.py
    │   ├── components/
    │   ├── pages/
    │   ├── utils/
    │
    └── README.md

------------------------------------------------------------------------

# 🎯 Usage Examples

### Quick Diagrams

-   Enter GitHub URL\
-   Select diagram type\
-   Generate → View → Download

### Chat Mode

Ask: - "Show authentication flow" - "Visualize database schema" - "Show
class hierarchy"

------------------------------------------------------------------------

# 🔧 Environment Variables

    OPENAI_API_KEY=your_key
    GITHUB_TOKEN=your_token

------------------------------------------------------------------------

# 🐛 Troubleshooting

-   Backend error → check `.env`\
-   Frontend no data → API URL wrong\
-   Mermaid blank → syntax error\
-   GitHub limit → use token

------------------------------------------------------------------------

# 🤝 Contributing

1.  Fork\
2.  Create branch\
3.  Commit\
4.  Push & PR

------------------------------------------------------------------------

# 📝 License

MIT License
