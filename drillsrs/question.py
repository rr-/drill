from drillsrs import util

question_prompt = "Question:"


def render_question_prompt(raw_question, raw_answers, tags):
    rendered_tags = "[%s]" % util.format_card_tags(tags) if tags else ""

    if util.is_raw_multiline(raw_question):
        rendered_question = util.from_raw_to_multiline(raw_question)
        return f"{question_prompt} {rendered_tags}\n{rendered_question}"
    else:
        return f"{question_prompt} {raw_question} {rendered_tags}"
