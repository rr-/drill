# drill-srs

A CLI program for learning things through [spaced repetition](https://en.wikipedia.org/wiki/Spaced_repetition).

### Features

- CLI (ideal for `tmux`+`ssh`)
- Multiple decks
- No configuration needed
- Colorful tags
- JSON exports/imports for easy deck manipulation
- HTML reports

![screenshot](https://cloud.githubusercontent.com/assets/1045476/23531471/d7989110-ffa6-11e6-9dad-b9b8201bc07e.png)


### How to use

Flashcards are organized in decks, so that you can study multiple subjects at
once. To start studying, first create a deck and populate it with cards
manually or through an import.

Each "study session" will then display the cards to memorize. Following the
study, you'll be invited to a "review session" of all cards shown so far, where
your answers will affect how often a given card will be shown for
re-evaluation. A correct answer increases the card's score by 1, while a
mistake decreases its score by 1.

This is how the score translates into the re-evaluation delay:

Card score | Wait time
---------- | ---------
0          | none (just after the study session)
1          | 4 hours
2          | 8 hours
3          | 1 day
4          | 3 days
5          | 1 week
6          | 2 weeks
7          | 1 month
8          | 4 months

For example, if you answered the given card correctly thrice (score 3) and now
made a mistake (score is 2 now), this card will re-appear after 8 hours. The
score can't fall outside the range in the table.

Such review system reinforces the quality of the memorization.

### Questions

**Q: Why not anki?**  
A: I like anki, but there's no CLI version I could use remotely, so I decided
   to roll my own simple program.

**Q: Why not SuperMemo or other better algorithms?**  
A: These are cool, but I wanted `drill` to stay simple. Additionally, the
system used by `drill` is very similar to the one used by
[wanikani.com](//wanikani.com), which I hold in very high regard.
