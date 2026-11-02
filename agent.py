from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# from langchain_mistralai import ChatMistralAI




from langchain_core.output_parsers import StrOutputParser

from tools import web_search,scrape_url

import os
from dotenv import load_dotenv
load_dotenv()

#model setup
llm=ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# FIRST AGENT
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

# 2ND AGENT-  READER AGENT

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

# writer chain - lcel pipeline , runnables

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert research writer.
        Produce accurate, structured, evidence-based research reports.
        Do not invent facts, statistics, quotations, or source URLs.
        Clearly distinguish established facts from uncertain claims.
        Cite sources using the URLs provided in the research material."""
    ),
    (
        "human",
        """Write a detailed research report on the following topic.

Topic: {topic}

Research Gathered:
{research}

Structure the report as follows:

1. Introduction
2. Key Findings
   - Explain at least three important findings.
   - Support claims using the supplied research.
   - Discuss relevant evidence and implications.
3. Limitations or Uncertainties
4. Conclusion
5. Sources
   - List the source URLs actually present in the research.
   - Do not invent URLs.

Write in a detailed, factual, professional style."""
    )
])


writer_chain=writer_prompt | llm | StrOutputParser() 

#critic_chain..

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a rigorous research reviewer.
        Evaluate factual support, completeness, logical consistency,
        source quality, relevance, and clarity.
        Do not claim to have verified sources unless evidence is provided."""
    ),
    (
        "human",
        """Review the following research report critically.

Report:
{report}

Use exactly this structure:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

Evidence and Source Concerns:
- ...

One-line Verdict:
..."""
    )
])


critic_chain=critic_prompt | llm | StrOutputParser()


# now we have to create a pipeline to connect them together.........
