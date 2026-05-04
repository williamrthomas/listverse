#!/usr/bin/env python3
"""Fix 404 entries and add more entries to reach ~100 new."""

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LISTS_JSON = REPO_ROOT / "data" / "lists.json"
LISTS_CSV = REPO_ROOT / "data" / "lists.csv"
TAGS_JSON = REPO_ROOT / "data" / "tags.json"

TODAY = "2026-05-04"


def fetch_gh_stats(owner, repo):
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}", "--jq",
             '{stars: .stargazers_count, forks: .forks_count, pushed: .pushed_at, '
             'issues: .open_issues_count, archived: .archived, watchers: .watchers_count, '
             'created: .created_at, license: .license.spdx_id}'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except:
        return None


def stars_approx(count):
    if count >= 1000:
        k = count / 1000
        if k >= 100:
            return f"{int(k)}k"
        elif k >= 10:
            return f"{k:.0f}k"
        else:
            return f"{k:.1f}k"
    return str(count)


def compute_quality_score(stars, last_commit, entry_count_str):
    score = 0.0
    if stars >= 50000: score += 3.0
    elif stars >= 10000: score += 2.5
    elif stars >= 5000: score += 2.0
    elif stars >= 1000: score += 1.5
    elif stars >= 500: score += 1.0
    else: score += 0.5

    from datetime import datetime
    if last_commit and last_commit != "unknown":
        try:
            lc = datetime.strptime(last_commit[:10], "%Y-%m-%d")
            days_ago = (datetime(2026, 5, 4) - lc).days
            if days_ago < 30: score += 3.0
            elif days_ago < 90: score += 2.5
            elif days_ago < 180: score += 2.0
            elif days_ago < 365: score += 1.5
            elif days_ago < 730: score += 1.0
            else: score += 0.5
        except: score += 1.0
    else:
        score += 1.0

    ec = entry_count_str.replace("+", "").replace(",", "").strip()
    try:
        ec_num = int(ec)
        if ec_num >= 500: score += 2.0
        elif ec_num >= 200: score += 1.5
        elif ec_num >= 100: score += 1.0
        else: score += 0.5
    except: score += 1.0

    score += 2.0  # curated bonus
    return min(10, max(1, round(score)))


def enrich_entry(entry):
    url = entry["github_url"]
    parts = url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    print(f"  Fetching {owner}/{repo}...", end=" ", flush=True)

    stats = fetch_gh_stats(owner, repo)
    if not stats:
        print("FAILED")
        return False

    entry["stars_count"] = stats["stars"]
    entry["forks_count"] = stats["forks"]
    entry["last_commit_date"] = stats["pushed"][:10] if stats.get("pushed") else "unknown"
    entry["open_issues_count"] = stats["issues"]
    entry["is_archived"] = stats["archived"]
    entry["watchers_count"] = stats["watchers"]
    entry["created_year"] = int(stats["created"][:4]) if stats.get("created") else 2020
    entry["stars_approx"] = stars_approx(stats["stars"])
    entry["added_date"] = TODAY
    entry["last_activity"] = entry["last_commit_date"][:4] if entry["last_commit_date"] != "unknown" else "unknown"
    entry["license"] = stats.get("license") or "Unknown"
    if entry["license"] == "NOASSERTION":
        entry["license"] = "Unknown"
    entry["quality_score"] = compute_quality_score(stats["stars"], entry["last_commit_date"], entry.get("entry_count_approx", "100+"))
    print(f"OK ({stats['stars']:,} stars)")
    return True


