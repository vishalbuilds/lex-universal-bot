## Lex Bot Generic

# Universal Bot

A production-ready Amazon Lex bot backend built in Python, specifically designed for seamless integration with Amazon Connect. This generic framework provides the foundational backend infrastructure to power intelligent conversational experiences in your contact center.
This project is focused on building a "Universal Bot" using a serverless architecture on AWS. The goal is to create a flexible and intelligent conversational agent that can be easily configured and extended.

## Project Overview

The Universal Bot leverages AWS Lambda for its core logic, DynamoDB for data persistence, and Amazon Bedrock for advanced generative AI capabilities, including Retrieval-Augmented Generation (RAG). The bot's structure and behavior will be defined in a YAML configuration, allowing for easy creation and management of different bot instances.

## Key Components

The architecture is planned around the following key components:

- **YAML to Bot Mapping**: A declarative way to define the bot's personality, intents, and conversational flows using a YAML file (e.g., `config/bot.yaml`). This configuration will be used to provision and update the bot.

- **AWS Lambda Function**: The central processing unit of the bot, located in `src/lambda_function.py`. It will handle incoming user requests, manage conversation state, and integrate with other services.

- **Amazon DynamoDB**: Used as the primary database for:

  - Storing conversation history and user data (e.g., in a `UniversalBot-Conversations` table).
  - Managing bot configuration and schema for the Conversational User Interface (CUI) (e.g., in a `UniversalBot-Config` table).

- **Amazon Bedrock**: Provides access to powerful foundation models to enable generative AI features.
  - **Prompt Engineering**: Carefully crafted prompts, managed in the `prompts/` directory, will guide the AI models to generate accurate and contextually relevant responses.
  - **Retrieval-Augmented Generation (RAG)**: The bot will use RAG to retrieve information from a knowledge base and use it to generate more informed and detailed answers, reducing hallucinations and providing up-to-date information.

## Development Roadmap / To-Do

- [ ] **Bot Definition**: Map YAML configuration to bot creation process.
- [ ] **Lambda Function**: Develop the core business logic for the bot.
- [ ] **DynamoDB Integration**: Define and implement the necessary database schemas and integration logic within the Lambda function.
- [ ] **CUI Database Schema**: Finalize the schema for the Conversational User Interface.
- [ ] **Bedrock Integration**: Integrate the Lambda function with Amazon Bedrock.
- [ ] **Prompt Engineering**: Design, test, and refine prompts for the language models.
- [ ] **RAG Implementation**: Build the RAG pipeline to connect the bot to a knowledge source.
