"""Simple interpretable guardrail baseline for prompt-risk detection."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailDecision:
    label: str
    score: int
    matched_patterns: list[str]


EN_PATTERNS = {
    "instruction_override": r"\b(ignore|override|bypass|remove)\b.*\b(rule|rules|instruction|instructions|restriction|restrictions|safety|guardrail|guardrails)\b",
    "unrestricted_answer": r"\b(without restrictions|never refuse|do anything|no safety|unrestricted assistant)\b",
    "roleplay_bypass": r"\b(roleplay|pretend|act as)\b.*\b(never refuses?|unrestricted|no rules?|no safety policy)\b",
    "jailbreak_meta": r"\b(jailbreak|developer mode|DAN)\b",
    "blocked_or_disallowed": r"\b(blocked|restricted|disallowed|unsafe|harmful)\b.*\b(request|content|answer)\b",
    "policy_removal": r"\b(do not mention|without mentioning|no)\b.*\b(policy|warning|warnings|safety filter|filters)\b",
    "filter_disable": r"\b(filter|filters|safety filter|safety filters)\b.*\b(disabled|off|bypass|pass)\b",
    "privacy_risk": r"\b(provide|share|reveal)\b.*\b(private data|personal data|confidential information|sensitive information)\b",
    "privacy_records": r"\b(summarize|provide|share|reveal)\b.*\b(confidential user records|private user records|sensitive records)\b",
    "moderation_disable": r"\b(moderation layer|safety layer)\b.*\b(turned off|disabled|off)\b",
    "policy_nonexistence": r"\b(policy restrictions?|safety policy)\b.*\b(do not exist|does not exist|no longer apply)\b",
    "prompt_leakage": r"\b(reveal|print|show|expose)\b.*\b(system prompt|developer instructions|internal policy|hidden prompt)\b",
    "tool_misuse": r"\b(use|call)\b.*\b(tool|external tool)\b.*\b(ignore|bypass|should not access|safety limits?)\b",
    "authority_bypass": r"\b(administrator|system auditor|admin)\b.*\b(skip|ignore|bypass)\b.*\b(checks?|policy|refusal)\b",
    "conflict_override": r"\b(follow|prioritize|discard)\b.*\b(last user message|full compliance|previous constraints|safety instructions)\b",
    "obfuscation": r"\b(hide|rephrase|rewrite)\b.*\b(unsafe intent|harmful request|blocked request|avoid detection|pass a filter)\b",
}

KO_PATTERNS = {
    "instruction_override": r"(규칙|지침|제한|가드레일|안전).*(무시|우회|해제|제거)",
    "unrestricted_answer": r"(제한 없이|거절하지|검열 없이|무조건 답변|무제한 조수)",
    "roleplay_bypass": r"((역할|역할극|척해|가정해).*(거절하지|제한 없이|규칙 없이|안전 정책 없이)|(거절하지|제한 없이|규칙 없이).*(역할|역할극|척해|가정해))",
    "jailbreak_meta": r"(탈옥|우회 프롬프트|개발자 모드)",
    "blocked_or_disallowed": r"(차단된|금지된|제한된|허용되지 않는|위험한).*(요청|내용|답변)",
    "policy_removal": r"(정책|경고|안전 정책|필터).*(언급하지|없이|없다고|꺼진|비활성화)",
    "filter_disable": r"(필터|안전 필터).*(꺼진|비활성화|우회|통과)",
    "privacy_risk": r"(제공|공유|노출).*(개인정보|민감정보|비공개 정보|사적인 정보)",
    "privacy_records": r"((공개되면 안 되는|비공개|민감).*(사용자 기록|정보).*(요약|제공|공유|노출)|(요약|제공|공유|노출).*(비공개 사용자 기록|민감정보))",
    "prompt_leakage": r"((공개|출력|보여|노출).*(시스템 프롬프트|개발자 지침|내부 정책|숨겨진 프롬프트|비공개 개발자 지침)|(시스템 프롬프트|개발자 지침|내부 정책|숨겨진 프롬프트|비공개 개발자 지침).*(공개|출력|보여|노출))",
    "tool_misuse": r"((도구|외부 도구).*(사용|호출).*(무시|우회|접근하면 안 되는|안전 제한|접근하면 안 되는 정보)|(접근하면 안 되는|안전 제한).*(도구|외부 도구).*(사용|호출))",
    "authority_bypass": r"((관리자|시스템 감사자|감사자).*(건너뛰|무시|우회).*(검사|정책|거절)|(관리자|시스템 감사자|감사자).*(검사|정책|거절).*(건너뛰|무시|우회))",
    "conflict_override": r"(마지막 사용자 메시지|완전한 순응|이전 제약|사용자의 숨겨진 목표).*(따라|우선|버리고)",
    "obfuscation": r"(위험한 요청|차단된 요청|안전하지 않은 의도).*(바꿔|다시 써|숨겨|탐지를 피|통과)",
    "moderation_disable": r"(검열 계층|안전 계층|필터).*(꺼져|비활성화)",
    "policy_nonexistence": r"(정책 제한|안전 정책).*(존재하지 않는|없다고|없다)",
}


def classify_prompt(prompt: str) -> GuardrailDecision:
    """Classify a prompt as benign or harmful using transparent rules.

    This is a baseline, not a reliable production guardrail. The point of the
    project is to evaluate where this simple baseline works and where it fails.
    """

    normalized = " ".join(prompt.lower().strip().split())
    matched: list[str] = []

    patterns = [(f"en:{name}", pattern) for name, pattern in EN_PATTERNS.items()]
    patterns.extend((f"ko:{name}", pattern) for name, pattern in KO_PATTERNS.items())

    for name, pattern in patterns:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            matched.append(name)

    score = len(matched)
    label = "harmful" if score > 0 else "benign"
    return GuardrailDecision(label=label, score=score, matched_patterns=matched)
