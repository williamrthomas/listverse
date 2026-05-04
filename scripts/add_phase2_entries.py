#!/usr/bin/env python3
"""Phase 2: Add ~100 new entries to data/lists.json.

This script:
1. Loads existing data/lists.json
2. Defines ~100 new entries across 10 subcategories
3. Fetches live GitHub stats for each new entry via gh CLI
4. Appends new entries to the array
5. Writes updated JSON
6. Regenerates data/lists.csv
7. Regenerates data/tags.json
"""

import csv
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LISTS_JSON = REPO_ROOT / "data" / "lists.json"
LISTS_CSV = REPO_ROOT / "data" / "lists.csv"
TAGS_JSON = REPO_ROOT / "data" / "tags.json"

TODAY = "2026-05-04"


def fetch_gh_stats(owner, repo):
    """Fetch live stats from GitHub API via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}", "--jq",
             '{stars: .stargazers_count, forks: .forks_count, pushed: .pushed_at, '
             'issues: .open_issues_count, archived: .archived, watchers: .watchers_count, '
             'created: .created_at, license: .license.spdx_id, has_pages: .has_pages, '
             'homepage: .homepage}'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  WARN: gh api failed for {owner}/{repo}: {result.stderr.strip()}")
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  WARN: exception for {owner}/{repo}: {e}")
        return None


def compute_quality_score(stars, last_commit, entry_count_str, is_curated=True):
    """Compute quality score 0-10 based on stars, recency, entry count, curation."""
    score = 0.0
    # Stars contribution (0-3)
    if stars >= 50000:
        score += 3.0
    elif stars >= 10000:
        score += 2.5
    elif stars >= 5000:
        score += 2.0
    elif stars >= 1000:
        score += 1.5
    elif stars >= 500:
        score += 1.0
    else:
        score += 0.5

    # Recency (0-3)
    if last_commit:
        try:
            lc = datetime.strptime(last_commit[:10], "%Y-%m-%d")
            days_ago = (datetime(2026, 5, 4) - lc).days
            if days_ago < 30:
                score += 3.0
            elif days_ago < 90:
                score += 2.5
            elif days_ago < 180:
                score += 2.0
            elif days_ago < 365:
                score += 1.5
            elif days_ago < 730:
                score += 1.0
            else:
                score += 0.5
        except ValueError:
            score += 1.0

    # Entry count (0-2)
    ec = entry_count_str.replace("+", "").replace(",", "").strip()
    try:
        ec_num = int(ec)
        if ec_num >= 500:
            score += 2.0
        elif ec_num >= 200:
            score += 1.5
        elif ec_num >= 100:
            score += 1.0
        else:
            score += 0.5
    except ValueError:
        score += 1.0

    # Curation quality (0-2)
    score += 2.0 if is_curated else 1.0

    return min(10, max(1, round(score)))


def stars_approx(count):
    """Convert star count to approximate string like '12k'."""
    if count >= 1000:
        k = count / 1000
        if k >= 100:
            return f"{int(k)}k"
        elif k >= 10:
            return f"{k:.0f}k"
        else:
            return f"{k:.1f}k"
    return str(count)


# ============================================================
# NEW ENTRIES — Phase 2
# ============================================================

NEW_ENTRIES = [
    # ========================
    # Natural Language Processing (~12 entries) — under "AI & Machine Learning"
    # ========================
    {
        "id": "nlp-progress",
        "name": "NLP-progress",
        "github_url": "https://github.com/sebastianruder/NLP-progress",
        "description": "Repository to track the progress in Natural Language Processing, including datasets and state-of-the-art results for the most common NLP tasks.",
        "maintainer": "sebastianruder",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "benchmarks", "research", "state-of-the-art"],
        "entry_count_approx": "400+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive leaderboard tracker for NLP tasks. Sebastian Ruder (DeepMind researcher) maintains this with academic rigor — every entry links to papers and datasets. Essential for knowing what's state-of-the-art on any NLP benchmark.",
        "related_lists": ["awesome-nlp", "awesome-deep-learning"],
        "list_type": "papers",
        "audience_level": "advanced",
        "use_cases": ["tracking NLP benchmarks", "finding SOTA models for specific tasks", "identifying research trends in NLP"],
        "has_website": True,
        "website_url": "https://nlpprogress.com",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-nlp"],
        "best_sections": ["Question Answering", "Machine Translation", "Sentiment Analysis"],
        "getting_started": "Jump directly to the task you care about (e.g., Named Entity Recognition, Sentiment Analysis) — each page shows the current SOTA model, its score, and a link to the paper. Compare across datasets to understand which approaches generalize.",
        "suggested_projects": [
            "Build a SOTA tracker dashboard that monitors NLP-progress for changes and alerts you when a new best result appears on your target task",
            "Create a benchmark comparison tool that plots model performance across multiple NLP tasks over time",
            "Develop a research paper recommender that suggests papers from NLP-progress based on your reading history"
        ],
        "featured_example": {
            "name": "Question Answering benchmarks",
            "url": "https://nlpprogress.com/english/question_answering.html",
            "why": "The QA section is the most actively updated and comprehensive — it tracks every major benchmark (SQuAD, TriviaQA, NaturalQuestions) with results going back years"
        }
    },
    {
        "id": "awesome-nlp",
        "name": "Awesome NLP",
        "github_url": "https://github.com/keon/awesome-nlp",
        "description": "A curated list of resources dedicated to Natural Language Processing (NLP).",
        "maintainer": "keon",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "tools", "libraries", "curated-list"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive general NLP awesome list. Well-organized by topic (libraries, datasets, NLP in other languages) and actively maintained. The go-to starting point for anyone exploring the NLP ecosystem.",
        "related_lists": ["nlp-progress", "awesome-dl4nlp"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["finding NLP libraries", "discovering NLP datasets", "exploring NLP tools across languages"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["nlp-progress", "awesome-machine-learning"],
        "best_sections": ["Libraries", "Datasets", "NLP in Other Languages"],
        "getting_started": "Start with the 'Libraries' section filtered by your programming language, then explore 'Datasets' for training data matching your use case. The 'NLP in Other Languages' section is uniquely valuable for multilingual projects.",
        "suggested_projects": [
            "Build a multilingual sentiment analysis API using libraries and datasets found in this list",
            "Create a text preprocessing pipeline benchmarking tool that compares spaCy, NLTK, and Stanza on your data",
            "Develop a domain-specific NER model using annotated datasets linked in the Datasets section"
        ],
        "featured_example": {
            "name": "spaCy",
            "url": "https://spacy.io",
            "why": "spaCy is the most production-ready NLP library — it offers the best balance of speed, accuracy, and developer experience for real-world NLP applications"
        }
    },
    {
        "id": "awesome-dl4nlp",
        "name": "Awesome Deep Learning for NLP",
        "github_url": "https://github.com/brianspiering/awesome-dl4nlp",
        "description": "A curated list of resources for deep learning approaches to natural language processing.",
        "maintainer": "brianspiering",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "deep-learning", "research", "tutorials"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Bridges deep learning and NLP specifically — where awesome-nlp covers the broad NLP landscape, this focuses on the transformer and neural network revolution. Great reading lists organized by technique (attention, transfer learning, etc.).",
        "related_lists": ["awesome-nlp", "awesome-deep-learning"],
        "list_type": "papers",
        "audience_level": "intermediate",
        "use_cases": ["learning deep learning for NLP", "finding DL-based NLP papers", "understanding transformer architectures"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["awesome-nlp"],
        "best_sections": ["Attention Mechanisms", "Transfer Learning", "Text Classification"],
        "getting_started": "Start with the 'Courses' section if you're new to DL+NLP, then move to 'Attention Mechanisms' and 'Transformers' — these are the foundational concepts behind modern NLP. The papers are ordered by accessibility.",
        "suggested_projects": [
            "Implement a text classification model following the progression from RNN to Transformer architectures outlined in the resources",
            "Build a custom fine-tuned language model for your domain using techniques from the Transfer Learning section",
            "Create a comparison notebook showing attention visualization across different NLP tasks"
        ],
        "featured_example": {
            "name": "Attention Is All You Need",
            "url": "https://arxiv.org/abs/1706.03762",
            "why": "The foundational transformer paper that changed everything — every modern LLM traces back to this architecture"
        }
    },
    {
        "id": "awesome-relation-extraction",
        "name": "Awesome Relation Extraction",
        "github_url": "https://github.com/roomylee/awesome-relation-extraction",
        "description": "A curated list of resources for relation extraction, a key NLP task for building knowledge graphs.",
        "maintainer": "roomylee",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "relation-extraction", "knowledge-graphs", "research"],
        "entry_count_approx": "150+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "A niche but exceptionally well-organized list for relation extraction — a critical subtask for building knowledge graphs from text. Papers are organized chronologically and by approach (distant supervision, neural, few-shot).",
        "related_lists": ["awesome-nlp", "awesome-dl4nlp"],
        "list_type": "papers",
        "audience_level": "advanced",
        "use_cases": ["building knowledge graphs", "extracting relationships from text", "information extraction research"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Papers", "Datasets", "Benchmarks"],
        "getting_started": "Start with the survey papers at the top to get an overview, then browse the 'Datasets' section to find benchmarks matching your domain. The papers are chronologically ordered — start from 2018+ for modern neural approaches.",
        "suggested_projects": [
            "Build a knowledge graph extraction pipeline that processes Wikipedia articles and extracts entity relationships",
            "Create a relation extraction model fine-tuned on a domain-specific dataset (medical, legal, financial)",
            "Develop a tool that takes raw text and outputs a visual knowledge graph using extracted relations"
        ],
        "featured_example": {
            "name": "DocRED dataset",
            "url": "https://github.com/thunlp/DocRED",
            "why": "DocRED is the largest document-level relation extraction dataset — it pushes beyond sentence-level extraction which is where the field is heading"
        }
    },
    {
        "id": "awesome-data-annotation",
        "name": "Awesome Data Annotation",
        "github_url": "https://github.com/taivop/awesome-data-annotation",
        "description": "A curated list of tools and resources for data annotation and labeling, essential for building ML training datasets.",
        "maintainer": "taivop",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "annotation", "labeling", "datasets", "tools"],
        "entry_count_approx": "100+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Fills a critical gap — everyone talks about models but data annotation is where projects succeed or fail. Covers text, image, audio, and video annotation tools. The comparison tables are particularly useful for choosing the right tool.",
        "related_lists": ["awesome-nlp", "awesome-public-datasets"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["choosing annotation tools", "setting up labeling workflows", "building training datasets"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Text Annotation", "Image Annotation", "Comparison Tables"],
        "getting_started": "Jump to the modality you need (text, image, audio) and use the comparison tables to narrow down tools. Pay attention to the 'self-hosted' vs 'cloud' distinction — this is the biggest decision for most teams.",
        "suggested_projects": [
            "Set up a Label Studio instance and build an annotation pipeline for a custom NER dataset",
            "Create a data quality dashboard that tracks inter-annotator agreement across your labeling project",
            "Build an active learning loop that prioritizes the most informative samples for human annotation"
        ],
        "featured_example": {
            "name": "Label Studio",
            "url": "https://labelstud.io",
            "why": "The most versatile open-source annotation platform — supports text, image, audio, video, and time series with a plugin architecture for custom interfaces"
        }
    },
    {
        "id": "snorkel",
        "name": "Snorkel",
        "github_url": "https://github.com/snorkel-team/snorkel",
        "description": "A system for programmatically building and managing training datasets without manual labeling.",
        "maintainer": "snorkel-team",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "data-labeling", "weak-supervision", "machine-learning"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Stanford-born framework that pioneered weak supervision — instead of hand-labeling thousands of examples, you write labeling functions and Snorkel combines them intelligently. A paradigm shift for teams that can't afford massive annotation budgets.",
        "related_lists": ["awesome-data-annotation", "awesome-machine-learning"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["programmatic data labeling", "reducing annotation costs", "weak supervision for ML"],
        "has_website": True,
        "website_url": "https://snorkel.ai",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Tutorials", "Labeling Functions", "Slicing Functions"],
        "getting_started": "Start with the introductory tutorial that walks through writing labeling functions for a text classification task. The key insight is writing multiple noisy labeling functions and letting Snorkel learn their accuracies automatically.",
        "suggested_projects": [
            "Build a sentiment classifier using only labeling functions — no manual labels — and compare it to a fully supervised baseline",
            "Create a domain-specific NER system using Snorkel's weak supervision to bootstrap training data from heuristics and external knowledge bases",
            "Develop a data programming pipeline that combines regex patterns, distant supervision, and LLM-generated labels"
        ],
        "featured_example": {
            "name": "Spam classification tutorial",
            "url": "https://www.snorkel.org/use-cases/01-spam-tutorial",
            "why": "The spam tutorial perfectly demonstrates the weak supervision paradigm — you go from zero labels to a working classifier in under an hour using just labeling functions"
        }
    },
    {
        "id": "spacy",
        "name": "spaCy",
        "github_url": "https://github.com/explosion/spaCy",
        "description": "Industrial-strength Natural Language Processing library with pre-trained pipelines for 70+ languages.",
        "maintainer": "explosion",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "python", "library", "production"],
        "entry_count_approx": "70+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The production NLP library. Where NLTK is academic and Hugging Face is research-first, spaCy is designed for real-world pipelines — fast, opinionated, and battle-tested. The trained pipeline ecosystem and spaCy Projects make it uniquely deployment-ready.",
        "related_lists": ["awesome-nlp", "nltk"],
        "list_type": "libraries",
        "audience_level": "intermediate",
        "use_cases": ["production NLP pipelines", "named entity recognition", "text processing at scale"],
        "has_website": True,
        "website_url": "https://spacy.io",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["nltk"],
        "best_sections": ["Models", "Pipelines", "spaCy Projects"],
        "getting_started": "Install with `pip install spacy` and download a model (`python -m spacy download en_core_web_sm`). The 'Usage' section in docs walks through tokenization, NER, and POS tagging. Start with the 101 guides before diving into custom components.",
        "suggested_projects": [
            "Build a custom NER pipeline for your domain (legal, medical, financial) using spaCy's training system",
            "Create a text analytics dashboard that processes documents with spaCy and visualizes entities, dependencies, and key phrases",
            "Develop a document processing pipeline using spaCy Projects that handles intake, processing, and export"
        ],
        "featured_example": {
            "name": "spaCy 101",
            "url": "https://spacy.io/usage/spacy-101",
            "why": "The interactive 101 guide is the fastest way to understand spaCy's design philosophy — it covers the core concepts in 15 minutes with runnable examples"
        }
    },
    {
        "id": "huggingface-transformers",
        "name": "Hugging Face Transformers",
        "github_url": "https://github.com/huggingface/transformers",
        "description": "State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX with thousands of pre-trained models.",
        "maintainer": "huggingface",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "transformers", "deep-learning", "python", "llm"],
        "entry_count_approx": "500+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "THE transformer library. With 500k+ models on the Hub and first-class support for every major architecture (BERT, GPT, T5, Llama, etc.), Hugging Face Transformers is the de facto standard for working with pre-trained language models. The pipeline API makes complex NLP tasks trivially easy.",
        "related_lists": ["awesome-nlp", "awesome-llm", "spacy"],
        "list_type": "frameworks",
        "audience_level": "all",
        "use_cases": ["using pre-trained language models", "fine-tuning models for specific tasks", "building NLP applications"],
        "has_website": True,
        "website_url": "https://huggingface.co/docs/transformers",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["awesome-llm"],
        "best_sections": ["Quick Tour", "Task Guides", "Model Hub"],
        "getting_started": "Start with `pip install transformers` and the pipeline API — you can do sentiment analysis, NER, translation, and summarization in 3 lines of code. Move to the Trainer API when you need to fine-tune, and explore the Model Hub for pre-trained checkpoints.",
        "suggested_projects": [
            "Fine-tune a BERT model on a domain-specific classification task using the Trainer API and push it to the Hub",
            "Build a semantic search engine over your documents using sentence-transformers and FAISS",
            "Create a multi-task NLP API that handles classification, NER, and summarization using the pipeline abstraction"
        ],
        "featured_example": {
            "name": "Hugging Face Model Hub",
            "url": "https://huggingface.co/models",
            "why": "The Model Hub hosts 500k+ pre-trained models with one-click inference demos — it's the npm of machine learning and the reason Transformers became the standard"
        }
    },
    {
        "id": "fairseq",
        "name": "fairseq",
        "github_url": "https://github.com/facebookresearch/fairseq",
        "description": "Facebook AI Research's sequence modeling toolkit for training custom models for translation, summarization, and other text generation tasks.",
        "maintainer": "facebookresearch",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "sequence-modeling", "translation", "research", "deep-learning"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Meta's research-grade sequence modeling toolkit — less user-friendly than Hugging Face but more flexible for custom architectures. Home of many landmark models (RoBERTa, BART, wav2vec). Best for researchers pushing the boundaries rather than application developers.",
        "related_lists": ["huggingface-transformers", "awesome-nlp"],
        "list_type": "frameworks",
        "audience_level": "advanced",
        "use_cases": ["training custom seq2seq models", "machine translation research", "reproducing FAIR papers"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["huggingface-transformers"],
        "best_sections": ["Examples", "Pre-trained Models", "Translation"],
        "getting_started": "Start with the README examples for your task (translation, language modeling, or summarization). The pre-trained model zoo includes RoBERTa, BART, and wav2vec checkpoints. Use the `fairseq-train` and `fairseq-generate` CLI tools for quick experiments.",
        "suggested_projects": [
            "Train a custom machine translation model for a low-resource language pair using fairseq's transformer implementation",
            "Reproduce a FAIR paper's results (e.g., RoBERTa) and compare against your own dataset",
            "Build a multilingual summarization system using fairseq's mBART pre-trained checkpoints"
        ],
        "featured_example": {
            "name": "RoBERTa pre-trained models",
            "url": "https://github.com/facebookresearch/fairseq/tree/main/examples/roberta",
            "why": "RoBERTa showed that BERT was undertrained — the pre-trained checkpoints here remain among the strongest encoder models for downstream NLP tasks"
        }
    },
    {
        "id": "corenlp",
        "name": "Stanford CoreNLP",
        "github_url": "https://github.com/stanfordnlp/CoreNLP",
        "description": "Stanford's Java-based NLP toolkit providing a wide range of linguistic analysis tools.",
        "maintainer": "stanfordnlp",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "java", "linguistics", "academic"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The academic gold standard for NLP analysis. CoreNLP predates the deep learning revolution but remains the most linguistically rigorous toolkit — its dependency parser, coreference resolution, and sentiment analysis are still reference implementations for many researchers.",
        "related_lists": ["awesome-nlp", "spacy", "nltk"],
        "list_type": "libraries",
        "audience_level": "advanced",
        "use_cases": ["linguistic analysis", "dependency parsing", "coreference resolution"],
        "has_website": True,
        "website_url": "https://stanfordnlp.github.io/CoreNLP/",
        "is_awesome_verified": False,
        "language_focus": "java",
        "overlaps_with": ["spacy", "nltk"],
        "best_sections": ["Annotators", "Usage", "Models"],
        "getting_started": "Download the JAR and models, then use the command-line interface for quick experiments. The server mode lets you access CoreNLP from any language via HTTP. For Python users, the stanza package provides a native Python interface to the same models.",
        "suggested_projects": [
            "Build a document analysis pipeline using CoreNLP's full annotator chain (tokenize, ssplit, pos, lemma, ner, parse, coref)",
            "Create a coreference resolution visualization tool that shows how entities are linked across a document",
            "Develop a linguistic feature extractor that computes syntactic complexity metrics for text readability analysis"
        ],
        "featured_example": {
            "name": "Stanza (Python interface)",
            "url": "https://stanfordnlp.github.io/stanza/",
            "why": "Stanza brings CoreNLP's linguistic rigor to Python with a modern API — it's the best of both worlds for researchers who want Stanford quality without writing Java"
        }
    },
    {
        "id": "nltk",
        "name": "NLTK",
        "github_url": "https://github.com/nltk/nltk",
        "description": "The Natural Language Toolkit — Python's foundational NLP library for education and research.",
        "maintainer": "nltk",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "python", "education", "linguistics"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The original Python NLP library and still the best for learning computational linguistics. NLTK prioritizes clarity and educational value over performance — every algorithm is implemented readably with extensive documentation. Not recommended for production, but invaluable for understanding NLP fundamentals.",
        "related_lists": ["awesome-nlp", "spacy", "corenlp"],
        "list_type": "libraries",
        "audience_level": "beginner",
        "use_cases": ["learning NLP", "prototyping NLP ideas", "accessing linguistic corpora"],
        "has_website": True,
        "website_url": "https://www.nltk.org",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["spacy"],
        "best_sections": ["NLTK Book", "Corpora", "Tokenizers"],
        "getting_started": "Start with the free NLTK Book (nltk.org/book) — it teaches NLP concepts through hands-on Python examples. Download the popular corpora with `nltk.download('popular')`. Use NLTK for learning and prototyping, then move to spaCy for production.",
        "suggested_projects": [
            "Work through the NLTK Book and build a text classifier for a corpus of your choice",
            "Create a corpus analysis tool that computes word frequencies, collocations, and concordances for any text collection",
            "Build a chatbot using NLTK's tokenization, POS tagging, and named entity recognition pipeline"
        ],
        "featured_example": {
            "name": "Natural Language Processing with Python (NLTK Book)",
            "url": "https://www.nltk.org/book/",
            "why": "The free online NLTK Book is the most accessible introduction to computational linguistics — it teaches NLP through practical Python programming rather than abstract theory"
        }
    },
    {
        "id": "awesome-vietnamese-nlp",
        "name": "Awesome Vietnamese NLP",
        "github_url": "https://github.com/undertheseanlp/NLP-Vietnamese-progress",
        "description": "Tracking progress and resources for Vietnamese Natural Language Processing.",
        "maintainer": "undertheseanlp",
        "category": "AI & Machine Learning",
        "subcategory": "Natural Language Processing",
        "tags": ["nlp", "vietnamese", "low-resource", "benchmarks"],
        "entry_count_approx": "80+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "An excellent example of a language-specific NLP resource list. Tracks Vietnamese NLP progress with benchmarks, datasets, and models specific to Vietnamese. Demonstrates the pattern for how every language community should organize their NLP resources.",
        "related_lists": ["awesome-nlp", "nlp-progress"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["Vietnamese NLP development", "finding Vietnamese language models", "benchmarking Vietnamese NLP tasks"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Word Segmentation", "Named Entity Recognition", "Datasets"],
        "getting_started": "Browse by NLP task (word segmentation, NER, POS tagging) to find Vietnamese-specific models and datasets. Word segmentation is uniquely important for Vietnamese — start there if building a Vietnamese NLP pipeline.",
        "suggested_projects": [
            "Build a Vietnamese text analytics pipeline combining word segmentation, POS tagging, and NER from the listed tools",
            "Create a Vietnamese sentiment analysis model using the datasets and pre-trained models referenced here",
            "Develop a bilingual (English-Vietnamese) information extraction system using cross-lingual transfer learning"
        ],
        "featured_example": {
            "name": "underthesea NLP toolkit",
            "url": "https://github.com/undertheseanlp/underthesea",
            "why": "The most comprehensive Vietnamese NLP toolkit — provides word segmentation, POS tagging, NER, and sentiment analysis in a single package"
        }
    },

    # ========================
    # Computer Vision (~10 entries) — under "AI & Machine Learning"
    # ========================
    {
        "id": "awesome-computer-vision",
        "name": "Awesome Computer Vision",
        "github_url": "https://github.com/jbhuang0604/awesome-computer-vision",
        "description": "A curated list of computer vision resources covering books, courses, papers, datasets, and software.",
        "maintainer": "jbhuang0604",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "deep-learning", "research", "curated-list"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive computer vision awesome list — maintained by a CV professor, it covers everything from classical image processing to modern deep learning approaches. Uniquely strong on educational resources (courses, textbooks) alongside tools and papers.",
        "related_lists": ["awesome-deep-vision", "awesome-deep-learning"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["learning computer vision", "finding CV papers and datasets", "discovering CV tools and libraries"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-deep-vision"],
        "best_sections": ["Courses", "Papers", "Datasets"],
        "getting_started": "If you're learning CV, start with the 'Courses' section — the Stanford CS231n and Michigan EECS courses are the gold standard. For practitioners, jump to 'Software' to find libraries, then 'Datasets' for benchmarks matching your application.",
        "suggested_projects": [
            "Build an image classification pipeline using a pre-trained model and fine-tune it on a custom dataset from the Datasets section",
            "Create a visual search engine that indexes product images using features from a CV model",
            "Develop a real-time object tracking system combining detection and tracking approaches listed here"
        ],
        "featured_example": {
            "name": "Stanford CS231n",
            "url": "http://cs231n.stanford.edu/",
            "why": "The most influential CV course ever created — Andrej Karpathy and Fei-Fei Li's lectures remain the best introduction to deep learning for computer vision"
        }
    },
    {
        "id": "awesome-deep-vision",
        "name": "Awesome Deep Vision",
        "github_url": "https://github.com/kjw0612/awesome-deep-vision",
        "description": "A curated list of deep learning resources for computer vision, organized by task and application.",
        "maintainer": "kjw0612",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "deep-learning", "research", "papers"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Focuses specifically on deep learning approaches to CV — more research-oriented than awesome-computer-vision. Papers are organized by task (detection, segmentation, generation) making it easy to trace the evolution of each subfield.",
        "related_lists": ["awesome-computer-vision", "awesome-deep-learning"],
        "list_type": "papers",
        "audience_level": "advanced",
        "use_cases": ["CV research papers", "tracking deep learning advances in vision", "finding task-specific architectures"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-computer-vision"],
        "best_sections": ["Object Detection", "Image Segmentation", "Image Generation"],
        "getting_started": "Navigate by the CV task you're working on (detection, segmentation, generation, etc.). Papers within each section are roughly chronological — read the earlier foundational papers first, then follow the progression to current approaches.",
        "suggested_projects": [
            "Implement a paper from the Object Detection section (like YOLO or DETR) from scratch to understand the architecture",
            "Build an image segmentation pipeline for a real-world use case (medical imaging, satellite imagery) using approaches from the list",
            "Create a style transfer application using generative models from the Image Generation section"
        ],
        "featured_example": {
            "name": "You Only Look Once (YOLO)",
            "url": "https://arxiv.org/abs/1506.02640",
            "why": "YOLO fundamentally changed real-time object detection — its single-shot approach proved that speed and accuracy aren't mutually exclusive"
        }
    },
    {
        "id": "openvino",
        "name": "OpenVINO",
        "github_url": "https://github.com/openvinotoolkit/openvino",
        "description": "Intel's open-source toolkit for optimizing and deploying AI inference across Intel hardware.",
        "maintainer": "openvinotoolkit",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "inference", "optimization", "deployment", "intel"],
        "entry_count_approx": "200+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Intel's answer to NVIDIA's TensorRT — optimizes models for deployment on CPUs, integrated GPUs, and VPUs. Particularly valuable if you're deploying CV models on edge devices or don't have GPU infrastructure. The Model Zoo and benchmark tools are excellent.",
        "related_lists": ["awesome-computer-vision", "opencv"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["optimizing model inference", "deploying CV on edge devices", "CPU-based AI deployment"],
        "has_website": True,
        "website_url": "https://docs.openvino.ai",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Model Optimization Guide", "Notebooks", "Model Zoo"],
        "getting_started": "Start with the Jupyter notebooks in the samples directory — they walk through converting and optimizing models from PyTorch/TensorFlow. The Model Zoo has 300+ pre-optimized models ready for immediate use. Focus on the 'Benchmark Tool' to measure speedups.",
        "suggested_projects": [
            "Take a PyTorch CV model and optimize it with OpenVINO, benchmarking the speedup on CPU vs GPU inference",
            "Build an edge deployment pipeline that converts, quantizes, and deploys a detection model to a Raspberry Pi or Intel NUC",
            "Create a multi-model inference server using OpenVINO's model serving that handles detection, classification, and segmentation simultaneously"
        ],
        "featured_example": {
            "name": "OpenVINO Notebooks",
            "url": "https://github.com/openvinotoolkit/openvino_notebooks",
            "why": "The notebook collection is the fastest way to see OpenVINO in action — 200+ Jupyter notebooks covering every common CV task with step-by-step optimization"
        }
    },
    {
        "id": "ultralytics",
        "name": "Ultralytics (YOLO)",
        "github_url": "https://github.com/ultralytics/ultralytics",
        "description": "Ultralytics YOLO — the state-of-the-art real-time object detection, segmentation, and classification library.",
        "maintainer": "ultralytics",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "object-detection", "yolo", "real-time", "python"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The easiest path to production object detection. YOLO11 achieves state-of-the-art accuracy with a dead-simple API — `model.predict(image)` is literally all you need. Supports detection, segmentation, classification, pose estimation, and oriented bounding boxes in one unified framework.",
        "related_lists": ["awesome-computer-vision", "detectron2"],
        "list_type": "frameworks",
        "audience_level": "all",
        "use_cases": ["object detection", "image segmentation", "real-time CV applications"],
        "has_website": True,
        "website_url": "https://docs.ultralytics.com",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["detectron2"],
        "best_sections": ["Quick Start", "Tasks", "Modes"],
        "getting_started": "Install with `pip install ultralytics` and run detection in 3 lines: `from ultralytics import YOLO; model = YOLO('yolo11n.pt'); results = model('image.jpg')`. The docs cover training custom models, exporting to ONNX/TensorRT, and deploying to edge devices.",
        "suggested_projects": [
            "Train a custom YOLO model on your own dataset using Roboflow for annotation and Ultralytics for training",
            "Build a real-time video analytics pipeline that counts objects, tracks movement, and generates heatmaps",
            "Deploy a YOLO model to a mobile device using NCNN or TFLite export for on-device inference"
        ],
        "featured_example": {
            "name": "YOLO11 Quickstart",
            "url": "https://docs.ultralytics.com/quickstart/",
            "why": "The quickstart gets you from zero to detecting objects in images in under 5 minutes — the API is so simple it feels like cheating"
        }
    },
    {
        "id": "detectron2",
        "name": "Detectron2",
        "github_url": "https://github.com/facebookresearch/detectron2",
        "description": "Meta AI's next-generation library for object detection, segmentation, and other visual recognition tasks.",
        "maintainer": "facebookresearch",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "object-detection", "segmentation", "research"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Meta's research-grade detection framework — more complex than YOLO but far more extensible. The modular design lets you mix and match backbones, heads, and data augmentations. The Model Zoo includes Mask R-CNN, RetinaNet, and panoptic segmentation baselines.",
        "related_lists": ["ultralytics", "awesome-computer-vision"],
        "list_type": "frameworks",
        "audience_level": "advanced",
        "use_cases": ["instance segmentation", "panoptic segmentation", "custom detection architectures"],
        "has_website": True,
        "website_url": "https://detectron2.readthedocs.io",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["ultralytics"],
        "best_sections": ["Getting Started", "Model Zoo", "Tutorials"],
        "getting_started": "Start with the Colab tutorials — they walk through training on custom datasets. The `DefaultPredictor` class handles inference in a few lines. For custom architectures, understand the config system first (it's YAML-based and very flexible).",
        "suggested_projects": [
            "Train a Mask R-CNN model on a custom instance segmentation dataset for your specific domain",
            "Build a panoptic segmentation pipeline that labels every pixel in an image with both stuff and thing classes",
            "Create a custom detection architecture by combining Detectron2 building blocks (backbone, FPN, head)"
        ],
        "featured_example": {
            "name": "Detectron2 Model Zoo",
            "url": "https://github.com/facebookresearch/detectron2/blob/main/MODEL_ZOO.md",
            "why": "The Model Zoo provides 50+ pre-trained models with detailed accuracy/speed trade-offs — essential for choosing the right baseline for your project"
        }
    },
    {
        "id": "opencv",
        "name": "OpenCV",
        "github_url": "https://github.com/opencv/opencv",
        "description": "The open-source computer vision library — the foundational toolkit for image and video processing.",
        "maintainer": "opencv",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "image-processing", "library", "c++", "python"],
        "entry_count_approx": "2500+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The canonical computer vision library that virtually every CV application depends on — 20+ years of development with bindings in Python, Java, and JavaScript. Even if you use higher-level frameworks for detection/segmentation, OpenCV handles the image I/O, transforms, and preprocessing underneath.",
        "related_lists": ["awesome-computer-vision", "openvino"],
        "list_type": "libraries",
        "audience_level": "all",
        "use_cases": ["image processing", "video analysis", "camera calibration", "feature detection"],
        "has_website": True,
        "website_url": "https://opencv.org",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Tutorials", "Image Processing", "Video Analysis"],
        "getting_started": "Install with `pip install opencv-python` and start with the official tutorials organized by module (core, imgproc, video, ml). For practical projects, the Python tutorials on image manipulation and video capture are the fastest starting point.",
        "suggested_projects": [
            "Build a document scanner that detects edges, applies perspective correction, and enhances contrast using classical CV techniques",
            "Create a real-time face detection and tracking system using OpenCV's DNN module with pre-trained models",
            "Develop an image stitching pipeline that creates panoramas from overlapping photos"
        ],
        "featured_example": {
            "name": "OpenCV-Python Tutorials",
            "url": "https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html",
            "why": "The Python tutorials are the most practical CV learning resource — they teach fundamentals like edge detection, contours, and histogram analysis through hands-on examples"
        }
    },
    {
        "id": "mediapipe",
        "name": "MediaPipe",
        "github_url": "https://github.com/google-ai-edge/mediapipe",
        "description": "Google's framework for building multimodal ML pipelines, specializing in real-time perception tasks like face/hand/pose detection.",
        "maintainer": "google-ai-edge",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "real-time", "ml-pipeline", "mobile", "edge"],
        "entry_count_approx": "30+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Google's perception pipeline framework — optimized for mobile and edge devices. The pre-built solutions (face mesh, hand tracking, pose estimation) are astonishingly fast and accurate. Ideal for interactive applications where you need real-time body/face/hand understanding.",
        "related_lists": ["awesome-computer-vision", "opencv"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["real-time pose estimation", "hand tracking", "face mesh detection", "mobile ML"],
        "has_website": True,
        "website_url": "https://ai.google.dev/edge/mediapipe/solutions/guide",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Solutions", "Framework", "Model Maker"],
        "getting_started": "Start with the pre-built Solutions (face detection, hand landmarks, pose estimation) — each has a Python/JS/Android quickstart. The Model Maker tool lets you customize models with your own data without deep ML expertise.",
        "suggested_projects": [
            "Build a gesture-controlled application using MediaPipe hand tracking to recognize custom hand gestures",
            "Create a fitness rep counter that uses pose estimation to track exercise form and count repetitions in real time",
            "Develop a sign language translator using hand landmark detection and a custom classifier trained on sign language datasets"
        ],
        "featured_example": {
            "name": "Hand Landmarks Detection",
            "url": "https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker",
            "why": "Hand landmark detection is MediaPipe's most impressive demo — 21 3D landmarks per hand at 30+ FPS on a phone, enabling entirely new interaction paradigms"
        }
    },
    {
        "id": "pytorch-image-models",
        "name": "PyTorch Image Models (timm)",
        "github_url": "https://github.com/huggingface/pytorch-image-models",
        "description": "The largest collection of PyTorch image models, with pre-trained weights, data augmentation, and training scripts.",
        "maintainer": "huggingface",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "pytorch", "image-classification", "pre-trained-models"],
        "entry_count_approx": "1000+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Ross Wightman's timm library is the backbone of modern image classification research — it contains 1000+ model architectures with pre-trained weights. When Hugging Face acquired it, it became even more accessible. If you need an image backbone, it's in timm.",
        "related_lists": ["awesome-computer-vision", "huggingface-transformers"],
        "list_type": "libraries",
        "audience_level": "intermediate",
        "use_cases": ["image classification", "feature extraction", "transfer learning backbones"],
        "has_website": True,
        "website_url": "https://huggingface.co/docs/timm",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Model List", "Training Scripts", "Results"],
        "getting_started": "Install with `pip install timm` and browse the model list to find the right accuracy/speed trade-off. Use `timm.create_model('model_name', pretrained=True)` to load any model. The `timm.data` module handles all augmentation and preprocessing consistently.",
        "suggested_projects": [
            "Run a systematic benchmark of different architectures (ResNet, EfficientNet, ConvNeXt, ViT) on your classification task to find the best accuracy/speed trade-off",
            "Build a feature extraction service that uses timm backbones to generate embeddings for image similarity search",
            "Train a custom image classifier using timm's training scripts with advanced augmentation (CutMix, MixUp, RandAugment)"
        ],
        "featured_example": {
            "name": "timm Results and Model List",
            "url": "https://github.com/huggingface/pytorch-image-models/blob/main/results/results-imagenet.csv",
            "why": "The comprehensive results CSV lets you compare 1000+ models on ImageNet with top-1/top-5 accuracy, parameters, and inference speed — essential for making informed architecture choices"
        }
    },
    {
        "id": "paddledetection",
        "name": "PaddleDetection",
        "github_url": "https://github.com/PaddlePaddle/PaddleDetection",
        "description": "PaddlePaddle's object detection and instance segmentation toolkit with production-ready models.",
        "maintainer": "PaddlePaddle",
        "category": "AI & Machine Learning",
        "subcategory": "Computer Vision",
        "tags": ["computer-vision", "object-detection", "paddlepaddle", "chinese-ai"],
        "entry_count_approx": "200+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Baidu's answer to Detectron2 and MMDetection — part of the PaddlePaddle ecosystem popular in China. Includes unique models like PP-YOLOE and PP-PicoDet optimized for both server and edge deployment. Valuable for understanding the Chinese AI ecosystem and accessing models not available elsewhere.",
        "related_lists": ["detectron2", "ultralytics"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["object detection", "instance segmentation", "edge deployment", "PaddlePaddle ecosystem"],
        "has_website": True,
        "website_url": "https://github.com/PaddlePaddle/PaddleDetection",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["detectron2", "ultralytics"],
        "best_sections": ["Model Zoo", "PP-YOLOE", "Deploy"],
        "getting_started": "Start with the Quick Start guide and try PP-YOLOE for detection or PP-PicoDet for mobile deployment. The Model Zoo includes detailed accuracy comparisons. Use `paddledet` CLI for training and evaluation.",
        "suggested_projects": [
            "Compare PP-YOLOE against YOLOv8 on a custom dataset to benchmark Paddle vs PyTorch ecosystems",
            "Deploy PP-PicoDet to a mobile device for real-time on-device object detection",
            "Build a multi-task vision system using PaddleDetection's detection and segmentation models together"
        ],
        "featured_example": {
            "name": "PP-YOLOE",
            "url": "https://github.com/PaddlePaddle/PaddleDetection/tree/release/2.7/configs/ppyoloe",
            "why": "PP-YOLOE achieves competitive accuracy with YOLO variants while being optimized for PaddlePaddle's deployment tools — it's the best entry point into the PaddlePaddle CV ecosystem"
        }
    },

    # ========================
    # Cloud & DevOps (~12 entries) — new subcategory under "Developer Tools & Coding"
    # ========================
    {
        "id": "awesome-aws",
        "name": "Awesome AWS",
        "github_url": "https://github.com/donnemartin/awesome-aws",
        "description": "A curated list of awesome AWS libraries, open-source repos, guides, and resources.",
        "maintainer": "donnemartin",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["aws", "cloud", "devops", "infrastructure"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "From the creator of system-design-primer — this is the most comprehensive AWS resource directory on GitHub. Organized by AWS service with icons, descriptions, and quality ratings. The 'Open Source Repos' section is the real gem — hundreds of tools you won't find in official docs.",
        "related_lists": ["system-design-primer", "awesome-scalability"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["finding AWS tools", "learning AWS services", "discovering open-source AWS projects"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Open Source Repos", "SDKs", "Command Line Tools"],
        "getting_started": "Browse by the AWS service you're using — each section has official resources, community guides, and open-source tools. The 'Open Source Repos' subsections are the most unique part — they list battle-tested community tools for each service.",
        "suggested_projects": [
            "Build a cost optimization dashboard using the AWS cost management tools listed here",
            "Set up a serverless application using the Lambda tools and frameworks from the Open Source Repos section",
            "Create an infrastructure-as-code template using the CloudFormation/Terraform resources cataloged here"
        ],
        "featured_example": {
            "name": "AWS CLI",
            "url": "https://aws.amazon.com/cli/",
            "why": "The AWS CLI is the gateway to every AWS service from the terminal — it's the first tool any AWS developer should master and the foundation for all automation"
        }
    },
    {
        "id": "devops-exercises",
        "name": "DevOps Exercises",
        "github_url": "https://github.com/bregman-arie/devops-exercises",
        "description": "Linux, Jenkins, AWS, SRE, Prometheus, Docker, Python, Ansible, Git, Kubernetes, Terraform exercises and interview questions.",
        "maintainer": "bregman-arie",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["devops", "interview", "exercises", "learning"],
        "entry_count_approx": "2500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The LeetCode of DevOps — 2500+ questions covering every topic a DevOps engineer needs to know. Questions range from basic to advanced, with answers included. Uniquely useful for both interview prep and identifying knowledge gaps in your DevOps skills.",
        "related_lists": ["system-design-primer", "developer-roadmap"],
        "list_type": "tutorials",
        "audience_level": "all",
        "use_cases": ["DevOps interview prep", "learning DevOps concepts", "identifying knowledge gaps"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["system-design-primer"],
        "best_sections": ["Linux", "Kubernetes", "AWS"],
        "getting_started": "Start with the topic you're weakest in — each section is self-contained. Try answering questions before looking at the solutions. The Linux and Networking sections are foundational — master those first before moving to cloud-specific topics.",
        "suggested_projects": [
            "Work through all the Kubernetes exercises and build a study guide summarizing key concepts you learned",
            "Create a DevOps knowledge assessment tool that quizzes team members using questions from this repo",
            "Build a hands-on lab environment (using Vagrant or Docker) that lets you practice the exercises interactively"
        ],
        "featured_example": {
            "name": "Kubernetes exercises",
            "url": "https://github.com/bregman-arie/devops-exercises/blob/master/topics/kubernetes/README.md",
            "why": "The Kubernetes section has 200+ questions from pod basics to CRDs — it's the most thorough K8s interview prep resource available for free"
        }
    },
    {
        "id": "awesome-sysadmin",
        "name": "Awesome Sysadmin",
        "github_url": "https://github.com/awesome-foss/awesome-sysadmin",
        "description": "A curated list of amazingly awesome open-source sysadmin resources.",
        "maintainer": "awesome-foss",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["sysadmin", "devops", "infrastructure", "open-source"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive directory of open-source sysadmin tools — from configuration management to monitoring to DNS. Maintained by the awesome-foss community with strict quality standards. Every tool listed has a brief description and license info, making it easy to evaluate options.",
        "related_lists": ["awesome-selfhosted", "the-book-of-secret-knowledge"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding sysadmin tools", "building infrastructure", "replacing proprietary tools with FOSS"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["the-book-of-secret-knowledge"],
        "best_sections": ["Monitoring", "Configuration Management", "DNS"],
        "getting_started": "Browse by the infrastructure category you need (monitoring, configuration management, backups, DNS). Each entry includes a brief description and license — focus on tools with active maintenance and a license compatible with your needs.",
        "suggested_projects": [
            "Set up a complete monitoring stack using tools from the Monitoring section (e.g., Prometheus + Grafana + Alertmanager)",
            "Build a self-hosted infrastructure dashboard that replaces 3-4 SaaS tools with open-source alternatives from this list",
            "Create an infrastructure-as-code setup using Ansible/Puppet entries to automate your server configuration"
        ],
        "featured_example": {
            "name": "Prometheus",
            "url": "https://prometheus.io",
            "why": "Prometheus is the CNCF-graduated monitoring standard — its pull-based model and powerful query language (PromQL) have become the lingua franca of modern infrastructure monitoring"
        }
    },
    {
        "id": "tools-of-the-trade",
        "name": "Tools of the Trade",
        "github_url": "https://github.com/cjbarber/ToolsOfTheTrade",
        "description": "Tools of the trade, from Hacker News — a curated directory of SaaS and developer tools.",
        "maintainer": "cjbarber",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["saas", "tools", "startups", "developer-tools"],
        "entry_count_approx": "400+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Born from a legendary Hacker News thread, this is the canonical directory of SaaS tools for dev teams and startups. Organized by function (identity, payments, email, etc.) with both free and paid options. The community commentary makes it more than just a list.",
        "related_lists": ["free-for-dev", "awesome-selfhosted"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding SaaS tools for startups", "evaluating developer tool options", "building a startup tech stack"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["free-for-dev"],
        "best_sections": ["Identity Verification", "Payments", "Email"],
        "getting_started": "Browse by the function you need (payments, email, analytics, etc.). Each category lists both established and emerging tools. Cross-reference with free-for-dev if you're bootstrapping on a budget.",
        "suggested_projects": [
            "Build a SaaS stack comparison tool that maps your requirements to recommended tools from this directory",
            "Create a startup tech stack template using the most recommended tools from each category",
            "Develop a cost calculator that estimates monthly expenses based on your chosen tools from this list"
        ],
        "featured_example": {
            "name": "Stripe",
            "url": "https://stripe.com",
            "why": "Stripe appears in nearly every HN discussion about payment tools — its developer experience set the standard for what API design should look like"
        }
    },
    {
        "id": "free-for-dev",
        "name": "Free for Dev",
        "github_url": "https://github.com/ripienaar/free-for-dev",
        "description": "A list of SaaS, PaaS, and IaaS offerings that have free tiers of interest to devops and infradev.",
        "maintainer": "ripienaar",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["free-tier", "saas", "devops", "startups"],
        "entry_count_approx": "1500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The ultimate directory of free-tier developer services — over 1500 entries across every category imaginable. Actively maintained with strict criteria (services must have permanent free tiers, not just trials). Essential for bootstrapping projects without spending money.",
        "related_lists": ["tools-of-the-trade", "awesome-selfhosted"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding free developer tools", "bootstrapping projects", "reducing infrastructure costs"],
        "has_website": True,
        "website_url": "https://free-for.dev",
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["tools-of-the-trade"],
        "best_sections": ["Major Cloud Providers", "CI/CD", "APIs and Data"],
        "getting_started": "Use the companion website (free-for.dev) for easier browsing, or search the README by category. Each entry lists the specific free tier limits. Start with 'Major Cloud Providers' for compute, then 'CI/CD' and 'APIs' for the rest of your stack.",
        "suggested_projects": [
            "Build and deploy a complete web application using only free-tier services — document the full stack and estimated savings",
            "Create a free-tier monitoring dashboard that tracks usage across all your free-tier services to avoid surprise charges",
            "Develop a 'free stack generator' that recommends a complete infrastructure from free-tier services based on your project type"
        ],
        "featured_example": {
            "name": "free-for.dev website",
            "url": "https://free-for.dev",
            "why": "The companion website makes the 1500+ entries searchable and browsable with filters — far easier than scrolling the massive README"
        }
    },
    {
        "id": "infracost",
        "name": "Infracost",
        "github_url": "https://github.com/infracost/infracost",
        "description": "Cloud cost estimates for Terraform in pull requests — see the cost impact before deploying.",
        "maintainer": "infracost",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["cloud", "cost-management", "terraform", "finops"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Solves the 'surprise cloud bill' problem by showing cost diffs in pull requests. Integrates with Terraform/OpenTofu and supports AWS, GCP, and Azure. The GitHub Actions integration means every infrastructure PR automatically shows its cost impact — a game-changer for FinOps.",
        "related_lists": ["awesome-aws", "awesome-sysadmin"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["cloud cost estimation", "FinOps automation", "infrastructure PR reviews"],
        "has_website": True,
        "website_url": "https://www.infracost.io",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Getting Started", "CI/CD Integration", "Supported Resources"],
        "getting_started": "Install the CLI and run `infracost breakdown --path .` in any Terraform directory to see cost estimates. Then set up the GitHub Actions integration to automatically comment cost diffs on infrastructure PRs.",
        "suggested_projects": [
            "Set up Infracost in your CI pipeline and create a monthly cost trend dashboard from the data",
            "Build a cost comparison tool that evaluates different Terraform architectures (e.g., EC2 vs Fargate) using Infracost diffs",
            "Create a FinOps policy engine that automatically flags PRs exceeding cost thresholds"
        ],
        "featured_example": {
            "name": "GitHub Actions integration",
            "url": "https://www.infracost.io/docs/integrations/cicd/",
            "why": "The CI/CD integration is where Infracost shines — it automatically posts cost diff comments on Terraform PRs, making cost a first-class review criteria"
        }
    },
    {
        "id": "grafana",
        "name": "Grafana",
        "github_url": "https://github.com/grafana/grafana",
        "description": "The open-source platform for monitoring and observability — visualize metrics, logs, and traces from any data source.",
        "maintainer": "grafana",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["monitoring", "observability", "dashboards", "devops"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The visualization layer of modern observability. Grafana connects to Prometheus, Elasticsearch, CloudWatch, and 100+ other data sources, unifying them in one dashboard. Its plugin ecosystem and community dashboard library mean you rarely start from scratch.",
        "related_lists": ["prometheus", "awesome-sysadmin"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["infrastructure monitoring", "application observability", "business metrics dashboards"],
        "has_website": True,
        "website_url": "https://grafana.com",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Data Sources", "Dashboards", "Alerting"],
        "getting_started": "Deploy with Docker (`docker run -p 3000:3000 grafana/grafana`), connect a Prometheus data source, then import a community dashboard from grafana.com/dashboards. The 'Getting Started' guide covers basic panels and queries in under 30 minutes.",
        "suggested_projects": [
            "Build a comprehensive infrastructure monitoring dashboard connecting Prometheus, Loki, and Tempo in a single Grafana instance",
            "Create an application SLO dashboard that tracks latency, error rate, and throughput with alerting on SLO violations",
            "Develop a multi-tenant dashboard system using Grafana's provisioning and organizations features"
        ],
        "featured_example": {
            "name": "Grafana Community Dashboards",
            "url": "https://grafana.com/grafana/dashboards/",
            "why": "The community dashboard library has 5000+ pre-built dashboards — instead of building from scratch, import one and customize it"
        }
    },
    {
        "id": "prometheus",
        "name": "Prometheus",
        "github_url": "https://github.com/prometheus/prometheus",
        "description": "The open-source systems monitoring and alerting toolkit, graduated from CNCF.",
        "maintainer": "prometheus",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["monitoring", "alerting", "metrics", "cncf", "devops"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The de facto standard for metrics collection in cloud-native environments. Its pull-based model, powerful PromQL query language, and massive exporter ecosystem make it the monitoring foundation for Kubernetes and beyond. CNCF-graduated and battle-tested at massive scale.",
        "related_lists": ["grafana", "awesome-sysadmin"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["infrastructure monitoring", "alerting", "metrics collection", "Kubernetes monitoring"],
        "has_website": True,
        "website_url": "https://prometheus.io",
        "is_awesome_verified": False,
        "language_focus": "go",
        "overlaps_with": [],
        "best_sections": ["Getting Started", "Exporters", "PromQL"],
        "getting_started": "Start with the 'Getting Started' guide to run Prometheus locally and scrape its own metrics. Learn PromQL basics (rate, sum, histogram_quantile) — it's the key to using Prometheus effectively. Then add exporters for your services (node_exporter for Linux, cAdvisor for containers).",
        "suggested_projects": [
            "Set up Prometheus monitoring for a Kubernetes cluster with node-exporter, kube-state-metrics, and custom service metrics",
            "Build a comprehensive alerting system using Prometheus Alertmanager with escalation policies and Slack/PagerDuty integration",
            "Create custom Prometheus exporters for your application services and build PromQL dashboards for key SLIs"
        ],
        "featured_example": {
            "name": "PromQL documentation",
            "url": "https://prometheus.io/docs/prometheus/latest/querying/basics/",
            "why": "PromQL is what makes Prometheus powerful — learning its operators and functions is more valuable than learning any specific exporter"
        }
    },
    {
        "id": "agile-sre",
        "name": "Agile SRE",
        "github_url": "https://github.com/dastergon/awesome-sre",
        "description": "A curated list of Site Reliability and Production Engineering resources.",
        "maintainer": "dastergon",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["sre", "reliability", "devops", "production-engineering"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive SRE resource directory — covers everything from Google's original SRE book concepts to modern platform engineering practices. Well-organized by topic (on-call, incident response, capacity planning) with both foundational readings and practical tools.",
        "related_lists": ["system-design-primer", "awesome-scalability"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["learning SRE practices", "building reliability culture", "finding SRE tools and processes"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-scalability"],
        "best_sections": ["On-Call", "Incident Response", "Monitoring"],
        "getting_started": "Start with the foundational readings in the 'Culture' section, then move to 'Monitoring' and 'On-Call' for practical implementation. The 'Post-Mortems' section is uniquely educational — learn from real incidents at major companies.",
        "suggested_projects": [
            "Implement an SLO-based alerting system for your services using the SLO/SLI frameworks described here",
            "Build an incident management workflow incorporating blameless post-mortems using the templates and processes listed",
            "Create a chaos engineering practice using the tools from the Reliability Testing section"
        ],
        "featured_example": {
            "name": "Google SRE Book",
            "url": "https://sre.google/sre-book/table-of-contents/",
            "why": "The free online SRE book from Google defined the entire discipline — every SRE practice traces back to the principles laid out here"
        }
    },
    {
        "id": "awesome-terraform",
        "name": "Awesome Terraform",
        "github_url": "https://github.com/shuaibiyy/awesome-terraform",
        "description": "A curated list of resources on HashiCorp's Terraform and OpenTofu.",
        "maintainer": "shuaibiyy",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["terraform", "iac", "infrastructure", "devops"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Terraform is the lingua franca of infrastructure-as-code, and this list catalogs the ecosystem around it — modules, providers, tools, and learning resources. Updated post-OpenTofu fork to include both ecosystems. The 'Tools' section has utilities that should be in every Terraform workflow.",
        "related_lists": ["awesome-aws", "infracost"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["finding Terraform modules", "learning IaC best practices", "improving Terraform workflows"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Tools", "Modules", "Tutorials"],
        "getting_started": "Start with the 'Tutorials' section if new to Terraform. For practitioners, jump to 'Tools' — utilities like tflint, checkov, and infracost should be in every Terraform pipeline. Browse 'Modules' to find pre-built infrastructure patterns for your cloud provider.",
        "suggested_projects": [
            "Set up a Terraform CI/CD pipeline with linting (tflint), security scanning (checkov), cost estimation (infracost), and automated plan/apply",
            "Build a reusable Terraform module for your most common infrastructure pattern and publish it to the registry",
            "Create a multi-environment infrastructure setup (dev/staging/prod) using Terraform workspaces and modules from this list"
        ],
        "featured_example": {
            "name": "Terraform Best Practices",
            "url": "https://www.terraform-best-practices.com",
            "why": "The best practices guide covers the structural and organizational patterns that separate professional Terraform code from spaghetti — essential reading before your IaC grows complex"
        }
    },
    {
        "id": "awesome-cloudformation",
        "name": "Awesome CloudFormation",
        "github_url": "https://github.com/aws-cloudformation/awesome-cloudformation",
        "description": "A curated list of resources and projects for AWS CloudFormation.",
        "maintainer": "aws-cloudformation",
        "category": "Developer Tools & Coding",
        "subcategory": "Cloud & DevOps",
        "tags": ["aws", "cloudformation", "iac", "infrastructure"],
        "entry_count_approx": "100+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Official AWS-maintained CloudFormation resource directory — uniquely authoritative since it comes from the CloudFormation team itself. Covers templates, tools, blog posts, and custom resource examples. Essential if you're deep in the AWS ecosystem and using native IaC.",
        "related_lists": ["awesome-aws", "awesome-terraform"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["AWS infrastructure-as-code", "finding CloudFormation templates", "learning CloudFormation patterns"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-aws"],
        "best_sections": ["Tools", "Templates", "Blog Posts & Talks"],
        "getting_started": "Start with the 'Blog Posts & Talks' section for conceptual understanding, then browse 'Templates' for ready-to-use patterns. The 'Tools' section lists utilities that make CloudFormation less painful — cfn-lint and rain are particularly useful.",
        "suggested_projects": [
            "Build a complete serverless application stack using CloudFormation templates from this collection",
            "Create a CloudFormation template library for your organization's common infrastructure patterns",
            "Set up a CloudFormation CI/CD pipeline with cfn-lint validation and stack review before deployment"
        ],
        "featured_example": {
            "name": "cfn-lint",
            "url": "https://github.com/aws-cloudformation/cfn-lint",
            "why": "cfn-lint catches CloudFormation errors before deployment — it validates templates against the complete resource specification, saving hours of debugging failed stack updates"
        }
    },

    # ========================
    # Security & Privacy (~8 entries) — new subcategory
    # ========================
    {
        "id": "awesome-security",
        "name": "Awesome Security",
        "github_url": "https://github.com/sbilly/awesome-security",
        "description": "A collection of awesome software, libraries, documents, books, resources and cool stuff about security.",
        "maintainer": "sbilly",
        "category": "Security & Privacy",
        "subcategory": "General Security",
        "tags": ["security", "infosec", "tools", "curated-list"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The broadest security awesome list — covers network security, web security, cryptography, reverse engineering, and more. Well-organized with clear categories and brief descriptions for each tool. The breadth makes it the best starting point for security professionals and developers alike.",
        "related_lists": ["awesome-hacking", "awesome-appsec", "the-book-of-secret-knowledge"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding security tools", "learning security concepts", "building security toolkits"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["the-book-of-secret-knowledge", "awesome-hacking"],
        "best_sections": ["Network", "Web", "Threat Intelligence"],
        "getting_started": "Start with the area matching your focus — 'Web' for application security, 'Network' for infrastructure, 'Operating System' for hardening. Each section lists tools from scanning to monitoring to response.",
        "suggested_projects": [
            "Build a personal security lab using tools from the Network and Web sections to practice vulnerability scanning and remediation",
            "Set up an automated security scanning pipeline using the CI/CD-compatible tools listed here",
            "Create a threat intelligence aggregation dashboard using the feeds and tools from the Threat Intelligence section"
        ],
        "featured_example": {
            "name": "OWASP ZAP",
            "url": "https://www.zaproxy.org/",
            "why": "ZAP is the most widely-used free web application security scanner — it integrates into CI/CD pipelines and makes security testing accessible to developers, not just security specialists"
        }
    },
    {
        "id": "awesome-hacking",
        "name": "Awesome Hacking",
        "github_url": "https://github.com/carpedm20/awesome-hacking",
        "description": "A curated list of awesome hacking tutorials, tools, and resources for security researchers and ethical hackers.",
        "maintainer": "carpedm20",
        "category": "Security & Privacy",
        "subcategory": "Ethical Hacking",
        "tags": ["hacking", "security", "ctf", "pentesting"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most popular hacking resource list on GitHub — covers CTF platforms, bug bounty resources, reverse engineering tools, and exploit development. Well-curated with a focus on educational and ethical hacking resources. Great for anyone wanting to understand offensive security.",
        "related_lists": ["awesome-security", "awesome-pentest", "payloads-all-the-things"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["learning ethical hacking", "CTF competition prep", "understanding offensive security"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-security", "awesome-pentest"],
        "best_sections": ["CTF", "Tutorials", "Tools"],
        "getting_started": "If you're new to hacking, start with the 'Tutorials' section and work through a CTF platform (TryHackMe, HackTheBox). For experienced practitioners, the 'Tools' section organized by technique (web, binary, crypto) is the fastest way to find what you need.",
        "suggested_projects": [
            "Work through the CTF resources and build a writeup blog documenting your solutions and techniques learned",
            "Set up a home lab with vulnerable VMs from the listed platforms and practice the attack techniques systematically",
            "Build a custom CTF challenge using the tools and frameworks referenced here for your team or community"
        ],
        "featured_example": {
            "name": "CTFtime",
            "url": "https://ctftime.org",
            "why": "CTFtime is the central hub for competitive CTF events — it tracks upcoming competitions, team rankings, and writeups from past events, making it the best way to start participating in the CTF community"
        }
    },
    {
        "id": "awesome-appsec",
        "name": "Awesome AppSec",
        "github_url": "https://github.com/paragonie/awesome-appsec",
        "description": "A curated list of resources for learning about application security.",
        "maintainer": "paragonie",
        "category": "Security & Privacy",
        "subcategory": "Application Security",
        "tags": ["appsec", "security", "web-security", "development"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Maintained by Paragonie (known for libsodium and security consulting), this list focuses specifically on application-level security — what developers need to know. Covers common vulnerabilities, secure coding practices, and security testing. More developer-friendly than pen-testing focused lists.",
        "related_lists": ["awesome-security", "owasp-cheatsheet"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["secure development practices", "understanding common vulnerabilities", "application security testing"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["owasp-cheatsheet"],
        "best_sections": ["General", "PHP", "Python"],
        "getting_started": "Start with the 'General' section for cross-language security principles, then navigate to your primary language for specific secure coding guides. The articles are ordered from foundational to advanced within each section.",
        "suggested_projects": [
            "Audit an existing application against the OWASP Top 10 using the testing tools and checklists referenced here",
            "Build a secure authentication system from scratch following the secure coding guidelines for your language",
            "Create a security review checklist for your team's code reviews based on the vulnerability categories covered"
        ],
        "featured_example": {
            "name": "OWASP Top 10",
            "url": "https://owasp.org/www-project-top-ten/",
            "why": "The OWASP Top 10 is the single most important document in application security — every developer should understand these vulnerability categories"
        }
    },
    {
        "id": "payloads-all-the-things",
        "name": "PayloadsAllTheThings",
        "github_url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
        "description": "A list of useful payloads and bypass techniques for web application security and penetration testing.",
        "maintainer": "swisskyrepo",
        "category": "Security & Privacy",
        "subcategory": "Penetration Testing",
        "tags": ["security", "payloads", "pentesting", "web-security"],
        "entry_count_approx": "1000+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive payload reference for web application security testing. Organized by vulnerability type (SQLi, XSS, SSRF, etc.) with real-world bypass techniques and methodology. Used by penetration testers worldwide as their primary reference during engagements.",
        "related_lists": ["awesome-hacking", "awesome-pentest"],
        "list_type": "tools",
        "audience_level": "advanced",
        "use_cases": ["penetration testing", "web security testing", "learning exploit techniques"],
        "has_website": True,
        "website_url": "https://swisskyrepo.github.io/PayloadsAllTheThings/",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-hacking"],
        "best_sections": ["SQL Injection", "XSS Injection", "Server Side Request Forgery"],
        "getting_started": "Navigate by vulnerability type — each page covers the theory, detection methods, exploitation techniques, and specific payloads with bypass variants. The 'Methodology and Resources' section provides structured approaches for security assessments.",
        "suggested_projects": [
            "Build a web application security scanner that tests for the vulnerability categories documented here",
            "Create a secure coding training module for developers that uses these payloads as examples of what to defend against",
            "Set up a vulnerable web application lab and practice the documented techniques in a safe environment"
        ],
        "featured_example": {
            "name": "SQL Injection methodology",
            "url": "https://swisskyrepo.github.io/PayloadsAllTheThings/SQL%20Injection/",
            "why": "The SQL injection section covers every database engine with bypass techniques for WAFs, parameterized queries, and error-based/blind/union variants — it's the most complete free SQLi reference"
        }
    },
    {
        "id": "awesome-pentest",
        "name": "Awesome Penetration Testing",
        "github_url": "https://github.com/enaqx/awesome-pentest",
        "description": "A collection of awesome penetration testing and offensive cybersecurity resources.",
        "maintainer": "enaqx",
        "category": "Security & Privacy",
        "subcategory": "Penetration Testing",
        "tags": ["pentesting", "security", "tools", "offensive-security"],
        "entry_count_approx": "400+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive penetration testing tool directory — organized by attack phase (recon, exploitation, post-exploitation, reporting). Each tool includes a brief description. The structured approach makes it useful both as a learning resource and as a reference during actual engagements.",
        "related_lists": ["awesome-hacking", "awesome-security", "payloads-all-the-things"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding pentesting tools", "structuring security assessments", "learning offensive security"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-hacking"],
        "best_sections": ["Online Resources", "Tools", "Vulnerability Databases"],
        "getting_started": "Follow the natural assessment flow — start with 'Reconnaissance Tools', then 'Vulnerability Analysis', 'Exploitation Tools', and 'Post-Exploitation'. This mirrors a real penetration test workflow and helps you learn methodology alongside tools.",
        "suggested_projects": [
            "Build a penetration testing toolkit installer that sets up your essential tools from this list in a fresh VM",
            "Create a methodology-driven assessment checklist that maps each engagement phase to specific tools from this list",
            "Develop an automated reconnaissance pipeline using the OSINT and scanning tools cataloged here"
        ],
        "featured_example": {
            "name": "Metasploit Framework",
            "url": "https://www.metasploit.com",
            "why": "Metasploit is the most widely-used penetration testing framework — it provides exploit modules, payloads, and post-exploitation tools in one integrated platform"
        }
    },
    {
        "id": "owasp-cheatsheet",
        "name": "OWASP Cheat Sheet Series",
        "github_url": "https://github.com/OWASP/CheatSheetSeries",
        "description": "The OWASP Cheat Sheet Series — concise, high-value application security guidance for developers and defenders.",
        "maintainer": "OWASP",
        "category": "Security & Privacy",
        "subcategory": "Application Security",
        "tags": ["security", "owasp", "best-practices", "development"],
        "entry_count_approx": "80+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most practical security reference for developers — 80+ cheat sheets covering authentication, session management, input validation, cryptography, and more. Each cheat sheet is concise, actionable, and peer-reviewed by OWASP security experts. Should be mandatory reading for every web developer.",
        "related_lists": ["awesome-appsec", "awesome-security"],
        "list_type": "tutorials",
        "audience_level": "all",
        "use_cases": ["secure coding reference", "security review checklists", "developer security training"],
        "has_website": True,
        "website_url": "https://cheatsheetseries.owasp.org",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-appsec"],
        "best_sections": ["Authentication", "Session Management", "Input Validation"],
        "getting_started": "Start with the 'Authentication Cheat Sheet' and 'Session Management Cheat Sheet' — these cover the most critical and commonly misimplemented security areas. Then reference specific sheets as you implement features (e.g., 'File Upload' before building upload functionality).",
        "suggested_projects": [
            "Implement authentication for a web app using the Authentication and Session Management cheat sheets as your specification",
            "Build a security linting tool that checks code against common mistakes described in the cheat sheets",
            "Create a developer onboarding security training program using the cheat sheets as the curriculum"
        ],
        "featured_example": {
            "name": "Authentication Cheat Sheet",
            "url": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
            "why": "The Authentication Cheat Sheet covers everything from password storage to multi-factor auth with clear do's and don'ts — implement auth by following this sheet and you'll avoid 90% of common mistakes"
        }
    },
    {
        "id": "prowler",
        "name": "Prowler",
        "github_url": "https://github.com/prowler-cloud/prowler",
        "description": "Open-source security tool for AWS, GCP, and Azure — performs security assessments, audits, and compliance checks.",
        "maintainer": "prowler-cloud",
        "category": "Security & Privacy",
        "subcategory": "Cloud Security",
        "tags": ["security", "aws", "cloud", "compliance", "auditing"],
        "entry_count_approx": "300+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The most popular open-source cloud security scanner — supports 300+ checks across AWS, GCP, and Azure covering CIS, PCI-DSS, HIPAA, and GDPR compliance frameworks. The CLI makes it easy to integrate into CI/CD pipelines. Essential for any team running cloud infrastructure.",
        "related_lists": ["awesome-security", "awesome-aws"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["cloud security assessment", "compliance auditing", "continuous security monitoring"],
        "has_website": True,
        "website_url": "https://prowler.com",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Getting Started", "Checks", "Compliance"],
        "getting_started": "Install with `pip install prowler` and run `prowler aws` to scan your AWS account. Results include severity levels and remediation guidance. Start with the CIS benchmark checks and expand to compliance frameworks relevant to your organization.",
        "suggested_projects": [
            "Set up Prowler in your CI/CD pipeline to run security checks before infrastructure deployments",
            "Build a multi-account security dashboard that aggregates Prowler results across all your cloud accounts",
            "Create a compliance tracking system that monitors Prowler check results over time and alerts on regressions"
        ],
        "featured_example": {
            "name": "CIS Benchmark checks",
            "url": "https://docs.prowler.com/projects/prowler-open-source/en/latest/",
            "why": "The CIS benchmark checks are the gold standard for cloud security posture — Prowler implements them all with clear remediation steps for each finding"
        }
    },
    {
        "id": "awesome-hacking-resources",
        "name": "Awesome Hacking Resources",
        "github_url": "https://github.com/vitalysim/Awesome-Hacking-Resources",
        "description": "A collection of hacking and penetration testing resources to help you on your journey to becoming an ethical hacker.",
        "maintainer": "vitalysim",
        "category": "Security & Privacy",
        "subcategory": "Ethical Hacking",
        "tags": ["hacking", "learning", "security", "resources"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "More learning-focused than awesome-hacking — organized as a study path for aspiring ethical hackers. Includes books, courses, YouTube channels, and practice platforms. The learning path structure makes it uniquely useful for beginners who don't know where to start.",
        "related_lists": ["awesome-hacking", "awesome-pentest"],
        "list_type": "tutorials",
        "audience_level": "beginner",
        "use_cases": ["learning ethical hacking", "finding security courses", "building a study path"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-hacking"],
        "best_sections": ["Getting Started", "YouTube Channels", "Books"],
        "getting_started": "Follow the 'Getting Started' section sequentially — it's designed as a learning path. Start with the recommended YouTube channels for visual learning, then move to practice platforms (TryHackMe, HackTheBox) for hands-on experience.",
        "suggested_projects": [
            "Work through the complete learning path and document your progress in a blog",
            "Build a curated study plan for a specific certification (CEH, OSCP) using resources from this list",
            "Create a mentorship curriculum for teaching ethical hacking to beginners using the structured resources here"
        ],
        "featured_example": {
            "name": "TryHackMe",
            "url": "https://tryhackme.com",
            "why": "TryHackMe offers guided, gamified hacking challenges that are perfect for beginners — the learning paths take you from zero to competent ethical hacker with hands-on practice"
        }
    },

    # ========================
    # APIs & Integration (~8 entries) — new subcategory
    # ========================
    {
        "id": "public-apis",
        "name": "Public APIs",
        "github_url": "https://github.com/public-apis/public-apis",
        "description": "A collective list of free APIs for use in software and web development.",
        "maintainer": "public-apis",
        "category": "APIs & Integration",
        "subcategory": "API Directories",
        "tags": ["apis", "free", "directory", "web-development"],
        "entry_count_approx": "1400+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The single most starred repository dedicated to listing free APIs — 300k+ stars and 1400+ APIs organized by category. Every entry includes auth type (apiKey, OAuth, None), HTTPS support, and CORS status. The de facto starting point when you need a free API for any purpose.",
        "related_lists": ["public-apis-n0shake", "awesome-json-datasets"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding free APIs", "building side projects", "prototyping applications", "hackathon resources"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["public-apis-n0shake", "awesome-json-datasets"],
        "best_sections": ["Development", "Finance", "Weather"],
        "getting_started": "Browse by category to find APIs matching your project. The table columns (Auth, HTTPS, CORS) are critical for choosing — filter for 'No' auth and 'Yes' CORS if you're building a frontend-only app. The Development and Data categories have the most versatile APIs.",
        "suggested_projects": [
            "Build a multi-API mashup dashboard that combines weather, news, and finance APIs into a personalized daily briefing",
            "Create an API health monitor that tracks uptime and response times for your favorite APIs from this list",
            "Develop a 'random project generator' that picks 2-3 random APIs and suggests a project idea combining them"
        ],
        "featured_example": {
            "name": "OpenWeatherMap",
            "url": "https://openweathermap.org/api",
            "why": "OpenWeatherMap's free tier is generous enough for real projects and the API is extremely well-documented — it's the API most developers use for their first API integration project"
        }
    },
    {
        "id": "public-apis-n0shake",
        "name": "Public APIs (n0shake)",
        "github_url": "https://github.com/n0shake/Public-APIs",
        "description": "A public list of APIs from around the web, organized by category with quality ratings.",
        "maintainer": "n0shake",
        "category": "APIs & Integration",
        "subcategory": "API Directories",
        "tags": ["apis", "directory", "web-development"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "A more curated alternative to the massive public-apis list — smaller but with quality ratings and brief descriptions. The focus on APIs with good documentation and reliability makes it better for production use rather than just prototyping.",
        "related_lists": ["public-apis"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding well-documented APIs", "building production integrations", "API discovery"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["public-apis"],
        "best_sections": ["Maps", "Music", "Sports"],
        "getting_started": "Browse by interest area — the descriptions are more detailed than in the larger public-apis list. Use this when you want quality over quantity and need APIs reliable enough for production applications.",
        "suggested_projects": [
            "Build a location-based application combining Maps and Weather APIs from this curated selection",
            "Create a sports data dashboard using the rated APIs from the Sports section",
            "Develop an API comparison tool that benchmarks similar APIs (e.g., multiple weather APIs) on reliability and data quality"
        ],
        "featured_example": {
            "name": "Spotify Web API",
            "url": "https://developer.spotify.com/documentation/web-api/",
            "why": "Spotify's API is one of the best-designed public APIs — rich data, excellent docs, and generous rate limits make it perfect for building music-related applications"
        }
    },
    {
        "id": "microsoft-api-guidelines",
        "name": "Microsoft REST API Guidelines",
        "github_url": "https://github.com/microsoft/api-guidelines",
        "description": "Microsoft's guidelines for designing RESTful APIs, used across Azure and Microsoft services.",
        "maintainer": "microsoft",
        "category": "APIs & Integration",
        "subcategory": "API Design",
        "tags": ["api-design", "rest", "guidelines", "best-practices"],
        "entry_count_approx": "30+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive publicly available REST API design guide from a major tech company. Covers naming conventions, versioning, error handling, pagination, and long-running operations. Battle-tested across Azure's hundreds of services. Essential reference for anyone designing production APIs.",
        "related_lists": ["public-apis", "openapi-directory"],
        "list_type": "tutorials",
        "audience_level": "intermediate",
        "use_cases": ["API design standards", "REST best practices", "organizational API governance"],
        "has_website": True,
        "website_url": "https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Naming", "Versioning", "Error Handling"],
        "getting_started": "Read the top-level guidelines document first for principles, then dive into specific sections as you design your API. The 'Naming' and 'Error Handling' sections address the most common API design mistakes.",
        "suggested_projects": [
            "Design a REST API following these guidelines end-to-end, documenting each design decision with references to the relevant guideline section",
            "Build an API linting tool that checks OpenAPI specs against Microsoft's guidelines",
            "Create an API design review checklist for your team based on these guidelines"
        ],
        "featured_example": {
            "name": "Error handling guidelines",
            "url": "https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md#handling-errors",
            "why": "The error handling section provides a structured error response format that's become an industry standard — adopt it and your API consumers will thank you"
        }
    },
    {
        "id": "spectral",
        "name": "Spectral",
        "github_url": "https://github.com/stoplightio/spectral",
        "description": "A flexible JSON/YAML linter with out-of-the-box support for OpenAPI v2 & v3, and AsyncAPI.",
        "maintainer": "stoplightio",
        "category": "APIs & Integration",
        "subcategory": "API Tooling",
        "tags": ["api", "linting", "openapi", "developer-tools"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The ESLint of API specifications — enforces consistent API design through configurable rules. Supports OpenAPI, AsyncAPI, and custom rulesets. Integrating Spectral into your CI pipeline catches API design issues before they reach consumers. The custom ruleset feature lets organizations encode their API standards.",
        "related_lists": ["openapi-directory", "microsoft-api-guidelines"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["API spec linting", "enforcing API standards", "CI/CD API validation"],
        "has_website": True,
        "website_url": "https://stoplight.io/open-source/spectral",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Getting Started", "Custom Rulesets", "CI Integration"],
        "getting_started": "Install with `npm install -g @stoplight/spectral-cli` and lint an OpenAPI spec with `spectral lint api.yaml`. The built-in OpenAPI rules catch common issues immediately. Create a custom ruleset to enforce your organization's API standards.",
        "suggested_projects": [
            "Create a custom Spectral ruleset that encodes your organization's API design guidelines and integrate it into CI",
            "Build an API quality scoring system that runs Spectral on all your OpenAPI specs and tracks improvement over time",
            "Develop a pre-commit hook that lints API specs before they're committed using Spectral"
        ],
        "featured_example": {
            "name": "Built-in OpenAPI ruleset",
            "url": "https://docs.stoplight.io/docs/spectral/4dec24461f3af-open-api-rules",
            "why": "The built-in OpenAPI rules catch 25+ common API design mistakes out of the box — add Spectral to your project and instantly improve API consistency"
        }
    },
    {
        "id": "openapi-directory",
        "name": "OpenAPI Directory",
        "github_url": "https://github.com/APIs-guru/openapi-directory",
        "description": "The world's largest machine-readable API directory — Wikipedia for Web APIs in OpenAPI format.",
        "maintainer": "APIs-guru",
        "category": "APIs & Integration",
        "subcategory": "API Directories",
        "tags": ["openapi", "api-specs", "directory", "machine-readable"],
        "entry_count_approx": "2500+",
        "format": "json",
        "has_contributions_guide": True,
        "editorial_notes": "Unlike public-apis which lists URLs, this provides actual machine-readable OpenAPI specifications for 2500+ APIs. This means you can auto-generate client SDKs, build API explorers, or compare API designs programmatically. Invaluable for API tooling developers.",
        "related_lists": ["public-apis", "spectral"],
        "list_type": "datasets",
        "audience_level": "intermediate",
        "use_cases": ["auto-generating API clients", "API design research", "building API tooling"],
        "has_website": True,
        "website_url": "https://apis.guru",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["public-apis"],
        "best_sections": ["APIs", "Fixup Scripts", "Contribution Guide"],
        "getting_started": "Browse the API directory at apis.guru to find specs visually, or clone the repo and use the JSON index to programmatically access any spec. Use the specs with code generators (openapi-generator, swagger-codegen) to auto-generate client libraries.",
        "suggested_projects": [
            "Build an API client generator that takes an OpenAPI spec from this directory and produces a typed SDK in your language",
            "Create an API design analytics tool that analyzes patterns across 2500+ specs (naming conventions, error formats, auth methods)",
            "Develop an API compatibility checker that detects breaking changes between spec versions"
        ],
        "featured_example": {
            "name": "APIs.guru Explorer",
            "url": "https://apis.guru",
            "why": "The web explorer lets you browse and try 2500+ APIs interactively — it's the fastest way to discover and evaluate APIs you didn't know existed"
        }
    },
    {
        "id": "awesome-api-devtools",
        "name": "Awesome API DevTools",
        "github_url": "https://github.com/yosriady/api-development-tools",
        "description": "A collection of useful resources for building RESTful HTTP+JSON APIs.",
        "maintainer": "yosriady",
        "category": "APIs & Integration",
        "subcategory": "API Tooling",
        "tags": ["api", "rest", "tools", "developer-tools"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive list of API development tools — covers the entire API lifecycle from design (Swagger, RAML) to testing (Postman, Insomnia) to documentation (Slate, Redoc) to monitoring. Organized by development stage, making it natural to find what you need.",
        "related_lists": ["spectral", "microsoft-api-guidelines"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding API development tools", "building API workflows", "improving API quality"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Design", "Testing", "Documentation"],
        "getting_started": "Navigate by the API development phase you need — Design for spec-first tools, Testing for validation, Documentation for generating docs. Most teams need at least one tool from each category for a complete API workflow.",
        "suggested_projects": [
            "Set up a complete API development workflow using one tool from each category (design, mock, test, document, monitor)",
            "Build an API documentation portal using the documentation generators listed here with auto-generated content from your OpenAPI spec",
            "Create an API testing pipeline that combines contract testing, integration testing, and performance testing tools from this list"
        ],
        "featured_example": {
            "name": "Insomnia",
            "url": "https://insomnia.rest",
            "why": "Insomnia is the best open-source API client — it combines request building, environment management, and OpenAPI spec integration in a clean, fast interface"
        }
    },
    {
        "id": "awesome-graphql",
        "name": "Awesome GraphQL",
        "github_url": "https://github.com/chentsulin/awesome-graphql",
        "description": "An awesome list of GraphQL resources — libraries, tools, services, and tutorials for all platforms.",
        "maintainer": "chentsulin",
        "category": "APIs & Integration",
        "subcategory": "API Frameworks",
        "tags": ["graphql", "api", "tools", "libraries"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive GraphQL ecosystem directory — covers servers, clients, tools, and services across every language. The sheer breadth is impressive, from Apollo to Relay to Hasura. The 'Tools' section alone lists 100+ utilities for schema management, code generation, and testing.",
        "related_lists": ["awesome-api-devtools", "awesome-javascript"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["finding GraphQL tools", "learning GraphQL", "building GraphQL APIs"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Libraries", "Tools", "Services"],
        "getting_started": "Start with the 'Tutorials' section if new to GraphQL. For implementation, browse 'Libraries' by your server language (Node.js, Python, Go) and 'Clients' by your frontend framework (React, Vue). The 'Tools' section has essential utilities for any GraphQL project.",
        "suggested_projects": [
            "Build a full-stack GraphQL application using a server and client library from this list with real-time subscriptions",
            "Create a GraphQL gateway that federates multiple REST APIs into a single GraphQL schema",
            "Develop a schema-first workflow using code generation tools from the Tools section"
        ],
        "featured_example": {
            "name": "Apollo GraphQL",
            "url": "https://www.apollographql.com",
            "why": "Apollo is the most complete GraphQL platform — from client-side caching to federation for microservices, it defines how most teams implement GraphQL in production"
        }
    },
    {
        "id": "awesome-grpc",
        "name": "Awesome gRPC",
        "github_url": "https://github.com/grpc-ecosystem/awesome-grpc",
        "description": "A curated list of useful resources for gRPC.",
        "maintainer": "grpc-ecosystem",
        "category": "APIs & Integration",
        "subcategory": "API Frameworks",
        "tags": ["grpc", "api", "microservices", "protobuf"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The official gRPC ecosystem list — maintained under the grpc-ecosystem GitHub org. Covers tools, libraries, middleware, and examples for every supported language. Uniquely includes gRPC-Web resources for browser-based gRPC. Essential for teams building microservices with gRPC.",
        "related_lists": ["awesome-graphql", "awesome-api-devtools"],
        "list_type": "mixed",
        "audience_level": "intermediate",
        "use_cases": ["building gRPC services", "finding gRPC tools", "gRPC-Web implementation"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Tools", "Language-Specific", "gRPC-Web"],
        "getting_started": "Start with the official gRPC quickstart for your language, then browse 'Tools' for utilities that improve the development experience (grpcurl, grpc-gateway, buf). The 'Language-Specific' sections have the best libraries and middleware for each ecosystem.",
        "suggested_projects": [
            "Build a microservice architecture using gRPC for inter-service communication with the tools listed here",
            "Create a gRPC-Web frontend that connects to a gRPC backend using the gRPC-Web section resources",
            "Develop a gRPC middleware chain (logging, auth, rate-limiting) using the middleware libraries from this list"
        ],
        "featured_example": {
            "name": "Buf",
            "url": "https://buf.build",
            "why": "Buf modernizes the Protobuf workflow — it replaces protoc with a faster, more user-friendly toolchain and adds linting, breaking change detection, and a schema registry"
        }
    },

    # ========================
    # Domain-Specific Data (~10 entries) — under "Data Sources & Datasets"
    # ========================
    {
        "id": "covid-19-data-nytimes",
        "name": "COVID-19 Data (NYT)",
        "github_url": "https://github.com/nytimes/covid-19-data",
        "description": "The New York Times' COVID-19 dataset — cumulative US county/state-level case and death counts compiled from official sources.",
        "maintainer": "nytimes",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["covid-19", "health-data", "time-series", "journalism"],
        "entry_count_approx": "10+",
        "format": "csv",
        "has_contributions_guide": False,
        "editorial_notes": "The most authoritative US COVID-19 dataset — compiled by NYT journalists who cross-referenced state/county reports daily. The data journalism methodology documentation is itself a masterclass in data collection. Historical but invaluable for teaching time-series analysis and epidemiology.",
        "related_lists": ["covid-19-data-jhu", "owid-datasets"],
        "list_type": "datasets",
        "audience_level": "all",
        "use_cases": ["epidemiological analysis", "time-series data practice", "data journalism examples"],
        "has_website": True,
        "website_url": "https://www.nytimes.com/interactive/2021/us/covid-cases.html",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["covid-19-data-jhu"],
        "best_sections": ["US Counties", "US States", "Methodology"],
        "getting_started": "Start with us-states.csv for state-level analysis or us-counties.csv for granular geographic data. The methodology documentation in the README explains important caveats about data collection that affect analysis. Use pandas for Python or readr for R.",
        "suggested_projects": [
            "Build an interactive county-level COVID dashboard with time-series charts and geographic heatmaps",
            "Create a comparative analysis of pandemic waves across US states using NYT data as the ground truth",
            "Develop a data quality audit comparing NYT, JHU, and WHO COVID datasets to understand data journalism methodology"
        ],
        "featured_example": {
            "name": "Methodology documentation",
            "url": "https://github.com/nytimes/covid-19-data#methodology-and-definitions",
            "why": "The methodology section is a rare public look at how professional data journalists collect and verify data at scale — applicable far beyond COVID"
        }
    },
    {
        "id": "owid-datasets",
        "name": "Our World in Data Datasets",
        "github_url": "https://github.com/owid/owid-datasets",
        "description": "Datasets used by Our World in Data — covering health, energy, education, poverty, and more global indicators.",
        "maintainer": "owid",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["global-data", "health", "economics", "research"],
        "entry_count_approx": "400+",
        "format": "csv",
        "has_contributions_guide": True,
        "editorial_notes": "Our World in Data is the gold standard for global development data — every dataset comes with detailed source documentation, methodology notes, and the actual visualizations built from the data. Covers an incredible range from CO2 emissions to democracy indices to childhood mortality.",
        "related_lists": ["covid-19-data-nytimes", "fivethirtyeight-data"],
        "list_type": "datasets",
        "audience_level": "all",
        "use_cases": ["global data analysis", "research data access", "data visualization source material"],
        "has_website": True,
        "website_url": "https://ourworldindata.org",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Health", "Energy", "Education"],
        "getting_started": "Browse ourworldindata.org to find a topic you care about, then find the corresponding dataset in the repo. Each dataset folder includes the data files, source documentation, and the chart configurations used on the website.",
        "suggested_projects": [
            "Build a global development dashboard that lets users explore correlations between indicators (GDP vs education vs health)",
            "Create a 'Gapminder-style' animated scatter plot using OWID data to tell a data story about development progress",
            "Develop a country comparison tool that visualizes any OWID indicator across time and countries"
        ],
        "featured_example": {
            "name": "CO2 and Greenhouse Gas Emissions",
            "url": "https://ourworldindata.org/co2-and-greenhouse-gas-emissions",
            "why": "The CO2 dataset is the most comprehensive freely-available emissions dataset — it's the data behind the climate charts you see cited in every major publication"
        }
    },
    {
        "id": "covid-19-data-jhu",
        "name": "COVID-19 Data (JHU)",
        "github_url": "https://github.com/CSSEGISandData/COVID-19",
        "description": "Johns Hopkins University CSSE COVID-19 dataset — the global reference for pandemic tracking with daily time-series data for 190+ countries.",
        "maintainer": "CSSEGISandData",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["covid-19", "geospatial", "health-data", "global"],
        "entry_count_approx": "20+",
        "format": "csv",
        "has_contributions_guide": False,
        "editorial_notes": "The global counterpart to NYT's US-focused data — JHU tracked COVID-19 across 190+ countries from January 2020. The geospatial (GIS) format makes it uniquely useful for mapping. While data collection ended in March 2023, it remains the most cited pandemic dataset in academic research.",
        "related_lists": ["covid-19-data-nytimes", "owid-datasets"],
        "list_type": "datasets",
        "audience_level": "all",
        "use_cases": ["global COVID analysis", "geospatial data analysis", "epidemiological research"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["covid-19-data-nytimes"],
        "best_sections": ["Time Series", "Daily Reports", "Data Sources"],
        "getting_started": "Start with the time_series_covid19_confirmed_global.csv for country-level trends. The daily reports in csse_covid_19_daily_reports/ provide snapshots with geographic coordinates. Use the UID lookup table to join data across files.",
        "suggested_projects": [
            "Build a global COVID-19 animated map showing the pandemic's geographic spread over time using the GIS coordinates",
            "Create a cross-country analysis comparing pandemic curves, policy interventions, and outcomes",
            "Develop a data pipeline that cleans and normalizes the JHU data for use in epidemiological models"
        ],
        "featured_example": {
            "name": "Global time series data",
            "url": "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series",
            "why": "The global time series data with latitude/longitude enables geographic analysis impossible with other COVID datasets — it powered the famous JHU dashboard seen by billions"
        }
    },
    {
        "id": "fivethirtyeight-data",
        "name": "FiveThirtyEight Data",
        "github_url": "https://github.com/fivethirtyeight/data",
        "description": "Data and code behind the stories and interactives published by FiveThirtyEight.",
        "maintainer": "fivethirtyeight",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["journalism", "politics", "sports", "data-analysis"],
        "entry_count_approx": "200+",
        "format": "csv",
        "has_contributions_guide": False,
        "editorial_notes": "The most famous data journalism archive — datasets behind FiveThirtyEight's stories on elections, sports, economics, and culture. Each dataset comes with a README explaining the methodology and linking to the original article. Perfect for learning data analysis through real-world journalism examples.",
        "related_lists": ["owid-datasets", "buzzfeed-data"],
        "list_type": "datasets",
        "audience_level": "all",
        "use_cases": ["data journalism analysis", "statistics practice", "portfolio project datasets"],
        "has_website": True,
        "website_url": "https://data.fivethirtyeight.com",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["buzzfeed-data"],
        "best_sections": ["Politics", "Sports", "Science & Health"],
        "getting_started": "Browse by topic folder — each folder corresponds to a FiveThirtyEight article and includes the data, a README with methodology, and sometimes the analysis code. The political datasets (polls, forecasts) are the most well-known, but the sports and culture datasets are equally interesting.",
        "suggested_projects": [
            "Reproduce a FiveThirtyEight analysis using their data and methodology, then extend it with your own questions",
            "Build an election forecast model using the polling data and compare your methodology to FiveThirtyEight's approach",
            "Create a data storytelling portfolio by analyzing 3-4 different FiveThirtyEight datasets and writing up your findings"
        ],
        "featured_example": {
            "name": "Polls data",
            "url": "https://github.com/fivethirtyeight/data/tree/master/polls",
            "why": "The polling data is the most comprehensive publicly-available political polling archive — it powered FiveThirtyEight's famous election forecasts"
        }
    },
    {
        "id": "buzzfeed-data",
        "name": "BuzzFeed News Data",
        "github_url": "https://github.com/BuzzFeedNews/everything",
        "description": "An index of all BuzzFeed News open-source data, analysis, libraries, tools, and guides.",
        "maintainer": "BuzzFeedNews",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["journalism", "data-analysis", "investigations", "open-data"],
        "entry_count_approx": "200+",
        "format": "mixed",
        "has_contributions_guide": False,
        "editorial_notes": "A remarkable archive of investigative data journalism — each entry links to both the data and the published article, showing how data drives real-world reporting. Includes investigations into surveillance, immigration, finance, and health. The code is as educational as the data itself.",
        "related_lists": ["fivethirtyeight-data", "owid-datasets"],
        "list_type": "datasets",
        "audience_level": "intermediate",
        "use_cases": ["investigative data analysis", "learning data journalism", "accessing public records data"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["fivethirtyeight-data"],
        "best_sections": ["Investigations", "Analysis", "Data"],
        "getting_started": "Browse the README index chronologically or by topic. Each linked repository includes the dataset, analysis notebooks, and the published article. Start with investigations that interest you — the Jupyter notebooks show professional data journalism methodology.",
        "suggested_projects": [
            "Follow the methodology of a BuzzFeed News investigation and apply it to a local or regional dataset",
            "Build a FOIA request tracker using techniques from the investigations that involved public records requests",
            "Create an investigative data analysis template based on the patterns in BuzzFeed News notebooks"
        ],
        "featured_example": {
            "name": "Surveillance planes investigation",
            "url": "https://github.com/BuzzFeedNews/2016-04-federal-surveillance-planes",
            "why": "The surveillance planes analysis is a masterclass in combining flight tracking data with geospatial analysis to reveal government surveillance patterns — investigative journalism through data science"
        }
    },
    {
        "id": "huggingface-datasets",
        "name": "Hugging Face Datasets",
        "github_url": "https://github.com/huggingface/datasets",
        "description": "The largest hub for ready-to-use ML datasets with a simple Python API for access and processing.",
        "maintainer": "huggingface",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["datasets", "machine-learning", "nlp", "python"],
        "entry_count_approx": "100000+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The npm of ML datasets — over 100k datasets accessible through a single Python API with built-in streaming, caching, and preprocessing. The Hub makes it trivial to find, preview, and load datasets for any ML task. Transforming how researchers and practitioners access training data.",
        "related_lists": ["huggingface-transformers", "awesome-public-datasets"],
        "list_type": "datasets",
        "audience_level": "all",
        "use_cases": ["loading ML datasets", "finding training data", "dataset preprocessing"],
        "has_website": True,
        "website_url": "https://huggingface.co/datasets",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["awesome-public-datasets"],
        "best_sections": ["Quick Start", "Dataset Cards", "Streaming"],
        "getting_started": "Install with `pip install datasets` and load any dataset in one line: `load_dataset('imdb')`. Browse the Hub at huggingface.co/datasets to find datasets with filters for task, language, size, and license. Dataset Cards show previews and usage examples.",
        "suggested_projects": [
            "Build a dataset search engine that indexes Hugging Face dataset cards and recommends datasets based on your ML task description",
            "Create a data preprocessing pipeline template that handles common tasks (tokenization, feature engineering, train/test split) for any HF dataset",
            "Develop a dataset quality analyzer that checks for common issues (class imbalance, missing values, data leakage) across datasets"
        ],
        "featured_example": {
            "name": "Hugging Face Dataset Hub",
            "url": "https://huggingface.co/datasets",
            "why": "The Dataset Hub is the fastest way to find ML datasets — previews, filters, and download stats help you choose the right dataset without downloading and inspecting each one"
        }
    },
    {
        "id": "paperswithcode",
        "name": "Papers With Code",
        "github_url": "https://github.com/paperswithcode/paperswithcode-data",
        "description": "Free and open resource with Machine Learning papers, code, datasets, methods, and evaluation tables.",
        "maintainer": "paperswithcode",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["machine-learning", "papers", "benchmarks", "research"],
        "entry_count_approx": "100000+",
        "format": "json",
        "has_contributions_guide": True,
        "editorial_notes": "The bridge between ML research and practice — every paper is linked to its code implementation and benchmark results. The leaderboard system tracks state-of-the-art across 5000+ benchmarks. Transforming ML reproducibility by making it trivial to find the code behind any paper.",
        "related_lists": ["nlp-progress", "huggingface-datasets"],
        "list_type": "papers",
        "audience_level": "intermediate",
        "use_cases": ["finding paper implementations", "tracking SOTA benchmarks", "ML reproducibility research"],
        "has_website": True,
        "website_url": "https://paperswithcode.com",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["nlp-progress"],
        "best_sections": ["Methods", "Datasets", "Benchmarks"],
        "getting_started": "Use the website to search by task (e.g., 'image classification', 'sentiment analysis') to find the current SOTA. Each result links to the paper, code, and dataset. The 'Libraries' tab shows which frameworks are most popular for each area.",
        "suggested_projects": [
            "Build a research alert system that monitors Papers With Code for new SOTA results in your areas of interest",
            "Create a paper reproducibility checker that tests whether linked code implementations match reported results",
            "Develop a trend analysis dashboard tracking which methods and architectures are gaining adoption across ML tasks"
        ],
        "featured_example": {
            "name": "SOTA leaderboards",
            "url": "https://paperswithcode.com/sota",
            "why": "The SOTA leaderboards are the most comprehensive cross-task benchmark tracker — they show exactly what's best for any ML task right now, with links to reproduce it"
        }
    },
    {
        "id": "awesome-datasets-ml",
        "name": "Awesome Datasets for ML",
        "github_url": "https://github.com/fordaz/awesome-datasets-for-machine-learning",
        "description": "A curated list of datasets organized by ML task — classification, regression, NLP, computer vision, and more.",
        "maintainer": "fordaz",
        "category": "Data Sources & Datasets",
        "subcategory": "Domain-Specific Data",
        "tags": ["datasets", "machine-learning", "training-data", "curated-list"],
        "entry_count_approx": "200+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Unlike general dataset lists, this one is organized by ML task type — making it immediately useful for practitioners who know their task but need training data. The task-based organization (classification, regression, NLP, CV, RL) saves time compared to browsing general dataset directories.",
        "related_lists": ["huggingface-datasets", "awesome-public-datasets"],
        "list_type": "datasets",
        "audience_level": "intermediate",
        "use_cases": ["finding task-specific training data", "ML project datasets", "benchmark dataset discovery"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-public-datasets"],
        "best_sections": ["NLP Datasets", "Computer Vision Datasets", "Tabular Data"],
        "getting_started": "Navigate directly to your ML task type — the list is organized so you can find datasets matching your specific problem (classification, regression, NLP, computer vision, etc.). Each entry notes the dataset size and whether it's beginner-friendly.",
        "suggested_projects": [
            "Build an ML benchmarking suite that trains and evaluates models across multiple datasets from each task category",
            "Create a dataset recommendation engine that suggests the best training data based on your problem description",
            "Develop a 'dataset cookbook' with analysis notebooks for one representative dataset from each task category"
        ],
        "featured_example": {
            "name": "Task-organized index",
            "url": "https://github.com/fordaz/awesome-datasets-for-machine-learning#readme",
            "why": "The task-based organization itself is the standout feature — it maps directly to how ML practitioners think about data needs"
        }
    },

    # ========================
    # RAG & Vector Databases (~8 entries) — under "AI Agents & Frameworks"
    # ========================
    {
        "id": "pgvector",
        "name": "pgvector",
        "github_url": "https://github.com/pgvector/pgvector",
        "description": "Open-source vector similarity search for PostgreSQL — store embeddings alongside your data.",
        "maintainer": "pgvector",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["vector-database", "postgresql", "embeddings", "similarity-search"],
        "entry_count_approx": "20+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The pragmatic choice for vector search — instead of a separate vector database, pgvector adds vector operations to PostgreSQL. This means your embeddings live alongside your relational data with full ACID guarantees. Perfect for teams already on Postgres who want to add semantic search without infrastructure complexity.",
        "related_lists": ["chroma", "weaviate", "awesome-postgres"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["semantic search", "RAG applications", "recommendation systems", "embedding storage"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["chroma", "weaviate", "qdrant", "milvus"],
        "best_sections": ["Getting Started", "Indexing", "Querying"],
        "getting_started": "Install the extension, create a vector column, insert embeddings, and query with `ORDER BY embedding <-> query_vector`. Start with IVFFlat indexing for good balance of speed and accuracy. The README covers everything you need in one page.",
        "suggested_projects": [
            "Add semantic search to an existing PostgreSQL-backed application using pgvector without any infrastructure changes",
            "Build a RAG pipeline that stores document chunks and embeddings in PostgreSQL and retrieves context for LLM prompts",
            "Create a hybrid search system combining pgvector similarity search with PostgreSQL full-text search for best-of-both-worlds retrieval"
        ],
        "featured_example": {
            "name": "pgvector HNSW indexing",
            "url": "https://github.com/pgvector/pgvector#hnsw",
            "why": "HNSW indexing support makes pgvector competitive with dedicated vector databases on query speed — you get vector search performance without leaving PostgreSQL"
        }
    },
    {
        "id": "chroma",
        "name": "Chroma",
        "github_url": "https://github.com/chroma-core/chroma",
        "description": "The AI-native open-source embedding database — the easiest way to build LLM apps with retrieval.",
        "maintainer": "chroma-core",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["vector-database", "embeddings", "rag", "llm"],
        "entry_count_approx": "30+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The developer-friendliest vector database — Chroma prioritizes simplicity and DX above all else. Runs in-memory for development, persists to disk for production, and the Python API is as simple as `collection.add(documents=[...])`. The go-to choice for prototyping RAG applications.",
        "related_lists": ["pgvector", "weaviate", "awesome-langchain"],
        "list_type": "tools",
        "audience_level": "beginner",
        "use_cases": ["RAG prototyping", "embedding storage", "semantic search for LLM apps"],
        "has_website": True,
        "website_url": "https://www.trychroma.com",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["pgvector", "weaviate", "qdrant", "milvus"],
        "best_sections": ["Getting Started", "Embeddings", "Usage Guide"],
        "getting_started": "Install with `pip install chromadb` and you're running in 3 lines: create a client, create a collection, add documents. Chroma auto-generates embeddings using Sentence Transformers. Move to persistent mode when ready for production.",
        "suggested_projects": [
            "Build a personal knowledge base that indexes your notes/documents and answers questions using RAG with Chroma + an LLM",
            "Create a semantic code search tool that embeds your codebase and retrieves relevant code snippets for natural language queries",
            "Develop a document QA system that compares retrieval quality across different embedding models using Chroma"
        ],
        "featured_example": {
            "name": "Chroma Getting Started",
            "url": "https://docs.trychroma.com/getting-started",
            "why": "The getting started guide shows the entire Chroma API in under 20 lines of code — it's the fastest path from zero to a working vector store"
        }
    },
    {
        "id": "weaviate",
        "name": "Weaviate",
        "github_url": "https://github.com/weaviate/weaviate",
        "description": "An open-source vector database that stores objects and vectors, allowing vector search with structured filtering.",
        "maintainer": "weaviate",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["vector-database", "search", "rag", "hybrid-search"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Weaviate occupies the middle ground between simple (Chroma) and enterprise (Milvus) — it's production-ready with excellent hybrid search (combining vector and keyword), built-in module system for auto-vectorization, and a GraphQL API. The strongest option for production RAG with complex filtering needs.",
        "related_lists": ["chroma", "qdrant", "milvus"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["production vector search", "hybrid search", "RAG with filtering"],
        "has_website": True,
        "website_url": "https://weaviate.io",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["chroma", "pgvector", "qdrant", "milvus"],
        "best_sections": ["Quickstart", "Modules", "Hybrid Search"],
        "getting_started": "Deploy with Docker and use the Python client to define a schema and import data. Weaviate's vectorizer modules auto-generate embeddings, so you can insert text directly. Start with the Quickstart tutorial, then explore hybrid search combining BM25 and vector similarity.",
        "suggested_projects": [
            "Build a production-grade semantic search engine with Weaviate's hybrid search combining keyword and vector relevance",
            "Create a multi-modal search system using Weaviate modules to search across text, images, and metadata simultaneously",
            "Develop a RAG pipeline with advanced filtering — retrieve documents by vector similarity while filtering on metadata (date, category, source)"
        ],
        "featured_example": {
            "name": "Hybrid search",
            "url": "https://weaviate.io/developers/weaviate/search/hybrid",
            "why": "Weaviate's hybrid search combines BM25 keyword matching with vector similarity in a single query — this solves the 'keyword gap' problem that pure vector search struggles with"
        }
    },
    {
        "id": "qdrant",
        "name": "Qdrant",
        "github_url": "https://github.com/qdrant/qdrant",
        "description": "High-performance open-source vector similarity search engine with advanced filtering support, built in Rust.",
        "maintainer": "qdrant",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["vector-database", "rust", "similarity-search", "performance"],
        "entry_count_approx": "40+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The performance-focused vector database — written in Rust, Qdrant delivers the lowest latency and highest throughput among open-source vector stores. Its payload filtering system is uniquely powerful, allowing complex filters without sacrificing vector search speed. Best for latency-sensitive production applications.",
        "related_lists": ["weaviate", "milvus", "chroma"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["high-performance vector search", "recommendation systems", "real-time similarity matching"],
        "has_website": True,
        "website_url": "https://qdrant.tech",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["weaviate", "milvus", "chroma", "pgvector"],
        "best_sections": ["Quick Start", "Filtering", "Optimization"],
        "getting_started": "Deploy with Docker and use the Python client. The gRPC API provides the lowest latency. Start with the Quick Start guide, then explore payload filtering — Qdrant's ability to filter on arbitrary JSON fields during vector search is its killer feature.",
        "suggested_projects": [
            "Build a high-performance recommendation engine using Qdrant's vector search with real-time filtering on user preferences",
            "Create a visual similarity search for e-commerce that finds visually similar products using image embeddings",
            "Develop a benchmark comparing Qdrant's query latency against other vector databases at various scales"
        ],
        "featured_example": {
            "name": "Payload filtering",
            "url": "https://qdrant.tech/documentation/concepts/filtering/",
            "why": "Qdrant's filtering system supports complex conditions (nested fields, geo, range) without a separate pre-filter step — vector search with business logic constraints in a single fast query"
        }
    },
    {
        "id": "milvus",
        "name": "Milvus",
        "github_url": "https://github.com/milvus-io/milvus",
        "description": "A cloud-native vector database built for scalable similarity search — supports billions of vectors.",
        "maintainer": "milvus-io",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["vector-database", "distributed", "cloud-native", "scalability"],
        "entry_count_approx": "60+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The enterprise-grade vector database — designed for billion-scale vector search with a distributed, cloud-native architecture. Graduated from the Linux Foundation AI & Data. Supports 10+ index types and GPU acceleration. The right choice when you've outgrown single-node solutions.",
        "related_lists": ["qdrant", "weaviate", "chroma"],
        "list_type": "tools",
        "audience_level": "advanced",
        "use_cases": ["billion-scale vector search", "enterprise RAG", "distributed similarity search"],
        "has_website": True,
        "website_url": "https://milvus.io",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["qdrant", "weaviate", "chroma", "pgvector"],
        "best_sections": ["Quick Start", "Architecture", "Index Types"],
        "getting_started": "Start with Milvus Lite for local development (`pip install pymilvus`), then graduate to Docker or Kubernetes for production. The PyMilvus client mirrors the API across all deployment modes. Understand the index types (IVF_FLAT, HNSW, IVF_PQ) to optimize for your use case.",
        "suggested_projects": [
            "Build a large-scale image search system that indexes millions of images using Milvus's distributed architecture",
            "Create a multi-tenant RAG platform where each tenant has isolated vector collections with different embedding models",
            "Develop a benchmark suite comparing Milvus index types (IVF, HNSW, PQ) on your specific data and query patterns"
        ],
        "featured_example": {
            "name": "Milvus architecture overview",
            "url": "https://milvus.io/docs/architecture_overview.md",
            "why": "The architecture documentation explains how Milvus achieves billion-scale search through its log-based design with separate storage and compute — essential reading for understanding distributed vector search"
        }
    },
    {
        "id": "trulens",
        "name": "TruLens",
        "github_url": "https://github.com/truera/trulens",
        "description": "Evaluation and tracking for LLM applications — measure quality, groundedness, and relevance of RAG and agent outputs.",
        "maintainer": "truera",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["llm-evaluation", "rag", "observability", "quality"],
        "entry_count_approx": "30+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Fills the critical gap of LLM output quality measurement — how do you know if your RAG system is actually retrieving relevant context and generating accurate answers? TruLens provides feedback functions for groundedness, relevance, and toxicity with a dashboard for tracking quality over time.",
        "related_lists": ["chroma", "weaviate", "awesome-langchain"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["RAG evaluation", "LLM quality monitoring", "groundedness checking"],
        "has_website": True,
        "website_url": "https://www.trulens.org",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Quickstart", "Feedback Functions", "RAG Triad"],
        "getting_started": "Install with `pip install trulens` and wrap your RAG pipeline with TruLens's recorder. The 'RAG Triad' metrics (Answer Relevance, Context Relevance, Groundedness) are the key metrics to track. The dashboard visualizes quality over time.",
        "suggested_projects": [
            "Add TruLens evaluation to your existing RAG pipeline and create a quality dashboard tracking the RAG Triad metrics",
            "Build an automated test suite for your LLM application that fails CI if quality scores drop below thresholds",
            "Create an A/B testing framework for RAG systems that compares different retrieval strategies using TruLens metrics"
        ],
        "featured_example": {
            "name": "RAG Triad evaluation",
            "url": "https://www.trulens.org/getting_started/core_concepts/rag_triad/",
            "why": "The RAG Triad (groundedness, relevance, context relevance) provides a principled framework for evaluating RAG systems — it catches the three most common failure modes"
        }
    },
    {
        "id": "langchain-rag-examples",
        "name": "LangChain.js RAG Examples",
        "github_url": "https://github.com/Smit-create/langchainjs-rag-examples",
        "description": "Practical RAG (Retrieval-Augmented Generation) examples using LangChain.js with various vector stores.",
        "maintainer": "Smit-create",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["rag", "langchain", "javascript", "examples"],
        "entry_count_approx": "20+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "A practical companion to the LangChain ecosystem — where the docs explain concepts, this repo provides working RAG examples with different vector stores (Chroma, Pinecone, Supabase). Each example is self-contained and runnable, making it the fastest way to bootstrap a RAG project in JavaScript.",
        "related_lists": ["awesome-langchain", "chroma", "weaviate"],
        "list_type": "tutorials",
        "audience_level": "beginner",
        "use_cases": ["learning RAG patterns", "RAG prototyping", "LangChain.js examples"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": "javascript",
        "overlaps_with": ["awesome-langchain"],
        "best_sections": ["Examples", "Vector Stores", "Document Loaders"],
        "getting_started": "Clone the repo and pick the example matching your vector store preference. Each example has its own README with setup instructions. Start with the Chroma example for the simplest setup, then try Pinecone or Supabase for production-ready alternatives.",
        "suggested_projects": [
            "Build a document QA chatbot using the RAG patterns from these examples with your own documents",
            "Create a comparison of vector store performance by running the same RAG pipeline across all example backends",
            "Develop a RAG template generator that scaffolds new projects based on these working examples"
        ],
        "featured_example": {
            "name": "Chroma RAG example",
            "url": "https://github.com/Smit-create/langchainjs-rag-examples",
            "why": "The Chroma example is the simplest complete RAG pipeline — it shows document loading, chunking, embedding, storage, and retrieval in a single runnable script"
        }
    },
    {
        "id": "pinecone-client",
        "name": "Pinecone Python Client",
        "github_url": "https://github.com/pinecone-io/pinecone-python-client",
        "description": "The official Python client for Pinecone — the fully managed vector database for production AI applications.",
        "maintainer": "pinecone-io",
        "category": "AI Agents & Frameworks",
        "subcategory": "RAG & Vector Databases",
        "tags": ["vector-database", "managed-service", "python", "production"],
        "entry_count_approx": "20+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Pinecone pioneered the managed vector database category — no infrastructure to manage, just an API. The Python client is clean and well-documented. While the service is paid, the free tier is generous enough for prototyping. Best for teams that want production vector search without ops overhead.",
        "related_lists": ["chroma", "weaviate", "qdrant"],
        "list_type": "tools",
        "audience_level": "beginner",
        "use_cases": ["managed vector search", "production RAG", "serverless similarity search"],
        "has_website": True,
        "website_url": "https://www.pinecone.io",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["chroma", "weaviate", "qdrant", "milvus"],
        "best_sections": ["Quickstart", "Indexes", "Query"],
        "getting_started": "Sign up for a free Pinecone account, install with `pip install pinecone`, and create an index. The serverless indexes are the simplest — you just specify the dimension and metric. Use `upsert()` to add vectors and `query()` to search.",
        "suggested_projects": [
            "Build a semantic search API using Pinecone's managed infrastructure with automatic scaling",
            "Create a RAG application that uses Pinecone for retrieval with metadata filtering for multi-tenant support",
            "Develop a migration tool that benchmarks your existing vector database against Pinecone on latency and recall"
        ],
        "featured_example": {
            "name": "Pinecone Quickstart",
            "url": "https://docs.pinecone.io/guides/get-started/quickstart",
            "why": "The quickstart demonstrates the entire Pinecone workflow in 10 lines of code — create index, upsert vectors, query — showing why managed vector databases are so appealing"
        }
    },

    # ========================
    # MLOps & Observability (~8 entries) — under "Data Engineering"
    # ========================
    {
        "id": "awesome-production-ml",
        "name": "Awesome Production Machine Learning",
        "github_url": "https://github.com/EthicalML/awesome-production-machine-learning",
        "description": "A curated list of awesome open-source libraries to deploy, monitor, version, scale, and secure production machine learning.",
        "maintainer": "EthicalML",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "production-ml", "deployment", "monitoring"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive MLOps tool directory — organized by the ML lifecycle stage (feature engineering, training, serving, monitoring, explainability). The breadth is unmatched, covering everything from experiment tracking to model serving to responsible AI. Essential for understanding the MLOps landscape.",
        "related_lists": ["mlflow", "bentoml", "made-with-ml"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding MLOps tools", "building ML infrastructure", "understanding the MLOps landscape"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Model Serving", "Data Pipeline", "Explainability"],
        "getting_started": "Browse by ML lifecycle stage — Feature Engineering for data prep, Training for experiment tracking, Serving for deployment, Monitoring for production. Each tool has a brief description and a badge showing its maturity level.",
        "suggested_projects": [
            "Build an end-to-end ML pipeline using one tool from each lifecycle stage listed here",
            "Create an MLOps maturity assessment tool that maps your current tools against the categories in this list",
            "Develop a comparison matrix of model serving frameworks (BentoML, Seldon, TorchServe) using the entries as candidates"
        ],
        "featured_example": {
            "name": "MLOps lifecycle diagram",
            "url": "https://github.com/EthicalML/awesome-production-machine-learning#readme",
            "why": "The lifecycle diagram in the README maps every MLOps concern to specific tools — it's the most comprehensive visual guide to the MLOps landscape"
        }
    },
    {
        "id": "made-with-ml",
        "name": "Made With ML",
        "github_url": "https://github.com/GokuMohandas/Made-With-ML",
        "description": "Learn how to design, develop, deploy, and iterate on production-grade ML applications.",
        "maintainer": "GokuMohandas",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "course", "production-ml", "best-practices"],
        "entry_count_approx": "40+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The best free course on production ML engineering — covers the full lifecycle from design to deployment with hands-on code. Unlike theory-heavy courses, Made With ML teaches by building a real text classification system end-to-end. The MLOps sections on testing, monitoring, and CI/CD are particularly strong.",
        "related_lists": ["awesome-production-ml", "mlflow"],
        "list_type": "tutorials",
        "audience_level": "intermediate",
        "use_cases": ["learning MLOps", "production ML best practices", "end-to-end ML engineering"],
        "has_website": True,
        "website_url": "https://madewithml.com",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["MLOps", "Testing", "Data Engineering"],
        "getting_started": "Follow the course sequentially — it builds on itself from product design through to production deployment. Each lesson has runnable code notebooks. The MLOps lessons on testing ML systems and CI/CD for ML are the most unique and valuable.",
        "suggested_projects": [
            "Complete the full Made With ML course end-to-end and deploy the production system to a cloud provider",
            "Adapt the course's ML system design framework to your own ML problem and document the design decisions",
            "Build a CI/CD pipeline for ML following the testing and deployment patterns taught in the course"
        ],
        "featured_example": {
            "name": "MLOps course module",
            "url": "https://madewithml.com/#mlops",
            "why": "The MLOps module covers testing, monitoring, and CI/CD for ML systems with working code — topics that most ML courses completely skip"
        }
    },
    {
        "id": "mlflow",
        "name": "MLflow",
        "github_url": "https://github.com/mlflow/mlflow",
        "description": "An open-source platform for the machine learning lifecycle — experiment tracking, model registry, and deployment.",
        "maintainer": "mlflow",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "experiment-tracking", "model-registry", "deployment"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The most widely adopted open-source MLOps platform — MLflow's experiment tracking alone has become the standard for ML teams. The 4 components (Tracking, Projects, Models, Registry) cover the core MLOps workflow. Databricks-backed but fully open-source and vendor-neutral.",
        "related_lists": ["awesome-production-ml", "zenml", "evidently"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["experiment tracking", "model versioning", "model deployment", "ML reproducibility"],
        "has_website": True,
        "website_url": "https://mlflow.org",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Tracking", "Models", "Registry"],
        "getting_started": "Install with `pip install mlflow` and add `mlflow.autolog()` to any training script — it automatically captures parameters, metrics, and artifacts. Launch the UI with `mlflow ui` to visualize experiments. Start with Tracking, then explore the Model Registry when you need to manage model versions.",
        "suggested_projects": [
            "Add MLflow tracking to an existing ML project and create an experiment comparison dashboard",
            "Build a model promotion pipeline using MLflow's Model Registry with staging/production environments",
            "Create a custom MLflow plugin that adds experiment tracking for a framework not natively supported"
        ],
        "featured_example": {
            "name": "MLflow Autologging",
            "url": "https://mlflow.org/docs/latest/tracking/autolog.html",
            "why": "Autologging captures experiment details with a single line of code — add `mlflow.autolog()` and instantly get full experiment tracking for scikit-learn, PyTorch, TensorFlow, and more"
        }
    },
    {
        "id": "bentoml",
        "name": "BentoML",
        "github_url": "https://github.com/bentoml/BentoML",
        "description": "The easiest way to serve AI/ML models in production — build, ship, and scale model inference services.",
        "maintainer": "bentoml",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "model-serving", "deployment", "inference"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The most developer-friendly model serving framework — BentoML wraps any ML model in a production-ready API with batching, GPU optimization, and Kubernetes deployment. The 'Bento' packaging format bundles model, code, and dependencies into a deployable artifact. Bridges the gap between Jupyter notebook and production endpoint.",
        "related_lists": ["mlflow", "awesome-production-ml"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["model serving", "ML API creation", "production deployment"],
        "has_website": True,
        "website_url": "https://www.bentoml.com",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Getting Started", "Adaptive Batching", "Deployment"],
        "getting_started": "Install with `pip install bentoml`, save a model with `bentoml.sklearn.save_model()`, create a Service class with a predict endpoint, and serve with `bentoml serve`. The entire flow from model to API takes about 10 minutes.",
        "suggested_projects": [
            "Deploy a multi-model inference service using BentoML that serves an ensemble of models behind a single API",
            "Build a GPU-optimized model serving pipeline with adaptive batching to maximize throughput",
            "Create a model A/B testing framework using BentoML's runner system to serve multiple model versions simultaneously"
        ],
        "featured_example": {
            "name": "BentoML Quickstart",
            "url": "https://docs.bentoml.com/en/latest/get-started/quickstart.html",
            "why": "The quickstart shows the complete journey from a trained model to a containerized, production-ready API in under 20 lines of code"
        }
    },
    {
        "id": "zenml",
        "name": "ZenML",
        "github_url": "https://github.com/zenml-io/zenml",
        "description": "An extensible, open-source MLOps framework to create reproducible ML pipelines.",
        "maintainer": "zenml-io",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "pipelines", "orchestration", "reproducibility"],
        "entry_count_approx": "40+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "ZenML takes the 'pipeline as code' approach to MLOps — you write standard Python functions and ZenML handles orchestration, artifact tracking, and deployment. The stack system lets you swap infrastructure components (Airflow vs Kubeflow, MLflow vs W&B) without changing pipeline code.",
        "related_lists": ["mlflow", "awesome-production-ml"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["ML pipeline orchestration", "reproducible ML workflows", "infrastructure-agnostic MLOps"],
        "has_website": True,
        "website_url": "https://zenml.io",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": [],
        "best_sections": ["Quickstart", "Stacks", "Pipelines"],
        "getting_started": "Install with `pip install zenml` and run `zenml init` in your project. Convert training scripts to pipelines using `@step` and `@pipeline` decorators. Start with the local stack, then configure cloud stacks when ready to scale.",
        "suggested_projects": [
            "Convert an existing ML training script into a reproducible ZenML pipeline with artifact versioning",
            "Build a multi-stack ML platform that runs the same pipeline on local, Kubernetes, and cloud infrastructure",
            "Create a continuous training pipeline that automatically retrains models when new data arrives using ZenML triggers"
        ],
        "featured_example": {
            "name": "ZenML Stack concept",
            "url": "https://docs.zenml.io/user-guide/production-guide/understand-stacks",
            "why": "The stack abstraction is ZenML's key innovation — it decouples pipeline logic from infrastructure, letting you switch from local to cloud with a single command"
        }
    },
    {
        "id": "evidently",
        "name": "Evidently",
        "github_url": "https://github.com/evidentlyai/evidently",
        "description": "An open-source ML observability platform — evaluate, test, and monitor ML models in production.",
        "maintainer": "evidentlyai",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "monitoring", "data-drift", "model-quality"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The most accessible ML monitoring tool — generates beautiful HTML reports and dashboards showing data drift, model quality degradation, and feature importance changes. Works with any model framework and integrates into CI/CD. Makes the invisible problem of model decay visible.",
        "related_lists": ["mlflow", "whylogs", "awesome-production-ml"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["model monitoring", "data drift detection", "ML testing in CI/CD"],
        "has_website": True,
        "website_url": "https://www.evidentlyai.com",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["whylogs"],
        "best_sections": ["Reports", "Tests", "Monitoring"],
        "getting_started": "Install with `pip install evidently` and generate your first report with `Report(metrics=[...]).run()`. The Data Drift report is the best starting point — it shows whether your production data distribution has shifted from training data. Use Tests for CI/CD integration.",
        "suggested_projects": [
            "Add Evidently monitoring to an existing ML pipeline with weekly drift reports and automated alerts on quality degradation",
            "Build an ML test suite using Evidently's Test system that runs in CI before model deployment",
            "Create a model performance dashboard that tracks prediction quality, data drift, and feature importance changes over time"
        ],
        "featured_example": {
            "name": "Data Drift Report",
            "url": "https://docs.evidentlyai.com/presets/data-drift",
            "why": "The Data Drift report is Evidently's flagship feature — a single function call generates a comprehensive visual report showing which features have shifted and by how much"
        }
    },
    {
        "id": "whylogs",
        "name": "whylogs",
        "github_url": "https://github.com/whylabs/whylogs",
        "description": "The open-source standard for data logging — profile any dataset for data quality, drift, and bias detection.",
        "maintainer": "whylabs",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["data-quality", "logging", "drift-detection", "observability"],
        "entry_count_approx": "30+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "whylogs takes a unique approach to data monitoring — instead of storing all your data, it creates lightweight statistical profiles that capture distributions, correlations, and anomalies. These profiles are mergeable, making it practical to monitor data at scale. The Apache 2.0 license and framework-agnostic design make it a solid foundation for data observability.",
        "related_lists": ["evidently", "awesome-production-ml"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["data profiling", "data quality monitoring", "pipeline observability"],
        "has_website": True,
        "website_url": "https://whylabs.ai/whylogs",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["evidently"],
        "best_sections": ["Getting Started", "Integrations", "Constraints"],
        "getting_started": "Install with `pip install whylogs` and profile a DataFrame with `why.log(df)`. The resulting profile is a compact statistical summary you can compare against baselines. Use constraints to define data quality rules that trigger alerts when violated.",
        "suggested_projects": [
            "Add whylogs profiling to every stage of your data pipeline and build a data quality dashboard",
            "Create a data quality gate in your ML pipeline that blocks model training when data profiles violate constraints",
            "Build a historical data quality tracker that stores daily profiles and visualizes data distribution changes over months"
        ],
        "featured_example": {
            "name": "whylogs constraints",
            "url": "https://whylogs.readthedocs.io/en/latest/examples/basic/Constraints_Suite.html",
            "why": "The constraints system lets you define data quality rules (no nulls, values in range, distribution within bounds) that act as automated guardrails for your data pipelines"
        }
    },
    {
        "id": "wandb",
        "name": "Weights & Biases",
        "github_url": "https://github.com/wandb/wandb",
        "description": "The ML experiment tracking platform — log, visualize, and compare experiments with a few lines of code.",
        "maintainer": "wandb",
        "category": "Data Engineering",
        "subcategory": "MLOps & Observability",
        "tags": ["mlops", "experiment-tracking", "visualization", "collaboration"],
        "entry_count_approx": "60+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Weights & Biases (W&B) has become the de facto experiment tracking tool for ML researchers — its hosted dashboard, collaborative features, and deep framework integrations make it addictive. The free tier is generous for individuals. While MLflow is more open, W&B's polish and UX are unmatched.",
        "related_lists": ["mlflow", "awesome-production-ml"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["experiment tracking", "hyperparameter sweeps", "model visualization", "team collaboration"],
        "has_website": True,
        "website_url": "https://wandb.ai",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["mlflow"],
        "best_sections": ["Quickstart", "Sweeps", "Reports"],
        "getting_started": "Sign up for a free account, install with `pip install wandb`, and add `wandb.init()` + `wandb.log()` to your training loop. The auto-integration with PyTorch Lightning, Keras, and Hugging Face means zero-config tracking for most frameworks.",
        "suggested_projects": [
            "Set up W&B experiment tracking for your ML project and create a comparative report of different model architectures",
            "Run a hyperparameter sweep using W&B Sweeps with Bayesian optimization across your model's configuration space",
            "Build a team ML dashboard using W&B Reports that summarizes weekly experiment results and model performance"
        ],
        "featured_example": {
            "name": "W&B Sweeps",
            "url": "https://docs.wandb.ai/guides/sweeps",
            "why": "Sweeps automate hyperparameter search with Bayesian optimization — define a config, launch agents, and W&B intelligently explores the parameter space while visualizing results in real-time"
        }
    },

    # ========================
    # Web Scraping & Data Collection (~8 entries) — under "Data Engineering"
    # ========================
    {
        "id": "awesome-web-scraping",
        "name": "Awesome Web Scraping",
        "github_url": "https://github.com/lorien/awesome-web-scraping",
        "description": "A curated list of web scraping tools, libraries, and resources organized by programming language.",
        "maintainer": "lorien",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["web-scraping", "data-collection", "tools", "libraries"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive web scraping directory — organized by language (Python, JavaScript, Ruby, etc.) and by function (HTTP clients, parsers, browsers, anti-bot bypass). The language-based organization is uniquely useful since scraping tools vary significantly across ecosystems.",
        "related_lists": ["awesome-crawler", "scrapy", "crawlee"],
        "list_type": "tools",
        "audience_level": "all",
        "use_cases": ["finding scraping tools", "building data collection pipelines", "choosing scraping libraries"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-crawler"],
        "best_sections": ["Python", "JavaScript", "Anti-Bot"],
        "getting_started": "Navigate to your programming language, then browse by category (HTTP clients, HTML parsers, browser automation). The 'Anti-Bot' section is critical reading — modern web scraping is as much about bypass techniques as it is about parsing.",
        "suggested_projects": [
            "Build a robust web scraping pipeline using tools from this list that handles JavaScript rendering, rate limiting, and proxy rotation",
            "Create a scraping framework comparison benchmark that tests speed, reliability, and anti-bot handling across the listed libraries",
            "Develop a scraping template generator that scaffolds projects with the right tools based on target site characteristics"
        ],
        "featured_example": {
            "name": "Python scraping section",
            "url": "https://github.com/lorien/awesome-web-scraping/blob/master/python.md",
            "why": "The Python section is the most comprehensive — it covers the full scraping stack from HTTP clients (requests, httpx) to parsers (BeautifulSoup, lxml) to frameworks (Scrapy, Crawlee)"
        }
    },
    {
        "id": "scrapy",
        "name": "Scrapy",
        "github_url": "https://github.com/scrapy/scrapy",
        "description": "A fast, high-level web crawling and web scraping framework for Python.",
        "maintainer": "scrapy",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["web-scraping", "python", "crawling", "framework"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The gold standard for Python web scraping — Scrapy's architecture (spiders, items, pipelines, middlewares) handles the full scraping lifecycle from request to structured output. Its async engine handles thousands of concurrent requests. The go-to choice for anything beyond simple one-off scraping.",
        "related_lists": ["awesome-web-scraping", "crawlee"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["large-scale web scraping", "structured data extraction", "web crawling"],
        "has_website": True,
        "website_url": "https://scrapy.org",
        "is_awesome_verified": False,
        "language_focus": "python",
        "overlaps_with": ["crawlee"],
        "best_sections": ["Tutorial", "Architecture", "Item Pipeline"],
        "getting_started": "Install with `pip install scrapy`, create a project with `scrapy startproject myproject`, generate a spider with `scrapy genspider`. The tutorial walks through extracting data from a real website. Focus on understanding the Spider → Item → Pipeline flow.",
        "suggested_projects": [
            "Build a job listing aggregator that scrapes multiple job boards and normalizes the data into a common format",
            "Create a price monitoring system that tracks e-commerce prices over time using Scrapy's scheduled crawls",
            "Develop a custom Scrapy pipeline that deduplicates, validates, and stores scraped data in a database"
        ],
        "featured_example": {
            "name": "Scrapy Tutorial",
            "url": "https://docs.scrapy.org/en/latest/intro/tutorial.html",
            "why": "The official tutorial is one of the best in any Python library — it teaches Scrapy's architecture through a practical example that you can run immediately"
        }
    },
    {
        "id": "crawlee",
        "name": "Crawlee",
        "github_url": "https://github.com/apify/crawlee",
        "description": "A web scraping and browser automation library for Node.js — build reliable crawlers with built-in anti-blocking.",
        "maintainer": "apify",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["web-scraping", "javascript", "browser-automation", "anti-blocking"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Crawlee is the modern JavaScript answer to Python's Scrapy — built by Apify (the web scraping company), it includes anti-blocking features (browser fingerprinting, proxy rotation, session management) out of the box. The Playwright integration makes it excellent for JavaScript-heavy sites.",
        "related_lists": ["scrapy", "playwright", "awesome-web-scraping"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["JavaScript web scraping", "browser automation", "anti-blocking scraping"],
        "has_website": True,
        "website_url": "https://crawlee.dev",
        "is_awesome_verified": False,
        "language_focus": "javascript",
        "overlaps_with": ["scrapy"],
        "best_sections": ["Quick Start", "Anti-Blocking", "Examples"],
        "getting_started": "Create a new project with `npx crawlee create` and choose between Cheerio (HTTP-based, fast) or Playwright (browser-based, handles JS). The built-in request queue and auto-scaling handle crawl management. Start with the Quick Start guide.",
        "suggested_projects": [
            "Build a web scraper for a JavaScript-heavy single-page application using Crawlee's Playwright integration",
            "Create a distributed crawling system using Crawlee with proxy rotation for large-scale data collection",
            "Develop a content change monitor that tracks website changes over time and sends notifications"
        ],
        "featured_example": {
            "name": "Anti-blocking features",
            "url": "https://crawlee.dev/docs/guides/avoid-blocking",
            "why": "Crawlee's anti-blocking guide covers browser fingerprinting, session rotation, and proxy management — it addresses the hardest part of modern web scraping"
        }
    },
    {
        "id": "playwright",
        "name": "Playwright",
        "github_url": "https://github.com/microsoft/playwright",
        "description": "Microsoft's framework for reliable end-to-end testing and browser automation for modern web apps.",
        "maintainer": "microsoft",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["browser-automation", "testing", "web-scraping", "cross-browser"],
        "entry_count_approx": "100+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "Playwright has rapidly become the preferred browser automation framework — faster and more reliable than Selenium, more powerful than Puppeteer (multi-browser support, auto-wait, network interception). While designed for testing, it's equally powerful for web scraping JavaScript-heavy sites.",
        "related_lists": ["puppeteer", "crawlee"],
        "list_type": "frameworks",
        "audience_level": "intermediate",
        "use_cases": ["browser automation", "end-to-end testing", "scraping JavaScript sites"],
        "has_website": True,
        "website_url": "https://playwright.dev",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["puppeteer"],
        "best_sections": ["Getting Started", "Auto-waiting", "Network"],
        "getting_started": "Install with `npm init playwright@latest` (Node.js) or `pip install playwright && playwright install` (Python). The codegen tool (`playwright codegen`) records your browser actions and generates code — the fastest way to create automation scripts.",
        "suggested_projects": [
            "Build a visual regression testing suite using Playwright's screenshot comparison for your web application",
            "Create a web scraping tool for JavaScript-heavy sites using Playwright's page.evaluate() for client-side data extraction",
            "Develop an automated form submission and workflow testing framework using Playwright's codegen as a starting point"
        ],
        "featured_example": {
            "name": "Playwright Codegen",
            "url": "https://playwright.dev/docs/codegen",
            "why": "Codegen records your browser interactions and generates test code in real-time — it's the fastest way to create reliable automation scripts without writing selectors by hand"
        }
    },
    {
        "id": "puppeteer",
        "name": "Puppeteer",
        "github_url": "https://github.com/puppeteer/puppeteer",
        "description": "Google's Node.js library for controlling headless Chrome/Chromium — the original browser automation powerhouse.",
        "maintainer": "puppeteer",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["browser-automation", "chrome", "javascript", "headless"],
        "entry_count_approx": "50+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The original headless Chrome automation library from the Chrome team. While Playwright has surpassed it in features, Puppeteer remains the most battle-tested option with the largest ecosystem of plugins and recipes. Its tight integration with Chrome DevTools Protocol gives it capabilities no other tool has.",
        "related_lists": ["playwright", "crawlee", "cheerio"],
        "list_type": "libraries",
        "audience_level": "intermediate",
        "use_cases": ["headless Chrome automation", "PDF generation", "screenshot capture", "web scraping"],
        "has_website": True,
        "website_url": "https://pptr.dev",
        "is_awesome_verified": False,
        "language_focus": "javascript",
        "overlaps_with": ["playwright"],
        "best_sections": ["Getting Started", "API", "Guides"],
        "getting_started": "Install with `npm install puppeteer` (includes Chromium) or `puppeteer-core` (bring your own browser). The API centers on `browser.newPage()` → page actions → `browser.close()`. Start with screenshots and navigation, then explore network interception.",
        "suggested_projects": [
            "Build a PDF generation service that renders web pages to high-quality PDFs using Puppeteer's print capabilities",
            "Create a visual monitoring tool that takes periodic screenshots of web pages and diffs them to detect changes",
            "Develop a performance auditing tool using Puppeteer's Chrome DevTools Protocol access to collect Core Web Vitals"
        ],
        "featured_example": {
            "name": "Chrome DevTools Protocol integration",
            "url": "https://chromedevtools.github.io/devtools-protocol/",
            "why": "Puppeteer's direct CDP access gives you capabilities beyond any other automation tool — network interception, performance profiling, and coverage analysis at the protocol level"
        }
    },
    {
        "id": "cheerio",
        "name": "Cheerio",
        "github_url": "https://github.com/cheeriojs/cheerio",
        "description": "Fast, flexible, and lean implementation of jQuery designed for the server — parse and manipulate HTML/XML.",
        "maintainer": "cheeriojs",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["html-parsing", "javascript", "jquery", "server-side"],
        "entry_count_approx": "20+",
        "format": "mixed",
        "has_contributions_guide": True,
        "editorial_notes": "The fastest HTML parser in the Node.js ecosystem — if you don't need JavaScript rendering, Cheerio parses HTML 8x faster than a headless browser. Its jQuery-like API makes it immediately familiar. The ideal choice for scraping static HTML pages where you need speed over browser features.",
        "related_lists": ["scrapy", "crawlee", "puppeteer"],
        "list_type": "libraries",
        "audience_level": "beginner",
        "use_cases": ["HTML parsing", "web scraping", "XML processing"],
        "has_website": True,
        "website_url": "https://cheerio.js.org",
        "is_awesome_verified": False,
        "language_focus": "javascript",
        "overlaps_with": [],
        "best_sections": ["Getting Started", "Selectors", "Manipulation"],
        "getting_started": "Install with `npm install cheerio`, load HTML with `cheerio.load(html)`, then use jQuery-style selectors to extract data: `$('.title').text()`. It's the simplest possible scraping tool — load HTML, select elements, get text.",
        "suggested_projects": [
            "Build a news aggregator that fetches and parses multiple news sites using Cheerio for fast HTML extraction",
            "Create a link checker that crawls a website, parses each page with Cheerio, and reports broken links",
            "Develop an RSS feed generator that scrapes websites without feeds and creates structured XML output"
        ],
        "featured_example": {
            "name": "Cheerio API documentation",
            "url": "https://cheerio.js.org/docs/api",
            "why": "The API mirrors jQuery so faithfully that any jQuery developer can start scraping immediately — the learning curve is essentially zero if you know CSS selectors"
        }
    },
    {
        "id": "awesome-crawler",
        "name": "Awesome Web Crawler",
        "github_url": "https://github.com/BruceDone/awesome-crawler",
        "description": "A collection of awesome web crawler, scraper, and spider tools and frameworks.",
        "maintainer": "BruceDone",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["web-crawling", "scraping", "tools", "curated-list"],
        "entry_count_approx": "300+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Focuses specifically on web crawling frameworks and tools — where awesome-web-scraping is organized by language, this is organized by function (general crawlers, browser rendering, cloud services, proxy tools). Uniquely covers crawling infrastructure (proxy pools, scheduling) that other lists miss.",
        "related_lists": ["awesome-web-scraping", "scrapy", "crawlee"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding crawling tools", "building crawling infrastructure", "comparing scraping frameworks"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["awesome-web-scraping"],
        "best_sections": ["Python", "JavaScript", "Cloud/SaaS"],
        "getting_started": "Browse by your programming language first, then look at the 'Cloud/SaaS' section for managed crawling services if you don't want to build infrastructure. The proxy management tools listed are essential for any serious crawling project.",
        "suggested_projects": [
            "Build a distributed web crawling system using a framework from this list with a job queue and deduplication",
            "Create a crawler comparison benchmark that tests frameworks on speed, memory usage, and politeness (robots.txt compliance)",
            "Develop a visual crawler builder that generates Scrapy/Crawlee code from user-selected page elements"
        ],
        "featured_example": {
            "name": "Scrapy (Python)",
            "url": "https://scrapy.org",
            "why": "Scrapy is listed first for good reason — its spider-based architecture, middleware system, and extensive ecosystem make it the most complete crawling framework"
        }
    },
    {
        "id": "awesome-osint",
        "name": "Awesome OSINT",
        "github_url": "https://github.com/jivoi/awesome-osint",
        "description": "A curated list of amazingly awesome Open Source Intelligence (OSINT) tools and resources.",
        "maintainer": "jivoi",
        "category": "Data Engineering",
        "subcategory": "Web Scraping & Data Collection",
        "tags": ["osint", "data-collection", "intelligence", "research"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most comprehensive OSINT tool directory — covers social media intelligence, geolocation, domain/IP research, people search, and more. While primarily aimed at security researchers and investigators, the data collection techniques are broadly applicable to any research project.",
        "related_lists": ["awesome-hacking", "awesome-web-scraping"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["open source intelligence gathering", "research data collection", "digital investigation"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Social Media", "Domain/IP Research", "Geospatial"],
        "getting_started": "Start with the category matching your research need — Social Media for people investigation, Domain/IP for technical research, Geospatial for location analysis. Each tool includes a brief description. Many tools have free tiers suitable for individual researchers.",
        "suggested_projects": [
            "Build an automated OSINT dashboard that aggregates information from multiple sources listed here for a given query",
            "Create a domain investigation tool that chains together DNS, WHOIS, and certificate tools from this list",
            "Develop a geolocation verification tool using the geospatial OSINT resources to verify image locations"
        ],
        "featured_example": {
            "name": "Shodan",
            "url": "https://www.shodan.io",
            "why": "Shodan is the search engine for internet-connected devices — its API and data make it the most powerful tool for understanding what's exposed on the internet"
        }
    },

    # ========================
    # Interesting / Exploratory (~6 entries)
    # ========================
    {
        "id": "project-ideas",
        "name": "Project Ideas",
        "github_url": "https://github.com/karan/Projects",
        "description": "A list of practical projects that anyone can solve in any programming language — from beginner to advanced.",
        "maintainer": "karan",
        "category": "Meta Lists",
        "subcategory": "Project Ideas",
        "tags": ["projects", "learning", "programming", "practice"],
        "entry_count_approx": "100+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The original project ideas list — predates most 'build your own X' repos. Projects are organized by category (numbers, text, networking, classes) and difficulty. Each project is described in 1-2 sentences, leaving implementation decisions to the developer. Simple but effective format.",
        "related_lists": ["app-ideas", "build-your-own-x", "project-based-learning"],
        "list_type": "projects",
        "audience_level": "all",
        "use_cases": ["finding programming projects", "practice exercises", "building a portfolio"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["app-ideas", "build-your-own-x"],
        "best_sections": ["Numbers", "Text", "Web"],
        "getting_started": "Pick a category matching your interest (Numbers for math-heavy, Text for string manipulation, Web for full-stack). Start with the simpler projects in each category and increase difficulty. Try implementing each project in two different languages to compare approaches.",
        "suggested_projects": [
            "Work through all projects in one category in a language you're learning and publish solutions to GitHub",
            "Build a project randomizer that picks a project based on your skill level and generates a starter template",
            "Create a community solutions gallery where developers can share and compare implementations"
        ],
        "featured_example": {
            "name": "Euler Problem implementations",
            "url": "https://github.com/karan/Projects#numbers",
            "why": "The Numbers section includes Euler-style problems that teach algorithmic thinking — they're the best warm-up exercises for interview prep"
        }
    },
    {
        "id": "app-ideas",
        "name": "App Ideas",
        "github_url": "https://github.com/florinpop17/app-ideas",
        "description": "A collection of application ideas which can be used to improve your coding skills, organized by difficulty tier.",
        "maintainer": "florinpop17",
        "category": "Meta Lists",
        "subcategory": "Project Ideas",
        "tags": ["projects", "learning", "web-development", "ideas"],
        "entry_count_approx": "100+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Goes beyond simple project descriptions — each idea includes a detailed specification with user stories, constraints, and bonus features. The three-tier system (Beginner, Intermediate, Advanced) makes it easy to find projects at your level. Uniquely includes example screenshots for many projects.",
        "related_lists": ["project-ideas", "build-your-own-x"],
        "list_type": "projects",
        "audience_level": "all",
        "use_cases": ["finding app project ideas", "improving coding skills", "building a portfolio"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": ["project-ideas", "build-your-own-x"],
        "best_sections": ["Beginner", "Intermediate", "Advanced"],
        "getting_started": "Browse by tier matching your experience level. Each project includes user stories (requirements), bonus features, and useful links. Start with Tier 1 to build confidence, then tackle Tier 2 and 3 for portfolio-worthy projects.",
        "suggested_projects": [
            "Complete one project from each tier and document the learning progression in a blog series",
            "Build the bonus features for a Tier 2 project and add your own twist to make it portfolio-ready",
            "Create a 'project matcher' that recommends app ideas based on the technologies you want to practice"
        ],
        "featured_example": {
            "name": "Pomodoro Timer (Tier 1)",
            "url": "https://github.com/florinpop17/app-ideas/blob/master/Projects/1-Beginner/Pomodoro-Clock.md",
            "why": "The Pomodoro Timer is the perfect first project — it teaches DOM manipulation, timers, and user interaction while building something genuinely useful"
        }
    },
    {
        "id": "realworld",
        "name": "RealWorld",
        "github_url": "https://github.com/gothinkster/realworld",
        "description": "The 'mother of all demo apps' — the same Medium.com clone built with every major frontend/backend framework.",
        "maintainer": "gothinkster",
        "category": "Meta Lists",
        "subcategory": "Project Ideas",
        "tags": ["demo-app", "frameworks", "comparison", "fullstack"],
        "entry_count_approx": "100+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The most ambitious framework comparison project ever — the same CRUD application (a Medium clone) implemented in React, Vue, Angular, Svelte, Rails, Django, Express, and 100+ other stacks. The shared API spec means you can mix any frontend with any backend. Invaluable for evaluating technology choices.",
        "related_lists": ["build-your-own-x", "project-based-learning"],
        "list_type": "projects",
        "audience_level": "intermediate",
        "use_cases": ["comparing frameworks", "learning new stacks", "understanding full-stack patterns"],
        "has_website": True,
        "website_url": "https://codebase.show/projects/realworld",
        "is_awesome_verified": False,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["Frontends", "Backends", "Fullstack"],
        "getting_started": "Pick a frontend and backend implementation in frameworks you want to compare. Run them together using the shared API spec. The README links to all implementations with their build status. Use codebase.show for a visual browser of all implementations.",
        "suggested_projects": [
            "Implement the RealWorld spec in a framework you're learning and compare your code to the existing implementation",
            "Build a performance benchmark that tests multiple frontend implementations on identical hardware and data",
            "Create a code comparison tool that highlights architectural differences between implementations of the same features"
        ],
        "featured_example": {
            "name": "RealWorld spec",
            "url": "https://realworld-docs.netlify.app/specifications/frontend/routing/",
            "why": "The shared API and routing spec is what makes RealWorld unique — it enables direct, fair comparisons between frameworks by holding the application constant"
        }
    },
    {
        "id": "awesome-selfhosted",
        "name": "Awesome Self-Hosted",
        "github_url": "https://github.com/awesome-selfhosted/awesome-selfhosted",
        "description": "A list of Free Software network services and web applications which can be hosted on your own servers.",
        "maintainer": "awesome-selfhosted",
        "category": "Meta Lists",
        "subcategory": "Self-Hosting",
        "tags": ["self-hosted", "privacy", "open-source", "infrastructure"],
        "entry_count_approx": "2000+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The definitive directory of self-hostable software — 2000+ applications covering everything from email to analytics to project management. Each entry includes language, license, and a brief description. The go-to resource for anyone wanting to replace SaaS with self-hosted alternatives.",
        "related_lists": ["awesome-sysadmin", "free-for-dev"],
        "list_type": "tools",
        "audience_level": "intermediate",
        "use_cases": ["finding self-hosted alternatives to SaaS", "building private infrastructure", "reducing vendor lock-in"],
        "has_website": True,
        "website_url": "https://awesome-selfhosted.net",
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-sysadmin"],
        "best_sections": ["Communication", "Office Suites", "Analytics"],
        "getting_started": "Browse by the SaaS tool you want to replace — the categories mirror common SaaS categories (project management, CRM, analytics, etc.). Each entry shows the programming language and license. Use the companion website for easier filtering and search.",
        "suggested_projects": [
            "Replace 3-5 SaaS tools with self-hosted alternatives from this list and document the migration process and cost savings",
            "Build a self-hosted homelab using Docker Compose with applications from different categories",
            "Create a self-hosted alternatives comparison matrix that maps popular SaaS products to their open-source equivalents"
        ],
        "featured_example": {
            "name": "Nextcloud",
            "url": "https://nextcloud.com",
            "why": "Nextcloud is the poster child of self-hosting — a full Google Workspace replacement (files, calendar, contacts, office, video calls) that you control completely"
        }
    },
    {
        "id": "awesome-for-beginners",
        "name": "Awesome First PR Opportunities",
        "github_url": "https://github.com/MunGell/awesome-for-beginners",
        "description": "A list of awesome beginners-friendly projects with labels for finding good first issues to contribute to.",
        "maintainer": "MunGell",
        "category": "Meta Lists",
        "subcategory": "Open Source",
        "tags": ["open-source", "beginners", "contributing", "first-pr"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "The bridge from learning to contributing — lists open-source projects that actively welcome newcomers with labeled 'good first issue' and 'help wanted' issues. Organized by programming language, making it easy to find contribution opportunities in your ecosystem. Essential for developers making their first open-source contribution.",
        "related_lists": ["project-ideas", "app-ideas"],
        "list_type": "mixed",
        "audience_level": "beginner",
        "use_cases": ["finding first open-source contributions", "building an open-source portfolio", "learning through contribution"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": [],
        "best_sections": ["JavaScript", "Python", "TypeScript"],
        "getting_started": "Navigate to your primary programming language and browse the listed projects. Look for projects that interest you, then check their 'good first issue' labels on GitHub. Read the project's CONTRIBUTING.md before making your first PR.",
        "suggested_projects": [
            "Make your first open-source contribution by finding a 'good first issue' in a project from this list",
            "Build a tool that monitors projects in this list for new beginner-friendly issues and sends notifications",
            "Create a mentorship matching system that pairs new contributors with experienced maintainers of listed projects"
        ],
        "featured_example": {
            "name": "First Contributions",
            "url": "https://github.com/firstcontributions/first-contributions",
            "why": "First Contributions teaches the GitHub fork-clone-branch-PR workflow through an actual contribution — it's the gentlest possible introduction to open-source collaboration"
        }
    },
    {
        "id": "awesome-creative-coding",
        "name": "Awesome Creative Coding",
        "github_url": "https://github.com/terkelg/awesome-creative-coding",
        "description": "A curated list of creative coding resources — generative art, data visualization, interactive experiences, and creative computation.",
        "maintainer": "terkelg",
        "category": "Meta Lists",
        "subcategory": "Creative Coding",
        "tags": ["creative-coding", "generative-art", "visualization", "interactive"],
        "entry_count_approx": "500+",
        "format": "markdown",
        "has_contributions_guide": True,
        "editorial_notes": "Bridges the gap between art and code — covers Processing, p5.js, shaders, generative art, and creative computation. The breadth is remarkable, from WebGL shaders to live coding to creative AI. One of the best lists for discovering that programming can be expressive and beautiful, not just functional.",
        "related_lists": ["awesome-dataviz", "awesome-d3"],
        "list_type": "mixed",
        "audience_level": "all",
        "use_cases": ["generative art creation", "creative coding learning", "interactive experience development"],
        "has_website": False,
        "website_url": None,
        "is_awesome_verified": True,
        "language_focus": None,
        "overlaps_with": ["awesome-dataviz"],
        "best_sections": ["Frameworks", "Shaders", "Inspiration"],
        "getting_started": "Start with the 'Frameworks' section — p5.js for beginners, Processing for depth, or Three.js for 3D. The 'Courses' section has structured learning paths. Browse 'Inspiration' to see what's possible before choosing your tools.",
        "suggested_projects": [
            "Create a generative art series using p5.js that evolves based on external data (weather, music, stock prices)",
            "Build an interactive data visualization that responds to user gestures using the frameworks listed here",
            "Develop a live coding environment for creative coding that compiles and renders code changes in real-time"
        ],
        "featured_example": {
            "name": "p5.js",
            "url": "https://p5js.org",
            "why": "p5.js is the most accessible creative coding framework — it inherits Processing's philosophy of making coding visual and immediate, with a web-native JavaScript implementation"
        }
    },
]


def main():
    print(f"Loading {LISTS_JSON}...")
    with open(LISTS_JSON) as f:
        existing = json.load(f)

    existing_ids = {e["id"] for e in existing}
    print(f"Found {len(existing)} existing entries")
    print(f"Adding {len(NEW_ENTRIES)} new entries...\n")

    # Check for duplicate IDs
    new_ids = {e["id"] for e in NEW_ENTRIES}
    dupes = existing_ids & new_ids
    if dupes:
        print(f"ERROR: Duplicate IDs found: {dupes}")
        sys.exit(1)

    # Fetch live stats for each new entry
    errors = []
    for i, entry in enumerate(NEW_ENTRIES):
        url = entry["github_url"]
        parts = url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        print(f"[{i + 1}/{len(NEW_ENTRIES)}] {owner}/{repo}...", end=" ", flush=True)

        stats = fetch_gh_stats(owner, repo)
        if stats:
            entry["stars_count"] = stats["stars"]
            entry["forks_count"] = stats["forks"]
            entry["last_commit_date"] = stats["pushed"][:10] if stats.get("pushed") else "unknown"
            entry["open_issues_count"] = stats["issues"]
            entry["is_archived"] = stats["archived"]
            entry["watchers_count"] = stats["watchers"]
            entry["created_year"] = int(stats["created"][:4]) if stats.get("created") else 2020
            entry["stars_approx"] = stars_approx(stats["stars"])
            entry["added_date"] = TODAY

            # Compute last_activity
            if entry["last_commit_date"] and entry["last_commit_date"] != "unknown":
                entry["last_activity"] = entry["last_commit_date"][:4]
            else:
                entry["last_activity"] = "unknown"

            # Determine license
            if stats.get("license") and stats["license"] != "NOASSERTION":
                entry["license"] = stats["license"]
            else:
                entry["license"] = entry.get("license", "Unknown")

            # Compute quality score
            entry["quality_score"] = compute_quality_score(
                stats["stars"],
                entry["last_commit_date"],
                entry.get("entry_count_approx", "100+")
            )

            print(f"OK ({stats['stars']:,} stars)")
        else:
            # Set defaults for failed fetches
            entry["stars_count"] = 0
            entry["forks_count"] = 0
            entry["last_commit_date"] = "unknown"
            entry["open_issues_count"] = 0
            entry["is_archived"] = False
            entry["watchers_count"] = 0
            entry["created_year"] = 2020
            entry["stars_approx"] = "0"
            entry["added_date"] = TODAY
            entry["last_activity"] = "unknown"
            entry["license"] = entry.get("license", "Unknown")
            entry["quality_score"] = 5
            errors.append(f"{owner}/{repo}")
            print("FAILED - using defaults")

        # Rate limit
        if (i + 1) % 25 == 0:
            time.sleep(1)

    # Append new entries
    all_entries = existing + NEW_ENTRIES
    print(f"\nTotal entries: {len(all_entries)}")

    # Write updated JSON
    with open(LISTS_JSON, "w") as f:
        json.dump(all_entries, f, indent=2)
        f.write("\n")
    print(f"Updated {LISTS_JSON}")

    # Regenerate CSV
    regenerate_csv(all_entries)
    print(f"Regenerated {LISTS_CSV}")

    # Regenerate tags
    regenerate_tags(all_entries)
    print(f"Regenerated {TAGS_JSON}")

    if errors:
        print(f"\nFailed repos ({len(errors)}): {', '.join(errors)}")

    print(f"\nDone! Added {len(NEW_ENTRIES)} new entries (total: {len(all_entries)})")


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


def regenerate_tags(data):
    """Regenerate tags.json with updated counts."""
    tag_map = {}
    for entry in data:
        for tag in entry.get("tags", []):
            if tag not in tag_map:
                tag_map[tag] = {"ids": [], "count": 0}
            tag_map[tag]["ids"].append(entry["id"])
            tag_map[tag]["count"] += 1

    # Only include tags with 2+ occurrences
    tags_list = []
    for tag, info in sorted(tag_map.items()):
        if info["count"] >= 2:
            tags_list.append({
                "tag": tag,
                "count": info["count"],
                "description": generate_tag_description(tag),
                "list_ids": sorted(info["ids"])
            })

    # Sort by count descending
    tags_list.sort(key=lambda x: -x["count"])

    tags_data = {"tags": tags_list}
    with open(TAGS_JSON, "w") as f:
        json.dump(tags_data, f, indent=2)
        f.write("\n")


TAG_DESCRIPTIONS = {
    "nlp": "Natural language processing tools and resources",
    "computer-vision": "Computer vision tools, models, and research",
    "deep-learning": "Deep learning frameworks and resources",
    "security": "Security tools, resources, and best practices",
    "pentesting": "Penetration testing tools and methodologies",
    "hacking": "Ethical hacking and security research resources",
    "apis": "API directories and resources",
    "api": "API tools and frameworks",
    "vector-database": "Vector similarity search databases",
    "rag": "Retrieval-augmented generation tools",
    "mlops": "Machine learning operations and lifecycle management",
    "web-scraping": "Web scraping tools and frameworks",
    "browser-automation": "Browser automation and testing tools",
    "devops": "DevOps tools, practices, and resources",
    "cloud": "Cloud computing tools and resources",
    "monitoring": "Monitoring and observability tools",
    "datasets": "Data collections and dataset directories",
    "machine-learning": "Machine learning tools and resources",
    "research": "Research papers and academic resources",
    "tools": "Developer tools and utilities",
    "curated-list": "Curated resource collections",
    "python": "Python libraries and tools",
    "javascript": "JavaScript tools and libraries",
    "llm": "Large language model resources and tools",
    "meta": "Meta-lists and list indexes",
    "open-source": "Open source projects and contributions",
    "learning": "Educational resources and courses",
    "production": "Production-grade tools and frameworks",
    "infrastructure": "Infrastructure tools and management",
    "sysadmin": "System administration tools",
    "saas": "Software as a Service tools",
    "free-tier": "Free tier services and tools",
    "aws": "Amazon Web Services tools and resources",
    "docker": "Docker containerization tools",
    "kubernetes": "Kubernetes orchestration tools",
    "data-collection": "Data collection and gathering tools",
    "projects": "Project ideas and exercises",
    "frameworks": "Software development frameworks",
    "libraries": "Code libraries and packages",
    "tutorials": "Tutorials and learning guides",
    "papers": "Research papers and publications",
    "benchmarks": "Performance benchmarks and comparisons",
    "best-practices": "Development best practices and guidelines",
    "web-development": "Web development tools and resources",
    "data-analysis": "Data analysis tools and techniques",
    "journalism": "Data journalism and investigative resources",
    "health-data": "Health-related datasets and tools",
    "global": "Global and international data resources",
    "deployment": "Application deployment tools",
    "inference": "Model inference and serving",
    "experiment-tracking": "ML experiment tracking tools",
    "data-quality": "Data quality monitoring tools",
    "web-crawling": "Web crawling frameworks and tools",
    "annotation": "Data annotation and labeling tools",
    "self-hosted": "Self-hosted software alternatives",
    "creative-coding": "Creative coding and generative art",
    "openapi": "OpenAPI specification tools",
    "graphql": "GraphQL tools and resources",
    "grpc": "gRPC tools and resources",
    "rest": "REST API tools and guidelines",
    "embeddings": "Embedding generation and storage",
    "similarity-search": "Similarity search tools",
    "terraform": "Terraform infrastructure-as-code",
    "iac": "Infrastructure as code tools",
    "compliance": "Security compliance tools",
    "data-drift": "Data drift detection tools",
    "model-registry": "ML model versioning and registry",
    "model-serving": "ML model serving frameworks",
    "pipelines": "Data and ML pipeline tools",
    "orchestration": "Workflow orchestration tools",
    "linting": "Code and spec linting tools",
    "directory": "Resource directories and catalogs",
}


def generate_tag_description(tag):
    """Generate a description for a tag."""
    return TAG_DESCRIPTIONS.get(tag, f"Resources related to {tag.replace('-', ' ')}")


if __name__ == "__main__":
    main()
