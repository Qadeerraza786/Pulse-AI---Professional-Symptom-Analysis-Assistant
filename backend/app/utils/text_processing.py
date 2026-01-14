"""
Text processing utilities for cleaning and formatting AI responses.
"""
import re

def clean_markdown_formatting(text: str) -> str:
    """
    Removes markdown formatting from text to ensure clean, plain text output.
    
    Args:
        text: Input text that may contain markdown formatting
        
    Returns:
        Cleaned text without markdown formatting
    """
    if not text:
        return ""
    
    # Remove markdown headers (###, ##, #)
    text = text.replace("### ", "").replace("## ", "").replace("# ", "")
    # Remove bold markdown (**text**)
    text = text.replace("**", "")
    
    # Remove markdown bullet points (-, *, •)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            cleaned_lines.append(stripped[2:].strip())
        elif stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("•"):
            cleaned_lines.append(stripped[1:].strip())
        else:
            cleaned_lines.append(line)
    
    text = "\n".join(cleaned_lines)
    # Remove multiple consecutive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace
    return text.strip()
