"""The five routes, their definitions, and the two prompts. TODO 1 and 4.

Write the definitions before you write any code. This is not a style
preference, it is the difference between a measurement and a coincidence.

If the boundary between a status chase and a request is not written down
before the prompt is written, then your prompt and the gold labels disagree
in a way neither of you has noticed, and the accuracy number you produce is
measuring the gap between your definitions and ours rather than the quality
of your classifier. You will not be able to tell those two apart afterwards.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# TODO 1. One sentence per route, written before any prompt.
# --------------------------------------------------------------------------
#
# Two pieces of advice, both of which cost people marks every year.
#
# Define each route by what the help desk is expected to DO, not by what the
# message feels like. "The sender is annoyed" is not a route: a request can
# be furious and a complaint can be perfectly polite. Tone is a property of
# the writing. The route is a property of the work.
#
# `other` still needs a real definition even though it means "everything
# else". A route defined only by exclusion is where a classifier hides its
# failures, and you will not find them at the checkpoint.
#
# You may disagree with the definitions in queries.py. If you do, that is a
# legitimate choice and it has a consequence: your accuracy is then measured
# against labels produced under a different convention. Decide deliberately
# and write the decision in DECISIONS.md.

ROUTE_DEFINITIONS = {
    "request": "The sender wants the help desk to take a concrete action, provide a service, or solve a specific problem.",
    "info": "The sender wants factual information or an explanation about a commune service, without asking for an action to be taken.",
    "status": "The sender wants an update on the progress or current state of a previously submitted request, case, or issue.",
    "complaint": "The sender wants the help desk to acknowledge dissatisfaction with a commune service, handling, delay, or outcome.",
    "other": "The sender's message does not require a service action, factual answer, status update, or complaint handling, and should be handled as a general or uncategorized message.",
}

ROUTES = tuple(ROUTE_DEFINITIONS)


def check_definitions_written() -> None:
    """Fail with the marker number rather than shipping placeholder text.

    Called by the runner before anything else. Without it, a group that
    starts coding at minute one gets a classifier prompt that literally
    contains the word TODO, a plausible-looking accuracy number, and no
    indication that block 1 never happened.
    """
    unwritten = [r for r, d in ROUTE_DEFINITIONS.items()
                 if not d or d.strip().upper().startswith("TODO")]
    if unwritten:
        raise NotImplementedError(
            f"TODO 1: these routes have no definition yet: {unwritten}.\n"
            f"Write one sentence each, in terms of what the help desk must "
            f"DO, before you run anything. That is block 1, and every number "
            f"you produce afterwards depends on it.")
    if SYSTEM_MONOLITH.strip().upper().startswith("TODO"):
        raise NotImplementedError(
            "TODO 4: the monolith control prompt is still a placeholder. "
            "It is the system your router has to beat, so it has to be a "
            "fair opponent.")


def _definition_block() -> str:
    width = max(len(r) for r in ROUTES)
    return "\n".join(f"{r:<{width}}  {d}" for r, d in
                     ROUTE_DEFINITIONS.items())


# The router prompt is built from your definitions, so there is one place to
# edit and the prompt cannot drift away from what you wrote down.

SYSTEM_ROUTER = f"""\
You classify one message arriving at the help desk of a Luxembourg commune \
into exactly one route. Messages arrive in English, French, or German.

{_definition_block()}

confidence  A number from 0 to 1. Use the whole range. If two routes are \
genuinely defensible for this message, say so with a low number rather than \
picking one confidently.
evidence    A span copied from the message, character for character, that \
justifies the route. Do not translate it and do not paraphrase it.
"""


# --------------------------------------------------------------------------
# TODO 4. The control.
# --------------------------------------------------------------------------

SYSTEM_MONOLITH = """\
You handle messages sent to the help desk of a Luxembourg commune.
Messages may be written in English, French, or German.

Decide what kind of help the sender needs and respond appropriately:

- For a request, acknowledge the requested action or problem and explain what should happen next.
- For an information question, answer using only information available in the message and your instructions. Do not invent facts.
- For a status query, acknowledge that the sender is asking about an existing case or request and explain that its status needs to be checked.
- For a complaint, acknowledge the specific problem or dissatisfaction without making promises about a fix or deadline.
- For anything else, respond appropriately without pretending that a service request, case, or complaint exists.

Answer in the language of the message and keep the response under eighty words.
"""


# --------------------------------------------------------------------------
# TODO 4b. The specialists. Write two of the five yourself.
# --------------------------------------------------------------------------
#
# `info` and `complaint` are written for you as worked examples. Read them
# and notice what each one can say that the monolith cannot: the info
# specialist is forbidden to invent a fact, and the complaint specialist is
# forbidden to promise a fix. Neither instruction could go in the monolith
# without also applying to the other four kinds.
#
# That is the actual argument for routing, and it is an argument about what
# you can guarantee rather than about average quality. Write the other three
# with the same question in mind: what can this specialist be forbidden to
# do, now that it only handles one kind of message?
#
# The `request` specialist is week 2's extractor. Its job is to produce the
# ServiceRequest record you already built and scored, not prose. Wiring your
# week 2 code in behind this route is the "if you finish early" task.

SPECIALISTS = {
    "request": ("You handle service requests that require the commune to take an action "
                "or solve a specific problem. Extract the structured service-request "
                "information required by the Week 2 ServiceRequest schema. Do not answer "
                "the sender conversationally and do not invent missing information."),
    "info": ("You answer a question about a commune service, using only "
             "what the message and your instructions contain. You have no "
             "reference material, so you must never state an opening time, "
             "a fee, a form number, or a deadline. Say what you can, say "
             "plainly what you would have to look up, and offer to find "
             "it. Answer in the language of the message, under eighty "
             "words."),
    "status": ("You handle requests for updates on an existing case, request, or issue. "
                "Acknowledge what the sender is waiting for, but do not create a new "
                "request and do not invent the current status, completion date, or case "
                "history. State that the existing case needs to be checked. Answer in "
                "the language of the message, under eighty words."),
    "complaint": ("You acknowledge a complaint about the commune service. "
                  "Name the specific thing the sender is dissatisfied with, "
                  "so it is clear you read it. Do not defend the service, "
                  "do not explain why it happened, and do not promise a "
                  "fix or a date. Say it is being escalated and to whom in "
                  "general terms. Answer in the language of the message, "
                  "under eighty words."),
    "other": ("You handle general messages that do not require a service action, factual "
              "service answer, status check, or complaint handling. Respond briefly and "
              "appropriately without creating a ticket, claiming a case exists, or "
              "escalating the message. Ask for clarification if the sender's intended "
              "help-desk action is unclear. Answer in the language of the message, "
              "under eighty words."),
}
