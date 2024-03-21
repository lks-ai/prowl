# ProwlStack: Use your `prowl` files in an organized way
# and stack them however you like
# Creator: Nathaniel Gibson (github.com/newsbubbles)

import re, os, glob

from .prowl import prowl
from .tool import ProwlTool
from .vllm import VLLM
from .error import ValidationError

CHROMADB_ENABLED = False
if CHROMADB_ENABLED:
    import chromadb

PROWL_PROMPT_FOLDER = 'prompts/'

class ProwlStack:
    def __init__(self, folder=PROWL_PROMPT_FOLDER, files=None, stream_level=prowl.StreamLevel.NONE, stop_event=None, token_event=None, variable_event=None, script_event=None, tools=None, silent:bool=False):
        self.silent = silent
        self.load_files = files
        self.folder = folder

        # Tasks
        self.use_chromadb = CHROMADB_ENABLED
        if self.use_chromadb:
            self.chroma = chromadb.Client()
            self.collection = self.chroma.create_collection(name="tasks")
        self.tasks = {} # holds text for each task
        self._inspect = {} # lookup for inspections run
        self.default_tasks = [] # default tasks order
        self.output_template_folder = folder
        
        # Variable/Run State: during a run, this will hold a copy of the variables for tool access
        # NOTE Do not use this if you are calling same stack from multiple threads!
        #   Best Practices: In a multithreading environment, use a different ProwlStack in different threads
        #self.variable_state = None
        # is holds the state of the input to run for your tools
        #self.kwargs = None
        
        # Tooling
        self.tools = {} if tools is None else tools
        self.load()
        self.inspect()
        
        # Callbacks
        # stop event expects you to return bool
        self.stream_level = stream_level # the enum to control which level to stream at by default
        self.stop_event = stop_event # for stop control from outside caller
        self.token_event = token_event # for streaming at token level
        self.variable_event = variable_event # for streaming at variable level
        self.script_event = script_event # for streaming at script/task level
            
    def print(self, *args, **kwargs):
        if not self.silent:
            print(*args, **kwargs)
    
    def add_task(self, name, folder='', reinspect=False):
        # add a task to the available tasks pool
        try:
            loaded = prowl.load(folder + name + '.prowl')
            self.tasks[name] = {
                'folder': folder,
                'code': loaded,
                'inspect': (None, None),
            }
            if reinspect:
                self.inspect()
        except Exception as e:
            print(f'Maybe `{name}.prowl` script not found in folder `{folder}`')
            print(e)
    
    def add_tool(self, tool:ProwlTool, reinspect=True):
        self.tools[tool.name] = tool
        if reinspect:
            self.inspect()
        
    def add_tools(self, *tools:list[ProwlTool], reinspect=True):
        for tool in tools:
            self.add_tool(tool)
        self.print('@Tools>', [v for v in self.tools.keys()])
        if reinspect:
            self.inspect()
    
    def get_available_tasks(self):
        return self.tasks.keys()
    
    def load(self):
        # load either the load files or all prowl files in self.foler
        # TODO Rearrange so that it first checks folders, then use load_files as a filter on what to load
        ff = []
        if self.load_files:
            for f in self.load_files:
                self.add_task(f, folder=self.folder)
            self.default_tasks = self.load_files
        
        if isinstance(self.folder, str):
            self.folder = [self.folder, PROWL_PROMPT_FOLDER]
        if PROWL_PROMPT_FOLDER not in self.folder:
            self.folder.append(PROWL_PROMPT_FOLDER)
        for folder in self.folder:
            if not folder.endswith('/'):
                folder += "/"
            self.print(f"Checking {folder} for prowl files...")
            prowl_files = glob.glob(os.path.join(folder, '*.prowl'))
            for f in prowl_files:
                n = os.path.basename(f).replace('.prowl', '')
                if self.load_files:
                    if n not in self.load_files:
                        continue
                self.add_task(n, folder=folder)
        self.print("Loaded `.prowl` Scripts:", list(self.tasks.keys()))
        
    def inspect_vars(self, code, task_name=None):
        #print(">> VAR INSPECT", task_name)
        declared, referenced, required = {}, {}, {}
        pattern = re.compile(prowl.PATTERN_FILL)
        #print(pattern)
        for match in pattern.finditer(code):
            var_name = match.group(1)
            if match.group(2) is not None:
                #print("\tDECLARE", var_name, match.group(2))
                declared[var_name] = match.start()
            else:
                #print("\tREFERENCE", var_name)
                referenced[var_name] = match.start()
        required = list(set(referenced) - set(declared))
        required = [(None, v) for v in required]
        return {
            'declared': list(declared.keys()),
            'referenced': list(referenced.keys()),
            'required': required,
            'task_name': task_name,
        }
        
    def inspect_tools(self, code, task_name=None):
        # is tool present in self.tools?
        # what type are each of the args? [variable, integer, script_name]
        # if arg is a variable, does it exist?
        # if arg is a script_name, is it loaded in the stack?
        # don't forget to add the tool inspect callback to get more inspect data
        #print('@>> TOOL INSPECT', task_name)
        matches = re.finditer(prowl.PATTERN_CALL, code)
        calls = {}
        rv, dv = {}, {}
        declared_vars, referenced_vars = [], []
        scripts = {}
        for match in matches:
            callback_name = match.group(1).strip() #match[0]
            start = match.start()
            arguments = match.group(2).split(',') #match[1].split(',')
            arguments = [arg.strip() for arg in arguments]
            tinspect = None
            #print("\t", callback_name, arguments)
            if callback_name in self.tools: # TODO This never happens?
                tool:ProwlTool = self.tools[callback_name]
                tinspect = tool.inspect_callback(task_name)
                #print("INSPECT", callback_name, tinspect)
            # add proper referenced variables and scripts (given the tool inspect callbacks)
            scr, ar = [], []
            for arg in arguments:
                if arg.isdigit():
                    continue
                if arg in self.tasks:
                    scripts[arg] = start
                    scr.append(arg)
                else:
                    # add to referenced vars if arg is in the referenced inspect return
                    # if in declared inspect return add to declared
                    # else default to referenced
                    rv[arg] = task_name
                    ar.append(arg)
                
            calls[callback_name] = (scr, ar)
        ck = list(calls.keys())
        declared_vars.extend(ck)
        referenced_vars.extend(rv)
        return {
            'tools': {'references': calls, 'required': ck},
            'variables': {'declared': declared_vars, 'referenced': referenced_vars},
            'scripts': {'required': list(scripts.keys())},
            'task_name': task_name,
        }

        
    def inspect(self):
        # take all loaded tasks and inspect their variables
        for k, task in self.tasks.items():
            v = self.inspect_vars(task['code'], task_name=k)
            tv = self.inspect_tools(task['code'], task_name=k)
            self.tasks[k]['inspect'] = (v, tv)
            
            # Add to chromadb
            if self.use_chromadb:
                print('Adding to ChromaDB:', k)
                md = {key: ', '.join(map(str, value)) for key, value in v.items()}
                self.collection.add(
                    documents=[task['code']],
                    metadatas=[md],
                    ids=[k]
                )
            
    def get_inspect(self, task_name):
        if task_name in self.tasks:
            vars, tools = self.tasks[task_name]['inspect']
            return vars, tools
        return None, None

    def search(self, query):
        if not self.use_chromadb:
            raise ValueError("Cannot run `CHROMADB_ENABLED` is set to False")
        self.print("Script Search Result Count:", self.collection.count())
        r = self.collection.query(query_texts=[query], n_results=2)
        # depluralize: format the search results properly
        o = []
        for i, id in enumerate(r['ids']):
            m = {
                'id': id[0],
                'document': r['documents'][i],
                'metadata': r['metadatas'][i],
                'distance': r['distances'][i]
            }
            print(m)
            o.append(m)
        return o

    def validate(self, tasks, variables:dict[str, prowl.Variable], report=False):
        # Validates any requested stack of tasks which will be run
        # -> by simulating a variable/script state pass of the requested stack of `tasks`
        # report=True makes it throw all errors to a return list or None
        # -> this is good for task error checking before a run
        # -> eg. when a user asks to run a stack but certain scripts are not present, a server can return a list of errors
        var = variables.keys()
        var_state = {} # all the variables that are declared. if not found from required, then bad juju
        script_state = {} # all the sripts that are already declared in this pass
        for v in var:
            var_state[v] = 1
        #print(var_state)
        errors = []
        # error utility
        def report_error(error:ValidationError):
            if report:
                errors.append(error.to_dict())
            else:
                raise error

        for i, task in enumerate(tasks):
            if task in self.tasks:
                t = self.tasks[task]
                vars, tools = t['inspect']
                #print(task, vars, tools)
                
                # Update requried vars from tools call
                # tools are var names, so need to make sure tool brings that back into vars
                for tin in tools['tools']['required']:
                    if tin not in self.tools:
                        report_error(ValidationError(1002,
                            f"Tool `{tin}` is not loaded in the stack and required in `{task}`",
                            data={'task': task, 'type': 'tool', 'required': tin}
                        ))
                
                # If the script is not loaded at all in possible tasks: doesn't have to be part of this run stack
                for sc in tools['scripts']['required']:
                    if sc not in self.tasks:
                        report_error(ValidationError(1003,
                            f"The script `{sc}` is required in `{task}` and doesn't seem to come before it in the stack.",
                            data={'task': task, 'type': 'script', 'required': sc}
                        ))
                    else:
                        # Check the variables declared in required scripts are loaded in the var state regardless
                        # the vars declared in script are required by this current task
                        # validate_callback will alter `vars` or `script_state`, see @out or @each
                        for tv in tools['tools']['required']:
                            tscripts, tvars = tools['tools']['references'][tv]
                            for tscript in tscripts:
                                ttool:ProwlTool = self.tools[tv]
                                ttool.validate_callback(task, tscript, vars, script_state)
                
                # check tool referenced variables against the declared variable state and get required
                for vref in tools['variables']['referenced']:
                    if vref not in vars['declared']:
                        vars['required'].append((None, vref))
                # Update declared vars from tool declarations (tool name is the var name in this case)
                vars['declared'].extend(tools['variables']['declared'])
                    
                # Update var state with declared variables
                for ref in vars['declared']:
                    if ref not in var_state:
                        var_state[ref] = 1
                    else:
                        var_state[ref] += 1
                        
                # Check required variables
                # req vars are a tuple (script, variable_name)
                if len(vars['required']) == 0:
                    continue
                else:
                    # TODO make sure I know which scripts these variables are in with a reverse lookup
                    varlist, scriptmap = [], {}
                    for tscript, tvar in vars['required']:
                        if tvar not in var_state:
                            varlist.append(tvar)
                            if tscript not in scriptmap and tscript:
                                scriptmap[tscript] = []
                            if tscript:
                                scriptmap[tscript].append(tvar)
                    if len(varlist) > 0:
                        print(task, vars, tools)
                        report_error(ValidationError(1004,
                            f"The script `{task}` requires variables not declared before it: {varlist}",
                            data={'task': task, 'type': 'variables', 'required': varlist, 'required_scripts': scriptmap}
                        ))
                    
                # Check requried tools
                
                # Check required scripts
                if task not in script_state:
                    script_state[task] = 0
                script_state[task] += 1
                
            else:
                report_error(ValidationError(1001,
                    f"Script `{task}` not found in folder(s): {self.folder}",
                    data={'task': task, 'type': 'file', 'required': f"{self.folder}/{task}.prowl"}
                ))
        tasks_stack = " -> ".join(tasks)
        if not report:
            self.print(f"✅ Requirements check passed for {tasks_stack}")
            return None
        return None if len(errors) == 0 else errors
    
    def process_inputs(self, inputs):
        variables = {}
        for k, v in inputs.items():
            variables[k] = prowl.Variable.from_dict({'name': k, 'value': v})
        return variables
    
    async def get_output(self, task_name:str, fill:prowl.Return):
        # Get the output from an output template with same name as task
        # This output is meant to be non-llm facing and only include variable references
        # TODO change to a format that is more atomic in storing .prout templates with their counterparts in memory
        t = self.tasks[task_name]
        fn = t['folder'] + task_name + ".prout"
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                fc = f.read()
            r = await self.fill(fc, variables=fill.variables)
            return r.completion

    async def run(self, tasks:list[str], atomic:bool=False, variables:dict=None, inputs:dict=None, stops:list[str]=['\n\n', '\n#'], prefix=None, continue_ratio=0.5, stream_level=prowl.StreamLevel.NONE):
        if variables is None:
            variables = {}
        if inputs:
            variables.update(self.process_inputs(inputs))
        self.validate(tasks, variables)

        usage, output = VLLM.Usage(), []
        completion = None if not prefix else prefix + '\n'
        for task in tasks:
            # check for stop from caller
            if self.stop_event:
                stop = await self.stop_event()
                if stop:
                    break
            # okay, business as usual, run the fill
            prompt = self.tasks[task]['code']
            if not atomic and completion:
                prompt = completion + prompt
            fill:prowl.Return = await self.fill(
                prompt, 
                variables=variables, 
                stops=stops, 
                callbacks=self.tools, 
                continue_ratio=continue_ratio, 
                stream_level=stream_level,
                stop_event=self.stop_event, 
                token_event=self.token_event, 
                variable_event=self.variable_event,
                script_name=task,
            )
            completion = fill.completion
            variables = fill.variables

            use = fill.usage.dict()
            usage.add(use) # adds current usage to total
            out = await self.get_output(task, fill)
            if out:
                output.append({'task': task, 'output': out})
            # Handle script streaming level events per fill
            if self.script_event and stream_level.value == prowl.StreamLevel.SCRIPT.value:
                await self.script_event(task, fill, output=out)

        return prowl.Return(completion, variables, usage, output=output)

    @staticmethod
    def add_usages(*usages:VLLM.Usage):
        u = VLLM.Usage()
        for usage in usages:
            u.add(usage.dict())
        return u

    # pass fill for tools instantiated with kwarg stack=
    async def fill(self, 
            template:str, 
            stops:list[str]=["\n\n", "\n#", "##"], 
            variables:dict=None, 
            callbacks:dict=None, 
            stop_event=None, 
            token_event=None, 
            variable_event=None, 
            continue_ratio=0.5, 
            stream_level=prowl.StreamLevel.NONE,
            script_name=None,
        ) -> prowl.Return:
        if variables is None:
            variables = {}

        return await prowl.fill(
            template, 
            stops=stops, 
            variables=variables, 
            callbacks=callbacks, 
            stop_event=stop_event, 
            token_event=token_event, 
            variable_event=variable_event, 
            continue_ratio=continue_ratio, 
            stream_level=stream_level, 
            script_name=script_name,
            silent=self.silent,
        )
        
StreamLevel = prowl.StreamLevel