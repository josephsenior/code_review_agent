"""
Base Agent class for all code review agents.

Provides common functionality like LLM initialization, prompt templates,
and error handling that all code review agents share.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


class BaseCodeReviewAgent(ABC):
    """
    Base class for all code review agents.
    
    Provides common functionality:
    - LLM initialization and configuration
    - Prompt template management
    - Error handling
    - Output parsing
    """
    
    def __init__(
        self,
        role: str,
        system_prompt: str,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        api_key: Optional[str] = None
    ):
        """
        Initialize the base code review agent.
        
        Args:
            role: The role/name of this agent
            system_prompt: System prompt defining the agent's behavior
            model_name: OpenAI model to use
            temperature: Temperature for LLM responses (lower for code review)
            api_key: OpenAI API key (if not provided, uses env var)
        """
        self.role = role
        self.system_prompt = system_prompt
        
        # Initialize LLM
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
            )
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        # Build prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])
        
        # Build chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    
    def _invoke(
        self,
        input_text: str,
        **kwargs
    ) -> str:
        """
        Invoke the agent's chain with input and optional context.
        
        Args:
            input_text: The input text for the agent
            **kwargs: Additional context variables for the prompt
            
        Returns:
            Agent's response as string
        """
        try:
            result = self.chain.invoke({
                "input": input_text,
                **kwargs
            })
            return result
        except Exception as e:
            error_msg = f"[{self.role}] Error processing request: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg) from e
    
    @abstractmethod
    def review(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """
        Review code. Must be implemented by subclasses.
        
        Args:
            code: The code to review
            language: Programming language (python, javascript, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with review results and findings
        """
        pass
    
    def get_role(self) -> str:
        """Get the agent's role."""
        return self.role

