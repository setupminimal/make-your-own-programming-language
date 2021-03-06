#!/usr/bin/env python3

"""
This file is part of the supplementary materials
for a talk called "Make Your Own Programming Language in 30 Minutes".

The git repository that contains this file starts from scratch, and
slowly builds its way up towards a working interpreter for a version
of Forth with several additional features meant to highlight how to
extend the basic language. The commit messages also explain what is
being done in each step and why, so be sure to take a look at those

The whole point is to get you excited about making your own programming
language - please grab a text editor, your programming language of choice,
and follow along! All the code in this repository is under a MIT license,
meaning that you can copy it, adapt it, and learn from it, freely and
without restriction, as long as you credit me (Daroc Alden) in any
derivative works.

With that said, let's dive right in.
"""

import sys

# These will be used momentarily in our 'interpret' function.
# `builtins` is used to represent the basic functions that are defined
# in python.
builtins = {}
# `definitions` is used to hold the definitions of user-defined words
definitions = {}

def interpret(program, stack=[]):
    """
    Interpret takes a program (with the first word last, as discussed above)
    and an optional stack of data to use, and performs whatever function
    the program describes upon the stack. The new stack is returned.
    """
    
    while program:
        # This removes the 'next' word in the program
        word = program.pop()

        # If that word is something that the user has defined,
        # we add the definition of that word onto the program,
        # which has the effect of making the interpreter do
        # whatever is in that definition next.
        if word in definitions.keys():
            program += definitions[word][:]
        # If, on the other hand, the word is a built-in word,
        # we just look up its definition and call the python
        # code that implements it. Notice how we pass in both
        # the program and the stack - that will be important
        # later, because it allows builtin words to modify the
        # remaining program.
        elif word in builtins.keys():
            builtins[word](program, stack)
        # If the word hasn't been defined, we check to see if
        # it's a constant, like `2`. If so, the data just gets
        # put on the stack.
        elif word.isnumeric():
            stack.append(int(word))
        # And if the word wasn't recognized, we emit an error
        # message and quit. We'll revise this later to add
        # a feature like Ruby's `method_missing` that can
        # do something more helpful.
        else:
            print(f'Unknown word {word}')
            sys.exit(1)
    
    return stack

# Finally, we need at least one builtin in order to have a program
# _do_ anything. This code just pops two numbers off the stack, adds
# them together, and puts the result back on the stack.
builtins['+'] = lambda p, stack: stack.append(stack.pop() + stack.pop())

# The same thing works for multiplication
builtins['*'] = lambda p, stack: stack.append(stack.pop() * stack.pop())

# But it won't quite work for subtraction. Subtraction actually cares
# about the order of its arguments, so we want to be careful to pop
# them off of the stack in the right order. By convention the subtrahend
# comes on the top of the stack, and the minuend under it.
# (minuend - subtrahend = result)
#
# This means that code like `3 2 -` will be `1`.
def subtract(program, stack):
    subtrahend = stack.pop()
    minuend = stack.pop()
    stack.append(minuend - subtrahend)

builtins['-'] = subtract

# Arithmetic operations aren't the only thing that we can do, though.
# Since everything in Forth happens on the stack, another class of basic
# useful operators are stack-manipulation operators, like `dup` (short for
# duplicate).

def dup(program, stack):
    value = stack.pop()
    stack.append(value)
    stack.append(value)

builtins['dup'] = dup

# This means that we can, for example, square a number by duplicating it
# and multiplying it by itself: `5 dup *`. See Example 2.

# So far, we've just been adding words to the `builtins` dictionary. How
# can we let people programming in our language define and use their own
# words? The answer is a cool trick, which explains why we've been passing
# the program as well as the stack to each of our built-in words. We'll make
# a built-in word that manipulates the _program_ instead of the stack.
def define(program, stack):
    # This word (usually called ':' in Forth, presumably because it looks
    # pretty) looks at the next word in the program, and then binds that word
    # to the following sequence of words
    name = program.pop()
    definition = []
    # We search through the program, adding everything that comes before
    # the next semicolon. Again, the semicolon is traditional. You can use
    # different words, like 'define' and 'end' if you want to.
    while program[-1] != ';':
        definition.append(program.pop())
    # Then we remove the trailing ';', so that the program won't actually
    # try to interpret it.
    program.pop()

    # By adding the words in the way we did, the definition has ended up
    # backwards relative to the program, so we'll reverse it so that it
    # matches up.
    definition.reverse()

    # Finally, we can add the definition to the `definitions` dictionary,
    # which is used up above in `interpret` to interpret user-defined
    # words.
    definitions[name] = definition

builtins[':'] = define
    
# We can now define our own words, like `: square dup * ;`, and then use them.
# See Example 3.

# We're still missing one thing to call this program our own: loops
#
# We can define our own functions, manipulate values, etc., but we can't
# ever repeat anything or go back, which means that we can't solve most programming
# problems. Luckily, there's a really easy way to add looping: Add conditional
# evaluation, i.e. if statements.
def unless(program, stack):
    if stack.pop(): # If the TOS is True
        program.pop() # Skip the next word

builtins['unless'] = unless

# Then, for demonstration, let's add `==` and `print`.

builtins['=='] = lambda p, stack: stack.append(stack.pop() == stack.pop())
builtins['print'] = lambda p, stack: print(stack.pop())

# Now we can do loops and if statements. See Example 4! At this point
# our language is minimally feature complete: It is a working programming
# language. From here, you might want to try making a few small programs,
# figuring out what would make writing those easier, and then try adding
# those features yourself. Happy hacking!


if __name__ == '__main__':
    # Programs to interpret get passed on the command line.
    # If there are none, or if someone asks for help, show them some help.

    if len(sys.argv) <= 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help = f"""
[python] {sys.argv[0]} programs...

Interpret several minimal forth programs in sequence. Libraries should
come before the programs that depend on them.
"""
        print(help)
        sys.exit(0)

    for file in sys.argv[1:]:
        with open(sys.argv[1], 'r') as f:
            # We're basing the language that we're creating here on Forth[1] for a very
            # simple reason. Most programming languages have some amount of syntax
            # that we would have to tokenize and parse. Forth-like languages have
            # basically no syntax at all - programs are just lists of words, separated
            # by whitespace.
            #
            # [1]: https://en.wikipedia.org/wiki/Forth_(programming_language)
            #
            # You can think of this step as the 'tokenization' step that a lot of other
            # programming languages need. The only real difference that since our
            # syntax is so simple, the code to split the program into tokens is also
            # really simple. If you wanted to, you could later extend this step
            # to do more complicated processing (for example, to handle parentheses
            # differently, so that they don't just get counted as part of the word
            # that they touch.)
            program = f.read().split()

        # We're later going to treat the source code of the program like a stack,
        # which means frequently popping from and appending to the source. That's
        # more efficient (in Python at least, which uses Array-backed lists) to do
        # from the end, so we reverse the program, so that the first word is at the end
        #
        # This is like the 'parsing' step in other programming languages: We're
        # changing the representation of the program into something that is easier for
        # our interpreter to deal with. In this case, since Forth has very little
        # syntax, that's quite easy. You could extend this step to do more complicated
        # parsing, for example to implement list literals. We'll add more complexity
        # here in future commits.
        program.reverse()
            
        # Show the results of interpreting the program.
        print(interpret(program))
