ANSITERM-FLASHCARD Specification
================================

Definitions
-----------
These definitions can be skipped on first reading. I find that keeping
a dictionary of terms guards against introducing synonyms in the
prose. Having more than one name for any concept is confusing.

Game
  Flash card sessions are not usually called games, but what
  definition of 'game' would include Solitaire and exclude flash cards?

Player
  the user of our game during the course of play.

Dealer
  The agent that does all card operations on behalf of the
  player. In a physical game, the player would also act as his own
  dealer. But separating the actions makes the role that the computer
  plays clearer.

Card
  A card is a pair of (question, answer). The representation of
  these fields can remain unspecified until concrete implementations are
  considered. A card in the dealt deck also needs an
  orientation. (question, answer, answer-up). Answer-up is a Boolean
  with the obvious meaning. The question/answer pair uniquely identifies
  a card. A game has no duplicate cards.

Card Set
  The set of all cards used for any play of the game. The card
  set is fixed during play, but of course the player can choose any set
  at the start of a game.

Decks
  During the course of play, the card set is partitioned into
  four decks: dealt, play, kept and trash. Any of these decks may be
  empty. Cards move among the decks during the course play, but the
  union of all of the decks is always equal to the card set.

Dealt Deck
  The currently dealt card. It may appear as answer-up or
  answer down. This deck never has more than one card, but it may be
  empty. Note that I usually say the "the dealt card" rather than "the
  top card of the dealt deck." The later is not wrong, but it is
  misleading, as there is no other card in the deck.

Trash Deck
  Cards that have been learned are tossed in the trash. The
  trash cards are never used again during the course of play. They are
  of no use to the program, but an explicit trash deck makes stating the game
  invariant easier. The trash deck is represented as a set.

Play Deck
  The source of cards to learn. Initially the entire card set
  appears in the play deck. Each deal operation moves the top card to
  the dealt deck. The shuffle operation moves all the cards from the
  kept deck to the top of the play deck. The play deck is a list of
  cards. There is no defined ordering relation on cards.

Kept Deck
  Cards that have been played, but not declared learned are
  saveed to the kept deck. Kept card are put back in play by the shuffle
  operation. The kept deck is a sequence with the most recent cards
  going to the end. The arrangement allows me to prevent recently seen
  cards from being immediately dealt again after a shuffle.

(Game) State
  The four decks: (dealt, play, kept and trash) plus the
  card set comprise the state. The card set never changes in any game
  play. The obvious optimization is to leave the card set out of the
  state, but I need it to specify the game invariant.

Start State
  At the beginning of a game play, the card set is shuffled
  in the the play deck. This is the result of the init operation.

Operation
  An operation changes the game state. Formally, the operation
  is a triple (before-state, operation-name, after-state). The set of
  operations are predefined and unchanging. We often refer to the
  operation by its name. We can also talk about the operation-triple.

Init (Operation)
  Establishes the start state.

Deal (Operation)
  Move the top card of the play deck to the dealt
  deck, question side up.

Flip (Operation)
  Turn over the dealt card to reveal the answer.

Keep (Operation)
  Move the dealt card to the kept deck

Toss (Operation)
  Move the dealt card to the trash deck

Shuffle (Operation)
  Randomize the kept deck, and place it on top of
  the play deck (which might be empty)

Introduction
------------
The goal of a user (henceforth the "player") is to learn a set of
facts, say a Chinese vocabulary, or maybe the prime factors of the
first 100 integers. This system presents a flash card game to assist
the player in achieving this goal.

Informally, the player does the following::

    start game with a card set
    while there are more unlearned cards:
        see question on the dealt card
        say answer out loud
        flip card
        self-score answer

There are two parts of the design to consider:

* The game state and operations on the state
* The user interface

I start with the first.

State Operations
----------------

The state is a five-tuple (card-set, dealt, play, kept, trash). The
card-set, dealt deck and trash are sets of cards as the sequence of
the cards do not matter.

The play deck is a stack of cards. The order is random, but must be
preserved. Cards are drawn from the top, and shuffled cards are added
to the top in bulk.

The kept deck is a list of cards. Each kept card are appended to the
end of the list. The shuffle operation resets the kept deck to the
empty list.

The dealt deck is a set containing at most one card. The card is
represented by a triple (question, answer, answer-up).

The cards in the other desks are represented by pairs (question,
answer). These two fields identify the card by value.

