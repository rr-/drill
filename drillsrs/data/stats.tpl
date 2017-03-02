<!DOCTYPE html>
<html>
<head>
    <title>drill report</title>
    <style type="text/css">
        body { font-family: sans-serif; text-align: center; font-size: 10pt; line-height: 20pt; }
        main { max-width: 40em; margin: 0 auto; }
        h1, h2 { font-weight: normal; }
        h1 { font-size: 18pt; }
        h2 { font-size: 14pt; }
        dl { width: 100%; }
        dt, dd { margin: 0 0.5em; box-sizing: border-box; }
        dt { text-align: right; width: 50%; float: left; }
        dt:after { content: ':'; }
        dd { text-align: left; }
        svg { border: 1px solid black; shape-rendering: crispEdges; }
        #main-chart-section svg { width: 100%; height: 10em; }
        #card-stats, #answer-stats { width: 50%; display: inline-block; float: left; }
        #bad-cards ul { list-style-position: inside; margin: 0; padding: 0; text-align: left; }
    </style>
</head>
<body>
<main>
    <h1>Statistics for &bdquo;{{ deck.name }}&rdquo; deck</h1>

    <section id='main-chart-section'>
        <h2>Ratio of correct to incorrect answers</h2>
        <svg id="ratio" xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {{ answer_histogram.length }} {{ answer_histogram.max_value }}" preserveAspectRatio="none">
            {% set vars = {'x': 0} %}
            {% for item in answer_histogram -%}
                <rect x="{{ vars.x }}" width="{{ item.weight }}" y="{{ answer_histogram.max_value - item.correct_answer_count }}" height="{{ item.correct_answer_count }}" fill="darkseagreen"/>
                <rect x="{{ vars.x }}" width="{{ item.weight }}" y="{{ answer_histogram.max_value - item.total_answer_count }}" height="{{ item.incorrect_answer_count }}" fill="red"/>
                <rect x="{{ vars.x }}" width="{{ item.weight }}" y="0" height="{{ answer_histogram.max_value }}" fill="transparent">
                    <title>{{ item.correct_answer_count }} correct answers, {{ item.incorrect_answer_count }} incorrect answers</title>
                </rect>
                {% if vars.update({'x': vars.x + item.weight}) %}{% endif %}
            {%- endfor %}
        </svg>

        <h2>Active cards over time</h2>
        <svg id="kot" xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {{ activity_histogram|length }} {{ activity_histogram_max }}" preserveAspectRatio="none">
            {% for item in activity_histogram %}
                <rect x="{{ loop.index - 1 }}" width="1" y="{{ activity_histogram_max - item }}" height="{{ activity_histogram_max }}" fill="darkseagreen"/>
                <rect x="{{ loop.index - 1 }}" width="1" y="0" height="{{ activity_histogram_max }}" fill="transparent">
                    <title>{{ activity_histogram|length - loop.index }} week(s) ago: {{ item }} items</title>
                </rect>
                <line x1="{{ loop.index - 1 }}" y1="0" x2="{{ loop.index - 1 }}" y2="{{ activity_histogram_max }}" stroke-width="1" vector-effect="non-scaling-stroke" stroke="rgba(0, 0, 0, 0.1)"/>
            {% endfor %}
        </svg>
    </section>

    <section id='text-section'>
        <div id='card-stats'>
            <h2>Card stats</h2>
            <dl>
                <div>
                    <dt>Total cards</dt>
                    <dd>{{ active_card_count + inactive_card_count }}</dd>
                </div>

                <div>
                    <dt>Active cards</dt>
                    <dd>{{ active_card_count }}</dd>
                </div>

                <div>
                    <dt>Inactive cards</dt>
                    <dd>{{ inactive_card_count }}</dd>
                </div>

                <div>
                    <dt>Percent active</dt>
                    <dd>{{ (active_card_count * 100.0 / (active_card_count + inactive_card_count))|round(2) }}%</dd>
                </div>
            </dl>
        </div>

        <div id='answer-stats'>
            <h2>Answer stats</h2>
            <dl>
                <div>
                    <dt>Total answers</dt>
                    <dd>{{ correct_answer_count + incorrect_answer_count }}</dd>
                </div>

                <div>
                    <dt>Correct answers</dt>
                    <dd>{{ correct_answer_count }}</dd>
                </div>

                <div>
                    <dt>Incorrect answers</dt>
                    <dd>{{ incorrect_answer_count }}</dd>
                </div>

                <div>
                    <dt>Percent correct</dt>
                    <dd>{{ (correct_answer_count * 100.0 / (correct_answer_count + incorrect_answer_count))|round(2) }}%</dd>
                </div>
            </dl>
        </div>
        <div style='clear:both'></div>
    </section>

    <section id='bad-cards'>
        <h2>Bad condition cards</h2>
        {% if bad_cards.empty %}
            <p>None!</p>
        {% else %}
            <p>List of cards guessed correctly less than {{ (bad_cards_threshold * 100.0)|round(2) }}% of the time.</p>
            <ul>
                {% for card in bad_cards %}
                    <li>
                        {{ card.question }} ({{ card.tags|join(', ') }}) - {{ (card.correct_answer_count * 100.0 / card.total_answer_count)|round(2) }}%
                    </li>
                {% endfor %}
            </ul>
        {% endif %}
    </section>
</main>
</body>
</html>
