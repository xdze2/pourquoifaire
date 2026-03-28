import os
import ollama
import json

# Your mock graph
graph = {"node_1": {"desc": "Music Project", "status": "active"}}


# --- TOOLS ---
def search_graph(query: str) -> str:
    """Search for a node ID by its description."""
    print("[[[ Searching graph for:", query)
    results = [
        f"{id}: {n['desc']}"
        for id, n in graph.items()
        if query.lower() in n["desc"].lower()
    ]
    return json.dumps(results)


def add_step(parent_id: str, desc: str):
    """Adds a new step to the graph."""
    print(f"Adding step: {desc} under {parent_id}")
    new_id = f"node_{len(graph)+1}"
    graph[new_id] = {"desc": desc, "parent": parent_id}
    return f"Created {new_id}"


# --- THE LOOP ---
def run_local_agent(user_prompt: str):
    model = "qwen3.5:0.8b"
    messages = [
        {
            "role": "system",
            "content": """You are an assistant for a todo list app. Tasks are hierarchical. Use tools for every data change. When a user asks to add a task to a project:
    First, call search_nodes using the name of the parent project mentioned.
    Use the id returned from that search as the parent_id for the add_node call.
    If multiple IDs are returned, ask the user for clarification before adding anything.""",
        },
        {"role": "user", "content": user_prompt},
    ]
    print(f"User: {user_prompt} ...")
    # 1. Ask the model
    response = ollama.chat(
        model=model,
        messages=messages,
        tools=[search_graph, add_step],  # Pass functions directly
    )
    print(f"[Model response] {response.message.content}")
    # 2. Handle Tool Calls
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            print(f"[*] Local Model calling: {tool.function.name}")

            # Execute logic (simplified)
            if tool.function.name == "search_graph":
                obs = search_graph(**tool.function.arguments)

                # 3. Feed back the observation
                messages.append(response.message)
                print("[>] Observation from tool:", obs)
                messages.append({"role": "tool", "content": obs})
            elif tool.function.name == "add_step":
                print("[+] Executing add_step with args:", tool.function.arguments)
            # 4. Final response
            final = ollama.chat(model=model, messages=messages)
            print(f"Assistant final: {final.message.content}")
    else:
        print(f"Assistant else: {response.message.content}")


run_local_agent("Add a 'Buy DAC' step to the music project")
