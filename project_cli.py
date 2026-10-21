#!/usr/bin/env python3
"""
project_cli.py - Unified Course Project Scaffolder & Blog Publisher
-------------------------------------------------------------------
A zero-dependency CLI tool to:
1. Scaffold course projects with:
   - architecture_and_notes/
   - README.md (rich metadata: where taught, instructor, syllabus, objectives)
   - tinker/ (notebooks & exploratory experiments)
   - blog/ (technical post draft & visual assets)
   - deployable/ (standalone Git-initialized microservice / repo)
2. Sync & reflect project blogs directly into `research-notebooks/` bundles,
   auto-updating the Single-Request Manifest (`manifest.json`) and triggering CDN cache purges.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 stdout encoding for Windows terminals
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent
COURSES_DIR = ROOT_DIR / "courses"
RESEARCH_DIR = ROOT_DIR / "research-notebooks"
MANIFEST_FILE = RESEARCH_DIR / "manifest.json"

NOTEBOOK_TEMPLATE = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Exploratory Data Analysis & Prototyping\n",
                "\n",
                "This notebook is designated for exploratory analysis, experimentation, and feature prototyping."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import numpy as np\n",
                "import pandas as pd\n",
                "\n",
                "print('Environment initialized successfully.')"
            ]
        }
    ],
    "metadata": {
        "language_info": {"name": "python", "version": "3.11"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}


def slugify(text: str) -> str:
    """Converts a title or name into a clean kebab-case slug."""
    text = text.lower().strip()
    for char in [" ", "_", "/", "\\", ":", ";", ".", ","]:
        text = text.replace(char, "-")
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-")


def prompt_input(prompt: str, default: str = "") -> str:
    """Prompt user with an optional default value."""
    if default:
        raw = input(f"{prompt} [{default}]: ").strip()
        return raw if raw else default
    else:
        while True:
            raw = input(f"{prompt}: ").strip()
            if raw:
                return raw


def cmd_new(args):
    """Scaffolds a new course project."""
    print("=" * 60)
    print("🚀 Scaffolding New Course Project")
    print("=" * 60)

    course_name = args.course or prompt_input("Course ID / Folder name (e.g. deeplearning-ai-mlops)")
    project_name = args.project or prompt_input("Project Name (e.g. model-monitoring-service)")
    platform = args.platform or prompt_input("Platform / Institution (e.g. Coursera, DeepLearning.AI, Stanford)", "Self-Directed")
    instructor = args.instructor or prompt_input("Instructor Name(s)", "Self-Taught")
    course_url = args.url or prompt_input("Course / Syllabus URL", "N/A")
    objective = args.objective or prompt_input("Project Objective", "Build, evaluate, and deploy a production-grade AI solution.")
    tech_stack = args.tech_stack or prompt_input("Primary Tech Stack (comma-separated)", "Python, PyTorch, Docker")

    course_slug = slugify(course_name)
    project_slug = slugify(project_name)

    project_dir = COURSES_DIR / course_slug / project_slug
    if project_dir.exists():
        print(f"❌ Error: Project directory already exists at: {project_dir}")
        sys.exit(1)

    print(f"\n📂 Creating directory tree at: {project_dir}")
    arch_dir = project_dir / "architecture_and_notes"
    tinker_dir = project_dir / "tinker"
    blog_dir = project_dir / "blog"
    blog_assets_dir = blog_dir / "assets"
    deploy_dir = project_dir / "deployable"
    deploy_src_dir = deploy_dir / "src"

    for d in [arch_dir, tinker_dir, blog_assets_dir, deploy_src_dir]:
        d.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    # 1. README.md
    readme_content = f"""# {project_name.replace('-', ' ').title()}

> **{objective}**

---

## 📌 Course & Curriculum Metadata

| Field | Details |
| :--- | :--- |
| **Course Title** | `{course_name}` |
| **Platform / Institution** | {platform} |
| **Instructor(s)** | {instructor} |
| **Course / Syllabus URL** | [{course_url}]({course_url}) |
| **Start Date** | {today} |
| **Status** | 🚧 In Progress |
| **Tech Stack** | `{tech_stack}` |

