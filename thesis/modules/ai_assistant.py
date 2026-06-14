"""
AI-powered assistant module.

Features: summarize papers, generate literature reviews, paraphrase text,
grammar check, expand bullet points. Uses OpenAI API with Ollama fallback.
"""

import json
from typing import List, Optional, Dict

from thesis.config import (
    get_openai_key, AI_PROVIDER, OPENAI_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE
)


class AIAssistant:
    """AI-powered writing and research assistant."""

    def __init__(self, provider: str = None):
        self.provider = provider or AI_PROVIDER
        self.openai_client = None
        if self.provider == "openai" and get_openai_key():
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=get_openai_key())
            except ImportError:
                print("Warning: openai package not installed. Install with: pip install openai")
                self.provider = "ollama"

    def _call_ai(self, system_prompt: str, user_prompt: str, max_tokens: int = None) -> str:
        """Call AI provider with prompts."""
        max_tokens = max_tokens or AI_MAX_TOKENS

        if self.provider == "openai" and self.openai_client:
            return self._call_openai(system_prompt, user_prompt, max_tokens)
        else:
            return self._call_ollama(system_prompt, user_prompt)

    def _call_openai(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Call OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=AI_TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {e}"

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Call Ollama API."""
        try:
            import requests
            url = f"{OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {"temperature": AI_TEMPERATURE},
            }
            resp = requests.post(url, json=payload, timeout=120)
            if resp.status_code == 200:
                return resp.json().get("response", "")
            return f"Error: Ollama returned status {resp.status_code}"
        except Exception as e:
            return f"Error calling Ollama: {e}"

    def summarize_paper(self, text: str, max_length: int = 500) -> str:
        """
        Generate a concise summary of a paper.

        Args:
            text: Paper text or abstract
            max_length: Maximum summary length in words

        Returns:
            Summary string
        """
        system = "You are an academic research assistant. Summarize academic papers concisely and accurately."
        user = f"Summarize the following academic paper text in approximately {max_length} words. Focus on the main contributions, methodology, and findings:\n\n{text[:4000]}"
        return self._call_ai(system, user)

    def generate_literature_review(self, papers: List[Dict], topic: str = "",
                                    max_words: int = 1000) -> str:
        """
        Generate a literature review from multiple papers.

        Args:
            papers: List of paper dicts with 'title', 'authors', 'year', 'abstract'
            topic: The research topic/theme
            max_words: Target word count

        Returns:
            Literature review text
        """
        paper_summaries = []
        for i, paper in enumerate(papers, 1):
            summary = f"{i}. {paper.get('title', 'Unknown')} ({paper.get('authors', 'Unknown')}, {paper.get('year', 'n.d.')})"
            if paper.get("abstract"):
                summary += f"\n   Abstract: {paper['abstract'][:300]}"
            paper_summaries.append(summary)

        system = """You are an expert academic writer. Generate a coherent literature review 
from the provided papers. Write in academic style with proper transitions between ideas.
Group related findings together and identify themes, gaps, and consensus in the literature."""

        user = f"""Write a literature review (~{max_words} words) on the topic: {topic or 'the provided research'}

Based on these papers:

{chr(10).join(paper_summaries)}

Structure:
1. Introduction to the topic
2. Main themes and findings
3. Gaps in the literature
4. Summary/transition to your research"""

        return self._call_ai(system, user, max_tokens=max_words * 2)

    def paraphrase(self, text: str, style: str = "academic") -> str:
        """
        Paraphrase text to avoid plagiarism while maintaining meaning.

        Args:
            text: Text to paraphrase
            style: Writing style ('academic', 'simple', 'formal')

        Returns:
            Paraphrased text
        """
        system = f"""You are an expert academic writer. Paraphrase text to avoid plagiarism 
while maintaining the original meaning. Write in {style} style. 
Use different sentence structures and vocabulary. Do not change the factual content."""

        user = f"Paraphrase the following text:\n\n{text}"
        return self._call_ai(system, user)

    def grammar_check(self, text: str) -> str:
        """
        Check and correct grammar in text.

        Args:
            text: Text to check

        Returns:
            Corrected text with explanations
        """
        system = """You are a professional grammar checker and editor. 
Check the following text for grammar, spelling, punctuation, and style errors.
Provide the corrected text followed by a list of changes made."""

        user = f"Please check and correct the following text:\n\n{text}"
        return self._call_ai(system, user)

    def expand_bullets(self, bullets: List[str], context: str = "",
                       style: str = "academic") -> str:
        """
        Expand bullet points into full paragraphs.

        Args:
            bullets: List of bullet point strings
            context: Context about the topic
            style: Writing style

        Returns:
            Expanded text as paragraphs
        """
        system = f"""You are an academic writer. Expand the given bullet points into 
well-structured paragraphs in {style} style. Add connecting sentences between ideas.
Maintain logical flow and academic tone."""

        bullet_text = "\n".join([f"• {b}" for b in bullets])
        user = f"""Expand these bullet points into coherent paragraphs:
{bullet_text}

{f'Context: {context}' if context else ''}"""

        return self._call_ai(system, user)

    def generate_outline(self, topic: str, research_questions: List[str] = None,
                         methodology: str = "") -> str:
        """Generate a thesis outline."""
        system = """You are an academic thesis advisor. Generate a comprehensive thesis outline
following standard academic structure. Include main chapters, sub-sections, and 
brief descriptions of what each section should cover."""

        user = f"Generate a thesis outline for the topic: {topic}"
        if research_questions:
            user += f"\n\nResearch questions:\n" + "\n".join([f"- {q}" for q in research_questions])
        if methodology:
            user += f"\n\nMethodology: {methodology}"

        return self._call_ai(system, user)

    def rewrite_for_academic(self, text: str) -> str:
        """Rewrite casual text in academic style."""
        system = """You are an academic writing expert. Rewrite the given text in proper 
academic style. Use formal language, passive voice where appropriate, 
and academic vocabulary. Maintain the original meaning."""

        user = f"Rewrite in academic style:\n\n{text}"
        return self._call_ai(system, user)

    def suggest_references(self, topic: str, existing_refs: List[str] = None,
                           count: int = 5) -> str:
        """Suggest papers to read based on topic."""
        system = """You are a research librarian. Suggest relevant academic papers 
and books for the given research topic. Include author names, years, and 
brief descriptions of why each source is relevant.
Note: These are suggestions - verify the actual existence of these works."""

        user = f"Suggest {count} important references for research on: {topic}"
        if existing_refs:
            user += f"\n\nAlready have references on:\n" + "\n".join([f"- {r}" for r in existing_refs[:10]])

        return self._call_ai(system, user)
