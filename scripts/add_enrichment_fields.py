#!/usr/bin/env python3
"""Add enrichment fields to all 100 entries in data/lists.json.

Adds three fields to each entry:
- getting_started (string): 1-2 sentence navigation guide
- suggested_projects (array of 2-3 strings): concrete project ideas
- featured_example (object or null): best resource with name, url, why

Usage:
    python scripts/add_enrichment_fields.py
"""

import csv
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LISTS_JSON = REPO_ROOT / "data" / "lists.json"
LISTS_CSV = REPO_ROOT / "data" / "lists.csv"

# ─── Enrichment data for all 100 entries ─────────────────────────────────────

ENRICHMENT = {
    "awesome": {
        "getting_started": "Start with the 'Platforms' and 'Programming Languages' sections to find lists matching your tech stack, then branch out to 'Front-End Development' or 'Back-End Development' based on your focus area.",
        "suggested_projects": [
            "Build a personalized awesome-list aggregator that pulls and merges lists from your tech stack into a single feed",
            "Create a CLI tool that searches across all linked awesome lists and returns matching resources by keyword",
            "Build a freshness tracker that monitors awesome lists for new additions and sends weekly digests"
        ],
        "featured_example": {
            "name": "awesome.re",
            "url": "https://awesome.re",
            "why": "The official companion website provides a badge system, linting tools, and contribution guidelines that define the standard for all awesome lists"
        }
    },
    "awesome-awesomeness": {
        "getting_started": "Navigate by programming language rather than topic — find your primary language first, then explore adjacent language ecosystems to discover cross-pollinating tools and patterns.",
        "suggested_projects": [
            "Build a language-ecosystem comparison dashboard that visualizes the breadth and depth of tooling across programming languages",
            "Create a 'polyglot explorer' that recommends equivalent libraries across different language ecosystems",
            "Develop a trend tracker comparing awesome-list growth rates across languages"
        ],
        "featured_example": None
    },
    "lists": {
        "getting_started": "Scroll past the technical sections to discover the unique non-technical lists (like 'awesome-fantasy' or 'awesome-food') — this is the only major index that covers both technical and non-technical curated collections.",
        "suggested_projects": [
            "Build a discovery engine that categorizes and tags all linked lists, enabling faceted search across the entire index",
            "Create a 'list health monitor' that checks each linked repository for activity, broken links, and staleness",
            "Develop a recommendation system that suggests lists based on a user's GitHub stars and interests"
        ],
        "featured_example": None
    },
    "awesome-awesome-awesome": {
        "getting_started": "Use this as a quick springboard when other meta-lists feel overwhelming — the smaller scope makes it easier to scan, and you'll find some unique curated collections not in the larger indexes.",
        "suggested_projects": [
            "Build a recursive list crawler that maps the full graph of list-to-list references",
            "Create a visualization showing the hierarchy of meta-lists and their overlap",
            "Develop a 'list diff' tool that finds unique entries in each meta-list not present in others"
        ],
        "featured_example": None
    },
    "the-book-of-secret-knowledge": {
        "getting_started": "Jump directly to the 'CLI Tools' and 'One-liners' sections for immediately actionable content, then explore the 'Web Tools' section for browser-based utilities you can start using today.",
        "suggested_projects": [
            "Build a terminal dashboard that integrates the best CLI tools from this list into a unified productivity workspace",
            "Create a 'sysadmin toolkit' installer script that sets up curated tools from this list for a new server",
            "Develop an interactive cheat-sheet app that indexes the one-liners and manuals referenced here"
        ],
        "featured_example": {
            "name": "CLI Tools section",
            "url": "https://github.com/trimstray/the-book-of-secret-knowledge#cli-tools-toc",
            "why": "The CLI tools section alone contains hundreds of curated command-line utilities organized by function, making it the single most actionable section for daily developer productivity"
        }
    },
    "awesome-machine-learning": {
        "getting_started": "Filter by your preferred programming language first (Python, R, Java, etc.) since the list is organized by language, then drill into framework-specific sections like TensorFlow or PyTorch.",
        "suggested_projects": [
            "Build a model comparison dashboard that benchmarks different ML frameworks listed here on a standard dataset",
            "Create an ML project scaffolder that generates boilerplate code using the best library for each task from this list",
            "Develop a recommendation engine that suggests the right ML library based on your dataset type and task"
        ],
        "featured_example": {
            "name": "scikit-learn",
            "url": "https://scikit-learn.org",
            "why": "Featured prominently across multiple sections, scikit-learn remains the most accessible and well-documented ML library for getting started with classical machine learning"
        }
    },
    "awesome-llm": {
        "getting_started": "Start with the 'Milestone Papers' section to understand the foundational research, then check 'LLM Training' for practical implementation guides and 'LLM Evaluation' for benchmarking your own models.",
        "suggested_projects": [
            "Build an LLM paper tracker that visualizes the timeline of milestone papers and their citation relationships",
            "Create a fine-tuning pipeline using the training resources listed here, targeting a domain-specific use case",
            "Develop a benchmark comparison tool that evaluates open-source LLMs using evaluation frameworks from this list"
        ],
        "featured_example": {
            "name": "LLM Evaluation section",
            "url": "https://github.com/Hannibal046/Awesome-LLM#llm-evaluation",
            "why": "The evaluation section provides the most comprehensive overview of LLM benchmarks and evaluation methods, which is essential for any serious LLM development work"
        }
    },
    "awesome-chatgpt-prompts": {
        "getting_started": "Browse the 'Act as...' prompts to find a role that matches your use case, then use the prompt structure as a template to craft your own variations — the power is in the role-assignment pattern, not the specific prompts.",
        "suggested_projects": [
            "Build a prompt template engine that lets users mix and match role-based prompts with custom instructions",
            "Create a prompt A/B testing tool that compares outputs from different prompt strategies on the same input",
            "Develop a prompt library app with tagging, search, and community voting features"
        ],
        "featured_example": {
            "name": "Act as a Linux Terminal",
            "url": "https://github.com/f/awesome-chatgpt-prompts#act-as-a-linux-terminal",
            "why": "The Linux Terminal prompt is the iconic example that demonstrated the power of role-based prompting and spawned an entire genre of 'act as' prompts"
        }
    },
    "prompt-engineering-guide": {
        "getting_started": "Begin with the 'Techniques' section and work through chain-of-thought and few-shot prompting before tackling advanced methods — the guide is structured as a progressive curriculum, not a reference manual.",
        "suggested_projects": [
            "Build a prompt engineering workbench that lets you experiment with each technique from the guide side-by-side",
            "Create an automated prompt optimizer that applies techniques from this guide to improve weak prompts",
            "Develop a teaching tool that walks users through each prompting technique with interactive examples"
        ],
        "featured_example": {
            "name": "Chain-of-Thought Prompting",
            "url": "https://www.promptingguide.ai/techniques/cot",
            "why": "The chain-of-thought section is the most practically impactful technique covered, with clear examples showing how to dramatically improve reasoning in LLM outputs"
        }
    },
    "awesome-prompt-engineering": {
        "getting_started": "Head to the 'Automatic Prompt Optimization' section first if you're building production systems, or start with 'Prompt Injection Defense' if you're focused on security — this list skews research-heavy.",
        "suggested_projects": [
            "Build a prompt injection fuzzer that tests your LLM application against attack patterns catalogued here",
            "Create an automatic prompt optimization pipeline using the research papers and tools listed",
            "Develop a prompt evaluation framework that scores prompts against the metrics described in the evaluation section"
        ],
        "featured_example": None
    },
    "awesome-chatgpt-sindresorhus": {
        "getting_started": "Start with the 'Official' section for direct OpenAI resources, then explore 'Browser Extensions' for tools that enhance your daily ChatGPT usage — skip to 'Developer Tools' when you're ready to build.",
        "suggested_projects": [
            "Build a browser extension that adds custom features to the ChatGPT interface using tools listed here as inspiration",
            "Create a ChatGPT integration hub that connects ChatGPT to your developer workflow tools",
            "Develop a CLI wrapper around the ChatGPT API that incorporates the best developer tools from this list"
        ],
        "featured_example": None
    },
    "ai-collection": {
        "getting_started": "Use the category headings (Art, Code, Copywriting, Video, etc.) as your primary navigation — this is a product directory, so browse by the task you need an AI tool for rather than by technology.",
        "suggested_projects": [
            "Build an AI tool comparison site that aggregates pricing, features, and user reviews for tools listed here",
            "Create a workflow automator that chains multiple AI tools from different categories into a single pipeline",
            "Develop a 'best AI tool for X' recommendation engine based on categorized entries from this list"
        ],
        "featured_example": None
    },
    "awesome-generative-ai": {
        "getting_started": "Navigate by modality — text, image, audio, or video generation — to find tools for your specific creative or technical need, then check the research section for papers behind the tools.",
        "suggested_projects": [
            "Build a multi-modal content generator that chains text, image, and audio tools from this list into a creative pipeline",
            "Create a generative AI landscape visualization showing tool relationships and capabilities across modalities",
            "Develop a side-by-side comparison tool for image generation services listed here"
        ],
        "featured_example": None
    },
    "awesome-deep-learning": {
        "getting_started": "Start with the 'Courses' section to build foundations, then use the 'Frameworks' section to choose your tools — the 'Papers' section is best approached after you have hands-on experience.",
        "suggested_projects": [
            "Build a deep learning study planner that creates a personalized curriculum from courses and papers in this list",
            "Create a framework comparison benchmark that evaluates DL frameworks listed here on standard tasks",
            "Develop an interactive paper reading group app that organizes papers from this list into a reading sequence"
        ],
        "featured_example": None
    },
    "machine-learning-tutorials": {
        "getting_started": "Navigate by topic (NLP, Computer Vision, Basics) rather than scrolling linearly — pick one topic that matches your learning goal, work through those tutorials, then expand to adjacent topics.",
        "suggested_projects": [
            "Build a tutorial progress tracker that lets you mark completion and rate tutorials from this list",
            "Create an ML learning path generator that sequences tutorials from this list based on your skill level",
            "Develop a hands-on ML notebook collection that implements key concepts from the linked tutorials"
        ],
        "featured_example": None
    },
    "deep-learning-papers-reading-roadmap": {
        "getting_started": "Follow the numbered progression strictly — start with section 1 (DL History) to understand foundational papers before jumping to section 2 (Methods), as each paper builds on concepts from earlier ones.",
        "suggested_projects": [
            "Build an interactive paper graph that visualizes citation relationships between papers in this roadmap",
            "Create a spaced-repetition flashcard system for key concepts from each paper in the reading order",
            "Develop a paper summary aggregator that collects community summaries and notes for each paper listed"
        ],
        "featured_example": {
            "name": "Deep Learning History section",
            "url": "https://github.com/floodsung/Deep-Learning-Papers-Reading-Roadmap#1-deep-learning-history-and-basics",
            "why": "The structured progression from AlexNet through ResNet to modern architectures provides the most effective self-study path for understanding how deep learning evolved"
        }
    },
    "free-programming-books": {
        "getting_started": "Use the language-specific sub-pages (not the main README) — navigate to your programming language's dedicated file for a much more organized and complete listing than the overview page.",
        "suggested_projects": [
            "Build a free learning resource aggregator with search, filtering by language and format (book, course, podcast)",
            "Create a reading list app that lets users curate personal selections from this massive collection",
            "Develop a 'what to learn next' recommender based on a user's current skills and this list's offerings"
        ],
        "featured_example": {
            "name": "Free Programming Books (English)",
            "url": "https://github.com/EbookFoundation/free-programming-books/blob/main/books/free-programming-books-langs.md",
            "why": "The English-language programming books file alone contains thousands of curated free resources organized by language, making it the single most comprehensive free learning resource on GitHub"
        }
    },
    "ai-for-beginners": {
        "getting_started": "Follow the 12-week lesson plan sequentially — each lesson builds on the previous one, with hands-on labs in each module. Start with Lesson 1 and resist the urge to skip ahead.",
        "suggested_projects": [
            "Build an AI concepts quiz app using the curriculum structure as a content framework",
            "Create a visual AI learning dashboard that tracks progress through all 24 lessons with lab completion status",
            "Develop a study group platform tailored to this curriculum's weekly structure with discussion forums per lesson"
        ],
        "featured_example": {
            "name": "Neural Networks lesson",
            "url": "https://github.com/microsoft/AI-For-Beginners/tree/main/lessons/4-ComputerVision",
            "why": "The Computer Vision module is the most hands-on section with practical TensorFlow and PyTorch labs that transform theoretical concepts into working code"
        }
    },
    "generative-ai-for-beginners": {
        "getting_started": "Work through lessons 1-5 (fundamentals and prompt engineering) before jumping to application-building lessons — the RAG and fine-tuning lessons assume you've mastered the prompting foundations.",
        "suggested_projects": [
            "Build a generative AI application following the RAG pattern taught in this course, using your own document corpus",
            "Create a prompt engineering practice platform with exercises based on each lesson's techniques",
            "Develop a multi-model chatbot that demonstrates concepts from each lesson in an interactive format"
        ],
        "featured_example": {
            "name": "Building Search Applications lesson",
            "url": "https://github.com/microsoft/generative-ai-for-beginners/tree/main/08-building-search-applications",
            "why": "The search applications lesson provides the most immediately practical skill — building RAG-powered search — with complete working code that can be adapted to real projects"
        }
    },
    "ai-agents-for-beginners": {
        "getting_started": "Begin with the agent design patterns lesson to understand the conceptual framework, then progress through tool use and multi-agent orchestration — each lesson includes runnable code samples.",
        "suggested_projects": [
            "Build a multi-agent system where agents with different roles collaborate to solve a complex task using patterns from this course",
            "Create a tool-use playground where you can define custom tools and watch an agent learn to use them",
            "Develop an agent evaluation harness that benchmarks different agent architectures covered in the lessons"
        ],
        "featured_example": {
            "name": "Multi-Agent Orchestration lesson",
            "url": "https://github.com/microsoft/ai-agents-for-beginners",
            "why": "The multi-agent orchestration lesson covers the most in-demand skill in the current AI landscape, with practical examples of agents coordinating to solve complex tasks"
        }
    },
    "llms-from-scratch": {
        "getting_started": "Follow the chapters sequentially from tokenization through pretraining — this is a linear tutorial, not a reference. Have a GPU-capable machine ready (even a free Colab GPU works) for the training chapters.",
        "suggested_projects": [
            "Build a miniature GPT model from scratch following the book's architecture, then fine-tune it on a custom dataset",
            "Create a visualization tool that shows attention patterns and token embeddings at each layer of the model you build",
            "Develop a comparative study implementing the model in both PyTorch (as in the book) and JAX to deepen understanding"
        ],
        "featured_example": {
            "name": "Chapter on Attention Mechanisms",
            "url": "https://github.com/rasbt/LLMs-from-scratch/tree/main/ch03",
            "why": "The attention mechanism chapter is the conceptual core — understanding self-attention from scratch is the single most important insight for grasping how modern LLMs work"
        }
    },
    "prompt-engineering-notebooks": {
        "getting_started": "Open the notebooks in order, starting with basic prompting techniques — each notebook is self-contained and runnable, so execute the cells as you read to see techniques in action.",
        "suggested_projects": [
            "Build a prompt technique benchmark that runs each notebook's approach against a standard evaluation set",
            "Create an interactive prompt engineering tutorial that adapts the notebook content into a web-based learning platform",
            "Develop a prompt optimization pipeline that automatically tests and compares techniques from different notebooks"
        ],
        "featured_example": {
            "name": "Chain-of-Thought Notebook",
            "url": "https://github.com/NirDiamant/Prompt_Engineering",
            "why": "The chain-of-thought notebook provides the clearest hands-on demonstration of how structured reasoning prompts dramatically improve LLM output quality"
        }
    },
    "awesome-chatgpt-humanloop": {
        "getting_started": "Focus on the 'Developer Tools' and 'APIs' sections for building with ChatGPT — this list is curated by practitioners at Humanloop, so the developer-focused entries are particularly well-vetted.",
        "suggested_projects": [
            "Build a ChatGPT API wrapper library that incorporates the best patterns from developer tools listed here",
            "Create an integration comparison tool that evaluates ChatGPT tools listed here against common use cases",
            "Develop a ChatGPT-powered internal tool using the API integrations catalogued in this list"
        ],
        "featured_example": None
    },
    "learn-prompting": {
        "getting_started": "Start with the 'Basics' section on learnprompting.org (the course website) rather than the raw GitHub files — the website version has interactive examples and is the intended learning experience.",
        "suggested_projects": [
            "Build a prompt engineering certification platform with quizzes based on each course module",
            "Create a prompt hacking CTF (capture the flag) challenge set using the prompt hacking defense section as inspiration",
            "Develop a multi-language prompt testing tool, leveraging the community translations of this course"
        ],
        "featured_example": {
            "name": "Prompt Hacking section",
            "url": "https://learnprompting.org/docs/category/-prompt-hacking",
            "why": "The prompt hacking section uniquely covers both offensive and defensive prompt techniques, making it essential reading for anyone deploying LLMs in production"
        }
    },
    "awesome-gpt": {
        "getting_started": "Use the category sections (API Wrappers, Browser Extensions, Mobile Apps) to find tools by how you want to interact with GPT — this is a compact list, so a quick full scan takes only minutes.",
        "suggested_projects": [
            "Build a GPT ecosystem dashboard that tracks and compares the tools listed here by popularity and features",
            "Create a unified GPT tool interface that integrates multiple API wrappers and extensions from this list",
            "Develop a GPT browser extension that combines the best features from extensions catalogued here"
        ],
        "featured_example": None
    },
    "awesome-llm-powered-agent": {
        "getting_started": "Start with the 'Planning' papers to understand the theoretical foundation, then read 'Tool Use' papers for practical implementation patterns — this is a research-oriented list best consumed as a reading program.",
        "suggested_projects": [
            "Build a research paper discussion tool that helps reading groups work through the agent papers listed here",
            "Create an agent architecture comparison framework implementing planning strategies from different papers",
            "Develop a survey paper generator that synthesizes findings across papers in the planning and tool-use sections"
        ],
        "featured_example": None
    },
    "awesome-llm-agents": {
        "getting_started": "Read the trend analysis first to understand the evolution of agent architectures, then dive into specific papers organized by capability — the timeline view helps contextualize when key innovations appeared.",
        "suggested_projects": [
            "Build an agent research timeline visualization showing the progression of key papers and frameworks",
            "Create a paper recommendation engine that suggests related agent research based on your reading history",
            "Develop an agent capability matrix comparing frameworks across dimensions like planning, memory, and tool use"
        ],
        "featured_example": None
    },
    "awesome-ai-agents": {
        "getting_started": "Use the category filters (Coding, Research, General-purpose, Multi-agent) to narrow down agents by your use case — E2B maintains this with a practitioner's lens, so the categorization is reliable.",
        "suggested_projects": [
            "Build an AI agent benchmark platform that evaluates agents listed here on standardized coding and research tasks",
            "Create an agent selection wizard that recommends the best agent from this list based on your requirements",
            "Develop a multi-agent orchestration layer that coordinates agents from different categories in this list"
        ],
        "featured_example": {
            "name": "Coding Agents section",
            "url": "https://github.com/e2b-dev/awesome-ai-agents",
            "why": "The coding agents section is the most comprehensive directory of AI coding assistants available, with consistent categorization that makes comparison practical"
        }
    },
    "awesome-code-ai": {
        "getting_started": "Navigate by function (Code Completion, Code Search, Developer Assistants) rather than scrolling — the Sourcegraph team organized this by developer workflow stage, which maps to how you'd actually adopt these tools.",
        "suggested_projects": [
            "Build an AI coding tool comparison matrix with feature grids based on the categories in this list",
            "Create a developer productivity study that measures the impact of different AI coding tools listed here",
            "Develop an AI code review assistant that combines approaches from multiple tools catalogued in this list"
        ],
        "featured_example": None
    },
    "awesome-langchain": {
        "getting_started": "Start with the 'Tools' section to see what integrations exist, then check 'Templates' for production-ready starting points — the tutorials section is best for filling specific knowledge gaps.",
        "suggested_projects": [
            "Build a LangChain template gallery with live previews and one-click deployment",
            "Create a LangChain integration testing framework that validates tool compatibility across versions",
            "Develop a RAG application using LangChain tools from this list, combining retrieval, memory, and agent components"
        ],
        "featured_example": None
    },
    "awesome-llm-apps": {
        "getting_started": "Browse by architecture pattern (RAG, Agents, Multi-Modal) rather than scrolling linearly — each entry is a working project with code, so clone the ones that match your use case and study the implementation.",
        "suggested_projects": [
            "Fork and extend a RAG application from this list to work with your own document corpus",
            "Build a meta-app that runs and compares multiple LLM applications from this list side-by-side",
            "Create a template generator that produces LLM app scaffolding based on patterns from the most popular entries"
        ],
        "featured_example": None
    },
    "awesome-generative-ai-filipecalegario": {
        "getting_started": "Explore the creative AI sections (Music Generation, Video Synthesis, 3D Modeling) that differentiate this from other gen-AI lists — it's the best resource for non-text generative AI tools.",
        "suggested_projects": [
            "Build a multi-modal creative pipeline that chains text-to-image, image-to-video, and audio generation tools from this list",
            "Create a generative AI gallery app that showcases outputs from different creative AI tools listed here",
            "Develop a creative AI toolkit comparison site focused on the unique music, video, and 3D tools in this list"
        ],
        "featured_example": None
    },
    "awesome-ai-sdks": {
        "getting_started": "Filter by what layer of the agent stack you need — orchestration frameworks for high-level control, tool-use SDKs for specific capabilities, or building blocks for custom architectures.",
        "suggested_projects": [
            "Build a multi-SDK agent that uses different SDKs from this list for different capabilities (one for orchestration, another for tool use)",
            "Create an SDK comparison benchmark that evaluates agent frameworks listed here on latency, reliability, and ease of use",
            "Develop a 'pick your agent stack' interactive guide based on the SDK categories in this list"
        ],
        "featured_example": None
    },
    "awesome-gpt-agents": {
        "getting_started": "Navigate by security domain (Defensive, Offensive, Incident Response) to find agents matching your cybersecurity workflow — this is a specialized security list, not a general GPT directory.",
        "suggested_projects": [
            "Build a security analysis pipeline that chains defensive and offensive GPT agents from this list",
            "Create a cybersecurity training platform using GPT agents listed here for interactive threat scenarios",
            "Develop a vulnerability assessment workflow that orchestrates multiple security GPT agents from this list"
        ],
        "featured_example": {
            "name": "Defensive Security agents",
            "url": "https://github.com/fr0gger/Awesome-GPT-Agents",
            "why": "The defensive security section provides immediately deployable GPT agents for threat analysis and incident response, curated by a recognized security researcher"
        }
    },
    "autonomous-agents": {
        "getting_started": "Use the timeline-based organization to follow the chronological evolution of agent research, then check the benchmarks section to understand how different approaches are evaluated.",
        "suggested_projects": [
            "Build an interactive agent research timeline with filterable views by capability (planning, memory, tool use)",
            "Create an agent benchmark aggregator that tracks performance across evaluation frameworks listed here",
            "Develop a research paper recommendation system trained on the citation patterns in this list"
        ],
        "featured_example": None
    },
    "best-gpts": {
        "getting_started": "Browse by category (Productivity, Creative, Developer Tools) and look for the ratings and descriptions — AgentOps curates for quality, so the top-rated entries in each category are reliable starting points.",
        "suggested_projects": [
            "Build a GPT store analytics dashboard that tracks popularity and ratings of custom GPTs listed here",
            "Create a GPT comparison tool that lets users test multiple custom GPTs from this list on the same prompt",
            "Develop a custom GPT recommendation engine based on user task descriptions and the categories in this list"
        ],
        "featured_example": None
    },
    "awesome-ai-tools": {
        "getting_started": "Navigate by modality (Text, Image, Video, Audio, Code) to find AI tools for your specific content type — the list is organized to help you find the right tool for a specific task quickly.",
        "suggested_projects": [
            "Build an AI tools comparison site with user reviews and pricing information for tools listed here",
            "Create a content creation pipeline that chains AI tools from different modality categories in this list",
            "Develop an AI tool discovery app that recommends tools from this list based on your creative workflow"
        ],
        "featured_example": None
    },
    "awesome-public-datasets": {
        "getting_started": "Navigate by domain (Agriculture, Biology, Economics, etc.) to find datasets for your research area — the domain-based organization is the fastest path to relevant data sources.",
        "suggested_projects": [
            "Build a dataset search engine with faceted filtering by domain, format, size, and update frequency",
            "Create a data quality dashboard that monitors the health and availability of datasets linked here",
            "Develop a dataset recommendation system that suggests relevant public datasets based on your research question"
        ],
        "featured_example": {
            "name": "Economics & Finance section",
            "url": "https://github.com/awesomedata/awesome-public-datasets#economics",
            "why": "The economics section is the most comprehensive and well-maintained domain category, with high-quality links to major economic data providers like FRED, World Bank, and IMF"
        }
    },
    "awesome-data": {
        "getting_started": "Look for the 'Core Datasets' section first — these are standardized, machine-readable datasets in the Frictionless Data format, which means they're immediately usable without cleaning or reformatting.",
        "suggested_projects": [
            "Build a Frictionless Data package explorer that previews and validates datasets from this collection",
            "Create an automated data pipeline that ingests standardized datasets from this list into your data warehouse",
            "Develop a dataset documentation generator using the metadata standards promoted in this collection"
        ],
        "featured_example": {
            "name": "Core Datasets",
            "url": "https://github.com/datasets/awesome-data#core-datasets",
            "why": "Core Datasets provides immediately usable, standardized data packages (GDP, population, S&P 500) that work out-of-the-box with Frictionless Data tools — no cleaning needed"
        }
    },
    "awesome-datascience": {
        "getting_started": "Start with the 'Toolboxes' section to set up your environment, then use the 'Tutorials' and 'Competitions' sections based on whether you prefer structured learning or learning by doing.",
        "suggested_projects": [
            "Build a data science project scaffolder that sets up environments using the best tools from this list",
            "Create a competition preparation toolkit that combines resources from the tutorials and competitions sections",
            "Develop a data science career roadmap app using the courses, certifications, and resources catalogued here"
        ],
        "featured_example": None
    },
    "datascience-python": {
        "getting_started": "Navigate by pipeline stage (Data Loading, Cleaning, Visualization, Modeling) to find the right Python library for each step of your data workflow — this list maps directly to the data science pipeline.",
        "suggested_projects": [
            "Build a Python data pipeline template that chains the best library from each stage category in this list",
            "Create a library comparison notebook that benchmarks alternative tools for each pipeline stage",
            "Develop a 'Python DS toolkit installer' that sets up a complete data science environment from this list's recommendations"
        ],
        "featured_example": None
    },
    "awesome-python-data-science": {
        "getting_started": "Use the category headings (Machine Learning, Deep Learning, NLP, Computer Vision, Time Series) as your primary filter — the brief descriptions next to each library help you quickly distinguish between similar options.",
        "suggested_projects": [
            "Build a Python data science library recommender that suggests the right library for your task based on categories here",
            "Create a library dependency analyzer that maps relationships between libraries in this list",
            "Develop a benchmark suite that compares libraries within each category on standard datasets"
        ],
        "featured_example": None
    },
    "awesome-bigdata": {
        "getting_started": "Navigate by data stack layer (Distributed Programming, SQL-like, Stream Processing, Columnar) to find tools at the right level of your architecture — this list is organized by infrastructure layer, not by use case.",
        "suggested_projects": [
            "Build a big data architecture diagram generator that recommends tools from this list for each layer of your stack",
            "Create a distributed system comparison matrix with performance benchmarks for tools listed here",
            "Develop a 'build your data stack' interactive wizard using the layered organization of this list"
        ],
        "featured_example": None
    },
    "awesome-public-datasets-caesar": {
        "getting_started": "Use the domain sections (Climate, Sports, Social Networks) to find datasets — check the overlap with awesomedata/awesome-public-datasets and focus on the unique sources this version offers in areas like sports and social network data.",
        "suggested_projects": [
            "Build a cross-domain dataset mashup tool that combines datasets from different sections for novel analyses",
            "Create a social network analysis project using the unique social graph datasets listed here",
            "Develop a sports analytics dashboard using the game and player datasets catalogued in this list"
        ],
        "featured_example": None
    },
    "game-datasets": {
        "getting_started": "Start with 'Player Behavior' datasets if you're interested in ML applications, or 'Game Design' datasets for generative AI projects — the 'Procedural Generation' section links to tools, not just data.",
        "suggested_projects": [
            "Build a game recommendation engine trained on player behavior datasets from this list",
            "Create a procedural level generator using game design datasets and AI techniques",
            "Develop a player behavior prediction model using the behavioral datasets catalogued here"
        ],
        "featured_example": None
    },
    "awesome-dataviz": {
        "getting_started": "Filter by your programming language (JavaScript, Python, R) first since visualization libraries are language-specific, then narrow by chart type — the list is organized to help language-first, chart-second decisions.",
        "suggested_projects": [
            "Build a visualization library comparison tool that renders the same dataset using different libraries from this list",
            "Create a 'pick your chart' interactive guide that recommends the best library from this list for each chart type",
            "Develop a cross-platform visualization framework that wraps multiple libraries listed here under a unified API"
        ],
        "featured_example": None
    },
    "awesome-d3": {
        "getting_started": "Start with the 'Charts' and 'Maps' sections for ready-to-use components, then explore 'Utilities' for lower-level building blocks — D3's ecosystem is layered, so start high-level and dig deeper as needed.",
        "suggested_projects": [
            "Build a D3 component gallery with live, editable previews of plugins and libraries from this list",
            "Create a D3 visualization starter kit that bundles the most useful utilities and chart libraries listed here",
            "Develop an interactive D3 learning platform using the learning resources and example charts from this list"
        ],
        "featured_example": None
    },
    "awesome-visualization-research": {
        "getting_started": "Read the 'Information Visualization' section for foundational theory, then browse 'Visual Analytics' for papers that bridge theory and practice — this is a reading list, so approach it as an academic syllabus.",
        "suggested_projects": [
            "Build an interactive paper navigator that lets you explore visualization research by topic and citation relationships",
            "Create a visualization design checklist tool based on principles extracted from papers in this list",
            "Develop a research paper implementation gallery that pairs papers with working code implementations"
        ],
        "featured_example": None
    },
    "awesome-graph-generation": {
        "getting_started": "Navigate by graph domain (Molecular, Social, Scene Graphs) based on your application area — this is a deep research list, so having a specific graph generation problem in mind before browsing will be most productive.",
        "suggested_projects": [
            "Build a molecular graph generator using the VAE-based approaches referenced in the molecular section",
            "Create a social network simulation tool implementing graph generation models from this list",
            "Develop a benchmark framework for evaluating graph generation methods described in these papers"
        ],
        "featured_example": None
    },
    "awesome-data-science-viz": {
        "getting_started": "Check both the Python tools (matplotlib, seaborn, plotly) and JavaScript tools (D3, Vega) sections to find the right tool for your context — the 'Notebooks' section is great for exploring tools hands-on.",
        "suggested_projects": [
            "Build a multi-library visualization dashboard that renders the same data across Python and JS tools from this list",
            "Create an EDA (exploratory data analysis) toolkit that bundles the best Python visualization tools listed here",
            "Develop a visualization recommendation engine that suggests the right tool from this list based on your data type"
        ],
        "featured_example": None
    },
    "awesome-dataviz-javierluraschi": {
        "getting_started": "Start with the 'R Libraries' section if you're in the R ecosystem (ggplot2, plotly for R, Shiny), then explore web frameworks for interactive dashboards — this list bridges R and web visualization.",
        "suggested_projects": [
            "Build an R-to-web visualization converter that renders R plots as interactive web visualizations using tools from this list",
            "Create a Shiny dashboard template gallery using the dashboarding tools and libraries catalogued here",
            "Develop a cross-platform charting library evaluation that compares R and web tools listed here side-by-side"
        ],
        "featured_example": None
    },
    "awesome-data-visualization-alpers": {
        "getting_started": "Explore the 'Communities' and 'Books' sections first to build foundational knowledge — this list uniquely focuses on the craft of visualization rather than specific tools.",
        "suggested_projects": [
            "Build a data visualization learning platform that curates courses, books, and communities from this list into a structured curriculum",
            "Create a visualization critique tool that applies design principles from the books referenced here",
            "Develop a community event aggregator for visualization conferences and meetups listed in this collection"
        ],
        "featured_example": None
    },
    "awesome-visualization-tasks": {
        "getting_started": "Start with the 'Task Taxonomies' section to learn the formal vocabulary (encode, arrange, filter, derive), then use the 'Design Guidelines' to apply these concepts — this is academic reference material best used alongside practical work.",
        "suggested_projects": [
            "Build a visualization task annotator that classifies chart interactions using taxonomies from this list",
            "Create a design guideline checker that evaluates visualizations against the frameworks catalogued here",
            "Develop a visualization design assistant that suggests appropriate task types based on the user's analytical question"
        ],
        "featured_example": None
    },
    "awesome-data-engineering": {
        "getting_started": "Navigate by pipeline stage (Databases, Stream Processing, Workflow Orchestration) to find tools at the right point in your data flow — the list mirrors the modern data engineering stack from ingestion to serving.",
        "suggested_projects": [
            "Build a data pipeline architecture generator that recommends tools from this list for each stage of your pipeline",
            "Create a data engineering tool comparison matrix with feature grids for tools in each category",
            "Develop an end-to-end data pipeline using one tool from each category in this list as a learning exercise"
        ],
        "featured_example": None
    },
    "data-engineer-roadmap": {
        "getting_started": "Follow the visual roadmap from top to bottom — it's designed as a skill progression, so start with programming languages and databases before moving to distributed systems and cloud platforms.",
        "suggested_projects": [
            "Build a data engineering skills tracker that maps your proficiency against the roadmap's skill tree",
            "Create a personalized learning plan generator that recommends courses and resources for each roadmap node",
            "Develop a skills assessment quiz that identifies gaps in your data engineering knowledge based on this roadmap"
        ],
        "featured_example": {
            "name": "Data Engineer Roadmap visual",
            "url": "https://github.com/datastacktv/data-engineer-roadmap",
            "why": "The visual roadmap itself is the standout resource — the single diagram provides the clearest visual overview of the entire data engineering skill tree available anywhere"
        }
    },
    "awesome-opensource-data-engineering": {
        "getting_started": "Navigate by pipeline stage (Ingestion, Storage, Query, Transformation, Orchestration) — each section maps to a real stage in your data pipeline, making it easy to pick one tool per stage to build a complete stack.",
        "suggested_projects": [
            "Build a fully open-source data stack by selecting one tool from each pipeline stage in this list",
            "Create an OSS data tool comparison dashboard with adoption metrics and feature matrices",
            "Develop a data engineering tool selection wizard that recommends the best open-source option for each pipeline stage"
        ],
        "featured_example": None
    },
    "awesome-workflow-engines": {
        "getting_started": "Use the language, license, and description columns in the comparison table to narrow your options quickly — the list is structured as a comparison matrix, so scan the table rather than reading entries individually.",
        "suggested_projects": [
            "Build a workflow engine selection tool that filters options based on language, license, and feature requirements",
            "Create a workflow migration guide that maps concepts between orchestrators listed here (Airflow → Dagster, Prefect → Temporal)",
            "Develop a benchmark suite that compares workflow engine performance on common data pipeline patterns"
        ],
        "featured_example": {
            "name": "Workflow engine comparison table",
            "url": "https://github.com/meirwah/awesome-workflow-engines",
            "why": "The structured comparison table with language, license, and descriptions for dozens of orchestrators is the most efficient way to evaluate and choose a workflow engine"
        }
    },
    "awesome-etl": {
        "getting_started": "Filter by your technology context — Python libraries for script-based ETL, enterprise platforms for large-scale integration, or streaming ETL for real-time needs. The categories map to ETL architecture decisions.",
        "suggested_projects": [
            "Build an ETL pipeline comparison benchmark that evaluates tools from this list on throughput and ease of use",
            "Create an ETL code generator that produces pipeline scaffolding for different tools listed here",
            "Develop a data integration monitoring dashboard using the logging and monitoring tools catalogued here"
        ],
        "featured_example": None
    },
    "awesome-dbt": {
        "getting_started": "Start with the 'Packages' section to find reusable dbt packages for common transformations, then explore 'Tools' for development workflow enhancements — the 'Tutorials' section is best for filling specific knowledge gaps.",
        "suggested_projects": [
            "Build a dbt package discovery tool with search, compatibility checking, and usage examples",
            "Create a dbt project template with pre-configured packages, testing, and CI/CD from tools in this list",
            "Develop a dbt documentation site generator that combines the best practices from tutorials listed here"
        ],
        "featured_example": {
            "name": "dbt Packages section",
            "url": "https://github.com/Hiflylabs/awesome-dbt#packages",
            "why": "The packages section provides the most immediately actionable content — reusable dbt packages that can save weeks of work on common transformation patterns like date spines, surrogate keys, and data testing"
        }
    },
    "awesome-streaming": {
        "getting_started": "Start with the 'Frameworks' section to compare stream processing engines (Kafka Streams, Flink, Spark Streaming), then check 'Readings' for architecture guidance on choosing between them.",
        "suggested_projects": [
            "Build a stream processing benchmark that compares frameworks from this list on latency, throughput, and fault tolerance",
            "Create a real-time data pipeline using Kafka and one of the processing frameworks listed here",
            "Develop a streaming architecture decision tool that recommends the right framework based on your requirements"
        ],
        "featured_example": None
    },
    "awesome-spark": {
        "getting_started": "Navigate by Spark component (SQL, Streaming, MLlib, GraphX) based on your workload type — the list is organized around Spark's module architecture, so find your module first.",
        "suggested_projects": [
            "Build a Spark performance tuning toolkit using optimization packages and tools from this list",
            "Create a PySpark project template with the best packages from each Spark component category",
            "Develop a Spark job monitoring dashboard using the observability tools catalogued here"
        ],
        "featured_example": None
    },
    "awesome-flink": {
        "getting_started": "Start with the 'Tutorials' section if you're new to Flink, then explore 'Connectors' to understand what data sources and sinks are available — the list complements the official Flink docs well.",
        "suggested_projects": [
            "Build a Flink connector testing framework that validates data source integrations from this list",
            "Create a Flink deployment automation toolkit using the deployment tools and guides listed here",
            "Develop a stream processing tutorial series that extends the learning resources in this list with hands-on projects"
        ],
        "featured_example": None
    },
    "awesome-db-tools": {
        "getting_started": "Navigate by function (IDEs, Monitoring, Migration, Testing) rather than by database type — the list is organized around what you need to do with your database, making it easy to find the right tool for each task.",
        "suggested_projects": [
            "Build a database toolkit installer that sets up a curated selection of tools from this list for a new project",
            "Create a database migration workflow using the schema management and migration tools catalogued here",
            "Develop a database monitoring dashboard that integrates multiple monitoring tools from this list"
        ],
        "featured_example": {
            "name": "IDEs section",
            "url": "https://github.com/mgramin/awesome-db-tools#ide",
            "why": "The IDEs section is the most comprehensive comparison of database management interfaces available — from DBeaver to DataGrip to web-based alternatives — organized to help you choose the right tool for your workflow"
        }
    },
    "awesome-python": {
        "getting_started": "Use the table of contents to jump directly to your functional area (Web Frameworks, Data Analysis, Testing, etc.) — with hundreds of entries, targeted navigation via the TOC is essential over scrolling.",
        "suggested_projects": [
            "Build a Python package discovery CLI that searches this list and returns recommendations with install commands",
            "Create a Python project dependency auditor that checks if better alternatives exist in this list",
            "Develop a 'Python toolkit builder' that generates a requirements.txt from curated selections across categories"
        ],
        "featured_example": {
            "name": "awesome-python.com",
            "url": "https://awesome-python.com",
            "why": "The companion website provides searchable, filterable access to the entire list with categories, descriptions, and links — far easier to navigate than the raw GitHub README for such a massive collection"
        }
    },
    "awesome-javascript": {
        "getting_started": "Navigate by functional category (Frameworks, Testing, Bundlers, Templating) for browser-side JS — remember this list focuses on client-side JavaScript, so check awesome-nodejs for server-side needs.",
        "suggested_projects": [
            "Build a JavaScript library size and performance comparison tool for libraries listed in each category",
            "Create a frontend project starter kit that bundles the best library from each category in this list",
            "Develop a browser compatibility checker for JavaScript libraries catalogued here"
        ],
        "featured_example": None
    },
    "awesome-go": {
        "getting_started": "Use awesome-go.com (the searchable website) instead of scrolling the README — with strict quality standards and test coverage requirements for listed packages, every entry meets a high bar.",
        "suggested_projects": [
            "Build a Go package quality dashboard that tracks test coverage, documentation, and maintenance status for entries in this list",
            "Create a Go project bootstrapper that generates projects with best-in-class packages from each category",
            "Develop a Go dependency recommendation engine based on categories and descriptions from this list"
        ],
        "featured_example": {
            "name": "awesome-go.com",
            "url": "https://awesome-go.com",
            "why": "The searchable companion website with category filtering is the best way to navigate this massive list, and the strict inclusion criteria (test coverage, godoc) ensure every listed package meets professional standards"
        }
    },
    "awesome-rust": {
        "getting_started": "Check the CI status badges next to each entry — this list uniquely shows build status, so you can quickly identify well-maintained projects. Navigate by 'Applications' for complete tools or 'Libraries' for building blocks.",
        "suggested_projects": [
            "Build a Rust crate health monitor that tracks CI status, version updates, and dependency freshness for entries in this list",
            "Create a Rust project template generator that pulls in recommended crates from each library category",
            "Develop a 'Rust alternatives to X' tool that maps popular tools in other languages to Rust equivalents from this list"
        ],
        "featured_example": None
    },
    "awesome-nodejs": {
        "getting_started": "Navigate by functionality (HTTP, Filesystem, Testing, Streams) — sindresorhus maintains this with strict quality criteria, so every entry is reliable. Focus on the category that matches your current project need.",
        "suggested_projects": [
            "Build a Node.js package comparison tool that benchmarks alternatives within each category from this list",
            "Create a Node.js API starter template using the best packages from the HTTP, testing, and database categories",
            "Develop a Node.js dependency audit tool that flags packages not meeting the quality standards of this list"
        ],
        "featured_example": None
    },
    "awesome-docker": {
        "getting_started": "Start with the 'Tools' section for day-to-day Docker workflow enhancements, then explore 'Security' for hardening your containers — the 'Development Environments' section is gold for dev setup optimization.",
        "suggested_projects": [
            "Build a Docker security scanning pipeline using the security tools catalogued in this list",
            "Create a Docker dev environment template that incorporates the best development workflow tools listed here",
            "Develop a container monitoring dashboard using the monitoring and logging tools from this list"
        ],
        "featured_example": None
    },
    "awesome-kubernetes": {
        "getting_started": "Use the starter guide section if you're new to K8s, then navigate by operational concern (Networking, Storage, Security, CI/CD) based on what you're implementing — the topic-based organization matches real operational decisions.",
        "suggested_projects": [
            "Build a Kubernetes cluster setup automation tool using best-practice tools from each category in this list",
            "Create a K8s security audit tool that checks your cluster against security tools and practices listed here",
            "Develop a Kubernetes learning lab that provisions practice clusters with tools from the starter guide section"
        ],
        "featured_example": None
    },
    "awesome-scalability": {
        "getting_started": "Pick a specific topic (Caching, Load Balancing, Consistency, Data Partitioning) and read the linked articles deeply — this is a reading list of real-world case studies, not a tool directory, so depth beats breadth.",
        "suggested_projects": [
            "Build a system design flashcard app using concepts and case studies from each topic section",
            "Create a scalability pattern reference tool that matches your architecture problem to relevant case studies from this list",
            "Develop a distributed system simulator that demonstrates patterns (caching, partitioning, replication) covered here"
        ],
        "featured_example": None
    },
    "github-cheat-sheet": {
        "getting_started": "Browse the 'URL Shortcuts' and 'Keyboard Shortcuts' sections first for immediate productivity wins — these are tricks you can start using in your next GitHub session without any setup.",
        "suggested_projects": [
            "Build a GitHub productivity extension that surfaces hidden features documented in this cheat sheet",
            "Create an interactive Git tips quiz that tests knowledge of the power-user tricks listed here",
            "Develop a GitHub workflow optimizer that suggests relevant shortcuts and features based on your usage patterns"
        ],
        "featured_example": {
            "name": "URL Shortcuts section",
            "url": "https://github.com/tiimgreen/github-cheat-sheet#url-shortcuts",
            "why": "The URL shortcuts section reveals powerful GitHub URL patterns (like .patch, .diff, compare views) that most developers never discover, providing immediate productivity improvements"
        }
    },
    "best-websites-programmer": {
        "getting_started": "Navigate by purpose (Learning, Practice, News, Jobs) rather than scrolling — this curates websites, not GitHub repos, so it fills a unique gap. The 'Coding Challenges' section is especially actionable.",
        "suggested_projects": [
            "Build a developer portal that aggregates feeds and content from the best websites listed here into a single dashboard",
            "Create a coding practice planner that schedules challenges from platforms listed in the Coding Challenges section",
            "Develop a tech news aggregator that combines RSS feeds from news sites and blogs catalogued in this list"
        ],
        "featured_example": None
    },
    "build-your-own-x": {
        "getting_started": "Pick a technology you use daily but don't fully understand (Git, Docker, a database) and find its 'Build Your Own' tutorial — the learning comes from building something you already know how to use.",
        "suggested_projects": [
            "Build your own Git implementation following the tutorial here, then extend it with custom features",
            "Create your own programming language using the compiler/interpreter tutorials in this list",
            "Build a container runtime from scratch following the Docker tutorial, then deploy a real application on it"
        ],
        "featured_example": {
            "name": "Build Your Own Git",
            "url": "https://github.com/codecrafters-io/build-your-own-x#build-your-own-git",
            "why": "The Git tutorials are the perfect entry point — you already use Git daily, so building it from scratch provides deep understanding of a tool you interact with constantly"
        }
    },
    "project-based-learning": {
        "getting_started": "Filter by your programming language first, then pick a project that produces something tangible you'd actually want to use — the best learning happens when you're invested in the output.",
        "suggested_projects": [
            "Build a project portfolio by completing one tutorial from each language section that interests you",
            "Create a learning path generator that sequences projects from this list by difficulty for a given language",
            "Develop a project-based coding bootcamp curriculum using the tutorials here as the core content"
        ],
        "featured_example": None
    },
    "system-design-primer": {
        "getting_started": "Start with the 'System Design Topics' index and work through the topics you're weakest in — use the Anki flash cards for memorization alongside the detailed topic pages for deep understanding.",
        "suggested_projects": [
            "Build a system design interview prep app that presents scenarios and evaluates architectural decisions",
            "Create a distributed system simulator that lets you experiment with load balancing, caching, and partitioning concepts from this guide",
            "Develop a system design documentation template based on the patterns and structures taught here"
        ],
        "featured_example": {
            "name": "Anki Flash Cards",
            "url": "https://github.com/donnemartin/system-design-primer#anki-flashcards",
            "why": "The Anki flash card deck is uniquely valuable — it turns complex system design concepts into spaced-repetition study material, combining the guide's depth with proven memorization techniques"
        }
    },
    "developer-roadmap": {
        "getting_started": "Visit roadmap.sh (the interactive website) rather than reading the GitHub README — the interactive roadmaps let you click into each node for learning resources and mark your progress.",
        "suggested_projects": [
            "Build a skills assessment tool that maps your experience against the roadmap nodes and identifies gaps",
            "Create a learning schedule generator that breaks a roadmap path into weekly study plans with resource links",
            "Develop a team skills matrix dashboard based on roadmap categories for engineering managers"
        ],
        "featured_example": {
            "name": "roadmap.sh",
            "url": "https://roadmap.sh",
            "why": "The interactive website transforms static roadmaps into clickable learning paths with community-contributed resources at each node — far superior to the static GitHub images"
        }
    },
    "openhands": {
        "getting_started": "Start with the quickstart guide to get the agent running locally, then try the benchmarks section to understand its capabilities and limitations before using it on your own codebase.",
        "suggested_projects": [
            "Build a CI/CD integration that uses OpenHands to automatically fix failing tests and create PRs",
            "Create a code review automation pipeline that uses OpenHands to provide AI-powered review feedback",
            "Develop a project scaffolding tool that uses OpenHands to generate and configure new projects from natural language descriptions"
        ],
        "featured_example": None
    },
    "n8n": {
        "getting_started": "Start with the template gallery to find a workflow close to what you need, then customize it — n8n's visual builder makes it faster to modify an existing template than to build from scratch.",
        "suggested_projects": [
            "Build an AI-powered content pipeline that uses n8n to orchestrate content generation, review, and publishing",
            "Create a customer support automation workflow connecting your helpdesk, CRM, and AI tools through n8n",
            "Develop a data monitoring system that uses n8n to collect metrics from multiple sources and trigger alerts"
        ],
        "featured_example": {
            "name": "AI Nodes",
            "url": "https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatollama/",
            "why": "The native AI nodes bridge traditional workflow automation with LLM capabilities, letting you add AI steps to any workflow without writing code — a unique capability among automation platforms"
        }
    },
    "langchain": {
        "getting_started": "Start with the 'Chains' documentation to understand the fundamental building blocks, then explore 'Agents' once you need dynamic tool selection — avoid jumping straight to agents, as chains cover most use cases more reliably.",
        "suggested_projects": [
            "Build a RAG chatbot using LangChain's retriever and chain components to answer questions about your own documents",
            "Create a multi-tool agent that uses LangChain's agent framework to dynamically select between search, code execution, and database queries",
            "Develop an LLM evaluation pipeline using LangChain's built-in evaluation tools to compare model performance"
        ],
        "featured_example": {
            "name": "Retrieval-Augmented Generation",
            "url": "https://python.langchain.com/docs/tutorials/rag/",
            "why": "The RAG tutorial is the most immediately practical entry point — it teaches the most common LLM application pattern with composable components you can adapt to any document corpus"
        }
    },
    "langflow": {
        "getting_started": "Start with the template gallery in the visual builder rather than building from scratch — drag-and-drop an existing template, then modify components to understand how the pieces connect.",
        "suggested_projects": [
            "Build a visual RAG pipeline with custom document processing and retrieval steps using Langflow's drag-and-drop interface",
            "Create a multi-agent workflow where different AI agents handle different parts of a complex task",
            "Develop a chatbot builder platform on top of Langflow that lets non-technical users create custom AI assistants"
        ],
        "featured_example": None
    },
    "dify": {
        "getting_started": "Start with the Workflow Builder to create a simple prompt-and-response flow, then add RAG and agent capabilities incrementally — Dify's modular architecture lets you add complexity gradually.",
        "suggested_projects": [
            "Build an enterprise knowledge base chatbot using Dify's RAG engine with your company's documentation",
            "Create a customer service automation platform using Dify's agent workflows and model management",
            "Develop a multi-model comparison tool using Dify's model management to evaluate different LLMs on the same prompts"
        ],
        "featured_example": {
            "name": "Workflow Builder",
            "url": "https://docs.dify.ai/guides/workflow",
            "why": "The visual workflow builder combines prompt engineering, RAG, and agent capabilities in a single interface, providing the fastest path from idea to production AI application"
        }
    },
    "crewai": {
        "getting_started": "Start by defining two agents with complementary roles (e.g., researcher + writer) and a simple task — the role-based paradigm is most intuitive when you start small and add agents as complexity grows.",
        "suggested_projects": [
            "Build a content creation crew with researcher, writer, and editor agents that produce blog posts from a topic",
            "Create a code review crew where different agents check for security, performance, and style issues",
            "Develop a market research pipeline where agents gather data, analyze trends, and generate reports collaboratively"
        ],
        "featured_example": None
    },
    "ragflow": {
        "getting_started": "Start with the document parsing features to understand RAGFlow's key differentiator — upload a complex PDF with tables and images first, then build a Q&A pipeline on top of the parsed output.",
        "suggested_projects": [
            "Build a legal document analysis system using RAGFlow's advanced PDF parsing and citation tracking",
            "Create a technical documentation search engine that handles complex diagrams, code blocks, and tables",
            "Develop a research paper Q&A system that maintains citation links back to specific pages and sections"
        ],
        "featured_example": {
            "name": "Document Parsing engine",
            "url": "https://github.com/infiniflow/ragflow",
            "why": "RAGFlow's deep document understanding — handling tables, images, and complex layouts with citation tracking — solves the hardest problem in RAG that simpler tools ignore"
        }
    },
    "open-webui": {
        "getting_started": "Install via Docker and connect to Ollama first for a zero-cost local setup, then explore the RAG and web search features — start with local models before connecting to paid APIs.",
        "suggested_projects": [
            "Deploy a team-wide AI chat platform using Open WebUI with role-based access control and shared conversation history",
            "Build a local knowledge base by connecting Open WebUI's RAG features to your project documentation",
            "Create a model comparison workflow using Open WebUI's multi-model support to evaluate different LLMs side-by-side"
        ],
        "featured_example": None
    },
    "ollama": {
        "getting_started": "Run 'ollama pull llama3' then 'ollama run llama3' to get started in under a minute — the CLI is intentionally simple, and the REST API at localhost:11434 is OpenAI-compatible for easy integration.",
        "suggested_projects": [
            "Build a local AI development environment with Ollama serving models to your IDE, terminal, and custom applications",
            "Create a model benchmarking tool that evaluates different quantized models from Ollama's library on your hardware",
            "Develop a private RAG system using Ollama for inference with no data leaving your machine"
        ],
        "featured_example": {
            "name": "Model Library",
            "url": "https://ollama.com/library",
            "why": "The model library provides one-command access to dozens of production-quality models (Llama, Mistral, Gemma, Phi) with optimized quantizations — the fastest path from zero to running local LLMs"
        }
    },
    "gemini-cli": {
        "getting_started": "Install with npm and authenticate with your Google account for free access, then try it in a codebase directory — Gemini CLI's massive context window means it can understand entire repositories at once.",
        "suggested_projects": [
            "Build a code review workflow that uses Gemini CLI to analyze entire PRs with full repository context",
            "Create a documentation generator that uses Gemini CLI's codebase understanding to produce accurate API docs",
            "Develop a migration assistant that uses Gemini CLI to plan and execute large-scale code refactoring across a repository"
        ],
        "featured_example": None
    },
    "awesome-database-learning": {
        "getting_started": "Start with the 'Storage Engines' section if you want to understand how databases work at the lowest level, or 'Query Optimization' if you're focused on performance — the PingCAP team structured this as a deep-dive learning resource.",
        "suggested_projects": [
            "Build a simple key-value storage engine from scratch following the storage engine papers and blogs listed here",
            "Create a query optimizer visualization tool that shows how different optimization strategies work",
            "Develop a database internals study group platform organized around the topic sections in this list"
        ],
        "featured_example": {
            "name": "Storage Engines section",
            "url": "https://github.com/pingcap/awesome-database-learning#storage-engine",
            "why": "The storage engines section — curated by PingCAP engineers who built TiDB — provides the most practical path to understanding database internals, from LSM-trees to B-trees to modern hybrid approaches"
        }
    },
    "awesome-mysql": {
        "getting_started": "Navigate by operational concern (Backup, Monitoring, Replication, Schema Migration) — this list is organized around the tasks of running MySQL in production, curated by a veteran database engineer.",
        "suggested_projects": [
            "Build a MySQL health monitoring dashboard using the monitoring and analysis tools listed here",
            "Create a MySQL migration pipeline using the schema migration tools catalogued in this list",
            "Develop a MySQL backup automation system using the backup tools and best practices referenced here"
        ],
        "featured_example": None
    },
    "awesome-postgres": {
        "getting_started": "Start with the extensions and tools sections to discover what makes PostgreSQL unique — the power of Postgres lies in its extension ecosystem, and this list is the best place to explore it.",
        "suggested_projects": [
            "Build a PostgreSQL extension showcase that demonstrates the capabilities of extensions listed here",
            "Create a Postgres performance tuning toolkit using the monitoring and optimization tools from this list",
            "Develop a PostgreSQL deployment automation tool using the management and backup tools catalogued here"
        ],
        "featured_example": None
    },
    "awesome-mongodb": {
        "getting_started": "Focus on the tools and libraries sections relevant to your programming language — MongoDB's ecosystem is language-specific, so finding the right driver and ODM for your stack is the critical first step.",
        "suggested_projects": [
            "Build a MongoDB schema design assistant that recommends document structures based on access patterns",
            "Create a MongoDB migration toolkit using the tools and libraries catalogued in this list",
            "Develop a MongoDB performance monitoring dashboard using the observability tools listed here"
        ],
        "featured_example": None
    },
    "awesome-db": {
        "getting_started": "Use this as a starting point for choosing a database — the list covers relational, document, graph, time-series, and other database types, so identify your data model first, then explore that category.",
        "suggested_projects": [
            "Build a database selection wizard that recommends the right database from this list based on your use case",
            "Create a multi-database comparison benchmark for different data models (relational, document, graph)",
            "Develop a database technology radar that tracks the maturity and adoption of databases catalogued here"
        ],
        "featured_example": None
    },
    "awesome-copilot": {
        "getting_started": "Browse by integration type — IDE extensions, CLI tools, and API wrappers — to find Copilot-compatible tools that fit your development workflow. Check the tips and configuration sections for optimizing your existing Copilot setup.",
        "suggested_projects": [
            "Build a Copilot productivity analytics tool that measures code suggestion acceptance rates and time saved",
            "Create a Copilot prompt library with custom instructions optimized for different coding tasks",
            "Develop a Copilot extension that adds domain-specific context from your codebase to improve suggestions"
        ],
        "featured_example": None
    },
    "awesome-cursorrules": {
        "getting_started": "Browse the rule examples by language and framework to find templates matching your stack, then customize them — the power of .cursorrules is in project-specific configuration, not generic rules.",
        "suggested_projects": [
            "Build a .cursorrules generator that creates optimized rule files based on your project's tech stack and conventions",
            "Create a cursorrules sharing platform where teams can publish and discover rule configurations",
            "Develop a cursorrules testing framework that validates rule effectiveness by measuring suggestion quality"
        ],
        "featured_example": None
    },
    "awesome-ai-coding-tools": {
        "getting_started": "Navigate by tool category (code completion, code review, documentation, testing) to find AI tools for each stage of your development workflow — the list maps to the software development lifecycle.",
        "suggested_projects": [
            "Build an AI coding tool benchmark that evaluates tools from this list on code quality, speed, and accuracy",
            "Create a developer workflow optimizer that recommends AI tools from this list for each stage of your SDLC",
            "Develop an AI tool integration framework that chains multiple AI coding tools into a unified development pipeline"
        ],
        "featured_example": None
    },
    "awesome-json-datasets": {
        "getting_started": "Browse by data domain (government, weather, sports, etc.) and note that these are all JSON APIs — they're immediately consumable from any programming language without format conversion.",
        "suggested_projects": [
            "Build a real-time data dashboard that visualizes live JSON feeds from multiple APIs listed here",
            "Create a JSON API aggregator that combines data from multiple sources in this list into a unified endpoint",
            "Develop a data exploration app that lets users query and visualize any JSON dataset from this collection"
        ],
        "featured_example": None
    },
    "awesome-chartjs": {
        "getting_started": "Start with the plugins section to extend Chart.js rather than building custom features from scratch — Chart.js's plugin ecosystem is its main strength, and this list catalogs the best plugins by chart type.",
        "suggested_projects": [
            "Build a Chart.js plugin gallery with live previews and configuration playgrounds for each plugin listed here",
            "Create a dashboard builder that uses Chart.js plugins from this list to offer a rich set of chart types",
            "Develop a Chart.js theme system using the styling and customization resources catalogued here"
        ],
        "featured_example": None
    },
    "awesome-dataviz-hal9": {
        "getting_started": "Explore by visualization type and technology — this list emphasizes modern, interactive visualization approaches with a focus on web technologies and AI-assisted visualization.",
        "suggested_projects": [
            "Build an AI-powered visualization recommender that suggests the best chart type and tool from this list for your data",
            "Create an interactive visualization playground that lets you try different tools listed here with your own data",
            "Develop a dataviz portfolio generator using the best tools and examples catalogued in this collection"
        ],
        "featured_example": None
    },
    "awesome-vscode": {
        "getting_started": "Navigate by extension category (Language Support, Productivity, Themes, Debugging) and install extensions incrementally — start with 2-3 from your most-needed category rather than installing everything at once.",
        "suggested_projects": [
            "Build a VS Code extension pack generator that creates curated extension bundles for specific tech stacks",
            "Create a VS Code settings sync and recommendation tool based on the extensions catalogued here",
            "Develop a VS Code productivity benchmark that measures the impact of different extension combinations on coding speed"
        ],
        "featured_example": None
    },
    "awesome-ai-gpts": {
        "getting_started": "Browse by use case category to find GPTs relevant to your workflow — this list focuses on practical, production-quality custom GPTs rather than novelty or experimental ones.",
        "suggested_projects": [
            "Build a custom GPT comparison tool that evaluates GPTs from this list on standard prompts for each category",
            "Create a GPT recommendation engine that suggests the best custom GPT from this list based on your task description",
            "Develop a GPT workflow builder that chains multiple custom GPTs from different categories into a multi-step pipeline"
        ],
        "featured_example": None
    }
}


