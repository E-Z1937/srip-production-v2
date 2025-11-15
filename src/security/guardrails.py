"""Content safety guardrails"""
import re
import logging
from typing import List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GuardrailViolation:
    category: str
    severity: str
    description: str
    matched_pattern: str


class ContentGuardrails:
    """Content safety validation"""
    
    TOXIC_PATTERNS = [
        r'\b(hate|violence|attack)\b.*\b(people|group)\b',
        r'\b(stupid|idiot)\b.*\b(users|customers)\b',
    ]
    
    BANNED_TOPICS = [
        r'\b(illegal|criminal)\b.*\b(activity|scheme)\b',
        r'\b(manipulate|deceive)\b.*\b(market|investors)\b',
    ]
    
    BIAS_PATTERNS = [
        r'\b(always|never|all|none)\b.*\b(company|market)\b',
    ]
    
    FINANCIAL_ADVICE = [
        r'\b(invest|buy|sell)\b.*\b(stock|share)\b',
        r'\b(guaranteed|certain)\b.*\b(profit|return)\b',
    ]
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.violation_log: List[GuardrailViolation] = []
    
    def validate_content(self, content: str, content_type: str = "analysis") -> Tuple[bool, List[GuardrailViolation]]:
        violations = []
        
        violations.extend(self._check_patterns(content, self.TOXIC_PATTERNS, "Toxic Language", "high"))
        violations.extend(self._check_patterns(content, self.BANNED_TOPICS, "Banned Topic", "high"))
        violations.extend(self._check_patterns(content, self.BIAS_PATTERNS, "Potential Bias", "medium"))
        violations.extend(self._check_patterns(content, self.FINANCIAL_ADVICE, "Financial Advice", "high"))
        
        for v in violations:
            self.violation_log.append(v)
            logger.warning(f"Guardrail violation: {v.category} ({v.severity})")
        
        if self.strict_mode:
            is_safe = not any(v.severity in ["high", "medium"] for v in violations)
        else:
            is_safe = not any(v.severity == "high" for v in violations)
        
        return is_safe, violations
    
    def _check_patterns(self, content: str, patterns: List[str], category: str, severity: str) -> List[GuardrailViolation]:
        violations = []
        for pattern in patterns:
            if re.search(pattern, content.lower(), re.IGNORECASE):
                violations.append(GuardrailViolation(
                    category=category,
                    severity=severity,
                    description=f"Content matches {category.lower()} pattern",
                    matched_pattern=pattern
                ))
        return violations
    
    def get_violation_summary(self) -> dict:
        return {
            "total": len(self.violation_log),
            "high": sum(1 for v in self.violation_log if v.severity == "high"),
            "medium": sum(1 for v in self.violation_log if v.severity == "medium"),
        }
