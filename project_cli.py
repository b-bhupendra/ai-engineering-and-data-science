#!/usr/bin/env python3
"""
project_cli.py - Course Project Scaffolder & Research Hub Publisher
-------------------------------------------------------------------
A clean, zero-dependency CLI tool to:
1. Scaffold course/tutorial projects under `courses/<slug>/` with:
   - architecture_and_notes/ (system blueprints & notes)
   - README.md (curriculum metadata: where taught, instructor, syllabus, objectives)
   - tinker/ (clean empty directory for scratchpads, notebooks, exploratory scripts)
   - blog/ (technical article draft & assets)
   - deployable/ (clean empty directory for production/deployment code)
2. Reflect & publish project blogs into `research-notebooks/` bundles,
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


def slugify(text: str) -> str:
    """Converts a title or name into a clean kebab-case slug."""
    text = text.lower().strip()
    for char in [" ", "_", "/", "\\", ":", ";", ".", ",", "(", ")", "[", "]", "{", "}"]:
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


def resolve_project_dir(name_or_course: str, subproject: str = None) -> Path:
    """Resolves project path, handling both flat courses/<name>/ and nested courses/<course>/<project>/."""
    slug_1 = slugify(name_or_course)
    if subproject and slugify(subproject) != slug_1:
        slug_2 = slugify(subproject)
        return COURSES_DIR / slug_1 / slug_2
    return COURSES_DIR / slug_1


def cmd_new(args):
    """Scaffolds a new course project without double-nesting and leaves folders clean."""
    print("=" * 60)
    print("🚀 Scaffolding New Course Project")
    print("=" * 60)

    raw_name = args.name or args.course or prompt_input("Course / Project Name (e.g. eda-in-hospitality-domain)")
    raw_sub = args.project

    # Avoid duplicate naming if course and project are identical
    if raw_sub and slugify(raw_sub) == slugify(raw_name):
        raw_sub = None

    platform = args.platform or prompt_input("Platform / Institution (e.g. Codebasics, Coursera, YouTube)", "Self-Directed")
    instructor = args.instructor or prompt_input("Instructor Name(s)", "Self-Taught")
    course_url = args.url or prompt_input("Course / Syllabus URL", "N/A")
    objective = args.objective or prompt_input("Project Objective", "Hands-on implementation and domain analysis.")
    tech_stack = args.tech_stack or prompt_input("Primary Tech Stack / Tools (e.g. Python, SQL, PowerBI, Excel)", "General")

    project_dir = resolve_project_dir(raw_name, raw_sub)
    if project_dir.exists():
        print(f"❌ Error: Project directory already exists at: {project_dir}")
        sys.exit(1)

    project_slug = project_dir.name
    display_title = project_slug.replace("-", " ").title()

    print(f"\n📂 Creating clean project structure at: {project_dir}")
    arch_dir = project_dir / "architecture_and_notes"
    tinker_dir = project_dir / "tinker"
    blog_dir = project_dir / "blog"
    blog_assets_dir = blog_dir / "assets"
    deploy_dir = project_dir / "deployable"

    for d in [arch_dir, tinker_dir, blog_assets_dir, deploy_dir]:
        d.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    # 1. README.md (acts as unified metadata index & filter for this course project)
    readme_content = f"""# {display_title}

> **{objective}**

---

## 📌 Course & Curriculum Metadata

| Field | Details |
| :--- | :--- |
| **Course / Project** | `{project_slug}` |
| **Platform / Institution** | {platform} |
| **Instructor(s)** | {instructor} |
| **Course / Syllabus URL** | [{course_url}]({course_url}) |
| **Start Date** | {today} |
| **Status** | 🚧 In Progress |
| **Tech Stack / Tools** | `{tech_stack}` |

---

## 📂 Project Organization

```text
{project_slug}/
├── architecture_and_notes/    # System blueprints, flowcharts, and study notes
│   └── architecture.md
├── tinker/                    # Scratchpads, exploratory notebooks, raw scripts (clean)
├── blog/                      # Technical article & visual assets for research hub
│   ├── article.md
│   └── assets/
└── deployable/                # Production-ready code, models, or deliverables (clean)
```

---

## 🎯 Objectives & Milestones

- [ ] Complete exploratory analysis and initial experiments in `tinker/`.
- [ ] Document architecture, methodology, and design choices in `architecture_and_notes/`.
- [ ] Package final deliverable/application in `deployable/`.
- [ ] Write technical summary in `blog/article.md` and publish via `python project_cli.py sync --name {project_slug}`.
"""
    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 2. architecture_and_notes/architecture.md
    arch_content = f"""# Architecture & Technical Notes: {display_title}

