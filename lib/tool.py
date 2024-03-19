
class ProwlTool:
    
    def __init__(self, stack=None, argmap=None, name=None, description=None):
        self.argmap = argmap or []
        self.name = name
        self.description = description
        self.stack = stack
    
    class Return:
        def __init__(self, completion, data):
            self.completion = completion
            self.data = data
            
    def run(self, *args, **kwargs):
        pass
    
    def vars(self, *args, **kwargs):
        pass
    
    def map_args(self, arguments):
        args = []
        kwargs = {}

        if not self.argmap:
            return self._map_args_default(arguments)

        for i, argument in enumerate(arguments):
            if i < len(self.argmap):
                mapping = self.argmap[i]
                if 'arg' in mapping:
                    args.append(argument)
                elif 'kwarg' in mapping:
                    kwargs[mapping['kwarg']] = argument
            else:
                args.append(argument)  # Default to positional argument
        return args, kwargs
    
    def _map_args_default(self, arguments):
        args = arguments
        return args, {}
    
    ## To use these kwargs functions you must 
    # declare **kwargs in the run method of your tool
    # pass your stack into your tool instantiation eg: SnippetTool(stack)
    # declare stack:ProwlStack in your tool class definition __init__
    # Example call in a run method to get completion:
    #   completion = self.completion(kwargs)

    def arg_name(self, kwargs:dict, index:int):
        return kwargs['__arguments'][index]
    
    def completion(self, kwargs:dict):
        return kwargs['__completion']
    
    def variables(self, kwargs:dict):
        return kwargs['__variables']
    
    def stream_level(self, kwargs:dict):
        return kwargs['__stream_level']
    
    def callback_match(self, kwargs:dict):
        return kwargs['__call_match']
    
    def inspect_callback(self, script_name):
        # use this for stack.inspect and return any extra requried variables
        # then inspect will handle the rest of variable requirement validation
        return None, None
    
    def validate_callback(self, context_name, subject_name, variable_state, script_state):
        # this allows you to place a specific validation with ValueError upon fail
        # example: in tools/out/tool.py, I don't need to check if the `subject_name` script exists
        # -> I need to check if the variables from that script are within the stack's variable state
        # -> thus the requirements for `context_name` script are properly met and we can return True
        pass
    
    def ns_update(self):
        # return any type of dictionary to go into the variable namespace in your tool
        # the namespace is already filled with variables at this point
        # you can fill it with overrides, or for instance I fill it with names of scripts on the stack in the @out tool
        return {}