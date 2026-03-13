"""Tests for GuideGenerator class"""

import pytest
from pathlib import Path
from unittest.mock import patch
from src.guide_generator import GuideGenerator


def test_guide_generator_creates_file():
    """Test that generate creates the guide file"""
    generator = GuideGenerator()
    output_path = Path("output/test_guide.md")

    # Ensure file doesn't exist
    if output_path.exists():
        output_path.unlink()

    generator.generate(output_path)

    assert output_path.exists()
    assert output_path.is_file()

    # Cleanup
    output_path.unlink()


def test_guide_generator_content():
    """Test that the guide contains expected sections"""
    generator = GuideGenerator()
    output_path = Path("output/test_guide_content.md")

    generator.generate(output_path)

    content = output_path.read_text()

    # Check for key sections
    assert "Profit Margin" in content
    assert "Operating Margin" in content
    assert "Free Cash Flow" in content
    assert "Return on Invested Capital" in content or "ROIC" in content
    assert "Interest Coverage" in content
    assert "Yahoo Finance" in content

    # Cleanup
    output_path.unlink()


def test_guide_generator_creates_parent_directory():
    """Test that parent directory is created if it doesn't exist"""
    generator = GuideGenerator()
    output_path = Path("test_output/nested/guide.md")

    # Ensure directory doesn't exist
    if output_path.parent.exists():
        if output_path.exists():
            output_path.unlink()
        try:
            output_path.parent.rmdir()
        except OSError:
            pass

    generator.generate(output_path)

    assert output_path.parent.exists()
    assert output_path.exists()

    # Cleanup
    if output_path.exists():
        output_path.unlink()
    try:
        output_path.parent.rmdir()
        output_path.parent.parent.rmdir()
    except OSError:
        pass


def test_guide_generator_default_path():
    """Test that default output path is output/guide.md"""
    generator = GuideGenerator()
    output_path = Path("output/guide.md")

    # Ensure file doesn't exist
    if output_path.exists():
        output_path.unlink()

    generator.generate()

    assert output_path.exists()

    # Cleanup
    output_path.unlink()


def test_guide_generator_content_accuracy():
    """Test that guide contains accurate formulas and instructions"""
    generator = GuideGenerator()
    output_path = Path("output/test_accuracy.md")

    generator.generate(output_path)
    content = output_path.read_text()

    # Verify formulas are present
    assert (
        "Net Income / Total Revenue" in content
        or "Net Income ÷ Total Revenue" in content
    )
    assert (
        "Operating Income / Total Revenue" in content
        or "Operating Income ÷ Total Revenue" in content
    )
    assert "Free Cash Flow" in content
    assert "NOPAT" in content or "Operating Income × (1 - tax rate)" in content
    assert "EBIT / Interest Expense" in content or "EBIT ÷ Interest Expense" in content

    # Cleanup
    output_path.unlink()