A system invariant is card set is equal to the union of the four decks
(assuming that answer-up flag in ignored when comparing cards.) Keep
this invariant in mind, and we need not again refer the card-set.

My ad hoc specification language is a hybrid of something like Z/TLA+
and Python. The prime designates the after state of a variable. For
example, x' = x, means that x was not changed. (y == 0, y' == y + 1,
y' == 1) is true. Remember that each line is a predicate and the lines
a joined by conjunction. Python expressions are used only if they have
no side-effects. The assignment statement is forbidden.

Init
----

::

    dealt' == {}
    play' == rand(card-set)
    kept' == []
    trash' == {}

GameOver
--------

::

    dealt == {}
    play == []
    kept == []
    trash == card-set

Deal
----

::

    dealt == {}
    len(play) > 0
    (answer, question) == play[0]
    dealt' == {(answer, question, True)}
    play' == play[1:]
    kept' == kept
    trash' == trash

Flip
----
Only the dealt card changes its state from answer-up == true to
answer-up == false. The identity of the dealt card remains the same. The
number of dealt card remains 1. The other stacks are not changed.

::

    dealt == {(question, answer, True)}
    dealt' == {(question, answer, False)}
    play' == play
    kept' == kept
    trash' == trash

Keep
----

::

    {(question, answer, False)} == dealt
    dealt' == {}
    play' == play
    kept' == kept + [(question, answer)]
    trash' == trash 

Toss
----

::

    {(question, answer, False)} == dealt
    dealt' == {}
    play' == play
    kept' == kept
    trash' == trash `union` {(question, answer)}

Shuffle
-------

::

    dealt == {}
    dealt' == dealt
    play' == rand(kept) ++ play
    kept' == []
    trash' == trash

The function rand() is what performs the actual shuffle. I could
assume that it is a built-in operation that I need not specify. But
there are a couple of problems. The shuffle should not be purely
random. It should place recently seen cards at the end of the shuffled
sequence.

::

    play' == rand(first-half(kept)) ++ rand(second-half(kept)) ++ play

Also, while this is not difficult in Python, doing the same in SQL is
more of a challenge.

History
-------
During any game, we can trace the sequence of successive of games
states. This history is subject to certain ordering constraints. We
must always begin a trace/history with 'init'. I may wish to annotate
each state with the operation that produced it.

::

    -- init --
    ({('2+2','4'), ('2*3','6')},    # card-set
     {},                            # dealt-set
     [('2+2','4'), ('2*3','6')],    # play-list
     [],                            # kept-list
     {})                            # trash-set
    -- deal -- 
    (_,                             # henceforth ignore unchanging card-set
     {('2+2','4', True)},           # dealt-set
     [('2*3','6')],                 # play-list
     [],                            # kept-list
     {})                            # trash-set
    -- flip --
     ({('2+2','4', False)},         # dealt-set
     [('2*3','6')],                 # play-list
     [],                            # kept-list
     {})                            # trash-set
    -- keep --
     ({},                           # dealt-set
     [('2*3','6')],                 # play-list
     [('2+2','4')],                 # kept-list
     {})                            # trash-set
    -- deal -- 
     ({('2*3','6', True)},          # dealt-set
     [],                            # play-list
     [('2+2','4')],                 # kept-list
     {})                            # trash-set
    -- flip --
    -- toss --
    -- shuffle --
    -- deal --
    -- flip --
    -- toss --
    -- deal --
    -- flip --
    -- toss --
     ({},                           # dealt-set
     [],                            # play-list
     [],                            # kept-list
     {('2*3','6'), ('2+2','4')})    # trash-set
    -- game-over --

A simple program can read any such history and tell us if it is
complete (lively) and correct (safety).

In this first version, a shuffle occurs only when play deck is
empty. Later versions may allow the player to request a shuffle.

Interface
---------
The player press a couple of keys (enter,delete). On the screen, he
can view one side the dealt card. The physical interface is very
simple. The main challange to make sure that player can only generate
correct state histories. I use a CSP specification. A game is a
concurrent program.

