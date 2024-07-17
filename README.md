# RAG Mini Bootcamp
In this pilot course, you'll build a Naive RAG-based question-answer agent that supports the following HTML documents:
- [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/html/2312.10997v5)
- [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)  

Understanding Naive RAG architecture is the first step towards understanding more advanced architectures and techniques appropriate for production settings.

# Repo Structure
```
.
├── .devcontainer  # Docker environment config files
├── 1 query_qa_rag_agent.ipynb  # Start here. Use to check your environment works.
├── 2 indexer.ipynb  # Tutorial 2
├── 3 retriever.ipynb  # Tutorial 3
├── 4 generator.ipynb  # Tutorial 4
├── 5 summary.ipynb  # Tutorial 5
├── LICENSE
├── README.md
├── cheat_code  # Completed, working code you can cheat off of if you get stuck
├── data  # Nothing useful in here for now
├── requirements.txt  # Python packages
└── workshop_code  # The code you will edit in the tutorials
```

# Dev Machine Setup

## Install Docker
Your development environment will be in a VSCode Dev Container to eliminate "works on my machine" issues. 

If you want to push your changes to your own fork, note that your SSH settings won't be copied to your Dev Container. Use a non-VSCode terminal to push your changes.

If you want to inspect the environment configuration, check out the folder ".devcontainer/". Feel free to ask any questions.

## Install VSCode
We will use VSCode for this tutorial because it supports both Python Notebooks and standard Python editing. Although other editors have their merits, VSCode is also the most standard editor in 2024. The containerized development environment is only tested to work with VSCode. If you want to use other editors like Pycharm, Jupyter, or Colab, you'll have to do some non-trivial devops work upfront.

## Install VSCode Remote Containers Extension
You will use this extension to develop within the Docker container dev environment.

Open VSCode > Extensions. Search for "Remote Containers". Click install.

## Install Git (Mac & *Nix)
If you're not sure, check if you have `git` installed already. Copy and paste this commmand into your terminal:
```
if command -v git &>/dev/null; then echo "Git is installed and on the PATH"; else echo "Git is not installed or not on the PATH"; fi
```

If it's not installed, install git using Homebrew, Apt, etc as appropriate.

## Install Git (Windows)
Easy option: install Git Bash  

Microsoft Official Option:
1. Install Windows Subsystem for Linux
2. Open Ubuntu shell
3. `apt install git`

# Repo Setup

## Fork and Clone the Repo
1. Go to [the Github repo for this course](https://github.com/tobkin/rag-mini-bootcamp)
2. Click Fork
3. Clone your forked repo with a terminal
4. `cd` into the `rag-mini-bootcamp` repo folder

## .env File Setup
We will use OpenAI embeddings, GPT3.5, and Couchbase Capella vector database for this tutorial, so you will need to securely store your API keys in a `.env` file. This file is in `.gitignore` so it doesn't accidentally get committed to the repo where your keys would be exposed.  

Create a `.env` file in the root of the repo from this template. You will fill it in in the next steps.  
```
# Replace this with Connection String from SDKs page in Couchbase console
CB_ENDPOINT="couchbases://cb.xxxxxxxxxxxxxxxx.cloud.couchbase.com" 
# From database access credentials in Couchbase console
CB_USERNAME="RAG_WORKSHOP" 
# From database access credentials in Couchbase console
CB_PASSWORD="<<password>>" 
# From the OpenAI API console
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## OpenAI API Setup
Go to OpenAI API settings. Create a new API key and copy it to the `.env` file. If you're out of free trial credits, purchase $5 of credits.

## Deploy Couchbase Trial Cluster
1. Sign up for a Couchbase account. Select any cloud provider and region. Click "Deploy Now".
2. [Trial - Cluster Console] Go to "Connect"
3. [SDKs Page] Add the Public Connection String to your .env file like so: `COUCHBASE_CLUSTER_URI=couchbases://cb.xxxxxxxxxxxxxxxx.cloud.couchbase.com`
4. [SDKs Page] Click the Allowed IP Addresses > Add Allowed IP > Allow Access from Anywhere > Add Allowed IP. 
5. [SDKs Page] Click Database Access > Create Database Access. Database Access Name: RAG_WORKSHOP. Bucket: All Buckets. Scope: All Scopes. Access: Read/Write. 
6. [SDKs Page] Select your database credentials
7. [SDKs Page] Choose Python

**Important notes if you adapt this configuration for production:**
1. Only whitelist IPs that are trusted
2. Use the principle of least priviledge when creating database access

## Create Couchbase Vector Search Index
1. Go to your console for Trial - Cluster
2. Go to Data Tools > Search
3. Click Create Search Index > Advanced Mode > Index Definition > Import from File
4. Upload `couchbase-index-definition.json` from the root of the workshop repo
5. Click Create Index

Couchbase Reference Docs: [Import a Search Index Definition with the Capella UI](https://docs.couchbase.com/cloud/search/import-search-index.html)

# Test Your Environment  
Open the folder "rag-mini-bootcamp" in VSCode. Open the folder in Dev Container mode by using Cmd/Ctrl + Shift + P > Dev Containers: Open Folder in Container. The first time, the container will take some time to build while it downloads the required packages.

Once the container is finished building, open `./query_qa_rag_agent.ipynb` in VSCode. Click "Run All". The notebook should display a GPT3.5 completion to the question about the paper. If you get an error, try to diagnose it or flag one of us for help.