**Course / Project:** {project_slug}  
**Platform:** {platform}  
**Instructor:** {instructor}  
**Date:** {today}

---

## 1. System & Domain Flow

```mermaid
graph TD
    Data[Raw Data / Ingestion] --> Processing[Cleaning &amp; Transformation]
    Processing --> Analysis[Analysis &amp; Modeling]
    Analysis --> Insights[Insights &amp; Deliverables]
```

---

## 2. Methodology & Key Decisions

- **Domain Context:**
- **Data Sources:**
- **Key Metrics / KPIs:**
- **Assumptions & Constraints:**
"""
    (arch_dir / "architecture.md").write_text(arch_content, encoding="utf-8")

    # 3. tinker/ (leave completely clean with only .gitkeep)
    (tinker_dir / ".gitkeep").write_text("", encoding="utf-8")

    # 4. deployable/ (leave completely clean with only .gitkeep)
    (deploy_dir / ".gitkeep").write_text("", encoding="utf-8")

    # 5. blog/assets/ (clean with .gitkeep)
    (blog_assets_dir / ".gitkeep").write_text("", encoding="utf-8")

    # 6. blog/article.md
    blog_content = f"""---
title: "{display_title}"
slug: "{project_slug}"
platform: "{platform}"
instructor: "{instructor}"
date: "{today}"
tags: [{', '.join(f'"{t.strip()}"' for t in tech_stack.split(','))}]
excerpt: "{objective}"
---

# {display_title}

> {objective}

---

## 1. Overview & Business Context

Introduce the domain problem, objectives, and real-world implications explored in this project.

---

## 2. Methodology & Exploration

Detail the techniques, tools, data hygiene practices, and exploration findings.

---

## 3. Key Findings & Insights

Highlight major takeaways, visualizations (place images in `assets/`), and actionable metrics.

---

## 4. Conclusion & Next Steps

