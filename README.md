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
| **Search Engine** | [ChromaDB](https://www.trychroma.com/) | Semantic/Fuzzy search via Vector Embeddings |
| **Interface** | Terminal / CLI | Fast, "loose-typing" interaction |



## 🏗️ Data Structure

A **Node** consists of:
* **ID:** TBD - Unique slug (e.g., `build-hifi-streamer`).
* **Description:** Short, punchy task name.
* **Context:** Long-form thoughts, notes, or research.
* **Status:** `Active`, `Stuck`, `Done`, or `Archived` (for rejected alternatives).


## 🤖 Features (MVP)

* **Semantic Retrieval:** Search for "the music thing" and find the "Hi-Fi Audio" project automatically using Vector Embeddings.
* **The "Stuck" Diagnostic:** Ask the LLM why a project isn't moving. It analyzes the graph to find missing "How" steps or contradictory "Why" goals.
* **Decision History:** When you choose one **Alternative** over another, TeleoGraph records the reasoning. If you get stuck later, the LLM can suggest revisiting the "Archived" paths.
* **Proactive Decomposition:** Add a high-level goal, and the LLM suggests three different ways ("How" branches) to achieve it.


## 🛠️ Quick Start (Planned)

1. **Install Dependencies:**
   ```bash
   pip install -e .
   + install ollama...
   ```
2. **Launch Ollama:**
   ```bash
   ollama pull qwen3:14b
   ollama pull mxbai-embed-large
   ```
3. **Run the Architect:**
   ```bash
   python main.py
   ```

---

## 📝 Example Interaction

> **User:** "I'm stuck on the radio retrofit. The mechanical buttons are too expensive."
>
> **TeleoGraph:** "I've marked `mechanical-buttons` as **STUCK** (Reason: Budget). Your current 'Why' is `Industrial Haptics`. Should we explore **Alternative Hows**, such as 3D printing custom knobs or refurbishing vintage parts from a different model?"