def regenerate_csv(data):
    """Regenerate lists.csv from the JSON data."""
    if not data:
        return

    fieldnames = list(data[0].keys())

    with open(LISTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for entry in data:
            row = {}
            for key, value in entry.items():
                if isinstance(value, dict):
                    # Serialize objects like featured_example as JSON
                    row[key] = json.dumps(value)
                elif isinstance(value, list):
                    row[key] = "|".join(str(v) for v in value)
                elif isinstance(value, bool):
                    row[key] = "TRUE" if value else "FALSE"
                elif value is None:
                    row[key] = ""
                else:
                    row[key] = value
            writer.writerow(row)


def main():
    print(f"Loading {LISTS_JSON}...")
    with open(LISTS_JSON) as f:
        data = json.load(f)

    total = len(data)
    print(f"Found {total} entries.")

    # Verify enrichment data covers all entries
    entry_ids = {entry["id"] for entry in data}
    enrichment_ids = set(ENRICHMENT.keys())

    missing_from_enrichment = entry_ids - enrichment_ids
    extra_in_enrichment = enrichment_ids - entry_ids

    if missing_from_enrichment:
        print(f"\nERROR: {len(missing_from_enrichment)} entries missing from enrichment data:")
        for eid in sorted(missing_from_enrichment):
            print(f"  - {eid}")
        return

    if extra_in_enrichment:
        print(f"\nWARNING: {len(extra_in_enrichment)} extra entries in enrichment data (not in lists.json):")
        for eid in sorted(extra_in_enrichment):
            print(f"  - {eid}")

    # Apply enrichment
    enriched_count = 0
    for entry in data:
        eid = entry["id"]
        enrichment = ENRICHMENT[eid]

        entry["getting_started"] = enrichment["getting_started"]
        entry["suggested_projects"] = enrichment["suggested_projects"]
        entry["featured_example"] = enrichment["featured_example"]
        enriched_count += 1

    print(f"\nEnriched {enriched_count}/{total} entries.")

    # Verify all entries have all 3 fields
    missing_fields = []
    for entry in data:
        for field in ["getting_started", "suggested_projects", "featured_example"]:
            if field not in entry:
                missing_fields.append((entry["id"], field))

    if missing_fields:
        print(f"\nERROR: {len(missing_fields)} missing fields:")
        for eid, field in missing_fields:
            print(f"  - {eid}: {field}")
        return

    # Write JSON
    print(f"\nWriting {LISTS_JSON}...")
    with open(LISTS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Regenerate CSV
    print(f"Writing {LISTS_CSV}...")
    regenerate_csv(data)

    print(f"\nDone! All {total} entries enriched with getting_started, suggested_projects, and featured_example.")


if __name__ == "__main__":
    main()