Summarize the outcomes and future scope.
"""
    (blog_dir / "article.md").write_text(blog_content, encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"✨ Project successfully created at: {project_dir.relative_to(ROOT_DIR)}")
    print("=" * 60)
    print("Clean directories ready for your work:")
    print(f"  • tinker/:       Place scratchpads, notebooks, scripts, or queries here (no forced boilerplate).")
    print(f"  • deployable/:   Place your deliverable/production code here.")
    print(f"  • blog/:         Draft your article in `blog/article.md`.")
    print(f"  • Publish command: python project_cli.py sync --name {project_slug}")


def find_project_directory(identifier: str) -> Path:
    """Finds project by slug in courses/ (either flat courses/<slug> or nested courses/<course>/<slug>)."""
    target_slug = slugify(identifier)

    # 1. Direct match: courses/<slug>
    direct = COURSES_DIR / target_slug
    if direct.exists() and direct.is_dir():
        return direct

    # 2. Search subdirectories: courses/*/<slug>
    if COURSES_DIR.exists():
        for course_folder in COURSES_DIR.iterdir():
            if course_folder.is_dir():
                sub = course_folder / target_slug
                if sub.exists() and sub.is_dir():
                    return sub

    return None


def cmd_sync(args):
    """Reflects a course project blog into a unified research-notebooks bundle."""
    print("=" * 60)
    print("🔄 Reflecting Course Project into `research-notebooks`")
    print("=" * 60)

    identifier = args.name or args.project or args.course or prompt_input("Project / Course Name")
    project_dir = find_project_directory(identifier)

    if not project_dir or not project_dir.exists():
        print(f"❌ Error: Could not locate project directory for '{identifier}' under `courses/`")
        sys.exit(1)

    project_slug = project_dir.name
    target_bundle = RESEARCH_DIR / project_slug
    target_bundle_assets = target_bundle / "assets"
    target_bundle_assets.mkdir(parents=True, exist_ok=True)

    print(f"Found course project: {project_dir.relative_to(ROOT_DIR)}")
    print(f"Target research bundle: {target_bundle.relative_to(ROOT_DIR)}")

    # 1. Copy blog article
    src_article = project_dir / "blog" / "article.md"
    dst_article = target_bundle / "article.md"
    if src_article.exists():
        dst_article.write_text(src_article.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"✓ Synced article: {dst_article.name}")
    else:
        print(f"⚠️ Warning: No blog article found at {src_article}")

    # 2. Copy architecture notes
    src_arch = project_dir / "architecture_and_notes" / "architecture.md"
    dst_arch = target_bundle / "architecture.md"
    if src_arch.exists():
        dst_arch.write_text(src_arch.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"✓ Synced architecture: {dst_arch.name}")

    # 3. Copy notebook or analysis files from tinker/ if present
    src_tinker = project_dir / "tinker"
    dst_nb = target_bundle / "notebook.ipynb"
    if src_tinker.exists():
        notebooks = list(src_tinker.glob("*.ipynb"))
        if notebooks:
            dst_nb.write_text(notebooks[0].read_text(encoding="utf-8"), encoding="utf-8")
            print(f"✓ Synced primary notebook: {notebooks[0].name} -> notebook.ipynb")
        elif dst_nb.exists():
            # If no notebook in tinker, ensure no obsolete notebook remains
            pass

    # 4. Copy blog assets
    src_assets = project_dir / "blog" / "assets"
    if src_assets.exists():
        for asset in src_assets.glob("*"):
            if asset.is_file() and asset.name != ".gitkeep":
                (target_bundle_assets / asset.name).write_bytes(asset.read_bytes())
                print(f"✓ Synced asset: {asset.name}")

    # 5. Parse metadata to update manifest.json
    article_text = dst_article.read_text(encoding="utf-8") if dst_article.exists() else ""
    title = project_slug.replace("-", " ").title()
    excerpt = "Comprehensive technical implementation and domain analysis."
    tags = ["Data Science", "Analysis"]
    platform = "Self-Directed"
    instructor = "Self-Taught"
    date_str = datetime.now().strftime("%Y-%m-%d")

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
        "course": project_dir.parent.name if project_dir.parent != COURSES_DIR else project_slug,
        "platform": platform,
        "instructor": instructor,
        "excerpt": excerpt,
        "tags": tags,
        "reading_time_minutes": reading_time,
        "date": date_str,
        "bundle": {
            "article": f"{project_slug}/article.md",
            "notebook": f"{project_slug}/notebook.ipynb" if dst_nb.exists() else None,
            "architecture": f"{project_slug}/architecture.md" if dst_arch.exists() else None,
            "assets_dir": f"{project_slug}/assets/"
        }
    }

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

    published_slugs = set()
    if MANIFEST_FILE.exists():
        try:
            m = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
            published_slugs = {p.get("slug") for p in m.get("projects", [])}
        except Exception:
            pass

    found_any = False
    for item in sorted(COURSES_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            # Check if it has direct project folders inside (e.g. architecture_and_notes) or subprojects
            has_direct_project = (item / "architecture_and_notes").exists() or (item / "README.md").exists()
            if has_direct_project:
                found_any = True
                status_icon = "🌐 Published" if item.name in published_slugs else "📝 Local only"
                print(f"📦 {item.name} [{status_icon}]")
            else:
                # Grouped course folder
                subprojects = [p for p in item.iterdir() if p.is_dir() and not p.name.startswith(".")]
                if subprojects:
                    found_any = True
                    print(f"🎓 Course: {item.name}")
                    for sp in subprojects:
                        status_icon = "🌐 Published" if sp.name in published_slugs else "📝 Local only"
                        print(f"   └── 📦 {sp.name} [{status_icon}]")

    if not found_any:
        print("\nNo course projects found. Run `python project_cli.py new` to create one!")


def main():
    parser = argparse.ArgumentParser(
        description="Unified Course Project Scaffolder & Research Hub Publisher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: new
    p_new = subparsers.add_parser("new", help="Scaffold a new course project")
    p_new.add_argument("--name", help="Course or project name (e.g. eda-in-hospitality-domain)")
    p_new.add_argument("--course", help="Course identifier (alias for --name if no subproject)")
    p_new.add_argument("--project", help="Optional subproject identifier")
    p_new.add_argument("--platform", help="Platform or institution where taught")
    p_new.add_argument("--instructor", help="Course instructor")
    p_new.add_argument("--url", help="Course URL or syllabus")
    p_new.add_argument("--objective", help="Project objective / description")
    p_new.add_argument("--tech-stack", help="Primary tech stack / tools")

    # Command: sync / publish
    p_sync = subparsers.add_parser("sync", aliases=["publish"], help="Sync project blog to research-notebooks bundle")
    p_sync.add_argument("--name", help="Project name / slug to sync")
    p_sync.add_argument("--course", help="Course directory identifier")
    p_sync.add_argument("--project", help="Subproject identifier")
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
        print("Course Project Scaffolder & Publisher")
        print("1. Scaffold New Project (`new`)")
        print("2. Sync / Publish Project to Research Hub (`sync`)")
        print("3. List Courses & Projects (`list`)")
        choice = input("\nSelect an option [1-3]: ").strip()
        if choice == "1":
            args.name = None
            args.course = None
            args.project = None
            args.platform = None
            args.instructor = None
            args.url = None
            args.objective = None
            args.tech_stack = None
            cmd_new(args)
        elif choice == "2":
            args.name = None
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
