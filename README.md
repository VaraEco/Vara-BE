# Vara-BE

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Code Overview](#code-overview)

## Introduction
Backend repository for Vara.

## Features
- Vara Chatbot

## Installation

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/VaraEco/Vara-BE.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Vara-BE
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure environment variables:
    ```bash
    PINECONE_API_KEY=''
    AWS_ACCESS_KEY_ID=''
    AWS_SECRET_ACCESS_KEY=''
    ```
5. Run:
   ```bash
    python app.py
   ```
    

## Code Overview
The backend currently only supports the chatbot functionality. The chatbot can be used to query the data inside the Green House Gas (GHG) Protocol document. We use the Pinecone vector database to house the 
chunks of the GHG protocol document. We used AWS  Bedrock to provision the Large Language Model (LLM). When the user enters their query on the frontend, the query is redirected to this backend. We currently support
chat history upto 6 previous conversations. The new query is transformed (if needed) considering the history. The transformed query is then used to retrieve the 4 most similar chunks from the GHG protocol document.
This reetireved context along with the query is then passed to our LLM to generate a response which is then sent back to the frontend.


