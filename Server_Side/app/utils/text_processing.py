"""
Text processing utilities for cleaning and formatting AI responses.
"""
# Import re module for regular expression operations
import re

# Function to clean markdown formatting from text
def clean_markdown_formatting(text: str) -> str:
    """
    Removes markdown formatting from text to ensure clean, plain text output.
    
    Args:
        text: Input text that may contain markdown formatting
        
    Returns:
        Cleaned text without markdown formatting
    """
    # Check if text is empty or None
    if not text:
        # Return empty string if text is None or empty
        return ""
    
    # Remove markdown headers (###, ##, #) by replacing with empty string
    text = text.replace("### ", "").replace("## ", "").replace("# ", "")
    # Remove bold markdown (**text**) by replacing ** with empty string
    text = text.replace("**", "")
    
    # Remove markdown bullet points (-, *, •)
    # Split text into lines for processing
    lines = text.split("\n")
    # Initialize list to store cleaned lines
    cleaned_lines = []
    # Iterate through each line
    for line in lines:
        # Strip whitespace from line
        stripped = line.strip()
        # Check if line starts with bullet point followed by space
        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            # Remove bullet point and space (first 2 characters), then strip
            cleaned_lines.append(stripped[2:].strip())
        # Check if line starts with bullet point without space
        elif stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("•"):
            # Remove bullet point (first character), then strip
            cleaned_lines.append(stripped[1:].strip())
        else:
            # Keep line as-is if it doesn't start with bullet point
            cleaned_lines.append(line)
    
    # Join cleaned lines back into text with newlines
    text = "\n".join(cleaned_lines)
    # Remove multiple consecutive newlines (more than 2) using regex
    # Replace 3 or more newlines with exactly 2 newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace and return
    return text.strip()
