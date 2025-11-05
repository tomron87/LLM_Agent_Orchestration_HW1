# 🤖 Prompting & Development Process
Documentation of development process and working with AI tools

---

## 0. 🎯 Document Purpose
This document records the complete development process of the system — from the idea and initial specification stage, through code and testing development, to interface improvements and documentation creation.
The emphasis is on the work process using AI tools (such as ChatGPT, Ollama and Claude) that served as professional helper tools in planning, documentation and real-time problem-solving.

---

> **General Note:**
> All examples and stages documented in this document represent only parts of a complete process of working with AI tools.
> At each stage in the project we performed an engineering thinking process: analyzing the problem and requirements, formulating precise prompts based on context, examining received outputs, and drawing conclusions before actual implementation.
> Thus AI served us as a learning, testing and validation tool — not a replacement for human thinking but an expansion of it.

---
## 1. 💻 Initial Installations on Mac Computer
- We performed initial analysis of all installation requirements for the virtual environment. We combined two existing README files (from installation instructions we received) with explanations we got in chat to understand how to perform installations on macOS, including creating virtual environment, installing Ollama and local health checking.
  [environment_setup_macOS.png](screenshot_images/environment_setup_macOS.png)
- Then we created a comprehensive and accurate `requirements.txt` file, so anyone running the project can set up an identical environment easily.
- In parallel we understood how to build the project structure to be generic, flexible and easy to run from any computer, according to submission guidelines.
  [general_structure_understanding.png](screenshot_images/general_structure_understanding.png)

## 2. 🧠 Idea Stage, Specification and Documentation
- We defined the system's central need and goals the system aims to achieve.
[First_project_demand.png](screenshot_images/First_project_demand.png)
- We developed the initial PRD document, and along the way updated it to be professional, accurate and matching the solution we actually built.
  [First_PRD_Demand.png](screenshot_images/First_PRD_Demand.png)
  [PRD_adjustments.png](screenshot_images/PRD_adjustments.png)
- We shaped the structure of all documentation documents in parallel with development, to maintain consistency and coordination between project and documents.
  [documentation_files_structure.png](screenshot_images/documentation_files_structure.png)
  [documentation_files_structure_adjustments.png](screenshot_images/documentation_files_structure_adjustments.png)
- We ensured complete consistency between all documents: PRD, Architecture, Installation & Testing, and Prompting.
  [documentation_flow_consistency.png](screenshot_images/documentation_flow_consistency.png)
---

## 3. 🏗️ Architecture Review and Logic Adaptations
- We examined architecture completeness against original requirements, and compared results between ChatGPT and Claude to get additional perspectives.
  [Architecture_validation_claude.png](screenshot_images/Architecture_validation_claude.png)
- We implemented improvements and updates in directory structure, service files (Services), and system's general configuration according to findings.

---

## 4. ⚙️ Building Tests and Health Checks
1. We checked which tests exist in initial architecture and whether they are sufficient.
   [unit_tests.png](screenshot_images/unit_tests.png)
2. We deepened understanding of differences between test types and built organized Unit Tests array.
   [unit_tests_undersanding.png](screenshot_images/unit_tests_undersanding.png)
3. We organized all tests by categories and directories — API tests, services, and Preflight.
   [Tests_structure.png](screenshot_images/Tests_structure.png)
4. We created unified test flow for all stages (including environment checks) and wrote Makefile allowing running entire system and tests with one click.
5. We updated `Installation_and_Testing.md` document to reflect all new testing stages.

---


## 5. 🗂️ Documentation Updates
- We updated PRD document to reflect final architecture and entire development process.
  [PRD_final_adjustmnet.png](screenshot_images/PRD_final_adjustmnet.png)
- We wrote README document serving as landing page for entire project, with convenient links to all accompanying documents.

---

## 6. 🎨 UI Improvement
- Initial UI version was built in basic and simple structure.
  [first_ui.png](screenshot_images/first_ui.png)
- We added functional features like API connection check, model selection, and conversation clearing, returning "alert" if model returns empty response and this is not an operation error.
  [UI_adjustments.png](screenshot_images/UI_adjustments.png)
- Then we redesigned the entire interface to be aesthetic and user-friendly, including adding message time display, copy buttons and balanced design.
  [Finale_UI_1.png](screenshot_images/Finale_UI_1.png)
  [Final_UI_2.png](screenshot_images/Final_UI_2.png)
- Each change was accompanied by health checks and connection to Backend to ensure proper data flow.


## 7. 🧾 Final Testing, Fixes and Full Documentation Update
- We finished preparing and checking all documents, including Prompting and Screenshots & Demonstrations.
- We performed final tests for entire system, including all functions, tests, general health and appearance.
- Organized Git repository was prepared, and verified that all required files are included and project can be fully run from any environment.


## 8. 🧩 Integration Between AI Tools
- During development, several artificial intelligence systems were used — ChatGPT, Ollama and Claude — to verify answers, check code efficiency and health, and examine additional ideas that one tool didn't suggest.
- The combination between them allowed getting different perspectives and led to a more stable and accurate result than any single tool could provide alone.

---

## 9. 📈 Learning and Improvement in Prompting Process
Throughout we learned that effective prompt must include clear **context (reference)** to what has been done so far, to allow the model to build on existing knowledge base and not answer generally.
We discovered it's better to formulate instructions in a role-oriented manner — define to the model what its role is, which conditions and constraints it must maintain, and exactly how we want the final output to look.
This method significantly improved response quality and precision of outputs we received.

---

## 10. 🔚 Summary and Insights
- AI tools served as central component in development process — both in building architecture, in helping with code and tests, and in streamlining and improving documentation.
- Working with AI tools made the development process more collaborative, focused and efficient.
- Creating precise prompts with context and defined role led to consistent and high-level results.
- AI use improved development quality, documentation and overall project work experience.
- The project demonstrates how smart integration of artificial intelligence in development process can raise professional level and save considerable time.
