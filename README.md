![logo_128](https://github.com/user-attachments/assets/83bcbe59-3ed5-41a4-b5ff-2a893dce81bc)
# PrOwl v0.1  
*Give your Prompts Wings!*

## Colab Demos  
- [![Colab](https://img.shields.io/badge/Google%20Colab-%23F9AB00.svg?style=for-the-badge&logo=google-colab&logoColor=white) PrOwl Demo](https://colab.research.google.com/drive/1x-9mkpawC3kh_3FKJcl7QE3UkRkvtAXL?usp=sharing)  
- [![Colab](https://img.shields.io/badge/Google%20Colab-%23F9AB00.svg?style=for-the-badge&logo=google-colab&logoColor=white) Scripting with PrOwl](https://colab.research.google.com/drive/1_StW54A8B4mAdRa4piBRxFxnhhyaaYuS#scrollTo=oTqFPlXHjZTN)

## Installation
PrOwl is available on PyPi:  
```bash
pip install prompt-owl
```
Alternatively, clone the repository and run:
```bash
cd prompt-owl
```
Make sure to set up your Environment variables for your OpenAI-API compatible endpoint (ala vLLM, oLlama, etc.)
The following is also located in `prowl/env.placeholder`
```
# To use this as your environment file, rename this to `.env`
# If you want this to be system-wide, .bashrc it or add to PATH in Winblows

# vLLM or any API for LLMs will go here
PROWL_VLLM_ENDPOINT=http://localhost:8000
PROWL_MODEL=mistralai/Mistral-7B-Instruct-v0.2
# If using OpenRouter or another paid API, even openAI
# PROWL_VENDOR_API_KEY=....
# If using Ollama
# PROWL_COMPLETIONS_ENDPOINT=/api/generate

# Comfy
PROWL_COMFY_ENDPOINT=127.0.0.1:8188

# Fal (for the Fal.ai tool)
# FAL_KEY=...
```


## Backstory

After months of wrestling with LangChain’s linear and string-burdened approach to prompt composition, I decided enough was enough. I wanted prompts to feel as intuitive as HTML 1.0—simple, declarative, and powerful. With PrOwl, I cranked out more prompt completions on day one than I had in seven months of LangChain. Now, prompts take center stage and Python coding is just there to support the prompt engineering. PrOwl makes prompt engineering the first-class citizen it deserves to be.

## The PrOwl Advantage

0. **Built for Local LLMs**: While many frameworks prioritize OpenAI compatibility, PrOwl was designed with [vLLM](https://github.com/vllm-project/vllm/) and [Mistral Instruct 7B](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) in mind, with possibilities to support even more LLM clients.
1. **Simplicity & Accessibility**: `.prowl` scripts are lightweight and designed for effortless integration into your Python code through the `ProwlStack`. Think less “boilerplate” and more direct, async prompt magic.
2. **Minimalism at Its Core**: With a tiny interpreter focusing on just the essential language features, PrOwl keeps your codebase clean and functions well-defined.
3. **Smart Problem Solving**:
   - **Separation of Concerns**: Keep your code and prompt composition distinct.
   - **Multi-Step Composition**: Build complex, multi-step prompts that flow naturally.
   - **Variable-First Generation**: Get data and text as part of the same generation, so you don’t waste time extracting variables later.
   - **Chaining & Stacking**: Every generated variable conditions subsequent outputs—a step beyond traditional chaining.
   - **Built-In Tools**: Create and utilize custom tools seamlessly.
   - **Hallucination Control**: Guide your LLM through a structured process to minimize off-track outputs.
   - **Multi-Generation Support**: Declare a variable multiple times and track its evolution like in a proper scripting language.
4. **Augmented Prompt Engineering**: Design your script alongside the LLM, integrating human standards into machine-generated output. It isn't "alignment", it is *conditioning*.

---

# PrOwl Prompt Writing

PrOwl is a simple, declarative language that uses inline variable declarations and references. This “fill-in-the-blank” style continuously guides the LLM, generating high-quality output while storing variable values for later use. Whether it’s a single-line attribute or a multiline narrative, every variable tells part of your story.

## Syntax Overview

In your `.prowl` scripts, use curly braces `{}` to denote variables. Here's how it works:

### Variable Declaration
Declare with:
```
{variable_name(max_tokens, temperature)}
```
- **max_tokens**: Sets the token limit. Use a lower number (e.g., 6–8) for short answers, or higher (30–5000) for more elaborate responses.
- **temperature**: Controls the LLM’s randomness. A lower value (0.0) ensures strict instruction following, while higher values (0.5, 1.0) introduce creative variability.

Multiline variables stand alone on their own line with an empty line below; single-line variables sit alongside other text.

### Referencing Variables
Simply write `{variable_name}` to reuse a previously generated value. This makes it easy to condition the output in later prompts without extra hassle.

---

# Examples

PrOwl scripts serve as interactive templates. Everything you write becomes part of the continuous prompt presented to the LLM. Take a look at this creative writing example:

```prowl
# Creative Writing

## Storytelling
Write a short and creative story with a {mood} mood that satisfies the user's request:
- Story Name: {story_name(24, 0.7)}
- Story Type: {story_type(12, 0.4)}
- Story Archetype: {story_archetype(12, 0.2)}

## Write the story
{story(1024, 0.8)}

## Critical Questions
Write a numbered list of up to four critical questions comparing the mood and the user request with the rewritten story. Identify what's missing or unconvincing:
{critical_questions(300, 0.1)}

## Critical Answers
Answer these questions, keeping in line with the {mood} mood:
{critical_answers(512, 0.35)}

## Rewrite
Now rewrite the story, ensuring it adheres strictly to the {mood} mood:
{rewrite(1800, 0.3)}
```

Notice the dynamic interplay: an input variable `{mood}` guides the output without additional plumbing. Input variables don’t need a declaration—they get their value from the user (or your Python code).

### Running a Script in Python

```python
from lib.prowl import prowl

template = "... the text from your .prowl script above ..."
mood = "Severely Happy"
result = prowl.fill(template, inputs={"mood": mood})

print(result.completion)  # See the completed prompt
print(result.get())       # View final variable values as a dictionary
```

Alternatively, using the ProwlStack, you can run scripts as blocks in a stack and from multiple folders, getting nicely formatted and organized results:

```python
from lib.stack import ProwlStack
import asyncio

stack = ProwlStack(folder=["prompts/monster/", "prompts/thought/"])
result = asyncio.run(stack.run(['monster', 'tot']))

print(result.completion)  # Completed prompt output
print(result.get())       # Final variable dictionary
```

### Doing "Cliffs Notes" Summarized Speech to Text on any Audio File
The prompt `sum_cliffs` can be found [here](https://github.com/lks-ai/prompt-library/blob/master/digest/sum_cliffs.prowl) and you can get it by cloning the [Prompt Library](https://github.com/lks-ai/prompt-library)
```py
import whisper

input_audio = "/audio/any_audio_file_or_format.aac"

model = whisper.load_model("base")
r = model.transcribe(input_audio)

print(r['text'])

from prowl.lib.stack import ProwlStack
import asyncio

stack = ProwlStack(folder='prowl/prompts/digest/')

rrs = asyncio.run(stack.run(['sum_cliffs'], inputs={'text': r['text']}, stops=["\n\n\n"]))

print(rrs.out())
```

---

# Using Tools

Humans have always built tools—the LLM era is no different. PrOwl includes built-in tools (like the `@comfy` tool) to, for instance, generate images. Here’s an example of using a tool within a script:

```prowl
# Make an Image
The goal is to create an image by first defining a subject, then crafting a prompt to feed into our comfy tool.

## Subject
Describe a subject for the image. Surprise me:
{subject(200, 0.6)}

## Mood
Give a one-word mood for this subject:
- Mood Word: {mood(8, 0.25)}

## Subject Physical Aspects
Detail the subject’s physical features:
{subject_aspects(320, 0.1)}

## Scene
Describe a scene reflecting the {mood} mood:
{scene(300, 0.2)} 

## Scene Physical Aspects
Summarize the scene’s physical details:
{scene_aspects(300, 0.05)}

## Scene Lighting
Offer a short phrase describing the lighting:
{lighting(200, 0.1)}

## Medium
State the artistic medium (e.g., "pencil drawing", "photo") or say DEFAULT:
- Image Medium: {medium(10, 0.1)} 

## Prompt Composition
Compose a comma-delimited set of key phrases summarizing the above:
{prompt(520, 0.0)}

{@comfy(prompt)}
```

At the end, the `@comfy` tool is invoked to generate an image based on the crafted prompt. You can add as many tools as needed.

---

# PrOwl is a Quine!

Not exactly a quine in the classic sense, but the `@prowl` tool almost is—it can finish its own script and even use tools within its prompt. Early in development, I realized PrOwl scripts can evolve: an LLM-based app writing an LLM-based app. In other words, your `.prowl` files aren’t just scripts—they’re self-referential, self-improving, and fully capable of generating dynamic, tool-integrated content.

The interesting natural conclusion of this dynamic is that an Agent could easily be made which prompts itself, or creates prompts for other agents; a meta-agent if you will.

---

# PrOwl Agents?

Agents are all the rage these days (see GPT Store, Crew.ai, AutoGen, LangChain, etc.). PrOwl isn’t necessarily an agent framework, but it lets you model agent tasks by integrating tools (like RAG, filesystem access, or the `@comfy` tool). Think of it as an Augmented Prompt Engineering framework—ideal for creating AI apps that are conditioned directly by user requests. It is trivial to create an Agentic workflow using `.prowl` scripts and some python for your agent class. In as far as the `@prowl` tool, it will eventually begin to write it's own scripts well, including tool usage after I can fine-tune a model using the ~100 scripts I've amassed over the last year.

The end game on Agents is to get a community going around Prompt Owl where people are actively testing, sharing, and publishing prompts to the training queue, and then get some money together to do fine-tuning on a much larger set of training examples.

---

# Using PrOwl from the Command Line

You can run ProwlStack directly from the terminal with the `prowl` command. For a quick start, simply run:
```sh
prowl -folder=prompts/ input output
```
This runs the `prompts/input.prowl` and `prompts/output.prowl` scripts:
- **input.prowl**
  ```prowl
  # User Request
  {user_request}
  ```
- **output.prowl**
  ```prowl
  # Fulfill the User Request
  {output(4096, 0.0)}
  ```

When executed, PrOwl first asks for an input (filling `{user_request}`), then processes the stack to generate `{output}`.

---

# Unit Testing

Your prompts are now scripts—and that means you can take advantage of version control, git, and unit tests. Modularize, debug, and mix-and-match your prompts as you see fit.

For example, run a simple stack with:
```sh
prowl -folder=prompts/ input intent output
```
This stack first gathers the user input, then disambiguates the intent, and finally outputs a conditioned result.

Sample output reveals both the filled variables and the full prompt used for debugging—a goldmine for prompt engineering.

---

# Command Line Options

PrOwl supports various flags to refine your runs:
- **atomic**: Run scripts without aggregating previous completion prompts. Ideal for isolated tests.
- **stop**: Define stop tokens (default: `\n\n`). Use comma-separated tokens to suit your generation (great for code or lengthy texts).

For example:
```sh
prowl -folder=prompts/world/ input world world_class world_race -atomic -stop="\\n\\n,\\n#"
```

These options provide granular control over prompt composition and output behavior.

# TODO / Known Issues
- Fix the 1 token bug (make it possible to declare a variable with max 1 token)
- Fix the CLI issue on the pypi package setup, still some pointing isssues.

---

Embrace prompt-first development with PrOwl—small in lines, big in vision. Happy prompting!