ADDITIONAL_ENTRIES = [
    # Replace awesome-datasets-ml (404) with a valid alternative
    {
        "id": "datasciencemasters",
        "name": "The Open Source Data Science Masters",
        "github_url": "https://github.com/datasciencemasters/go",
        "description": "An open-source curriculum for learning data science — a free alternative to expensive data science programs.",
        "maintainer": "datasciencemasters",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["data-science", "curriculum", "learning", "open-source"],
        "entry_count_approx": "100+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "A well-structured self-paced data science curriculum covering math, statistics, programming, and ML. Each topic links to free courses, textbooks, and datasets. The opinionated learning path saves you from the paradox of choice that plagues self-learners.",
        "related_lists": ["awesome-datascience", "awesome-public-datasets"],
        "list_type": "tutorials",
        "audience_level": "beginner",
        "use_cases": ["self-paced data science education", "finding free learning resources", "structured curriculum planning"],
        "has_website": True,
        "website_url": "http://datasciencemasters.org",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["awesome-datascience"],
        "best_sections": ["Fundamentals", "Machine Learning", "Visualization"],
        "getting_started": "Follow the curriculum sequentially — it's designed as a learning path from foundations (math, stats) to practice (ML, visualization). Each resource is annotated with time estimates and difficulty. Start with the fundamentals even if you're tempted to skip ahead.",
        "suggested_projects": [
            "Complete the full curriculum and build a capstone project applying techniques from each section",
            "Create a progress tracker dashboard that monitors your completion of each curriculum section",
            "Fork the curriculum and customize it for your specific data science career goals"
        ],
        "featured_example": {
            "name": "The curriculum structure",
            "url": "https://github.com/datasciencemasters/go#the-open-source-data-science-masters",
            "why": "The opinionated ordering of topics — fundamentals first, then tools, then specialization — reflects how data science is actually practiced"
        }
    },
    # Replace langchain-rag-examples (404) with a valid repo
    {
        "id": "rag-from-scratch",
        "name": "RAG From Scratch",
        "github_url": "https://github.com/langchain-ai/rag-from-scratch",
        "description": "LangChain's comprehensive tutorial series on building RAG applications from scratch.",
        "maintainer": "langchain-ai",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["rag", "langchain", "tutorials", "llm"],
        "entry_count_approx": "20+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The official LangChain RAG tutorial series — builds up RAG concepts progressively from basic retrieval to advanced techniques like query decomposition, re-ranking, and CRAG. Each lesson has both a video explanation and a runnable notebook. The best structured resource for learning RAG properly.",
        "related_lists": ["awesome-langchain", "chroma", "weaviate"],
        "list_type": "tutorials",
        "audience_level": "intermediate",
        "use_cases": ["learning RAG patterns", "RAG implementation", "understanding retrieval techniques"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["awesome-langchain"],
        "best_sections": ["Indexing", "Retrieval", "Generation"],
        "getting_started": "Follow the notebooks in order — each builds on the previous. Start with the basics of indexing and retrieval, then progress to advanced techniques like multi-query, RAG fusion, and corrective RAG. Each notebook is self-contained and runnable.",
        "suggested_projects": [
            "Build a document QA system implementing each RAG technique from the series and compare their effectiveness",
            "Create an evaluation framework that benchmarks basic vs advanced RAG techniques on your own documents",
            "Develop a RAG pipeline that combines the best techniques from the series into a production-ready system"
        ],
        "featured_example": {
            "name": "Corrective RAG (CRAG)",
            "url": "https://github.com/langchain-ai/rag-from-scratch",
            "why": "The CRAG notebook shows how to add self-correction to RAG — the system evaluates retrieved documents and falls back to web search if they're irrelevant"
        }
    },
    # Additional entries to reach ~100
    {
        "id": "awesome-react",
        "name": "Awesome React",
        "github_url": "https://github.com/enaqx/awesome-react",
        "description": "A collection of awesome things regarding the React ecosystem — libraries, tools, and resources.",
        "maintainer": "enaqx",
        "category": "Developer Tools & Coding",
        "subcategory": "JavaScript",
        "tags": ["react", "javascript", "web-development", "frontend"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive React ecosystem directory — covers everything from state management to testing to animation. Organized by concern rather than alphabetically, making it practical for finding solutions. The ecosystem breadth is staggering, reflecting React's dominance in frontend development.",
        "related_lists": ["awesome-javascript", "awesome-nodejs"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["finding React libraries", "learning React patterns", "building React applications"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": "javascript",
        "overlaps_with": ["awesome-javascript"],
        "best_sections": ["React State Management", "React Styling", "React Testing"],
        "getting_started": "Navigate by the concern you're solving — state management, routing, forms, etc. The 'React General Resources' section has the best learning materials. For library selection, check star counts and recent activity in the linked repos.",
        "suggested_projects": [
            "Build a React application using one library from each major category (state, routing, forms, testing) from this list",
            "Create a React library comparison dashboard that tracks stars, downloads, and bundle sizes across competing libraries",
            "Develop a React project starter kit using the most recommended tools from each category"
        ],
        "featured_example": {
            "name": "React Official Documentation",
            "url": "https://react.dev",
            "why": "The new React docs (react.dev) are the best framework documentation ever written — interactive examples, hooks-first approach, and escape hatches for every concept"
        }
    },
    {
        "id": "awesome-typescript",
        "name": "Awesome TypeScript",
        "github_url": "https://github.com/dzharii/awesome-typescript",
        "description": "A collection of awesome TypeScript resources — libraries, tools, tutorials, and patterns.",
        "maintainer": "dzharii",
        "category": "Developer Tools & Coding",
        "subcategory": "TypeScript",
        "tags": ["typescript", "javascript", "web-development", "tools"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive TypeScript ecosystem directory — covers the type system, tooling, runtime libraries, and patterns. Uniquely includes sections on advanced type-level programming and utility types. Essential for TypeScript developers beyond the basics.",
        "related_lists": ["awesome-javascript", "awesome-react"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["finding TypeScript tools", "learning advanced TypeScript", "TypeScript library discovery"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": "typescript",
        "overlaps_with": ["awesome-javascript"],
        "best_sections": ["Libraries", "Tools", "Tutorials"],
        "getting_started": "Start with the 'Tutorials' section if learning TypeScript. For experienced developers, the 'Tools' and 'Libraries' sections are organized by use case. The 'Awesome TypeScript' section covers advanced patterns and type-level programming.",
        "suggested_projects": [
            "Build a full-stack TypeScript application using libraries from this list for both frontend and backend",
            "Create a TypeScript utility type library inspired by the advanced type patterns documented here",
            "Develop a TypeScript project template with linting, testing, and build tools from this collection"
        ],
        "featured_example": {
            "name": "TypeScript Handbook",
            "url": "https://www.typescriptlang.org/docs/handbook/",
            "why": "The official TypeScript Handbook is the gold standard for learning TypeScript's type system — from basics to advanced generics and conditional types"
        }
    },
    {
        "id": "awesome-fastapi",
        "name": "Awesome FastAPI",
        "github_url": "https://github.com/mjhea0/awesome-fastapi",
        "description": "A curated list of awesome things related to FastAPI — the modern Python web framework.",
        "maintainer": "mjhea0",
        "category": "Developer Tools & Coding",
        "subcategory": "Python",
        "tags": ["python", "fastapi", "web-development", "api"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The go-to resource for FastAPI developers — covers extensions, boilerplates, tutorials, and production patterns. FastAPI has become the default choice for Python APIs, and this list catalogs the ecosystem that's grown around it. The 'Open Source Projects' section showcases real-world FastAPI applications.",
        "related_lists": ["awesome-python", "awesome-api-devtools"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["finding FastAPI extensions", "learning FastAPI patterns", "building Python APIs"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": "python",
        "overlaps_with": ["awesome-python"],
        "best_sections": ["Third-Party Extensions", "Tutorials", "Open Source Projects"],
        "getting_started": "Start with the 'Tutorials' section for learning, then browse 'Third-Party Extensions' for authentication, databases, and caching. The 'Boilerplates' section saves days of setup for new projects.",
        "suggested_projects": [
            "Build a production-ready REST API using FastAPI with authentication, database, and caching extensions from this list",
            "Create a FastAPI microservice template incorporating the best practices from the listed tutorials",
            "Develop a FastAPI extension comparison tool that benchmarks competing libraries for common needs (auth, ORM, caching)"
        ],
        "featured_example": {
            "name": "FastAPI Official Tutorial",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "why": "FastAPI's official tutorial is one of the best API framework tutorials ever written — it teaches type hints, dependency injection, and async in the context of building real APIs"
        }
    },
    {
        "id": "awesome-llm-reasoning",
        "name": "Awesome LLM Reasoning",
        "github_url": "https://github.com/atfortes/Awesome-LLM-Reasoning",
        "description": "A curated collection of papers and resources on reasoning in large language models.",
        "maintainer": "atfortes",
        "category": "AI & Machine Learning",
        "subcategory": "Large Language Models",
        "tags": ["llm", "reasoning", "research", "papers"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Focuses on the hottest area of LLM research — reasoning capabilities. Covers chain-of-thought, tool use, mathematical reasoning, and multi-step problem solving. The taxonomy of reasoning types is uniquely valuable for understanding the landscape of LLM capability research.",
        "related_lists": ["awesome-llm", "awesome-deep-learning"],
        "list_type": "papers",
        "audience_level": "advanced",
        "use_cases": ["LLM reasoning research", "understanding chain-of-thought", "improving LLM outputs"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-llm"],
        "best_sections": ["Chain-of-Thought", "Tool Use", "Mathematical Reasoning"],
        "getting_started": "Start with the 'Survey Papers' section for an overview of LLM reasoning capabilities. Then dive into specific reasoning types (chain-of-thought, tool use, planning) matching your research interest. Papers are chronologically ordered within each section.",
        "suggested_projects": [
            "Implement and compare different chain-of-thought prompting strategies on a benchmark dataset",
            "Build a reasoning evaluation framework that tests LLMs on multi-step problems using techniques from these papers",
            "Create a survey visualization showing the evolution of LLM reasoning techniques over time"
        ],
        "featured_example": {
            "name": "Chain-of-Thought Prompting",
            "url": "https://arxiv.org/abs/2201.11903",
            "why": "The chain-of-thought paper showed that simply asking LLMs to 'think step by step' dramatically improves reasoning — one of the most impactful prompting discoveries"
        }
    },
    {
        "id": "awesome-rag",
        "name": "Awesome RAG",
        "github_url": "https://github.com/frutik/Awesome-RAG",
        "description": "A curated list of resources and research on Retrieval-Augmented Generation.",
        "maintainer": "frutik",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["rag", "llm", "retrieval", "research"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive RAG-specific resource list — covers papers, tools, techniques, and evaluation methods. While other lists include RAG as a section, this one dives deep into the nuances (chunking strategies, re-ranking, hybrid search, multi-modal RAG). Essential for anyone building production RAG systems.",
        "related_lists": ["chroma", "weaviate", "awesome-langchain"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["building RAG systems", "RAG research", "improving retrieval quality"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Papers", "Tools", "Evaluation"],
        "getting_started": "Start with the foundational RAG papers, then explore the 'Tools' section for practical implementation options. The 'Evaluation' section is critical — many RAG systems fail because teams don't measure retrieval quality properly.",
        "suggested_projects": [
            "Build a RAG evaluation pipeline using the metrics and benchmarks from the Evaluation section",
            "Implement and compare different chunking strategies (fixed, semantic, recursive) using tools from this list",
            "Create a RAG pipeline that combines techniques from multiple papers (hybrid search + re-ranking + query expansion)"
        ],
        "featured_example": {
            "name": "RAG survey papers",
            "url": "https://github.com/frutik/Awesome-RAG#survey",
            "why": "The survey papers provide the most comprehensive overview of RAG techniques, limitations, and best practices — required reading before building a production RAG system"
        }
    },
    {
        "id": "awesome-ci-cd",
        "name": "Awesome CI/CD",
        "github_url": "https://github.com/cicdops/awesome-ciandcd",
        "description": "A curated list of awesome tools for continuous integration, continuous delivery, and DevOps.",
        "maintainer": "cicdops",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["ci-cd", "devops", "automation", "tools"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive CI/CD tool directory — covers build, test, deploy, and monitoring tools across the entire delivery pipeline. Includes both self-hosted and SaaS options. The breadth covers everything from Jenkins to GitHub Actions to obscure but powerful alternatives.",
        "related_lists": ["awesome-sysadmin", "devops-exercises"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["choosing CI/CD tools", "building delivery pipelines", "automating deployments"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Online Build System", "Self-Hosted Build System", "Deploy"],
        "getting_started": "Browse by the pipeline stage you need — Build, Test, Deploy, Monitor. Then decide between hosted (GitHub Actions, CircleCI) and self-hosted (Jenkins, Drone) based on your infrastructure. The 'Deploy' section covers both traditional and container-based deployment tools.",
        "suggested_projects": [
            "Set up a complete CI/CD pipeline for a multi-service application using tools from each category",
            "Build a CI/CD tool comparison that benchmarks build times, pricing, and feature sets across the listed options",
            "Create a pipeline template generator that scaffolds CI/CD configurations based on your tech stack"
        ],
        "featured_example": {
            "name": "GitHub Actions",
            "url": "https://github.com/features/actions",
            "why": "GitHub Actions has become the default CI/CD for open-source projects — its marketplace, native GitHub integration, and generous free tier make it the easiest starting point"
        }
    },
    {
        "id": "awesome-actions",
        "name": "Awesome GitHub Actions",
        "github_url": "https://github.com/sdras/awesome-actions",
        "description": "A curated list of awesome GitHub Actions — workflows, utilities, and deployment tools.",
        "maintainer": "sdras",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["github-actions", "ci-cd", "automation", "devops"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Curated by Sarah Drasner (former VP of Developer Experience at Netlify), this list catalogs the best GitHub Actions by category. The quality bar is high — each action includes a brief description and has been reviewed for usefulness. The 'Deployment' and 'Linting' sections are particularly valuable.",
        "related_lists": ["awesome-ci-cd", "github-cheat-sheet"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding GitHub Actions", "automating workflows", "CI/CD with GitHub"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Deployment", "Linting", "Utilities"],
        "getting_started": "Browse by what you want to automate — deployment, testing, linting, or project management. Each action includes setup instructions and example workflows. Start with the 'Starter Workflows' section for common patterns.",
        "suggested_projects": [
            "Set up a comprehensive GitHub Actions workflow combining linting, testing, and deployment actions from this list",
            "Create a custom GitHub Action that solves a common workflow problem in your organization",
            "Build an actions comparison tool that tracks reliability and performance of similar actions"
        ],
        "featured_example": {
            "name": "Deploy to GitHub Pages action",
            "url": "https://github.com/peaceiris/actions-gh-pages",
            "why": "The GitHub Pages deployment action demonstrates the power of Actions — deploy any static site with 4 lines of YAML"
        }
    },
    {
        "id": "awesome-privacy",
        "name": "Awesome Privacy",
        "github_url": "https://github.com/pluja/awesome-privacy",
        "description": "A curated list of privacy-respecting services and software alternatives — replace surveillance tools with private alternatives.",
        "maintainer": "pluja",
        "category": "Security & Privacy",
        "subcategory": "Privacy",
        "tags": ["privacy", "security", "open-source", "alternatives"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most practical privacy resource — instead of just listing privacy tools, it maps common services to privacy-respecting alternatives (e.g., Gmail → ProtonMail, Google Maps → OpenStreetMap). Each alternative includes a brief description and privacy assessment. Essential for anyone taking digital privacy seriously.",
        "related_lists": ["awesome-selfhosted", "awesome-security"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding privacy-respecting alternatives", "reducing digital surveillance", "privacy-first tool selection"],
        "has_website": True,
        "website_url": "https://awesome-privacy.xyz",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-selfhosted"],
        "best_sections": ["Cloud Storage", "Email", "Browsers"],
        "getting_started": "Browse by the category of tool you want to replace — email, cloud storage, messaging, etc. Each section lists alternatives with privacy assessments. The companion website provides an easier browsing experience with filtering.",
        "suggested_projects": [
            "Create a personal privacy migration plan replacing your current tools with alternatives from this list",
            "Build a privacy score calculator that evaluates your current tool stack against the alternatives listed here",
            "Develop a privacy-respecting tool recommendation engine based on user requirements"
        ],
        "featured_example": {
            "name": "Proton Mail",
            "url": "https://proton.me/mail",
            "why": "Proton Mail is the most accessible privacy-respecting email — end-to-end encryption with a user experience that rivals Gmail"
        }
    },
    {
        "id": "awesome-embedded-ml",
        "name": "Awesome Embedded and IoT Machine Learning",
        "github_url": "https://github.com/embedded-machine-learning/awesome-embedded-machine-learning",
        "description": "A curated list of awesome resources for embedded and edge machine learning — TinyML, on-device inference, and model optimization.",
        "maintainer": "embedded-machine-learning",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["edge-ai", "tinyml", "embedded", "optimization", "computer-vision"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Covers the growing field of running ML models on resource-constrained devices — microcontrollers, mobile phones, and edge hardware. Includes model compression techniques, hardware-specific optimizations, and deployment tools. Critical as AI moves from cloud to edge devices.",
        "related_lists": ["openvino", "mediapipe", "ultralytics"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["edge AI deployment", "model optimization", "TinyML development"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Frameworks", "Model Optimization", "Hardware"],
        "getting_started": "Start with the 'Frameworks' section to find tools supporting your target hardware (TensorFlow Lite, ONNX Runtime, OpenVINO). Then explore 'Model Optimization' for compression techniques (quantization, pruning, distillation) that make models fit on edge devices.",
        "suggested_projects": [
            "Deploy an image classification model to a Raspberry Pi using TFLite and benchmark inference speed vs accuracy tradeoffs",
            "Build an edge AI demo that runs object detection on a microcontroller using TinyML techniques from this list",
            "Create a model optimization pipeline that applies quantization, pruning, and distillation to reduce model size for edge deployment"
        ],
        "featured_example": {
            "name": "TensorFlow Lite",
            "url": "https://www.tensorflow.org/lite",
            "why": "TFLite is the most mature framework for deploying ML on mobile and embedded devices — its converter and interpreter make the cloud-to-edge transition straightforward"
        }
    },
    {
        "id": "awesome-ai-guidelines",
        "name": "Awesome AI Guidelines",
        "github_url": "https://github.com/EthicalML/awesome-artificial-intelligence-guidelines",
        "description": "A curated list of AI ethics guidelines, principles, standards, and regulations from organizations worldwide.",
        "maintainer": "EthicalML",
        "category": "AI & Machine Learning",
        "subcategory": "AI Ethics",
        "tags": ["ai-ethics", "guidelines", "regulation", "responsible-ai"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "From the same team behind awesome-production-machine-learning — this tracks AI ethics guidelines from governments, companies, and research institutions worldwide. Uniquely comprehensive in covering both voluntary guidelines and binding regulations (EU AI Act, etc.). Essential context for responsible AI development.",
        "related_lists": ["awesome-production-ml", "awesome-machine-learning"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["understanding AI regulations", "responsible AI development", "AI governance frameworks"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Principles", "Regulation", "Industry Standards"],
        "getting_started": "Start with the 'Principles' section for foundational AI ethics frameworks, then check the 'Regulation' section for binding requirements in your jurisdiction. The 'Industry Standards' section covers practical implementation guides from major tech companies.",
        "suggested_projects": [
            "Build an AI ethics compliance checker that maps your ML system against relevant guidelines from this list",
            "Create a comparison matrix of AI ethics frameworks across different countries and organizations",
            "Develop an AI risk assessment template based on the frameworks and regulations cataloged here"
        ],
        "featured_example": {
            "name": "EU AI Act",
            "url": "https://artificialintelligenceact.eu/",
            "why": "The EU AI Act is the world's first comprehensive AI regulation — understanding its risk categories and requirements is essential for any team deploying AI in or to the EU"
        }
    },
    {
        "id": "awesome-streaming-tools",
        "name": "Awesome Streaming",
        "github_url": "https://github.com/manuzhang/awesome-streaming",
        "description": "A curated list of awesome streaming frameworks, applications, and resources.",
        "maintainer": "manuzhang",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["streaming", "real-time", "data-engineering", "frameworks"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Already in the collection under Data Engineering > Stream Processing. This entry focuses on the real-time data collection aspects — streaming APIs, event streaming platforms, and real-time data pipeline tools.",
        "related_lists": ["awesome-data-engineering", "awesome-spark", "awesome-flink"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["real-time data processing", "stream processing", "event-driven architecture"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-streaming"],
        "best_sections": ["Streaming Engines", "Streaming Libraries", "Applications"],
        "getting_started": "Browse by your scale needs — 'Streaming Libraries' for embedded processing, 'Streaming Engines' for distributed systems. The section is organized by language and framework, making it easy to find tools matching your tech stack.",
        "suggested_projects": [
            "Build a real-time data pipeline using one of the streaming engines to process and analyze live data",
            "Create a streaming analytics dashboard that processes events in real-time using tools from this list",
            "Develop a comparison benchmark of streaming frameworks on throughput, latency, and fault tolerance"
        ],
        "featured_example": {
            "name": "Apache Kafka",
            "url": "https://kafka.apache.org",
            "why": "Kafka is the backbone of most real-time data architectures — its distributed log model enables everything from event streaming to change data capture"
        }
    },
]


def main():
    print(f"Loading {LISTS_JSON}...")
    with open(LISTS_JSON) as f:
        data = json.load(f)

    existing_ids = {e["id"] for e in data}
    print(f"Current entries: {len(data)}")

    # Remove 404 entries
    remove_ids = {"awesome-datasets-ml", "langchain-rag-examples"}
    data = [e for e in data if e["id"] not in remove_ids]
    removed = len(remove_ids)
    print(f"Removed {removed} entries with 404 repos")

    # Add new entries
    new_entries = []
    for entry in ADDITIONAL_ENTRIES:
        if entry["id"] in existing_ids:
            print(f"  Skipping {entry['id']} (already exists)")
            continue
        if entry["id"] == "awesome-streaming-tools":
            # Skip this one since awesome-streaming already exists
            print(f"  Skipping {entry['id']} (overlaps with existing)")
            continue
        if enrich_entry(entry):
            new_entries.append(entry)
        else:
            print(f"  WARN: Could not enrich {entry['id']}")

    data.extend(new_entries)
    print(f"\nAdded {len(new_entries)} new entries")
    print(f"Total entries: {len(data)}")

    # Write JSON
    with open(LISTS_JSON, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Updated {LISTS_JSON}")

    # Regenerate CSV
    fieldnames = list(data[0].keys())
    with open(LISTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for entry in data:
            row = {}
            for key, value in entry.items():
                if isinstance(value, list):
                    row[key] = "|".join(str(v) for v in value)
                elif isinstance(value, bool):
                    row[key] = "TRUE" if value else "FALSE"
                elif isinstance(value, dict):
                    row[key] = json.dumps(value)
                elif value is None:
                    row[key] = ""
                else:
                    row[key] = value
            writer.writerow(row)
    print(f"Regenerated {LISTS_CSV}")

    # Regenerate tags
    tag_map = {}
    for entry in data:
        for tag in entry.get("tags", []):
            if tag not in tag_map:
                tag_map[tag] = {"ids": [], "count": 0}
            tag_map[tag]["ids"].append(entry["id"])
            tag_map[tag]["count"] += 1

    tags_list = []
    TAG_DESCS = {
        "nlp": "Natural language processing tools and resources",
        "computer-vision": "Computer vision tools, models, and research",
        "security": "Security tools, resources, and best practices",
        "apis": "API directories and resources",
        "vector-database": "Vector similarity search databases",
        "rag": "Retrieval-augmented generation tools",
        "mlops": "Machine learning operations and lifecycle management",
        "web-scraping": "Web scraping tools and frameworks",
        "devops": "DevOps tools, practices, and resources",
        "monitoring": "Monitoring and observability tools",
        "datasets": "Data collections and dataset directories",
        "tools": "Developer tools and utilities",
        "curated-list": "Curated resource collections",
        "python": "Python libraries and tools",
        "javascript": "JavaScript tools and libraries",
        "llm": "Large language model resources and tools",
    }
    for tag, info in sorted(tag_map.items()):
        if info["count"] >= 2:
            tags_list.append({
                "tag": tag,
                "count": info["count"],
                "description": TAG_DESCS.get(tag, f"Resources related to {tag.replace('-', ' ')}"),
                "list_ids": sorted(info["ids"])
            })
    tags_list.sort(key=lambda x: -x["count"])

    with open(TAGS_JSON, "w") as f:
        json.dump({"tags": tags_list}, f, indent=2)
        f.write("\n")
    print(f"Regenerated {TAGS_JSON}")


if __name__ == "__main__":
    main()
