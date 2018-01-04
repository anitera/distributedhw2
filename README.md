# distributedhw2
RPC peer-to-peer Sudoku

Sudoku can work in LAN, if your network starts with 172. (for eduroam and campuswifi) I found that the python UDP-brodcast meets problems for this host, but from any other network it works fine (I checked for Super mobile network and Elisa).

To run application type: 
	python sudoku.py

Than you need to enter your nickname or choose existing. After that you will see the session window, one client can create a game, than another client will see it in that window. It appears authomatically without need to reopen any window.
After all players connect you will see the game window, after pressing the '?' type the number (1-9). After some player win the game "Winner is rita"(name of the winner) or "Game has been dropped by host" (if the host close the game).
