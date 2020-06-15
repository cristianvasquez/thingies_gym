# Thingy's grid-world

This grid world is full of thingies that love apples.

## Base rules

* Thingies can move in the grid in four directions.
* Thingies spend apples to move around.
* From time to time, trees with apples appear in the grid
* Thingies can collect apples from the trees
* A thingy that doesn't have any apple left dies
* Thingies can perform actions per turn simultaneously. Each turn the order of execution is selected randomly

## Winter is coming ruleset

* From time to time, the season switches between summer and winter. 
* When is summer, more apples appear in the trees, and fewer apples are needed to survive.
When it is winter, fewer apples appear in the trees, and more apples are needed to survive.

## Houses ruleset

* There are houses in the grid. They start as 'Wild' houses
* When a thingy stays in a house, it eats fewer apples.
* A house can hold a maximum number of thingies.

## Rent and buy ruleset

* A thingy can buy a 'Wild' house, paying a one-time fee in apples. The house becomes 'Owned'
* If a thingy stays in an 'Owned' house, pays apples to the owner.

## Fractional ownership ruleset

* A thingy can occupy a 'Wild' house gaining 'ownership' proportional to the stay. The house becomes 'Fractional'
* All thingies, owners or not, pay rent in 'Fractional' houses. Apples go proportionally to the previous owners.

# Life if not eternal ruleset

* Thingies are mortal. There is a probability of death, proportional to their age.

## Offsprings ruleset

* Thingys can have little thingies

- Variants:
* 'Owned' houses can be inherited or not
* 'Fractional' houses can be inherited or not

## Other ideas

* Thingies can plant trees, paying in apples
* Thingies can buy trees, paying in apples
* Thingies can build barricades, paying in apples
* Thingies can give away apples to other thingies

# Rewards

A combination of:

- points each turn the thingy is alive. (survival)
- points each turn their offsprings are still alive 
- points proportional to gathered apples. 

## Installation

The games use  [ursina engine](https://www.ursinaengine.org/) for rendering. 

to install:
```sh
pip install git+https://github.com/pokepetter/ursina.git
```

To see the graphical version, install
