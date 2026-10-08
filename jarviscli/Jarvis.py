# -*- encoding: utf-8 -*-

import os
import re
from difflib import get_close_matches
from colorama import Fore
import sys
import tempfile
from CmdInterpreter import CmdInterpreter

# register hist path
HISTORY_FILENAME = tempfile.TemporaryFile('w+t')


PROMPT_CHAR = '~>'

"""
    AUTHORS' SCOPE:
        We thought that the source code of Jarvis would
        be more organized if we treat Jarvis as Object.
        So we decided to create this Jarvis Class which
        implements the core functionality of Jarvis in a
        simpler way than the original __main__.py.
    HOW TO EXTEND JARVIS:
        In progress..
    DETECTED ISSUES:
        * Furthermore, "near me" command is unable to find
        the actual location of our laptops.
"""


class Jarvis(CmdInterpreter, object):
    # variable used at Breakpoint #1.
    # allows Jarvis say "Hi", only at the first interaction.
    first_reaction_text = ""
    first_reaction_text += Fore.CYAN + \
        'Speech output is disabled by default.' + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.CYAN + 'To enable spoken replies, type: '
    first_reaction_text += Fore.RESET + Fore.MAGENTA + 'enable sound' + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.CYAN + \
        "For microphone input, use 'hear' after installing optional audio support." + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.CYAN + \
        "Type 'help' for a list of available actions." + Fore.RESET
    first_reaction_text += "\n"
    prompt = (
        Fore.MAGENTA
        + "{} Hi, what can I do for you?\n".format(PROMPT_CHAR)
        + Fore.RESET)

    # Used to store user specific data

    def __init__(self, first_reaction_text=first_reaction_text,
                 prompt=prompt, first_reaction=True,
                 directories=["jarviscli/plugins", "custom"]):
        directories = self._rel_path_fix(directories)

        if sys.platform == 'win32':
            self.use_rawinput = False
        self.regex_dot = re.compile('\\.(?!\\w)')
        CmdInterpreter.__init__(self, first_reaction_text, prompt,
                                directories, first_reaction)

    def _rel_path_fix(self, dirs):
        dirs_abs = []
        work_dir = os.path.dirname(__file__)
        # remove 'jarviscli/' from path
        work_dir = os.path.dirname(work_dir)

        # relative -> absolute paths
        for directory in dirs:
            if not directory.startswith(work_dir):
                directory = os.path.join(work_dir, directory)
            dirs_abs.append(directory)
        return dirs_abs

    def default(self, data):
        """Jarvis let's you know if an error has occurred."""
        requested = getattr(self, "_last_user_input", data).strip()
        normalized = re.sub(r"[^\w\s]", "", requested.lower()).strip()
        command_names = self._command_names()
        suggestions = get_close_matches(
            normalized, sorted(command_names), n=3, cutoff=0.68
        )
        if suggestions:
            formatted = ", ".join(f"'{command}'" for command in suggestions)
            self.say(
                f"I couldn't identify '{requested}'. Did you mean {formatted}?",
                Fore.MAGENTA,
            )
        else:
            self.say(
                f"I couldn't identify '{requested}'. Type 'help' for commands.",
                Fore.MAGENTA,
            )

    def _command_names(self):
        """Return registered leaf commands and built-in command names."""
        names = {"help", "status", "exit", "quit", "goodbye"}

        def collect(storage, prefix=()):
            for part, action in storage.items():
                command = prefix + (part,)
                if action.is_callable_plugin():
                    names.add(" ".join(command))
                children = action.get_plugins()
                if children:
                    collect(children, command)

        collect(self._plugin_manager.get_plugins())
        return names

    def precmd(self, line):
        """Hook that executes before every command."""
        self._last_user_input = line.strip()
        words = line.split()
        HISTORY_FILENAME.write(line + '\n')

        # append calculate keyword to front of leading char digit (or '-') in line
        if words and (words[0].isdigit() or line[0] == "-"):
            line = "calculate " + line
            words = line.split()

        if line.startswith("help"):
            return line
        if line.startswith("status"):
            return line

        if not words:
            line = "None"
        else:
            line = self.parse_input(line)
        return line

    def postcmd(self, stop, line):
        """Hook that executes after every command."""
        if self.first_reaction:
            self.prompt = (
                Fore.MAGENTA
                + "{} What can I do for you?\n".format(PROMPT_CHAR)
                + Fore.RESET)
            self.first_reaction = False
        if self.enable_voice:
            self.speech.text_to_speech("What can I do for you?\n")

    def speak(self, text):
        if self.enable_voice:
            self.speech.text_to_speech(text)

    def parse_input(self, data):
        """This method gets the data and assigns it to an action"""
        data = data.lower()
        # say command is better if data has punctuation marks
        if "say" not in data:
            data = data.replace("?", "")
            data = data.replace("!", "")
            data = data.replace(",", "")

            # input sanitisation to not mess up urls / numbers
            data = self.regex_dot.sub("", data)

        # Check if Jarvis has a fixed response to this data
        if data in self.fixed_responses:
            output = self.fixed_responses[data]
        else:
            # if it doesn't have a fixed response, look if the data corresponds
            # to an action
            output = self.find_action(
                data, self._plugin_manager.get_plugins().keys())
        return output

    def find_action(self, data, actions):
        """Checks if input is a defined action.
        :return: returns the action"""
        if not actions:
            return "None"

        action_names = set(actions)
        words = data.split()
        if "near" in words:
            near_index = words.index("near")
            initial_words = words[:near_index]
            remaining_words = words[near_index + 1:]
            return "near " + " ".join(
                initial_words + ["|"] + remaining_words
            )

        # Route through the first command word so nested groups work: for
        # "movie search title", dispatch to `movie` before matching `search`.
        for index, word in enumerate(words):
            if word in action_names:
                return word + " " + " ".join(words[index + 1:])
        return "None"

    def executor(self, command):
        """
        If command is not empty, we execute it and terminate.
        Else, this method opens a terminal session with the user.
        We can say that it is the core function of this whole class
        and it joins all the function above to work together like a
        clockwork. (Terminates when the user send the "exit", "quit"
        or "goodbye command")
        :return: Nothing to return.
        """
        if command:
            self.execute_once(command)
        else:
            self.cmdloop()
