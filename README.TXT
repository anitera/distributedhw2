+++++++++++++++++++++++++++++++++
++++WELCOME TO SUDOKU PROJECT++++
+++++FOR DISTRIBUTED SUSTEMS+++++
+++++MADE BY TEAM TEXT LORDS+++++
+++++++++++++++++++++++++++++++++

Authors: Margarita Dekret, Viacheslav Komisarenko, 
	 Olga Kaminska, Viktor Mysko



Structure of ptoject:

file name | class name	| functions of class 	| functions in file

client.py | GamePlaying() | __init__ 		| stop_execution
			  | update_state     	| sigint_handler
			  | update_scores    	|		
			  | update_game		|
			  | get_status	        |
			  | run 		|
			  | close		|
			  | playing_game	|
			  | listening_server	|
server.py | Server()	| listen
			| start
			| session_updater
Board_gui.py | Board()	| __init__		| return_board
			| initialize_board
			| show_board
			| set_board_number
			| set_board_numbers
			| EnterVal
			| Click
			| draw_board_numbers
			| draw_table_score
			| set_table
			| end_game
client.ini |
client_handler.py | ClientHandler() | __init__
				    | set_sessions
				    | run
				    | __handle
dependencies.txt |
Generation.py | Scale()	| __init__		| return_answer
			| show			| return_question_and_answer
			| transp
			| rows_change
			| columns_change
			| square_change_horizontal
			| square_change_vertical
			| combination
host_port_authorization.py | HostPort() | __init__	| hostPortAuthorization
					| setHostPort	| sendPortHost
					| getHostPort
login.py | Nickname()	| __init__		| send_data
			| setNickname		| authorization
			| getNickname		| validate_nickname
						| show_nicknames
						| load_nicknames
						| enter_nickname
protocol.py |
README.md |
README.txt |
sessions.ini |
sessions.py | Player()	| __init__		| get_name
			| get_name		| add_player
			| get_socket		| remove_player
			| send			| new_session
	    | GameHandler() | __init__		| get_session
			    | add_player	| save_sessions
			    | remove_player	| current_sessions
			    | get_token		| load_sessions
			    | get_name	
			    | get_status
			    | play_turn
			    | sent_to_players
			    | update_clients_boards
			    | update_clients_scores
			    | update_game
			    | run
			    | game_observer
	    | GameSession() | __init__
			    | get_token	
			    | get_size
			    | get_state
			    | get_total
			    | set_name
			    | get_name
sessions_authorization.py |  | 			| send_data_sessions
						| validate_session_name_and_size
						| sessionStart
sudoku_solver.py | 	|			| solve_sudoku
						| exact_cover
						| solve
						| select
						| deselect
								

