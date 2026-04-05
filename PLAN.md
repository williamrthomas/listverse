# ListVerse Expansion Plan

## Current State (Phase 1 - Complete)

- **100 curated entries** across 9 categories
- Focus areas: Data, AI/ML, Agents, Visualization, Data Engineering, Developer Tools
- Structured JSON + CSV data with editorial metadata
- All entries verified against live GitHub repositories

### Category Distribution

| Category | Count |
|----------|-------|
| Meta Lists | 5 |
| AI & Machine Learning | 20 |
| AI Agents & Frameworks | 15 |
| Data Sources & Datasets | 10 |
| Data Visualization | 10 |
| Data Engineering | 10 |
| Developer Tools & Coding | 15 |
| Coding Agents & AI Dev Tools | 10 |
| Databases & Knowledge | 5 |

---

## Phase 2: Expand to ~200 Lists

**Goal**: Double coverage by adding new subcategories and deepening existing ones.

### New Subcategories to Add
- **NLP & Natural Language Processing** — tokenizers, NER, sentiment analysis, text generation
- **Computer Vision** — image classification, object detection, segmentation, OCR
- **MLOps & Model Deployment** — model serving, experiment tracking, feature stores
- **Cloud & Infrastructure** — AWS, GCP, Azure resources and tools
- **Security & Privacy** — cybersecurity tools, privacy-preserving ML, threat intelligence
- **Web Development** — React, Vue, Svelte, Next.js, CSS frameworks
- **Mobile Development** — iOS, Android, React Native, Flutter
- **API & Backend** — REST, GraphQL, gRPC, microservices

### Existing Categories to Deepen
- Data Engineering: Add Airflow, Dagster, Prefect-specific lists
- Databases: Add Redis, Elasticsearch, ClickHouse, DuckDB lists
- AI Agents: Track emerging agent frameworks and benchmarks
- Data Viz: Add Observable, Plotly, Matplotlib-specific lists

### Quality Criteria
- Minimum 50 stars (or exceptional content quality for niche lists)
- Last meaningful commit within 2 years
- Active issue tracker or contribution history
- Clear organization and navigation

---

## Phase 3: Relationship Graph

**Goal**: Build a structured graph of relationships between lists.

### Relationship Types
- **recommends**: List A explicitly links to List B
- **overlaps**: Lists A and B cover similar territory with >30% topic overlap
- **complements**: Lists A and B cover different aspects of the same domain
- **supersedes**: List A is a more comprehensive/maintained version of List B

### Implementation
- Add `relationships` field to schema with typed edges
- Generate a relationship JSON file (`data/relationships.json`)
- Create a visualization of the list graph (D3.js or Mermaid)
- Add "See Also" sections to README based on graph

### Data Model
```json
{
  "source": "awesome-python",
  "target": "awesome-python-data-science",
  "type": "complements",
  "notes": "awesome-python covers the full ecosystem; awesome-python-data-science goes deep on ML/data libraries"
}
```

---

## Phase 4: Automation & Freshness

**Goal**: Keep data accurate and current with automated checks.

### Automated Checks (GitHub Actions)
- **Star count updater**: Weekly cron job to refresh `stars_approx` via GitHub API
- **Activity checker**: Flag lists with no commits in 12+ months
- **Link validator**: Monthly check for 404'd or moved repositories
- **Entry count estimator**: Parse README.md files to approximate list sizes
- **License detector**: Auto-detect license changes

### Freshness Scoring
- Calculate a freshness score (0-100) based on:
  - Last commit date (40%)
  - Issue/PR activity (20%)
  - Star velocity (20%)
  - Contributor count trend (20%)
- Display freshness badges in README

### Notifications
- Open GitHub Issues when a tracked list is archived or deleted
- Monthly report PR with updated statistics

---

## Phase 5: Web Interface

**Goal**: Build a searchable, filterable web directory.

### Features
- Full-text search across names, descriptions, and editorial notes
- Filter by category, subcategory, stars, activity level
- Sort by stars, freshness, recently added
- Tag-based cross-referencing and exploration
- Responsive design for mobile browsing

### Technical Stack
- Static site generated from JSON data
- GitHub Pages hosting (zero cost)
- Client-side search (Lunr.js or Fuse.js)
- Minimal JavaScript, fast loading

### Pages
- Home: Featured lists, stats dashboard, category overview
- Browse: Filterable grid/list view of all entries
- Detail: Per-list page with editorial notes, related lists, freshness score
- Graph: Interactive relationship visualization
- About: Methodology, contribution guide, changelog

---

## Timeline

| Phase | Target | Status |
|-------|--------|--------|
| Phase 1 | 100 lists, JSON + CSV | Complete |
| Phase 2 | 200 lists, new categories | Planned |
| Phase 3 | Relationship graph | Planned |
| Phase 4 | Automation pipeline | Planned |
| Phase 5 | Web interface | Planned |
