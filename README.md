# AI Engineering & Data Science

A comprehensive repository for coursework, hands-on projects, experiments, and production implementations in Artificial Intelligence, Machine Learning, Deep Learning, and Data Science.

---

## 📂 Repository Structure

All work is integrated directly under course-centric modules:

```text
ai-engineering-and-data-science/
├── project_cli.py            # ⚡ CLI to scaffold new projects & publish to research-notebooks
├── courses/                  # Coursework, projects, and implementations
│   └── <course-name>/
│       └── <project-name>/
│           ├── README.md                  # Metadata: Platform, instructor, URL, objectives
│           ├── architecture_and_notes/    # System design diagrams, ADRs, study notes
│           ├── tinker/                    # Exploratory prototyping & EDA notebooks (.ipynb)
│           ├── blog/                      # Technical article & visual assets for research hub
│           └── deployable/                # Standalone Git-initialized microservice / app
├── research-notebooks/       # Standalone public blog hub & CDN edge retrieval bundle
└── README.md
```

---

## ⚡ Project CLI (`project_cli.py`)

A zero-dependency Python tool to scaffold projects and publish technical articles to the [research-notebooks](https://github.com/b-bhupendra/research-notebooks) CDN hub.

### 1. Scaffold a New Project
```bash
# Interactive mode (prompts for course, platform, instructor, etc.):
python project_cli.py new

# Or specify flags directly:
python project_cli.py new \
  --course "ml-foundations" \
  --project "spam-detection-classifier" \
  --platform "Coursera / Stanford" \
  --instructor "Andrew Ng" \
  --url "https://coursera.org/learn/machine-learning" \
  --objective "End-to-end spam SMS classification using Naive Bayes and Logistic Regression" \
  --tech-stack "Python, Scikit-Learn, FastAPI"
```

### 2. Publish / Sync Blog to Research Hub
```bash
# Sync local blog draft, notebook, and architecture to research-notebooks/ bundle:
python project_cli.py sync --course ml-foundations --project spam-detection-classifier

# Automatically commit and push to GitHub (triggers CDN purge & webhook):
python project_cli.py sync --course ml-foundations --project spam-detection-classifier --push
```

### 3. List All Courses & Projects
```bash
python project_cli.py list
```

---

## 🛠️ Tech Stack & Tools

- **Languages:** Python, SQL
- **Data & ML Libraries:** NumPy, Pandas, Scikit-Learn, PyTorch / TensorFlow
- **Data Engineering & Ops:** Git, DVC, Docker, MLflow, FastAPI
- **Environments:** Jupyter Lab / Notebooks, VS Code

---

## 🔗 Connected Research Hub

- **[b-bhupendra/research-notebooks](https://github.com/b-bhupendra/research-notebooks)**: Public CDN-powered technical research repository utilizing the single-request manifest pattern, Brotli compression, and automated edge cache invalidation.

---
*Created for tracking course progress, implementations, and AI engineering milestones.*
