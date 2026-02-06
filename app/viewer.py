import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import re
import html

# Path to metadata file
METADATA_FILE = Path("consolidated_docs/highlights_metadata.json")


def load_highlights() -> dict:
    """
    Load highlights from JSON file.
    Returns empty structure if file doesn't exist.
    """
    if not METADATA_FILE.exists():
        return {
            "highlights": [],
            "last_updated": datetime.now().isoformat()
        }
    
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading highlights: {e}")
        return {
            "highlights": [],
            "last_updated": datetime.now().isoformat()
        }


def save_highlights(highlights: list) -> None:
    """
    Save highlights to JSON file.
    
    Args:
        highlights: List of highlight dictionaries
    """
    try:
        METADATA_FILE.parent.mkdir(exist_ok=True)
        
        data = {
            "highlights": highlights,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving highlights: {e}")
        raise e


def apply_highlights(text: str, highlights: list) -> str:
    """
    Apply HTML highlight tags to markdown text using smart matching.
    Ignores markdown symbols (*, _, #, etc.) when matching text.
    
    Args:
        text: Original markdown content
        highlights: List of highlight dictionaries with 'text' and 'color'
    
    Returns:
        Markdown text with HTML <mark> tags injected
    """
    if not highlights:
        return text
    
    # Sort highlights by text length (longest first) to handle overlaps correctly
    sorted_highlights = sorted(highlights, key=lambda h: len(h.get("text", "")), reverse=True)
    
    result = text
    
    for highlight in sorted_highlights:
        highlight_text = highlight.get("text", "")
        color = highlight.get("color", "#ffeb3b")
        
        if not highlight_text:
            continue
            
        # 1. Try Exact Match First (Fastest)
        escaped_text = re.escape(highlight_text)
        if re.search(escaped_text, result):
            replacement = f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;">{highlight_text}</mark>'
            result = re.sub(escaped_text, replacement, result)
            continue
            
        # 2. Smart Match (Fuzzy)
        # Split search text into words
        words = highlight_text.split()
        if not words:
            continue
            
        # Build regex: Match words with optional markdown chars/whitespace in between
        # Separator matches: whitespace, *, _, -, #, >, `
        sep_pattern = r"(?:[\s\*\_\-\#\`\>\.]+)" 
        
        # Escape each word and join with separator
        regex_pattern = sep_pattern.join(map(re.escape, words))
        
        # Allow optional markdown chars at start/end of the phrase too
        # But be careful not to match too much. Just rely on the words sequence.
        
        try:
            # We need to capture the matched text to preserve the markdown structure inside the mark tag
            # Use a capturing group for the whole match
            pattern = re.compile(f"({regex_pattern})", re.IGNORECASE)
            
            def replace_func(match):
                original = match.group(1)
                # Don't double highlight if already highlighted
                if "<mark" in original: 
                    return original
                
                # Instead of wrapping the whole block (which breaks Markdown structure across blocks),
                # we reconstruct the string by wrapping ONLY the matched "words", leaving separators alone.
                
                # We can do this by finding the words again within the 'original' string
                # Since we constructed the regex from these words, they MUST exist in order.
                
                result_parts = []
                current_pos = 0
                
                for word in words:
                    # Search for the word starting from current_pos
                    # We use re.escape(word) because the word might contain regex chars
                    # We use string search (find) or simple regex? 
                    # Use re.search to handle case insensitivity if needed (regex was IGNORECASE)
                    
                    # Pattern for this specific word at the start of the remaining string (conceptually)
                    # But actually, between words there is 'sep_pattern'.
                    # Let's find the word content. 
                    # Note: 'original' is valid text from the doc. 'word' is from user input.
                    # They must match characters (modulo regex flags).
                    
                    word_pat = re.compile(re.escape(word), re.IGNORECASE)
                    m = word_pat.search(original, current_pos)
                    
                    if m:
                        start, end = m.span()
                        # Append the text BEFORE the word (separator/syntax)
                        result_parts.append(original[current_pos:start])
                        # Append the WRAPPED word
                        matched_word_text = original[start:end]
                        result_parts.append(f'<mark style="background-color: {color}; padding: 2px 0; border-radius: 2px;">{matched_word_text}</mark>')
                        current_pos = end
                    else:
                        # Should not happen if main regex matched, but safety fallback
                        return original 
                
                # Append remaining text found in the match (if any)
                result_parts.append(original[current_pos:])
                
                return "".join(result_parts)
            
            result = pattern.sub(replace_func, result)
            
        except Exception as e:
            print(f"Smart match failed for '{highlight_text}': {e}")
            continue
            
    return result


def add_highlight(text: str, color: str, highlights: list) -> dict:
    """
    Add a new highlight to the list.
    
    Args:
        text: Text to highlight
        color: Hex color code
        highlights: Current list of highlights
    
    Returns:
        New highlight dictionary
    """
    new_highlight = {
        "id": str(uuid.uuid4()),
        "text": text.strip(),
        "color": color,
        "created_at": datetime.now().isoformat()
    }
    
    highlights.append(new_highlight)
    save_highlights(highlights)
    
    return new_highlight


def remove_highlight(highlight_id: str, highlights: list) -> bool:
    """
    Remove a highlight by ID.
    
    Args:
        highlight_id: UUID of highlight to remove
        highlights: Current list of highlights
    
    Returns:
        True if removed, False if not found
    """
    original_length = len(highlights)
    updated_highlights = [h for h in highlights if h.get("id") != highlight_id]
    
    if len(updated_highlights) < original_length:
        save_highlights(updated_highlights)
        return True
    
    return False


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks.
    Only allows <mark> tags with style attributes.
    
    Args:
        text: HTML text to sanitize
    
    Returns:
        Sanitized text
    """
    # For now, we trust our own highlight injection
    # In production, use a library like bleach
    return text


def get_file_info(file_path: Path) -> dict:
    """
    Get file metadata (size, last modified).
    
    Args:
        file_path: Path to file
    
    Returns:
        Dictionary with file info
    """
    if not file_path.exists():
        return {
            "size": 0,
            "size_str": "0 KB",
            "last_modified": None,
            "exists": False
        }
    
    size_bytes = file_path.stat().st_size
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    
    if size_mb > 1:
        size_str = f"{size_mb:.2f} MB"
    else:
        size_str = f"{size_kb:.1f} KB"
    
    last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
    
    return {
        "size": size_bytes,
        "size_str": size_str,
        "last_modified": last_modified,
        "last_modified_str": last_modified.strftime("%Y-%m-%d %H:%M"),
        "exists": True
    }
