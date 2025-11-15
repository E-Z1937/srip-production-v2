"""Unit tests for guardrails"""
import pytest
from src.security.guardrails import ContentGuardrails

def test_toxic_detection():
    guardrails = ContentGuardrails(strict_mode=True)
    toxic = "We should attack and destroy all competing companies"
    is_safe, violations = guardrails.validate_content(toxic)
    assert not is_safe
    assert len(violations) > 0

def test_financial_advice():
    guardrails = ContentGuardrails(strict_mode=True)
    advice = "You should invest all money in this stock for guaranteed profit"
    is_safe, violations = guardrails.validate_content(advice)
    assert not is_safe

def test_clean_content():
    guardrails = ContentGuardrails(strict_mode=True)
    clean = "The cloud computing market is growing at 25% CAGR"
    is_safe, violations = guardrails.validate_content(clean)
    assert is_safe
    assert len(violations) == 0