::

    GAME = KEYBOARD || PLAYER || DEALER || SCREEN

    PLAYER = view-q -> (decide -> A)
      where
        A = enter -> B || delete -> A
        B = view-a -> (enter -> (score-no -> PLAYER) | delete -> (score-yes -> PLAYER))

    KEYBOARD = (enter -> KEYBOARD) | (delete -> KEYBOARD) | (_ -> KEYBOARD)

    DEALER = show-q -> (show-a -> (score-yes -> DEALER | score-no -> DEALER))

    SCREEN = (show-q -> (view-q -> SCREEN)) | (show-a -> (view-a -> SCREEN))

    alphabet(PLAYER) = {view-q decide view-a enter score-yes delete score-no}
    alphabet(KEYBOARD) = {enter delete}
    alphabet(SCREEN) = {show-q view-q show-a view-a}
    alphabet(DEALER) = {show-q show-a score-yes score-no}

The player can view the question, but only if the screen is showing
it. The same for answer.

The player can 'decide' his answer, but that is a private matter that is
not shared. Since it just happens in the player's mind, it does not result
in any system action either.

The player can press a key. Only the enter and delete key events are
shared with the keyboard. So any key other than enter and delete are
accepted by the keyboard, but ignored by the player process. Note that
after 'decide' the delete would deadlock if I did not skip it like I
do in definition A.

Only the player shares the keyboard's alphabet. I can group these
processes, and hide the keyboard alphabet from the rest of the
system::

    PLAYER  
    == 
    view-q -> (decide -> A) 
    A = enter -> B || delete -> A
    B = view-a -> (enter -> (score-no -> PLAYER) | delete -> (score-yes -> PLAYER))
    ==
    view-q -> (decide -> A)
    A = enter -> B || delete -> A
    B = view-a -> (score-no -> PLAYER) | score-yes -> PLAYER)
    ==  // {enter, delete}
    view-q -> (decide -> B)
    B = view-a -> (score-no -> PLAYER) | score-yes -> PLAYER)
    ==
    view-q -> (decide -> (view-a -> (score-no -> PLAYER) | score-yes -> PLAYER)))
    ==
    PLAYER'

I can also hide the private 'decide' event and get

::

    PLAYER' = view-q -> (view-a -> (score-no -> PLAYER') | score-yes -> PLAYER'))
    
    GAME = (KEYBOARD || PLAYER) // {enter delete decide} || DEALER || SCREEN

[I want a simple tool to check for deadlocks.]

Start-Up
--------
The description of SCREEN is abstract. I have said nothing about the
actual I/O needed to display data. This was deliberate (despite the
project name) as I want the high-level specification to describe a
whole family of possible implementations (html, curses, Tk). But by
not committing to a particular technology, it is hard to say what
operations are needed and how to represent them by abstractions. I am
going to assume that screen devices need some opening ceremony and
closing ceremony. I know curses does. If some technology does not
require initialization, the open may be seen as a no-op.

::

    SCREEN = open-screen -> (start -> SCREEN-LOOP)
    SCREEN-LOOP = (show-q -> (view-q -> SCREEN-LOOP)) | (show-a -> (view-a -> SCREEN-LOOP))

The open-screen event is private to screen. It must be completed
before the screen service loop is running. The 'start' event provides
synchronization for the other processes.

To start a game, the player needs to provide a card set (name). The
dealer needs to shuffle those cards and designate them as the play
deck. After these start-up operations are complete, the game may
proceed as already specified. (PLAYER' is the hidden-keyboard view of
PLAYER).

::

    PLAYER0 = name-cardset!name -> PLAYER'
    PLAYER' = view-q -> (view-a -> (score-no -> PLAYER') | score-yes -> PLAYER'))

    DEALER0 = name-cardset?name -> (start -> DEALER)
    DEALER = show-q -> (show-a -> (score-yes -> DEALER | score-no -> DEALER))

The player does not need a 'start' event as synchronization is already
implied by 'name-cardset'.

Termination
-----------
Once all of the card set is in the trash deck, there is nothing more
to do. We need to clean-up and quit.

How to specify the 'learned' condition?  One option is to add state
and conditional logic to the process definitions. I do that
below. Another option is just to assert the the learned event can
arise somehow, and then deal with it.

::

    DEALER = (show-q -> (show-a -> (score-yes -> DEALER | score-no -> DEALER))) | (learned -> SKIP)
    SCREEN-LOOP = (show-q -> (view-q -> SCREEN-LOOP)) | (show-a -> (view-a -> SCREEN-LOOP) | (learned -> SKIP)
    PLAYER' = (view-q -> (view-a -> (score-no -> PLAYER') | score-yes -> PLAYER'))) | (learned -> SKIP)

SKIP is CSP's way of expression graceful termination. Without it our
finished processes would just hang forever waiting for more events
that will never come.

Attaching Operations
--------------------
[TBD]
