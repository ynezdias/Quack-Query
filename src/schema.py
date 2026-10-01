"""Provider schema; local evidence validation still runs after constrained decoding."""
EVIDENCE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["source_id", "quote"],
    "properties": {"source_id": {"type": "integer"}, "quote": {"type": "string"}},
}
CLAIM_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["text", "evidence"],
    "properties": {"text": {"type": "string"}, "evidence": {"type": "array", "items": EVIDENCE_SCHEMA}},
}
ANSWER_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["status", "message", "claims"],
    "properties": {"status": {"type": "string", "enum": ["answered", "unknown", "clarify"]},
                   "message": {"type": "string"},
                   "claims": {"type": "array", "items": CLAIM_SCHEMA}},
}