---

## 📂 Project Architecture

```text
{project_slug}/
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
"""
    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 2. architecture_and_notes/architecture.md
    arch_content = f"""# System Architecture & Technical Specifications

**Project:** {project_name}  
**Course:** {course_name}  
**Date:** {today}

---

## 1. High-Level Flowchart

```mermaid
graph TD
    Client([Client / API Consumer]) --> Gateway[API Gateway / Service]
    Gateway --> Preprocessor[Data Preprocessing Pipeline]
    Preprocessor --> Inference[Model Inference Engine]
    Inference --> Storage[(Database / Feature Store)]
```

---

## 2. Technical Decisions & ADR Notes

- **Language / Framework:** {tech_stack}
- **Data Ingestion Strategy:**
- **Inference Strategy:**
- **Observability & Logging:**
"""
    (arch_dir / "architecture.md").write_text(arch_content, encoding="utf-8")

    # 3. tinker/exploration.ipynb
    (tinker_dir / "exploration.ipynb").write_text(json.dumps(NOTEBOOK_TEMPLATE, indent=1), encoding="utf-8")

    # 4. blog/article.md
    blog_content = f"""---
title: "{project_name.replace('-', ' ').title()}"
slug: "{project_slug}"
course: "{course_slug}"
platform: "{platform}"
instructor: "{instructor}"
date: "{today}"
tags: [{', '.join(f'"{t.strip()}"' for t in tech_stack.split(','))}]
excerpt: "{objective}"
---

# {project_name.replace('-', ' ').title()}

> {objective}

---

## 1. Introduction & Problem Statement

Describe the core problem, context from **{course_name}**, and what this implementation accomplishes.

---

## 2. Architectural Blueprint & Design Choices

Explain key architectural patterns and reference diagrams placed in `assets/`.

---

## 3. Implementation Highlights

Walk through key code blocks, optimizations, and benchmarks.

---

## 4. Key Takeaways & Future Directions

Summarize learnings, failure modes encountered, and potential enhancements.
"""
    (blog_dir / "article.md").write_text(blog_content, encoding="utf-8")

    # 5. deployable/ starter files
    (deploy_src_dir / "__init__.py").write_text("", encoding="utf-8")
    deploy_main = f"""\"\"\"
Main entry point for {project_name}.
\"\"\"

def main():
    print("🚀 Initializing {project_name} service...")
    print("Loaded configuration successfully.")

if __name__ == "__main__":
    main()
"""
    (deploy_dir / "main.py").write_text(deploy_main, encoding="utf-8")
    (deploy_dir / "requirements.txt").write_text("# Production dependencies\n", encoding="utf-8")
    print("✓ Scaffolding `deployable/` service skeleton (tracked by root repository).")

    print("\n" + "=" * 60)
    print(f"✨ Project successfully created at: courses/{course_slug}/{project_slug}")
    print("=" * 60)
    print("Next steps:")
    print(f"  1. Explore notebooks:   courses/{course_slug}/{project_slug}/tinker/")
    print(f"  2. Design architecture: courses/{course_slug}/{project_slug}/architecture_and_notes/")
    print(f"  3. Write blog draft:    courses/{course_slug}/{project_slug}/blog/article.md")
    print(f"  4. Publish to blog:     python project_cli.py sync --course {course_slug} --project {project_slug}")


def cmd_sync(args):
    """Reflects a course project blog into a unified research-notebooks bundle."""
    print("=" * 60)
    print("🔄 Reflecting Course Project into `research-notebooks`")
    print("=" * 60)

    course_name = args.course or prompt_input("Course Name / Folder")
    project_name = args.project or prompt_input("Project Name / Folder")

    course_slug = slugify(course_name)
    project_slug = slugify(project_name)

    project_dir = COURSES_DIR / course_slug / project_slug
    if not project_dir.exists():
        print(f"❌ Error: Project not found at: {project_dir}")
        sys.exit(1)

    target_bundle = RESEARCH_DIR / project_slug
    target_bundle_assets = target_bundle / "assets"
    target_bundle_assets.mkdir(parents=True, exist_ok=True)

    print(f"Target research bundle: {target_bundle}")

    # Copy blog article
    src_article = project_dir / "blog" / "article.md"
    dst_article = target_bundle / "article.md"
    if src_article.exists():
        dst_article.write_text(src_article.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"✓ Synced article: {dst_article.name}")
    else:
        print(f"⚠️ Warning: No blog article found at {src_article}")

    # Copy architecture notes
    src_arch = project_dir / "architecture_and_notes" / "architecture.md"
    dst_arch = target_bundle / "architecture.md"
    if src_arch.exists():
        dst_arch.write_text(src_arch.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"✓ Synced architecture: {dst_arch.name}")

    # Copy exploration notebook
    src_nb = project_dir / "tinker" / "exploration.ipynb"
    dst_nb = target_bundle / "notebook.ipynb"
    if src_nb.exists():
        dst_nb.write_text(src_nb.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"✓ Synced notebook: {dst_nb.name}")

    # Copy blog assets
    src_assets = project_dir / "blog" / "assets"
    if src_assets.exists():
        for asset in src_assets.glob("*"):
            if asset.is_file():
                (target_bundle_assets / asset.name).write_bytes(asset.read_bytes())
                print(f"✓ Synced asset: {asset.name}")

    # Parse metadata to update manifest.json
    article_text = dst_article.read_text(encoding="utf-8") if dst_article.exists() else ""
    title = project_name.replace("-", " ").title()
    excerpt = "Comprehensive technical implementation and evaluation."
    tags = ["AI Engineering", "Data Science"]
    platform = "Self-Directed"
    instructor = "Self-Taught"
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Simple frontmatter parser
    if article_text.startswith("---"):
        parts = article_text.split("---", 2)
        if len(parts) >= 3:
            fm_lines = parts[1].strip().splitlines()
            for line in fm_lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == "title" and val:
                        title = val
                    elif key == "excerpt" and val:
                        excerpt = val
                    elif key == "platform" and val:
                        platform = val
                    elif key == "instructor" and val:
                        instructor = val
                    elif key == "date" and val:
                        date_str = val
                    elif key == "tags" and val:
                        val = val.strip("[]")
                        tags = [t.strip().strip('"').strip("'") for t in val.split(",") if t.strip()]

    # Estimate reading time (approx 200 words per minute)
    word_count = len(article_text.split())
    reading_time = max(1, round(word_count / 200))

    # Update manifest.json
    if not MANIFEST_FILE.exists():
        manifest_data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "version": "2.0.0",
            "repository": "b-bhupendra/research-notebooks",
            "updated_at": datetime.now().isoformat() + "Z",
            "cdn_base": "https://cdn.jsdelivr.net/gh/b-bhupendra/research-notebooks@main",
            "projects": []
        }
    else:
        manifest_data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))

    manifest_data["updated_at"] = datetime.now().isoformat() + "Z"
    projects = manifest_data.get("projects", [])

    entry = {
        "slug": project_slug,
        "title": title,
        "course": course_slug,
        "platform": platform,
        "instructor": instructor,
        "excerpt": excerpt,
        "tags": tags,
        "reading_time_minutes": reading_time,
        "date": date_str,
        "bundle": {
            "article": f"{project_slug}/article.md",
            "notebook": f"{project_slug}/notebook.ipynb",
            "architecture": f"{project_slug}/architecture.md",
            "assets_dir": f"{project_slug}/assets/"
        }
    }

    # Replace existing or append
    existing_idx = next((i for i, p in enumerate(projects) if p.get("slug") == project_slug), None)
    if existing_idx is not None:
        projects[existing_idx] = entry
        print(f"✓ Updated existing entry in manifest.json for slug: {project_slug}")
    else:
        projects.append(entry)
        print(f"✓ Added new entry to manifest.json for slug: {project_slug}")

    manifest_data["projects"] = projects
    MANIFEST_FILE.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    print(f"✓ Successfully wrote updated {MANIFEST_FILE}")

    # Optional Push to research-notebooks
    if args.push:
        print("\n🚀 Pushing reflected bundle to `b-bhupendra/research-notebooks`...")
        try:
            subprocess.run(["git", "add", "."], cwd=RESEARCH_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"Publish/Update bundle: {project_slug}"], cwd=RESEARCH_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=RESEARCH_DIR, check=True)
            print("✓ Pushed to GitHub! CDN purge workflow dispatched.")
        except Exception as e:
            print(f"⚠️ Git push failed or nothing to commit: {e}")

    print("\n" + "=" * 60)
    print("🎉 Reflection Complete!")
    print(f"Edge CDN Article URL: https://cdn.jsdelivr.net/gh/b-bhupendra/research-notebooks@main/{project_slug}/article.md")
    print("=" * 60)


def cmd_list(args):
    """Lists all available courses, projects, and publication status."""
    print("=" * 60)
    print("📚 Courses & Projects Overview")
    print("=" * 60)

    if not COURSES_DIR.exists():
        print("No courses directory found.")
        return

    # Load manifest slugs
    published_slugs = set()
    if MANIFEST_FILE.exists():
        try:
            m = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
            published_slugs = {p.get("slug") for p in m.get("projects", [])}
        except Exception:
            pass

    found_any = False
    for course_dir in sorted(COURSES_DIR.iterdir()):
        if course_dir.is_dir() and not course_dir.name.startswith("."):
            print(f"\n🎓 Course: {course_dir.name}")
            projects = [p for p in course_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
            if not projects:
                print("   (No projects yet)")
            for p in projects:
                found_any = True
                status_icon = "🌐 Published" if p.name in published_slugs else "📝 Local only"
                print(f"   └── 📦 {p.name} [{status_icon}]")

    if not found_any:
        print("\nNo course projects created yet. Run `python project_cli.py new` to get started!")


def main():
    parser = argparse.ArgumentParser(
        description="Unified Course Project Scaffolder & Research Hub Publisher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: new
    p_new = subparsers.add_parser("new", help="Scaffold a new course project")
    p_new.add_argument("--course", help="Course directory identifier")
    p_new.add_argument("--project", help="Project name identifier")
    p_new.add_argument("--platform", help="Platform or institution where taught")
    p_new.add_argument("--instructor", help="Course instructor")
    p_new.add_argument("--url", help="Course URL or syllabus")
    p_new.add_argument("--objective", help="Project objective / description")
    p_new.add_argument("--tech-stack", help="Primary tech stack")

    # Command: sync / publish
    p_sync = subparsers.add_parser("sync", aliases=["publish"], help="Sync project blog to research-notebooks bundle")
    p_sync.add_argument("--course", help="Course directory identifier")
    p_sync.add_argument("--project", help="Project name identifier")
    p_sync.add_argument("--push", action="store_true", help="Automatically commit & push to GitHub")

    # Command: list
    subparsers.add_parser("list", help="List all courses and project publication status")

    args = parser.parse_args()

    if args.command in ["new"]:
        cmd_new(args)
    elif args.command in ["sync", "publish"]:
        cmd_sync(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        # Default to interactive menu if no command provided
        print("Course Project Scaffolder & Publisher")
        print("1. Scaffold New Project (`new`)")
        print("2. Sync / Publish Project to Research Hub (`sync`)")
        print("3. List Courses & Projects (`list`)")
        choice = input("\nSelect an option [1-3]: ").strip()
        if choice == "1":
            args.course = None
            args.project = None
            args.platform = None
            args.instructor = None
            args.url = None
            args.objective = None
            args.tech_stack = None
            cmd_new(args)
        elif choice == "2":
            args.course = None
            args.project = None
            args.push = False
            cmd_sync(args)
        elif choice == "3":
            cmd_list(args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
