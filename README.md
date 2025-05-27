## About This Repository

```json
{
  "note" : "This repository includes all code and relevant materials developed for the TEG project",
  "university" : "Polsko-Japońska Akademia Technik Komputerowych",
  "description" : "An AI powered chatbot, that would help corporate employees to get information from database, help employees with company policy and job related queries.",
} 
````

## 🕹 Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)


## 🚀 How to Run


**Clone the repository**

   ```
   git clone https://github.com/pawar-jayesh/pjait-teg-project.git
   cd pjait-teg-project
  ```

**Create a virtual environment for backend, database, company policy and mcp server**

  ```
  python -m venv venv
  ```

**Activate the Python virtual environment**
  ```
  source venv/bin/activate      # Bash
  venv\Scripts\activate         # Powershell / Command-Prompt
  ```

**Install dependencies in all the environments**

  ```
  pip install -r requirements.txt
  ```

**Environment Variables**

  backend (.env):
  ```
  OPEN_AI_KEY=="your-api-key"
  ```

  company-policy (.env):
  ```
  OPENAI_API_KEY=="your-api-key"
  ```

  database (.env):
  ```
  OPENAI_API_KEY=="your-api-key"
  ```

  mcp-server (.env):
  ```
  TAVILY_API_KEY="your-api-key"
  WEATHER_API_KEY="your-api-key"
  OPENAI_API_KEY="your-api-key"
  ```


**Run the app**

  backend:
  ```
  cd backend
  ```
  ```
  source venv/bin/activate      # Bash
  venv\Scripts\activate         # Powershell / Command-Prompt
  ```
  ```
  python app.py
  ```


  company-policy:
  ```
  cd company-policy
  ```
  ```
  source venv/bin/activate      # Bash
  venv\Scripts\activate         # Powershell / Command-Prompt
  ```
  ```
  python workflow/agent_graph.py
  ```


  database:
  ```
  cd database
  ```
  ```
  source venv/bin/activate      # Bash
  venv\Scripts\activate         # Powershell / Command-Prompt
  ```
  ```
  python sql-server.py
  ```

  mcp-server:
  ```
  cd mcp-server
  ```
  ```
  source venv/bin/activate      # Bash
  venv\Scripts\activate         # Powershell / Command-Prompt
  ```
  ```
  python mcp_server.py
  ```

  frontend:
  ```
  Using Live Server Plugin

  On VS Code:
  
  Install the Live Server extension.
  Open the HTML file you want to run.
  Click the "Go Live" button in the bottom-right corner of VS Code.
  Your default browser will open with the running page and auto-refresh on changes.
  ```


## Acknowledgements

This project is part of a the TEG project for the PJATK coursework. Special thanks to the instructors involved in the guidance of this task.