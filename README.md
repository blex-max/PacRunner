# PacRunner

A simple curses program implemented via python curses reimagining our favourite munching semicircle into a sidescrolling runner game. YomYom!

## Dependencies

- Python (written and tested with 3.13, but I don't knowingly use any features introduced after 3.10)
- Poetry (tested with >= 1.8.4)

The project relies on only two further libraries, installation of which will be handled automatically.

## Installation

First download the latest release and unzip. I recommend installing into a virtual environment, or perhaps with pipx if you want global availablilty. Regardless, from within the unzipped release directory, installation is as simple as:
```
poetry install
```
to run, simply call:
```
pacrunner
```

## Audio

In game sounds were downloaded from [classicgaming.cc](https://classicgaming.cc/classics/pac-man/sounds). The music is a short extract from Power-Pill - Pac-Man, a bootleg remix of the pacman theme. These usages are not endorsed.

## TODO

In general, 'clean up and refactor the codebase'. This project was written very quickly and with 'just make it work' as the sole guiding philosophy. The idea took form as I wrote. As such, forward-planning the structure would have been fruitless! You might call this a prototype, which I will now iterate on at least once, to formalise the internal design.

The program is largely feature complete for v1.0, excepting for:
- argpase CLI for passing some basic runtime options (mute, quickstart, perhaps more)
- possible changes to the difficulty curve in response to playtesting
- inevitable bugfixing, as I have had very few people QA this project
- possibly some user config options, like turning off the title animation and so on

Once I'm happy with those we'll have a v1.0 release

I'd be happy to add further features if players desired them - please make requests on this github and if there's any interest I'll collate them into a v2 release

## Licence 

TBD
 
