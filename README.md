# How and Why 

- "Yet another todo list app"
- a **Reasoning Engine** for complex projects.
- Most task managers focus on *what* and *when*. "How and Why" focuses on **Why** and **How**.
- TeleoGraph ?
- Structuring projects as a **Directed Acyclic Graph (DAG)** of intent, it uses local AI to help you decompose goals, evaluate alternatives, and identify exactly why a project is "stuck."
- Toy project to test LLMs


## 🚀 Core Philosophy: The Why/How Axis

Every task in TeleoGraph is a **Node** linked by two primary vectors:
* **UPWARD (The "Why"):** Every task must justify its existence. If it doesn't link to a higher goal, it is "noise."
* **DOWNWARD (The "How"):** Tasks are decomposed into **Steps** (sequential) or **Alternatives** (choices). 

This structure allows the system to perform **Functional Analysis**, ensuring your actions align with your high-level intent.


## 🛠️ The Tech Stack

TeleoGraph is designed to be **local-first** and **minimalist**:

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Source of Truth** | [SQLModel](https://sqlmodel.tiangolo.com/) (SQLite) | Managing the graph structure & metadata |
| **Brain** | [Ollama](https://ollama.com/) | Natural language processing & reasoning |
| **Logic Engine** | Python (ReAct Pattern) | Orchestrating the agent's actions |
| **Vector Search** | [sqlite-vec](https://github.com/asg017/sqlite-vec) + Ollama `nomic-embed-text` | Semantic/Fuzzy search via 768-dim embeddings |
| **Interface** | Terminal / CLI | Fast, "loose-typing" interaction |



## 🏗️ Data Structure

A **Node** consists of:
* **ID:** TBD - Unique slug (e.g., `build-hifi-streamer`).
* **Description:** Short, punchy task name.
* **Context:** Long-form thoughts, notes, or research.
* **Status:** `Active`, `Stuck`, `Done`, or `Archived` (for rejected alternatives).


## 🤖 Features

### ✅ Currently Implemented (MVP)
* **Basic Task Management:** Add, modify, and search nodes via CLI
* **Data Portability:** JSON import/export for backup and migration
* **Smart Vector Embeddings:** 768-dimensional embeddings using `nomic-embed-text`, combining description + context + type
* **Semantic Search:** Fuzzy similarity search using sqlite-vec for intelligent task discovery

### 🚧 Planned Features
* **Semantic Retrieval:** Search for "the music thing" and find the "Hi-Fi Audio" project automatically using Vector Embeddings.
* **The "Stuck" Diagnostic:** Ask the LLM why a project isn't moving. It analyzes the graph to find missing "How" steps or contradictory "Why" goals.
* **Decision History:** When you choose one **Alternative** over another, TeleoGraph records the reasoning. If you get stuck later, the LLM can suggest revisiting the "Archived" paths.
* **Proactive Decomposition:** Add a high-level goal, and the LLM suggests three different ways ("How" branches) to achieve it.


## 🛠️ Quick Start

### 1. Install Ollama

**On Linux/macOS:**
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the embedding model (optimized for short texts, 768-dim)
ollama pull nomic-embed-text

# (Optional) Pull a reasoning model for future features
ollama pull qwen3:14b
```

**On Windows:**
Download from [ollama.ai](https://ollama.ai) and run the installer, then:
```bash
ollama pull nomic-embed-text
```

### 2. Install Python Dependencies
```bash
pip install -e .
```

### 3. Run the CLI
```bash
how_and_why --help
```

**Available Commands:**
- `how_and_why add` - Add a new task
- `how_and_why search --query "text"` - Search by exact text match
- `how_and_why find --query "semantic search"` - Semantic vector search
- `how_and_why modify --id <id>` - Modify an existing task
- `how_and_why export --output nodes.json` - Export all tasks to JSON
- `how_and_why import --input nodes.json` - Import tasks from JSON

## 📊 Current Implementation Status

- ✅ **Basic CRUD Operations:** Add, modify, search nodes via CLI
- ✅ **JSON Import/Export:** Backup and restore your data
- ✅ **Smart Vector Embeddings:** 768-dim using description + context + type for rich semantic understanding
- ✅ **Semantic Search:** Fuzzy search via `find` command for intelligent discovery
- 🚧 **Graph Reasoning:** LLM-powered analysis and suggestions (planned)

---

## 📝 Example Interaction

> **User:** "I'm stuck on the radio retrofit. The mechanical buttons are too expensive."
>
> **TeleoGraph:** "I've marked `mechanical-buttons` as **STUCK** (Reason: Budget). Your current 'Why' is `Industrial Haptics`. Should we explore **Alternative Hows**, such as 3D printing custom knobs or refurbishing vintage parts from a different model?"

---

## 🤖 Development

This project is being developed with the assistance of **GitHub Copilot**, an AI-powered coding assistant that helps with:
- Code generation and completion
- Architecture design and refactoring
- Documentation writing
- Debugging and testing
- Package management and dependency resolution

GitHub Copilot accelerates development while maintaining code quality and following best practices.
