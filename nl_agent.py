from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the Anthropic API key from an environment variable
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


if not anthropic_api_key:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable.")

# Initialize the Claude language model
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620",
                    temperature=0.7, 
                    anthropic_api_key=anthropic_api_key)

# Create a prompt template for summarization
summary_template = """
Analyze and summarize the following article in 4-5 concise sentences. Your summary should be informative, well-structured, and capture the essence of the article. Please adhere to the following guidelines:

1. Main Topic: Clearly state the primary subject or issue discussed in the article.
2. Key Individuals: Identify and mention any significant people or organizations involved.
3. Important Events: Highlight any notable events, decisions, or actions described.
4. Context: Provide brief background information if necessary for understanding the topic.
5. Implications: If applicable, briefly mention any potential impacts or consequences discussed.
6. Timeframe: Include relevant dates or time periods mentioned in the article.

MAKE SURE THE SUMMARY IS 50 WORDS MAXIMUM. This rule is important should always be adhered.

Use each of those guidelines as points to include in the summary, however please write the summary as a paragraph. As if it is giving the reader an intro and quick look into what the article is discussing.

Ensure that your summary gives a reader a comprehensive overview of the article's content without unnecessary details. Maintain a neutral tone and focus on factual information.

Article: {article_content}

Summary:
"""

prompt = ChatPromptTemplate.from_template(summary_template)

# Create a RunnableSequence for summarization
summarize_chain = RunnableSequence(
    prompt,
    llm,
    StrOutputParser(),
)

