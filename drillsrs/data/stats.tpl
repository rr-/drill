<!DOCTYPE html>
<html>
<head>
    <title>drill report</title>
    <style type='text/css'>
        body { font-family: sans-serif; text-align: center; font-size: 10pt; line-height: 20pt; color: #333; }
        main { max-width: 50em; margin: 0 auto; }
        h1, h2 { font-weight: normal; }
        h1 { font-size: 18pt; }
        h2 { font-size: 14pt; }
        dl { width: 100%; }
        dt, dd { margin: 0 0.5em; box-sizing: border-box; }
        dt { text-align: right; width: 50%; float: left; }
        dt:after { content: ':'; }
        dd { text-align: left; }
        svg { shape-rendering: crispEdges; }
        #card-stats, #answer-stats { width: 50%; display: inline-block; float: left; }
        #bad-cards ul { list-style-position: inside; margin: 0; padding: 0; text-align: left; }
        .tag-grey { background: #DDD; }
        .tag-blue { background: #DDF; }
        .tag-green { background: #DFD; }
        .tag-red { background: #FDD; }
        .tag-aqua { background: #DFF; }
        .tag-pink { background: #FDF; }
        .tag-yellow { background: #FFB; }

        table { width: 100%; border-spacing: 0; border-collapse: collapse; }
        table th { background: #EEE; font-weight: normal; }
        table td, table th { border: 1px solid #333; padding: 0.1em 0.5em; }

        svg .main-area { fill: rgba(250, 220, 100, 0.5); shape-rendering: geometricPrecision; }
        svg .main-line { fill: none; stroke: orange; stroke-width: 1px; shape-rendering: geometricPrecision; }
        svg .background { fill: #FAFAFA; }
        svg .axis path { fill: none; stroke: grey; stroke-width: 1px; shape-rendering: crispEdges; }
        svg .grid .tick line { stroke: #333; stroke-opacity: 0.1; shape-rendering: crispEdges; }
        svg .correct_answer_count { fill: rgba(50, 180, 0, 0.8); shape-rendering: geometricPrecision; }
        svg .incorrect_answer_count { fill: rgba(240, 20, 20, 0.8); shape-rendering: geometricPrecision; }

        svg .day { fill: #FFF; stroke: rgba(0,0,0,0.1); }
        svg .month { fill: none; stroke: #333; stroke-width: 1px; shape-rendering: crispEdges; }
    </style>
</head>
<body>
<main>
    <script src='//d3js.org/d3.v4.min.js'></script>
    <script src='//d3js.org/d3-scale-chromatic.v1.min.js'></script>

    <h1>Statistics for the &bdquo;{{ deck.name }}&rdquo; deck</h1>

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
                    <dd>{{ percent(active_card_count, active_card_count + inactive_card_count) }}%</dd>
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
                    <dd>{{ percent(correct_answer_count, correct_answer_count + incorrect_answer_count) }}%</dd>
                </div>
            </dl>
        </div>
        <div style='clear:both'></div>
    </section>

    <section id='learning-heatmap'>
        <h2>Learning activity</h2>
    </section>

    <section id='reviews-history'>
        <h2>Reviews over time</h2>
    </section>

    <section id='active-card-count-history'>
        <h2>Active cards over time</h2>
    </section>

    <section id='bad-cards'>
        <h2>Bad condition cards</h2>
        {% if bad_cards %}
            <p>List of cards guessed correctly less than {{ (bad_cards_threshold * 100.0)|round(2) }}% of the time.</p>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Question</th>
                        <th>Answers</th>
                        <th>Tags</th>
                        <th>Answers correct</th>
                    </tr>
                </thead>
                <tbody>
                    {% for card in bad_cards %}
                        <tr>
                            <td>{{ card.id }}</td>
                            <td>{{ card.question }}</td>
                            <td>{{ card.answers|join(', ') }}</td>
                            <td>{{ tags(card.tags) }}</td>
                            <td>
                                {{ card.correct_answer_count }} / {{ card.total_answer_count }}
                                ({{ percent(card.correct_answer_count, card.total_answer_count) }}%)
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>None!</p>
        {% endif %}
    </section>

    <p><small>Generated at {{ date.strftime('%Y-%m-%d %H:%M:%S') }}</small></p>
</main>
<script>
function getDate(dateString)
{
    let [year, month, day] = dateString.split('-').map(x => parseInt(x));
    return new Date(Date.UTC(year, month - 1, day));
}

const data = {{ tojson(learning_history) }};
data.forEach(d => d.date = getDate(d.date));

d3.formatDefaultLocale({
    decimal: '.',
    'thousands': '\u202F',
    grouping: [3],
});

function drawGrid(svg, xScale, yScale, width, height)
{
    svg.append('g')
        .attr('class', 'x grid')
        .attr('transform', 'translate(0,' + height + ')')
        .call(
            d3.axisBottom()
            .scale(xScale)
            .tickFormat('')
            .tickSize(-height)
            .ticks(12));
    svg.append('g')
        .attr('class', 'y grid')
        .call(
            d3.axisLeft()
            .scale(yScale)
            .tickFormat('')
            .tickSize(-width)
            .ticks(5));
}

function drawAxes(svg, xScale, yScale, height)
{
    svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(
            d3.axisBottom()
            .scale(xScale)
            .tickFormat(d3.timeFormat('%b %Y')));
    svg.append('g')
        .attr('class', 'y axis')
        .call(d3.axisLeft().scale(yScale));
    svg.selectAll('.x.axis text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-45)');
}

function drawActiveCardCountHistoryChart()
{
    const margin = {top: 10, right: 10, bottom: 50, left: 50};
    const target = d3.select('#active-card-count-history');
    const width = (
        target.node().getBoundingClientRect().width
        - margin.left
        - margin.right);
    const height = width / 3.0;

    // scales
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width - width / data.length]);
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.total_active_card_count)])
        .range([height, 0]);

    // main
    const svg = target
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    // plot
    svg.append('path')
        .attr('class', 'main-area')
        .datum(data)
        .attr('d',
            d3.area()
            .x(d => xScale(d.date))
            .y0(yScale(0))
            .y1(d => 1 + yScale(d.total_active_card_count)));
    svg.append('path')
        .attr('class', 'main-line')
        .datum(data)
        .attr('d',
            d3.line()
            .x(d => xScale(d.date))
            .y(d => 1 + yScale(d.total_active_card_count)));

    drawGrid(svg, xScale, yScale, width, height);
    drawAxes(svg, xScale, yScale, height);
}

function drawReviewsHistoryChart()
{
    const margin = {top: 10, right: 10, bottom: 50, left: 50};
    const target = d3.select('#reviews-history');
    const width = (
        target.node().getBoundingClientRect().width
        - margin.left
        - margin.right);
    const height = width / 3.0;

    // scales
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width - width / data.length]);
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.incorrect_answer_count + d.correct_answer_count)])
        .range([height, 0]);

    // main
    const svg = target
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    const area = d3.area()
        .x(d => xScale(d.data.date))
        .y0(d => 0.5 + yScale(d[0]))
        .y1(d => 0.5 + yScale(d[1]));
    const stack = d3.stack()
        .keys(['incorrect_answer_count', 'correct_answer_count']);

    // plot
    svg.selectAll('.day')
        .data(stack(data))
        .enter()
        .append('path')
        .attr('class', d => d.key)
        .attr('d', area);

    drawGrid(svg, xScale, yScale, width, height);
    drawAxes(svg, xScale, yScale, height);
}

function drawStudyActivityHeatMap()
{
    const margin = {top: 10, right: 10, bottom: 10, left: 50};
    const target = d3.select('#learning-heatmap');
    const width = (
        target.node().getBoundingClientRect().width
        - margin.left
        - margin.right);
    const cellSize = width / 53;
    const height = cellSize * 7;

    const color = d3.scalePow()
        .domain([0, 100])
        .clamp(true)
        .range(['#F5F5D5', '#4A0']);

    const svg = target
        .selectAll('svg')
        .data(d3.set(data, d => d.date.getFullYear()).values().map(d => parseInt(d)))
        .enter()
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .attr('class', 'RdYlGn')
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    svg.append('text')
        .attr('transform', 'translate(-12,' + cellSize * 3.5 + ')rotate(-90)')
        .style('text-anchor', 'middle')
        .text(d => d);

    const rect = svg.selectAll('.day')
        .data(d => d3.utcDays(
            new Date(Date.UTC(d, 0, 1)),
            new Date(Date.UTC(d + 1, 0, 1))))
        .enter().append('rect')
        .attr('class', 'day')
        .attr('width', cellSize)
        .attr('height', cellSize)
        .attr('x', d => d3.utcMonday.count(d3.utcYear(d), d) * cellSize)
        .attr('y', d => ((d.getDay() + 6) % 7) * cellSize)
        .datum(d3.timeFormat('%Y-%m-%d'));

    rect.append('title')
        .text(d => d);

    svg.selectAll('.month')
        .data(d => d3.utcMonths(
            new Date(Date.UTC(d, 0, 1)),
            new Date(Date.UTC(d + 1, 0, 1))))
        .enter().append('path')
        .attr('class', 'month')
        .attr('d', monthPath);

    const nest = d3.nest()
        .key(d => d.date.toISOString().substring(0, 10))
        .rollup(d => d3.sum(d, d => d.new_active_card_count))
        .map(data);

    rect.filter(d => nest.has(d) || (new Date(d) < new Date()))
        .attr('class', 'day')
        .attr('style', d => 'fill: ' + color(nest.get(d) || 0))
        .select('title')
        .text(d => d + ': ' + (nest.get(d) || 0));

    function monthPath(t0) {
        const t1 = new Date(Date.UTC(t0.getFullYear(), t0.getMonth() + 1, 0));
        const d0 = (t0.getDay() + 6) % 7;
        const w0 = d3.utcMonday.count(d3.utcYear(t0), t0)
        const d1 = (t1.getDay() + 6) % 7;
        const w1 = d3.utcMonday.count(d3.utcYear(t1), t1);
        return 'M' + (w0 + 1) * cellSize + ',' + d0 * cellSize
            + 'H' + w0 * cellSize
            + 'V' + 7 * cellSize
            + 'H' + w1 * cellSize
            + 'V' + (d1 + 1) * cellSize
            + 'H' + (w1 + 1) * cellSize
            + 'V' + 0
            + 'H' + (w0 + 1) * cellSize
            + 'Z';
    }
}

drawReviewsHistoryChart();
drawActiveCardCountHistoryChart();
drawStudyActivityHeatMap();
</script>
</body>
</html>
