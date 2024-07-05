# Dev Machine Setup

## Install Docker
Your development environment will be in a dev container to eliminate "works on my machine" issues. Due to variability in how individual developers configure their base OS, around 50% of course attendees have environment-related issues completing the tutorial if using their base OS instead of a container.

On a clean OS configuration, Python venv will also work. However, it will not be supported by instructors or TAs during the live course due to variability in OS configurations.

Recent OS distributions no longer support system-level installation of Python packages.

## Install VSCode
We will use VSCode for this tutorial because it supports both Python Notebooks and standard Python editing. Although other editors have their merits, VSCode is also the most standard editor in 2024. The containerized development environment is only tested to work with VSCode. You must use VSCode to get instructor or TA support during the workshop. 

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

## Install Python
Check for a working Python installation by launching a terminal and run the following command:  
```
python3 --version
```

It should display the Python version you have installed.

# Repo Setup

## Fork and Clone the Repo
1. Go to [the Github repo for this course](https://github.com/tobkin/rag-mini-bootcamp)
2. Click Fork
3. Clone your forked repo with a terminal
4. `cd` into the `rag-mini-bootcamp` repo folder

## Create Virtual Environment & Install Dependencies
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## .env File Setup
We will use OpenAI embeddings, GPT3.5, and Weaviate Cloud Services vector database for this tutorial, so you will need to securely store your API keys in a `.env` file. This file is in `.gitignore` so it doesn't accidentally get committed to the repo where your keys would be exposed.  

Create a `.env` file in the root of the repo from this template:  
```
WCS_URL=https://xxxxx-xxxxxxxx.weaviate.network
WCS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

First, you'll fill in the WCS keys. Go to Weaviate Cloud Services, create a free sandbox vector database, and copy the URL and API key provided in the dashboard for the sandbox to the `.env` file.

Second, go to OpenAI API settings. Create a new API key and copy it to the `.env` file. If you're out of free trial credits, purchase $5 of credits.

# Test Your Environment
Open `./cheat-code/query_qa_rag_agent.ipynb` in VSCode. Click "Run All" and select the `venv` python environment if prompted. The notebook should display a GPT3.5 completion to the question about the paper. If you get an error, try to diagnose it or flag one of us for help.