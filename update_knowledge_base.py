#!/usr/bin/env python3
"""
Script to update the Ledger Bot knowledge base with content from oracle-gl-publisher repo
"""
import os
from pathlib import Path

GL_PUBLISHER_PATH = Path.home() / "IdeaProjects" / "oracle-gl-publisher"
KNOWLEDGE_BASE_PATH = Path.home() / "ledger-bot-app" / "knowledge_base.txt"

def read_file(path):
    """Read file content safely"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def append_to_knowledge_base(content, section_title):
    """Append content to knowledge base"""
    with open(KNOWLEDGE_BASE_PATH, 'a') as f:
        f.write(f"\n\n## {section_title}\n\n")
        f.write(content)
    print(f"✅ Added: {section_title}")

def main():
    print("Updating Ledger Bot knowledge base...")
    print(f"Reading from: {GL_PUBLISHER_PATH}")
    print(f"Writing to: {KNOWLEDGE_BASE_PATH}\n")
    
    # Add module READMEs
    modules = ["api", "queue-processor", "audit-status-processor", "db"]
    for module in modules:
        readme_path = GL_PUBLISHER_PATH / module / "README.md"
        if readme_path.exists():
            content = read_file(readme_path)
            if content:
                append_to_knowledge_base(content, f"{module.upper()} Module Details")
    
    # Add important ADRs
    adr_files = [
        "0007-idempotency-key-meaning.md",
        "0010-Reversals-in-GL-Publisher.md",
        "0003-add-oracle-import-check-logic.md"
    ]
    
    for adr_file in adr_files:
        adr_path = GL_PUBLISHER_PATH / "docs" / "adr" / adr_file
        if adr_path.exists():
            content = read_file(adr_path)
            if content:
                append_to_knowledge_base(content, f"ADR: {adr_file.replace('.md', '')}")
    
    # Add a simple Impact Builder example
    print("\n✨ Knowledge base updated!")
    print("Restart the bot to load the new knowledge.")

if __name__ == "__main__":
    main()
