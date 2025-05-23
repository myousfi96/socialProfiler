"""
UI styles and CSS for the Streamlit application.
"""

# Custom CSS for components like tags and tweet cards
CUSTOM_CSS = """
<style>
.tag {
    background: #3A3B40;
    color: #F2F2F2;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    margin: 4px 4px;
    display: inline-block;
    white-space: nowrap;
}
.tweet-card {
    background-color: #111214;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.75rem;
}
</style>
"""

# HTML for sentiment legend
SENTIMENT_LEGEND_HTML = """
<div style='display:flex;gap:18px;margin-top:4px;font-size:0.9rem'>
<div><span style='display:inline-block;width:14px;height:14px;
                  background:#dc3545;border-radius:3px;
                  margin-right:6px'></span>Negative</div>
<div><span style='display:inline-block;width:14px;height:14px;
                  background:#ffc107;border-radius:3px;
                  margin-right:6px'></span>Neutral</div>
<div><span style='display:inline-block;width:14px;height:14px;
                  background:#28a745;border-radius:3px;
                  margin-right:6px'></span>Positive</div>
</div>
"""

def render_tags(keywords):
    """
    Render a list of keywords as HTML tags.
    
    Args:
        keywords: List of keyword strings
        
    Returns:
        HTML string with formatted tags
    """
    if not keywords:
        return ""
    
    return "".join(f"<span class='tag'>{kw}</span>" for kw in keywords[:5]) 