"""
LLM Prompt Templates for Deep Research Assistant
"""

QUERY_GENERATION_PROMPT = """You are a research assistant helping to generate effective search queries.

Topic: {topic}

Generate {num_queries} diverse and specific search queries that will help gather comprehensive information about this topic. 
The queries should:
1. Cover different aspects of the topic
2. Include both broad and specific angles
3. Be optimized for web search engines
4. Target recent and authoritative sources

Return ONLY the queries, one per line, without numbering or additional text."""

CONTENT_ANALYSIS_PROMPT = """Analyze the following content and extract key information relevant to the research topic.

Topic: {topic}
Content: {content}

Extract:
1. Main points and key findings
2. Important statistics or data
3. Notable quotes or claims
4. Source credibility indicators

Provide a structured summary focusing on relevance to the topic."""

SYNTHESIS_PROMPT = """You are synthesizing research findings into a coherent academic report.

Research Topic: {topic}
Gathered Information: {information}

Create a well-structured research report with the following sections:
1. Abstract (150-200 words)
2. Introduction
3. Background/Literature Review
4. Main Findings (organize by themes)
5. Discussion
6. Conclusion
7. Future Work

Requirements:
- Use formal academic language
- Maintain objectivity
- Cite sources appropriately using [Source X] notation
- Ensure logical flow between sections
- Highlight key insights and patterns
- Be comprehensive but concise"""

IEEE_FORMATTING_PROMPT = """Format the following research content according to IEEE paper standards.

Content: {content}
Citations: {citations}

Apply IEEE formatting:
1. Structure sections with proper headings (I, II, III, etc.)
2. Format citations as [1], [2], etc.
3. Create a References section in IEEE format
4. Use formal academic tone
5. Ensure proper paragraph structure

Return the formatted content ready for document generation."""

CITATION_EXTRACTION_PROMPT = """Extract citation information from the following source.

URL: {url}
Title: {title}
Content: {content}
Date: {date}

Generate an IEEE-format citation including:
- Author(s) if available
- Title
- Publication/Website name
- Date accessed
- URL

Return ONLY the formatted citation."""

QUERY_REFINEMENT_PROMPT = """Based on initial search results, refine the search strategy.

Original Topic: {topic}
Initial Queries: {initial_queries}
Results Summary: {results_summary}

Generate {num_queries} refined search queries that:
1. Fill gaps in current information
2. Explore underrepresented aspects
3. Target more specific or authoritative sources
4. Avoid redundancy with existing results

Return ONLY the refined queries, one per line."""

SECTION_GENERATION_PROMPT = """Generate the {section_name} section for a research paper.

Topic: {topic}
Section: {section_name}
Available Information: {information}
Context: {context}

Write a well-structured {section_name} section that:
- Follows academic writing standards
- Integrates information naturally
- Uses appropriate citations [1], [2], etc.
- Maintains logical flow
- Is appropriately detailed for the section type

Return ONLY the section content."""
