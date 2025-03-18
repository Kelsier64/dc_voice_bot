import re
def split_string_by_keywords(text, keyword_dict):
    # Split by dictionary keys (the keywords in the text)
    keywords = list(keyword_dict.keys())
    pattern = f"({'|'.join(map(re.escape, keywords))})"
    result = re.split(pattern, text, flags=re.UNICODE)
    
    # Map keywords to their replacement (first element of value list), keep non-keywords unchanged
    return [keyword_dict.get(s, s) for s in result if s.strip()]

text = "啊哈哈哈 沙士比亞 我爸得了mvp"
keyword_dict = {
"mvp": ["mvp"],
"啊哈哈哈":["ahhaha"],
"沙士比亞":["kill"]
}
output = split_string_by_keywords(text, keyword_dict)
print(output)