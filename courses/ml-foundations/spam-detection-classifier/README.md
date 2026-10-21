# Spam Detection Classifier

> **End-to-end spam SMS classification using Naive Bayes and Logistic Regression**

---

## 📌 Course & Curriculum Metadata

| Field | Details |
| :--- | :--- |
| **Course Title** | `ml-foundations` |
| **Platform / Institution** | Coursera / Stanford |
| **Instructor(s)** | Andrew Ng |
| **Course / Syllabus URL** | [https://coursera.org/learn/machine-learning](https://coursera.org/learn/machine-learning) |
| **Start Date** | 2026-10-21 |
| **Status** | 🚧 In Progress |
| **Tech Stack** | `Python, Scikit-Learn, FastAPI` |

---

## 📂 Project Architecture

```text
spam-detection-classifier/
├── architecture_and_notes/    # System design diagrams, ADRs, study notes
│   └── architecture.md
├── tinker/                    # Exploratory prototyping & EDA notebooks
│   └── exploration.ipynb
├── blog/                      # Technical article & visual assets for research-notebooks
│   ├── article.md
│   └── assets/
└── deployable/                # Standalone Git-initialized microservice / package
    ├── src/
    ├── requirements.txt
    └── main.py
```

---

## 🎯 Objectives & Milestones

- [ ] Complete exploratory analysis and initial model prototyping in `tinker/`.
- [ ] Define system architecture and technical design specifications in `architecture_and_notes/`.
- [ ] Implement production service with tests and containerization in `deployable/`.
- [ ] Draft technical article in `blog/article.md` and publish to `research-notebooks` via `python project_cli.py sync`.

---

## 🚀 Running the Deployable Service

```bash
cd deployable
pip install -r requirements.txt
python main.py
```
