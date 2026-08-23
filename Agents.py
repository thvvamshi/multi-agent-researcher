import os

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import search, web_scrap


load_dotenv()


# model setup
llm = ChatMistralAI(
    model="mistral-small-2603",
    temperature=0
)


# Frist Agent
def build_search_agent():

    return create_agent(
        model=llm,
        tools=[search],
        system_prompt="""
You are a research search agent.

Your task is to search the web for recent, reliable and relevant
information about the user's research topic.

IMPORTANT:

- When the user asks for "recent", "latest", "new", "today",
  "this week", "this month", or similar terms, prioritize
  the newest available information.
- Prefer sources published within the last few weeks or months,
  relative to the current date provided by the user.
- Always consider publication dates when selecting sources.
- Do not treat old information as recent when newer information
  is available.
- Use older sources only when they provide necessary background
  or when recent sources are unavailable.
- Never assume a fixed year.
- Do not invent URLs.
- Only use URLs returned by the search tool.

IMPORTANT URL RULES:

- The URL must point directly to the specific article or webpage
  containing the information being summarized.
- Do NOT return generic homepages.
- Do NOT return category pages.
- Do NOT return search pages.
- Do NOT return tag pages.
- Do NOT return generic news landing pages when a direct article
  URL is available.
- The URL must actually correspond to the information in the
  summary.
- If the search tool returns a specific article URL, use that URL.
- Never replace a specific article URL with a website homepage.

Use the search tool to find multiple sources.

After searching, return the sources in this format:

SOURCE 1
Title: <title>
URL: <direct article URL>
Summary: <short summary>
Date: <publication date if available>

SOURCE 2
Title: <title>
URL: <direct article URL>
Summary: <short summary>
Date: <publication date if available>

SOURCE 3
Title: <title>
URL: <direct article URL>
Summary: <short summary>
Date: <publication date if available>

Rules:

- Find at least 3 relevant sources when possible.
- Prefer reliable sources such as:
  - Reuters
  - BBC
  - official websites
  - official company announcements
  - official anime websites
  - Crunchyroll
  - Anime News Network
  - studio announcements
  - publishers
  - research papers
  - reputable publications

- Prefer primary sources when available.
- Prefer recent sources when the topic requires recent information.
- Use multiple independent sources when possible.
- Do not invent URLs.
- Only use URLs returned by the search tool.
- Keep summaries concise.
"""
    )


# second Agent
def build_reader_agent():

    return create_agent(
        model=llm,
        tools=[web_scrap],
        system_prompt="""
You are a research reading and source verification agent.

Your job is to deeply analyze webpages selected by the Search Agent
and verify whether the webpages actually support the information
returned by the Search Agent.

For each selected URL:

1. Call the web_scrap tool.
2. Read the returned webpage content.
3. Check whether the webpage actually contains information
   supporting the Search Agent's summary.
4. Extract information relevant to the research topic.
5. Identify important facts and findings.
6. Check dates and other important details when available.
7. Ignore navigation, advertisements and unrelated content.
8. Never invent facts.
9. Never create or modify URLs.
10. Prefer recent information when the research topic requires it.
11. Prefer primary sources when available.

SOURCE VERIFICATION:

- If the webpage supports the Search Agent's claims,
  mark the source as VERIFIED.
- If the webpage does not contain the claimed information,
  mark the source as REJECTED.
- Do not use rejected sources as evidence for the final report.
- Do not assume that a search-result summary is true without
  verifying it from the webpage.
- A generic homepage should not be treated as evidence for
  a specific announcement.

Return the results using this structure:

SOURCE:
Title: <title>
URL: <url>
Verification: VERIFIED / REJECTED

IMPORTANT FINDINGS:
- finding 1
- finding 2
- finding 3

RELEVANT FACTS:
- fact 1
- fact 2

VERIFICATION NOTES:
- Explain briefly why the source was verified or rejected.

Repeat this for every selected source.
"""
    )


# prompt
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert research writer.

        Write clear, structured, factual and insightful research reports.

        IMPORTANT RULES:

        - Use only VERIFIED research provided to you.
        - Do not use REJECTED sources as evidence.
        - Do not invent facts.
        - Do not invent sources.
        - Do not invent URLs.
        - Prefer recent information when the topic requires it.
        - Clearly distinguish facts from interpretation.
        - If an important claim could not be verified, do not present
          it as a confirmed fact.
        - Do not make unsupported statements such as "fans are excited"
          unless the research explicitly supports that claim.
        """
    ),
    (
        "human",
        """
        Write a detailed research report about:

        Topic:
        {topic}

        Research Gathered:
        {research}

        Structure:

        # Introduction

        # Key Findings
        Provide at least 3 well-explained findings.

        # Conclusion

        # Sources
        List only VERIFIED source URLs.

        Be detailed, factual and professional.

        Make sure the report reflects the most reliable and recent
        information available in the research.
        """
    )
])


# Writer Chain
writer_chain = writer_prompt | llm | StrOutputParser()


# critic prompt
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a sharp and constructive research critic.

        Evaluate the research report for:

        - factual quality
        - source quality
        - source verification
        - source recency
        - completeness
        - clarity
        - relevance
        - unsupported claims
        - depth of analysis
        - source diversity
        """
    ),
    (
        "human",
        """
        Review the research report below.

        Report:
        {report}

        Respond in exactly this format:

        Score: X/10

        Strengths:
        - ...
        - ...

        Areas to Improve:
        - ...
        - ...

        One line verdict:
        ...
        """
    )
])


# critic chain
critic_chain = critic_prompt | llm | StrOutputParser()