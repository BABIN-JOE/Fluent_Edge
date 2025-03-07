import language_tool_python

# Initialize LanguageTool
try:
    tool = language_tool_python.LanguageToolPublicAPI('en-US')
except Exception as e:
    print(f"⚠️ WARNING: Failed to initialize LanguageToolPublicAPI. Using local LanguageTool. Error: {e}")
    tool = language_tool_python.LanguageTool('en-US')

def check_grammar(text):
    if not text.strip():
        return []  # Return empty if no text

    # Capitalize first letter if it's lowercase
    text = text[0].upper() + text[1:] if text[0].islower() else text

    try:
        matches = tool.check(text)
        corrections = []

        for match in matches:
            # Ignore UPPERCASE_SENTENCE_START errors
            if match.ruleId == "UPPERCASE_SENTENCE_START":
                continue

            corrections.append({
                "sentence": match.context,
                "error": match.ruleId,
                "suggestion": match.replacements
            })

        return corrections
    except Exception as e:
        print(f"❌ ERROR: Grammar check failed. {e}")
        return []