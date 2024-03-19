# PrOwl v 0.1
*Give your Prompts Wings!*

## Backstory

I got sick of using langchain for prompt composition.  I got sick of thinking of prompts as linear unidirectional processes that were broken up into strings.  I wanted prompts to be more like HTML 1.0 and after 7 months of using Langchain, I got more prompt completion tasks done using the first mockup version of prowl on day one than I had in the whole 7 months using langchain as part of my production system. Needless to say I've now switched completely to this because it lets me really feel like I'm doing the task of `prompt engineering` instead of python coding where prompts are a second-class citizen. So this is a prompting-first language with an interpreter and a processing stack that lets you stack up `prowl` tasks on top of each other.

## Benefits of using the PrOwl Language

0. **Built for Local LLMs**: While many other frameworks focus on being OpenAI compatible and treat local LLMs as a secondary goal, I started writing prowl with [vLLM](https://github.com/vllm-project/vllm/) and [Mistral Instruct 7b](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) in mind, and I left that as is for now, with the possibility of building more LLM clients in the future.

1. **Simplicity and Accessibility**: The `.prowl` scripts are designed for ease of writing and use, both as standalone scripts and within Python code through the `ProwlStack`. This simplicity extends to the `prowl` utility, ensuring a user-friendly experience. I use async methods throughout.

2. **Code Cleanliness and Minimalism**: The core interpreter of `.prowl` is intentionally kept small, focusing on essential language features. This minimalism fosters code cleanliness and well-defined functions, making it straightforward for users to engage with.

3. **Solving Key Problems**:
   - **Separation of Code and Prompt**: `.prowl` resolves the challenge of combining Python and prompt composition, allowing a clear distinction between the two.
   - **Multi-Step Prompt Composition**: Writing complex prompts becomes more manageable, enabling organization and integration within Python code.
   - **Variable-First Generation**: A standout feature of `.prowl` is its variable-centric approach. It generates data alongside text, providing a tidy output that includes all specified variables, saving the step of extracting data from text.
   - **Chaining and Stacking**: `.prowl` enhances LLM output through 'Stacking', where each variable further conditions subsequent outputs. This is a significant advancement over traditional chaining methods.
   - **Advanced Tooling**: `.prowl` allows for unique tool creation and usage within scripts, enhancing its utility and extending its language capabilities.
   - **Hallucination Control**: The script’s structure helps control hallucinations by guiding the LLM through each step, conditioning the generation of subsequent variables.
   - **Multi-Generation**: The language allows for the declaration of the same variable multiple times, tracking each distinct value throughout the script, akin to traditional scripting languages.

4. **Augmented Prompt Engineering**: With `.prowl`, users can apply advanced prompt engineering techniques, writing their prompt *alongside* the LLM. This enables more dynamic, structured, and creative generation results for LLMs which still adhere and align with human standards.

# PrOwl Prompt Writing

PrOwl (Prompt Owl) or prowl is a simple declarative language that uses in-line variable declaration and referencing to continuously fill out a multi-step prompt that conditions the LLM into creating high quality output. It does so by using a fill-in-the-blank style syntax that is simple yet very robust.

## Syntax
prowl script uses "{}" curly braces to define and reference variables place in-line with a surrounding text. This simple syntax with variable declaration prompts the LLM with all prior text from the script and makes it generate a response, storing the variable value it generated for later use. Variables can be single line or multiline.

### Variable Declaration
To declare a variable in prowl, use the syntax {variable_name(max_tokens, temperature)} including the curly braces. If it is a single-line variable it has other text on the same line while a multiline variable is on a line of it's own and has an empty line beneath it.
- *max_tokens*: an integer value which limits the number of tokens that the LLM generates. For single line variables, which have no trailing empty line and are probably short answers that are a couple words, use a low number of max_tokens like 6 or 8. If the single line variables could be as long as a sentence, maybe it is a good idea to make it into a multiline, which might have max_tokens between 30 and 5000.
- *temperature*: a float value which controls how strictly the LLM should stick to it's prompt conditioning for the completion of the variable. Some people call this creativity, but it is more aligned with stochasticity or randomness. An example temperature for variables which need results that follow an instruction as strictly as possible is 0.0, whereas a temperature of 0.5 would be good for some creativity and 1.0 might be unpredictable.

When expecting the output of a variable, remember that a single line varible has other text on the same line while a multiline variable is on a line of it's own and has an empty line beneath it. Single line variables are for attributes of things whereas multiline is made for getting longer form responses and specifying an instruction which controls how the LLM generates the response before the variable declaration.

### Referencing a Variable
All variables that have been previously declared and filled are available for referencing simply with the syntax {variable_name}. That will insert the variable's value in the completion prompt from the stored value that was generated by the LLM. Referenced variables do not always have to be declared and can be used as input from the user.

# Examples
In PrOwl, your scripts serve as "interactive templates" for your LLM. What does that mean? It means that everything you write in your script will become part of a continuous prompt that faces your LLM.

Let's look at a very simple example that has some complex steps which are easy to grok:
```prowl
# Creative Writing

## Storytelling
Write a short and creative story with a {mood} mood that satisfies the user's request:
- Story Name: {story_name(24, 0.7)}
- Story Type: {story_type(12, 0.4)}
- Story Archectype: {story_archetype(12, 0.2)}

## Write the story
{story(1024, 0.8)}

## Critical Questions
Write a numbered list of up to four questions that critically compare the mood and the user request with the rewritten story and ask what details are missing and what doesn't sound convincing:
{critical_questions(300, 0.1)}

## Critical Answers
Answer the above questions, adhering to the {mood} mood. Be concise but provide complete answers:
{critical_answers(512, 0.35)}

## Rewrite
Now rewrite the story given everything considered making sure it sticks to the {mood} mood:
{rewrite(1800, 0.3)}

```

Notice that I actually included what is called "Tree of Thought" prompting here, very quickly and easily, keeping my temperature down for those calls and keeping it minimal.  After that I have it rewrite the story it generated first, and I don't need to actually *pass* the variables from previous steps to the Rewrite step, because it can already see them as part of it's imput prompt for the `rewrite` variable declaration.

### Input Variables

In this script, you might have noticed I'm using a variable I didn't declare called `{mood}`. This is an input variable. Normally if I'm using ProwlStack I'd include this on `stack.run()` but every argument you can use for that command you can also put into `prowl.fill()` which executes some text input.  If I were to put this script in a python variable and run it through prowl fill, I'd pass input of mood like this:
```python
from lib.prowl import prowl

template = "... the text from the above script ..."
mood = "Severely Happy"
result = prowl.fill(template, inputs={"mood": mood})

print(result.completion) # output the filled out prompt
print(result.get()) # print a simple dictionary of final variable values
```
Let's look at another way to run that in python, using ProwlStack. In fact, you can find that same example `.prowl` script in the `prompts/monster/monster.prowl` in this repository, so let's point the stack at that folder ad then run `creative` followed by another `tot` (tree of thought, which you'll find in `prompts/thought/`).
```python
from lib.stack import ProwlStack

stack = ProwlStack(folder=["prompts/monster/", "prompts/thought/"])

result = asyncio.run(stack.run(['monster', 'tot']))

print(result.completion) # output the filled out prompt
print(result.get()) # print a simple dictionary of final variable values
```
You can quickly see that adding more and more of these scripts would be a hassle only using them as strings just using `prowl` but with `ProwlStack` I can set up completely different orders of these prowl scripts to run at any point I want, with the same return format.

# Using Tools
Ever since the stone age, and possibly before, humans have been using tools. Now LLM's can use tools and everyone is generally happy about this. Here are some examples of using some built in `ProwlTool`s in your scripts.

```prowl
# Make an Image
The goal of this task is to make an image by first choosing a subject and then generating a prompt for it which we will use the comfy tool to generate an image from.

## Subject
Describe a subject for the image. Choose anything people would take photos of, surprise me:
{subject(200, 0.6)}

## Mood
Choose a single word mood for this subject, for example "creative" or "melancholy":
- Mood Word: {mood(8, 0.25)}

## Subject Physical Aspects
Write a brief paragraph which describes more about the physical aspects of the Subject. Be sure to talk about details missing from your previous description which logically make sense:
{subject_aspects(320, 0.1)}

## Scene
Write a brief paragraph describing a scene for this subject which reflects the {mood} mood:
{scene(300, 0.2)} 

## Scene Physical Aspects
Describe the physical aspects of the scene in a couple of sentences:
{scene_aspects(300, 0.05)}

## Scene Lighting
Write a short phrase which describes the lighting and the shadows of the scene:
{lighting(200, 0.1)}

## Medium
Choose the artistic medium that this image is represented in, for example "pencil drawing" or "photo", or say DEFAULT to let the image generator model choose:
- Image Medium: {medium(10, 0.1)} 

## Prompt Composition
Write a comma delimited set of key phrases on a single line which describes all of the above. be sure to only use commas to separate phrases:
{prompt(520, 0.0)}

{@comfy(prompt)}
```

At the very end (but can be anywhere), I call the comfy tool and I feed it the resulting prompt. There is only one current default workflow for the comfy tool currently, but you can add whichever one you want. There are also more arguments to the comfy tool but I will save that for another time.

# PrOwl is a Quine!

Well not quite, but the `@prowl` tool *is* one when you run it and it finishes your script for you.

A quine is a kind of self-referential program in computer programming and is an example of recursion, where the program's output is the same as its source code. This concept can be extended to include programs that are able to reproduce themselves in other environments or modify themselves while retaining their ability to reproduce.

*It completely prompts itself and can use tools in the prompt!*

Okay, English. Early on in PrOwl I realized that since `.prowl` scripts are plain text written in a language, perhaps I could teach LLM how to code in the language and generate scripts that PrOwl can run afterward, giving you back a data object which solves some user request by generating steps with variables and the completed prompt. If each PrOwl script can be considered an LLM-based App which can take input and produces objective output, then you can say that this feature is an "AI app-making AI app".

## PrOwl Agents?

There is a concept called *Agents* that is currently taking LLMs by storm. OpenAI just released the GPT store, and there are already tons of agent frameworks out there like Crew.ai, AutoGen, and even LangChain. All of these agents need some sort of set up in python for using the tools they have available to them. I'd like to say that this feature of PrOwl is not necessarily an Agent, but it does allow prowl to model agentic tasks with tools like RAG, file system access, and even the @comfy tool which lets your prowl script output images that are generated by image models through a local comfy server.  It can be a powerful tool to create tool using behavior in agents that is automatically aligned and conditioned by a user request written in a short message in plain english.

If anything, this really turns PrOwl into an Augmented Prompt Engineering framework, which you can use in your Agents of any kind.

## Using PrOwl from the Command Line

You can use ProwlStack directly from the command line by using the `prowl` command in the terminal.  The command works something like the `python` command. If you pass it information on a stack to run, it will first validate and then run that stack. However if you just type `./prowl` with no arguments, you enter into the *Augmented Prompt Composer* which helps you to write `.prowl` scripts based on your request.

## Running from Command Line

Here are some examples of what you wantto us

Run one of the simplest and tiniest stacks you can run with just the built-in core scripts.

```prowl
./prowl prompts/ input output
```

What that does is run the `prompts/input.prowl` and `prompts/output.prowl` script. If you look at them, they are dead simple, and literally almost the same as if you were just to give a user input to an LLM and have it respond to that input.  In fact writing the last sentence took more typing than these two scripts combined! Let's take a look:

```input.prowl
# User Request
{user_request}

```

```output.prowl
# Fulfill the User Request
{output(4096, 0.0)}

```

What do these scripts do?

The `./prowl` command in `/prowl.py` assures that when you run the special input script in your desired stack, it will first ask you the value of input, and then pipe that through to the rest of the stack, (filling out the `user_request` variable as it fills `input.prowl`). `output.prowl` is filled next, and it doesn't require any variables, only declares the `output` variable.

## Unit Testing

Because your prompts are now scripts in their own right, this means you can enjoy all of the wonders the scripting languages have to offer: versioning, git, unit tests, etc. This really helps organize your prompts and modularize them as well so that you can simply mix and match them in your final application using a list of their names.

Unit testing is a great one that I'm already really beneffiting from, letting me quickly debug scripts in different scenarios they will be facing in my end application. As you probably already know, unit testing is key for not only debugging but app turnaround time.

### Lets Run One

Using only the `.prowl` scripts located in the root `prompts/` folder lets see how using the prowl command line interface works.  I'm going to make a simple stack that includes the user request, disambiguates their request into an intent, then fulfills that user request on output. It will give us back the corresponding variables. We will then compare that to the same request without the intent block to see how the block conditions the output. This is going to be fun!

```sh
./prowl prompts/ input intent output
```

Output:
```
Prompt Owl (PrOwl) version 0.1 beta
-----------------------------------
Working From [OBFUSCATED]/prowl
Folder: ./
Scripts: ['input', 'intent', 'output']
-----------------------------------
Checking ./ for prowl files...
Checking prompts/ for prowl files...
Loaded `.prowl` Scripts: ['intent', 'input', 'output']
@Tools> ['out', 'file', 'include', 'script', 'comfy', 'time', 'list']

You included an `input` block. Enter a value for `{user_request}`...
@>> User Request>
```

I then answered with a request and pressed Enter to continue the stack:
```
How high is mount everest?
```

This is what I got out...

#### Variables
```json
{'completion': "...", 'variables': {'user_request': {'value': 'how high is mount everest?', 'history': [], 'usage': {'prompt_tokens': 0, 'total_tokens': 0, 'completion_tokens': 0, 'elapsed': 0}}, 'user_intent': {'value': 'to provide the height of Mount Everest', 'history': [], 'usage': {'prompt_tokens': 59, 'total_tokens': 89, 'completion_tokens': 30, 'elapsed': 4.183416366577148}}, 'output': {'value': 'Mount Everest is the highest mountain in the world, with a height of approximately 8,848.86 meters (29,031.7 feet) above sea level.', 'history': [], 'usage': {'prompt_tokens': 78, 'total_tokens': 120, 'completion_tokens': 42, 'elapsed': 4.09203028678894}}}, 'usage': {'prompt_tokens': 137, 'total_tokens': 209, 'completion_tokens': 72, 'elapsed': 8.275446653366089}, 'output': []}
```

#### Completion Prompt
This is the prompt that is completed inline and output so that you can debug how the LLM sees each section as it is filling it out.
```
# User Request
how high is mount everest?

# User Intent
What is the user's intended meaning? Disambiguate the request and write one sentence about it's pragmatic intention. Be concise and accurate:
- The user is requesting I to provide the height of Mount Everest


# Fulfill the User Request
Mount Everest is the highest mountain in the world, with a height of approximately 8,848.86 meters (29,031.7 feet) above sea level.


```
You can see that the user intent really helps steer the fulfillment of the request. Well, I can see it.

### Lets see how it works without `intent`

#### Variables

```json
{'completion': '# User Request\nHow high is mount everest?\n\n# Fulfill the User Request\nMount Everest is the highest mountain above sea level, with an elevation of 8,848.86 meters (29,031.7 feet) as of 2020. This measurement was made by a team of Chinese surveyors using satellite data and ground measurements. The previous record, which was 8,848.86 meters (29,031.7 feet), was set in 2005 by a Chinese team. Mount Everest is located in the Mahalangur mountain range in the Himalayas, and straddles the border between Nepal and Tibet. It is a popular destination for mountaineers from around the world, and many people dream of reaching its summit.\n\n', 'variables': {'user_request': {'value': 'How high is mount everest?', 'history': [], 'usage': {'prompt_tokens': 0, 'total_tokens': 0, 'completion_tokens': 0, 'elapsed': 0}}, 'output': {'value': 'Mount Everest is the highest mountain above sea level, with an elevation of 8,848.86 meters (29,031.7 feet) as of 2020. This measurement was made by a team of Chinese surveyors using satellite data and ground measurements. The previous record, which was 8,848.86 meters (29,031.7 feet), was set in 2005 by a Chinese team. Mount Everest is located in the Mahalangur mountain range in the Himalayas, and straddles the border between Nepal and Tibet. It is a popular destination for mountaineers from around the world, and many people dream of reaching its summit.', 'history': [], 'usage': {'prompt_tokens': 22, 'total_tokens': 181, 'completion_tokens': 159, 'elapsed': 12.067103862762451}}}, 'usage': {'prompt_tokens': 22, 'total_tokens': 181, 'completion_tokens': 159, 'elapsed': 12.067103862762451}, 'output': []}
```

#### Completion Prompt Output

```
# User Request
How high is mount everest?

# Fulfill the User Request
Mount Everest is the highest mountain above sea level, with an elevation of 8,848.86 meters (29,031.7 feet) as of 2020. This measurement was made by a team of Chinese surveyors using satellite data and ground measurements. The previous record, which was 8,848.86 meters (29,031.7 feet), was set in 2005 by a Chinese team. Mount Everest is located in the Mahalangur mountain range in the Himalayas, and straddles the border between Nepal and Tibet. It is a popular destination for mountaineers from around the world, and many people dream of reaching its summit.
```

You might notice the first thing is that I only asked... how high is mount everest.  I didn't ask for all of this extra information. This is how the `intent` block conditions. If you look at the script for `intent.prowl`, or just read the completion prompt before the one above, you wll see that there is a specific instruction in there that conditions the answer saying to "Be Concise". This instruction may very well bleed through to the output script, affecting it's length. You might think, well that is possibly out of scope, but if you really think about it, in situations where you need to capture the user intent, you only want to fulfill that intent and nothing else.  Besides that, if you really care about that conditioning you can run the same stack in python with `prepend=False` in the run call.

### Some More Command line Arguments

Prowl automatically parses `flags` out of your command line arguments like so...

```bash
./prowl prompts/world/ input world world_class world_race -atomic -stop=\\n\\n,\\n#
```

Above you see that I set a boolean flag called `atomic` and a *list* flag called `stop`.  In essence what this does is set the `stops` and `atomic=True` kwargs when calling stack.run() in the prowl.py command line interpreter.

What do they do?
- `atomic`: Makes it so that the *completion* prompt does not run through the stack and allows for running a test on scripts which include variables from other scripts, or use the `@out` tool to call other script's output templates into them. Variables do pass through from script to script in your stack but the previously completed prompts from other scripts does not.
- `stop`: Lets you set the stop tokens for your stack run, which both the LLM will stop on and prowl will make sure the generated variable coheres to. This comes in handy when you are trying to get prowl to generate code, or long form output.  The default stop is set to `\n\n` which is just two return characters. Set as many stops as you want using comma to separate them into a list.

Other stuff

Fatal generation recovery. The `prowl` interpreter tries at least five times to make sure it gets the right type of return for a variable. During this, it slowly moves the temperature up to try to improve the chance of there being a correct answer given by the LLM for your variable. In the case that it still can't give you what you need, it will raise an error saying it couldn't do it.