## AI Dungeon Master for RPG-Text Game

This project explores the potential of Large Language Models (LLMs) in creating a text-based RPG game with an AI Dungeon Master. The code utilizes Kivy for the user interface and leverages Mistral or Llama27b models for generating interactive storylines.

**Project Goals:**

* **Understanding LLM Capabilities:** Investigate the ability of LLMs to produce creative and engaging text responses suitable for an interactive game.
* **Custom LLM Behavior:** Define templates and guidelines to influence LLM outputs without extensive fine-tuning, creating a unique chatbot experience.
* **LLM-powered Application:** Build a functional AI Dungeon Master chatbot to demonstrate the practical use of LLMs in real-world scenarios.

**Features:**

* **Character Creation:** Players define their characters by allocating points to attributes like vitality, strength, agility, and intelligence.
* **Dynamic Storytelling:** The AI Dungeon Master generates stories based on player input, fostering an immersive gaming experience.
* **Combat System:** Players engage in battles with enemies, with outcomes determined by dice rolls and player decisions.
* **User Interface:** A user-friendly interface built with Kivy allows players to interact through buttons and text inputs.


## Running Mistral LLM on Python using Ollama with Langchain

This guide outlines how to leverage the Mistral LLM within your Python applications through Ollama and Langchain.

**Prerequisites:**

* **Python 3.x:** Ensure you have Python 3 installed on your system.
* **Ollama:** Install Ollama using `pip install ollama`.
* **Langchain:** Install Langchain with `pip install langchain`.
* **Mistral Model:** Download the Mistral model using `ollama pull mistral-base/6B`.

**Steps:**

1. **Import Libraries:**

```python
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
```

2. **Load Mistral Model:**

```python
model='mistral' #or llama2
llm = Ollama(model=model,callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
```

3. **Send Prompt and Get Response:**

```python
prompt = "What is the meaning of life?"
response = mistral_model.chat(prompt)

print(response)
```

**Explanation:**

- We import the necessary libraries: `langchain` for LLM interaction and `OllamaLLM` from Langchain for accessing Ollama models.
- The `mistral_model` is loaded using `OllamaLLM.from_name()`, specifying the downloaded Mistral model name.
- We send a prompt using the `chat()` method of the model and store the response.


**Additional Notes:**

- Remember to download the Mistral model using `ollama pull mistral-base/6B` before running the script.
- Refer to the Ollama documentation for more details on available models and functionalities: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- Explore the Langchain documentation for advanced LLM usage patterns: [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)


**Template-Based LLM Control**

This code utilizes templates to guide the LLM's responses within the game, promoting a more controlled and immersive storytelling experience. It essentially creates a custom chat GPT model behavior without extensive fine-tuning.

**Goal:**

The code aims to establish a set of guidelines and templates that the LLM (Large Language Model) adheres to when generating responses in your game. This promotes a more immersive and controlled storytelling experience.

**Breakdown:**

* **Template Strings:**
  - The code defines multiple template strings that structure the LLM's output:
    - `template_header`: Sets the overall objective and writing style for the LLM.
    - `template_str`: Provides information about the player character and additional guidelines for the LLM.
    - `template_main`: Formats the conversation flow, displaying the current conversation history, player input, and LLM response.
* **Prompt Creation:**
  - The code combines these templates into a single `template` string.
  - A `PromptTemplate` object is created using this template, specifying placeholders for dynamic elements like conversation history and player input.
  - This `PROMPT` object is then assigned to the `conversation.prompt` attribute.

**Benefits:**

* **Consistency:** The templates ensure the LLM's responses follow a specific format, enhancing readability and maintaining the narrative flow.
* **Control:** The guidelines within the templates steer the LLM's storytelling in a desired direction, preventing unwanted elements like premature combat or conclusive endings.
* **Player Agency:** The templates emphasize prompting the player for decisions, fostering a sense of interactivity and control within the game.



This approach ensures consistent LLM output, avoids unwanted elements, and encourages player decision-making, leading to a more engaging gameplay experience.

**Future Enhancements**

This project lays the groundwork for further exploration in LLM-powered text-adventure games. Here are some exciting possibilities:

* **Dynamic Prompt Generation:** Leverage player data like character attributes, location, and world details to craft personalized prompts for a more meaningful narrative.
* **AI-Driven Storytelling:** Empower the LLM to actively participate in storytelling by generating descriptions, crafting dialogue, and introducing plot twists based on player choices.
* **Worldbuilding and Quests:** Integrate map systems, complex narratives with branching storylines, and procedurally generated quests to create a truly immersive and dynamic game experience.

This is project was done to get experience in LLMs, however the given concept in this project is not yet done by anyone as of March 2024. Current AI-powered Text-RPG games basically only utilize AI model to create the game flow. However using dynamic prompt generation by using object information of players, and in more detailed work, inventory, level, experience, stat, skill information combined with map system and given set of world with mission, true text-rpg that is actually powered by AI can be achieved.
