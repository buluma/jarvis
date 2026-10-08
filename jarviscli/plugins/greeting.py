from plugin import alias, plugin


@alias("hi", "hello", "hey", "how are you", "good morning", "good evening")
@plugin("greet")
def greet(jarvis, s):
    """Respond to a greeting and help the user get started."""
    jarvis.say("Hi! Try 'help' to browse commands, or tell me what you need.")
