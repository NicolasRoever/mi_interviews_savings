def _extract_content(resp) -> str:
    """
    Safely extract assistant content from either object- or dict-like responses.
    """
    try:
        # SDK object style
        return resp.choices[0].message.content
    except Exception:
        # Dict style fallback
        return resp["choices"][0]["message"]["content"]