# VTES data for TCG Arena

This repository contains data to play 'Vampire: The Eternal Struggle' (VTES) on TCG Arena.

[Add Game](https://tcg-arena.fr/load/aHR0cHMlM0ElMkYlMkZyYXlrd2FzaGluZ3Rvbi5naXRodWIuaW8lMkZUQ0ctQXJlbmEtVlRFUyUyRkdhbWVfVmFtcGlyZV8lMjBUaGUlMjBFdGVybmFsJTIwU3RydWdnbGUuanNvbg==) on TCG Arena.

## Description


The project:

* Fetches up-to-date card data using the KRCG API
* Applies relevant tags for VTES game modes (Standard & V5)
* Converts card data to format suitable for TCG Arena


## Getting Started

This guide contains steps you need to get the data generator working locally on your system. If you are wanting to avoid fetching all card data, you can use the KRCG [Static files](https://static.krcg.org/) instead. 

### Dependencies

* Python v3.14 or later

### Installing

1. Create a Virtual environment

~~~
python -m venv venv
~~~

2. Activate the virtual environment

~~~
# Windows:
.venv\Scripts\activate
# Linux:
source venv/bin/activate
~~~

3. Install vtes4tcgarena from project root

~~~
python -m pip install -e .
~~~

### Executing program

~~~
vtes4tcgarena
~~~

## Contributors

* Rayk (Original creator)

* Ollie (Maintainer)
