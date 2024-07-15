# connect4
A simple AI Agent setup to play connect4 against a human through command line interface

## Importing the package and Evnironment Setup
virtualenv -p python3.9 <env_name>\
pip install git+ssh://git@github.com/Saahil-Agr/connect4.git#egg=connect4\
pip install -r requirements.txt

# Interactive Game Play Usage
python run.py --help\
python run.py -a GreedyAgent -r 6 -c 7 -v
  - Specifies the number of rows and cols as well as if you want the game to be verbose.