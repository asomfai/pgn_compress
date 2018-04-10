from decimal import *
import math
import string
import colorama
import sys

colorama.init()

# rows and columns are indexed by numbers [0:7]

#DONE: fill default board
#DONE: read a play from a file
#DONE: castling
#DONE: fix castling
#DONE: play back and check every steps validity
#DONE: generate numeric code
#DONE: read PGN file with more games
#DONE: decoding
#DONE: create castling move class
#DONE: create e.p. move class
#todo: support Pawn promotion (pawn move followed by =<piece type>)
#todo: make table a class
#todo: en passant
#todo: batch files: more binaries in bin, more tables in in one log file

############################# Chess Table Representation #############################
class Piece (object):
# pieces: color:w/b Type:King,Queen,Rooks,Bishops,kNights,Pawns
	def __init__(self, Color, Type, Moved=False):
		self.Color = Color
		self.Type = Type
		self.Moved = Moved
		
		if Color not in ["w","b"]:
			raise Exception("Bad color",Color)

		if Type not in ["Q","K","B","R","N","P"]:
			raise Exception("Bad Type",Type)

		if Moved not in [True,False]:
			raise Exception("Bad Moved",Moved)
						
	def isWhite(self):return self.Color=="w";
	def isBlack(self):return self.Color=="b";

	def isMoved(self):return self.Moved;

	def isQueen(self):return self.Type == "Q";
	def isKing(self):return self.Type == "K";
	def isRook(self):return self.Type == "R";
	def isBishop(self):return self.Type == "B";
	def isKnight(self):return self.Type == "N";
	def isPawn(self):return self.Type == "P";
	
	def toString(self):return self.Color+self.Type;
	
		

############################# define move #############################
class Move (object):
	def __init__(self, piece, to_x,to_y,capture=False):
		self.piece = piece
		self.to_x = to_x
		self.to_y = to_y
		self.capture = capture
		self.from_x=None
		self.from_y=None
				
		if self.to_x not in range(0,8):raise Exception("Bad move to",self.to_x,self.to_y,capture)
		if self.to_y not in range(0,8):raise Exception("Bad move to",self.to_x,self.to_y,capture)
		if self.capture not in [True,False] :raise Exception("Bad move to",to_x,to_y,capture)
		
	def toString(self):
		string = self.piece.toString()
		if self.from_x != None: string += 'abcdefgh'[self.from_x]
		if self.from_y != None: string += str(self.from_y+1)
		string += 'abcdefgh'[self.to_x] 
		string += str(self.to_y+1)
		if self.capture:
			string += "X"

		return string
		
	def Match(self, other):
		if type(other) is Castling: return False
		if type(other) is EnPassant:
			return self.piece.isPawn() and other.piece.isPawn() and self.to_x == other.to_x and self.to_y == other.to_y
		if self.to_x != other.to_x or self.to_y != other.to_y : return False
		return self.piece.Type == other.piece.Type


class Castling (object):
	def __init__(self, piece, to_x,to_y):
		self.piece = piece
		self.to_x = to_x
		self.to_y = to_y
		self.from_x=None
		self.from_y=None

	def toString(self):
		string = self.piece.toString()
		if self.to_x==2: string += " O-O-O to "+str(self.to_x)
		else: string += " O-O to "+str(self.to_x)
		return string

	def Match(self, other):
		if not type(other) is Castling: return False
		if self.to_x != other.to_x: return False
		return True

class EnPassant (Move):
	def __init__(self, piece, to_x,to_y,capture_x,capture_y):
		super(EnPassant,self).__init__(piece, to_x,to_y,True)
		self.ep_x=capture_x
		self.ep_y=capture_y

	def toString(self):
		return super(EnPassant,self).toString()+"e.p."
		
############################# directional moves: King,Queen,Bishop,Rook #############################

# direction table:
direction=[[-1,-1],[-1, 0],[-1, 1],[ 0, 1],[ 1, 1],[ 1, 0],[ 1,-1],[ 0,-1]]


# return: [] if not valid, [to_x,to_y] if valid, [to_x,to_y,"!<captured_piece>"] if opposite players piece is captured
def ValidMove(to_x,to_y,piece):
	#print "piece",piece.toString()," move to ",to_x,to_y,
#	print LastMove
#	if LastMove!=None and LastMove.piece.isPawn() and piece.isPawn():
#		print LastMove.from_x,LastMove.from_y,LastMove.to_x, LastMove.to_y ,to_x, to_y

	if not to_x in range(0,8) or not to_y in range(0,8):
		#print "out"
		return None
	if table[to_x][to_y]==None:
		#print "valid, free"
		#check en passant
		if LastMove!=None and LastMove.piece.isPawn() and piece.isPawn():
			if LastMove.from_y-LastMove.to_y in [-2,2] and LastMove.from_x == LastMove.to_x and (LastMove.from_y+LastMove.to_y)/2 == to_y:
				return EnPassant(piece,to_x,to_y,LastMove.to_x,LastMove.to_y)
		return Move(piece,to_x,to_y)
	elif table[to_x][to_y].Color!=piece.Color:
		#print "valid, capture"
		return Move(piece,to_x,to_y,True)

	#print "occupied"
	return None
	

def DirectionalMove(x,y,start,step,max_range,piece):
	steps=[] # possible steps
	if table[x][y] != piece:
		print 'figure @',x,' ',y,'=',table[x][y].toString(),'is not a '+piece.toString()+'!'
		return steps
	else:
		for dir in range(start,8,step):
			dx=direction[dir][0]
			dy=direction[dir][1]
			for distance in range(1,max_range+1):
				next_x=x+dx*distance
				next_y=y+dy*distance
				valid_step=ValidMove(next_x,next_y,piece);
				if valid_step!=None:steps.append(valid_step)
				if valid_step==None or valid_step.capture:
					break;
	return steps

def QueenMoves(x,y,piece):
	return DirectionalMove(x,y,0,1,7,piece)

def RookMoves(x,y,piece):
	return DirectionalMove(x,y,1,2,7,piece)

def BishopMoves(x,y,piece):
	return DirectionalMove(x,y,0,2,7,piece)

############################# special moves #############################

def KingMoves(x,y,piece):
	steps = []
	if not piece.Moved:
		if not(y == 0 and piece.isWhite() or y==7 and piece.isBlack()):raise Exception("King.Moved does not match its rank!")
		if not(x == 4):raise Exception("King.Moved does not match its file!")
		for rook_file,castling_direction in [(0,-1),(7,+1)]:
			#rook at start position, not moved
			if table[rook_file][y]!=None and table[rook_file][y].Moved==False and table[rook_file][y].isRook():
				#no pieces between them
				castling_possible=True
				for x_r in range(x+castling_direction,rook_file,castling_direction):
					if table[x_r][y]!=None:
						castling_possible=False
						break
				if castling_possible:
					steps.append(Castling(piece,x+2*castling_direction,y))
					
	return steps+DirectionalMove(x,y,0,1,1,piece)

KnightMoveDeltas=[[-1,-2],[-1, 2],[ 1,-2],[ 1, 2],[-2,-1],[-2, 1],[ 2,-1],[ 2, 1]]
def KnightMoves(x,y,piece):
	steps=[]
	if table[x][y] != piece:
		print 'figure @',x,' ',y,'=',table[x][y].toString(),'is not a '+piece.toString()+'!'
		return steps
	for knigt_move in KnightMoveDeltas:
		valid_move=ValidMove(x+knigt_move[0],y+knigt_move[1],piece)
		if valid_move!=None:
			steps.append(valid_move)
	return steps
	
def PawnMoves(x,y,piece):
	#print "check pawn moves @",x,y
	steps=[]
	if table[x][y] != piece:
		print 'figure @',x,' ',y,'=',table[x][y].toString(),'is not a '+piece.toString()+'!'
		return steps
		
	direction = 1 if piece.isWhite() else -1
	#print direction
	# forward
	valid_move=ValidMove(x,y+direction,piece)
	if valid_move != None and valid_move.capture==False:
		steps.append(valid_move)
		#print steps
		#when not moved yet, pawn may step make 2 steps forward
		if valid_move!= None and valid_move.capture==False and not piece.Moved:
			valid_move=ValidMove(x,y+direction+direction,piece)
			if valid_move != None:steps.append(valid_move)
	#capture left or right
	valid_move=ValidMove(x-1,y+direction,piece)
	if valid_move != None and valid_move.capture:steps.append(valid_move)
	valid_move=ValidMove(x+1,y+direction,piece)
	if valid_move != None and valid_move.capture:steps.append(valid_move)

	if False:
		for move in steps:print move.toString(),
	return steps

def GeneralMove(x,y):
	steps=[]
	piece=table[x][y]
	if piece==None:return []
#	print x,y,piece.toString()
	if piece.isKing():return KingMoves(x,y,piece)
	if piece.isQueen():return QueenMoves(x,y,piece)
	if piece.isBishop():return BishopMoves(x,y,piece)
	if piece.isRook():return RookMoves(x,y,piece)
	if piece.isKnight():return KnightMoves(x,y,piece)
	if piece.isPawn():return PawnMoves(x,y,piece)
			
	raise Exception("Something really bad happened @"+x+y)
	return []
	
#do a move
def DoMove(x_from,y_from,input_move):

	# last move - used for e.p.
	global LastMove
	
	#print "Make Move:",move.toString()
	x_to=input_move.to_x
	y_to=input_move.to_y
	#check
	piece=table[x_from][y_from]
	if piece==None:
		raise Exception('Move from empty field',x_from,y_from)
	
	moves=GeneralMove(x_from,y_from)
 #	print len(moves),"moves"
	for move in moves:
		#print move.toString()
		if move.to_x==x_to and move.to_y==y_to:
			#castling
			if type(move) is Castling:
				if y_to not in [0,7]:raise Exception("Castling move error - bad rank")
				if x_to not in [2,6]:raise Exception("Castling move error - bad file")
				if table[x_to][y_to]!=None:raise Exception("Castling move error - occupied")
				if x_to==2:
					if table[0][y_to]==None or not table[0][y_to].isRook():raise Exception("Castling rook missing")
					table[3][y_to],table[0][y_to]=table[0][y_to],table[3][y_to] # move rook
					table[4][y_to],table[2][y_to]=table[2][y_to],table[4][y_to] # move king
					table[2][y_to].Moved=table[3][y_to].Moved=True
				elif x_to==6:
					if table[7][y_to]==None or not table[7][y_to].isRook():raise Exception("Castling rook missing")
					table[7][y_to],table[5][y_to]=table[5][y_to],table[7][y_to] # move rook
					table[6][y_to],table[4][y_to]=table[4][y_to],table[6][y_to] # move king
					table[5][y_to].Moved=table[6][y_to].Moved=True
				else:
					raise Exception('Not a valid castling move.')
			elif type(move) is EnPassant:
				assert(table[x_to][y_to]==None)
				table[x_to][y_to],table[x_from][y_from]=table[x_from][y_from],table[x_to][y_to]
				table[x_to][y_to].Moved=True
				#capture en passant pawn
				assert LastMove.piece.isPawn()
				table[LastMove.to_x][LastMove.to_y]=None
			else:
				#print x_to,y_to,table[x_to][y_to]
				#normal move
				#empty field?
				if table[x_to][y_to]==None:
					table[x_to][y_to],table[x_from][y_from]=table[x_from][y_from],table[x_to][y_to]
					table[x_to][y_to].Moved=True
				#capture other players piece?
				elif table[x_to][y_to].Color!=table[x_from][y_from].Color:
					table[x_to][y_to]=table[x_from][y_from]
					table[x_from][y_from]=None
					table[x_to][y_to].Moved=True
				else:
					raise Exception('Field occupied by friendly piece',table[x_to][y_to])
				
	LastMove = input_move; LastMove.from_x=x_from; LastMove.from_y=y_from
#	print "New Last Move=",LastMove.toString()

#	except Exception as inst:
#		print inst
#		raise inst
#		pass

	
# setup initial table
table = []
LastMove = None
def SetupTable():

	global table
	
	empty_square=None
	line=[empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square]
	table=[line[:],line[:],line[:],line[:],line[:],line[:],line[:],line[:]]

	table[0][0]=Piece('w','R');table[7][0]=Piece('w','R')
	table[1][0]=Piece('w','N');table[6][0]=Piece('w','N')
	table[2][0]=Piece('w','B');table[5][0]=Piece('w','B')
	table[3][0]=Piece('w','Q')
	table[4][0]=Piece('w','K')
	for i in range(0,8):table[i][1]=Piece('w','P');table[i][6]=Piece('b','P');table[i][7]=None if table[i][0]==None else Piece('b',table[i][0].Type)

def PrintTable():
	return
	print " abcdefgh"
	for y in range(7,-1,-1):
		line_string=str(y+1)
		for x in range(0,8):
			line_string += colorama.Back.YELLOW if (x+y) % 2 == 1 else colorama.Back.BLUE
			field=table[x][y]
			if field == None:
				line_string += " "
			else:
				if field.Color=="w":
					line_string += colorama.Fore.WHITE 
				else: 
					line_string += colorama.Fore.BLACK
				line_string += field.Type
				
		print line_string+colorama.Style.RESET_ALL

def LogTable(step):
	string=str(step)+".\n"
	string+=" abcdefgh\n"
	for y in range(7,-1,-1):
		string+=str(y+1)
		for x in range(0,8):
			field=table[x][y]
			if field == None:
				string += " "
			else:
				string += field.Type if field.Color =="w" else field.Type.lower()
		string+="\n"
		
	string+="\n"
	return string			
	
############################# read PGN file #############################

class TokenFile:
	
	class EndOfFile:
		def __init__(self):
			pass

	def __init__(self,filename):
		print "opening ",filename,
		my_file=open(filename)
		self.string = my_file.read()
		self.pos=0
		self.len=len(self.string)
		my_file.close()
		print self.len,"chars"
		
	def isWhiteSpaceChar(self,char):
		return char in " \t\n"
				
	def skip_whitespaces(self):
		while True:
			c = self.getChar()
			if not self.isWhiteSpaceChar(c):
				return c
			self.nextChar()
				
	def getChar(self):
		if self.pos>=self.len:
			print "TokenFile.EndOfFile"
			raise TokenFile.EndOfFile()
		return self.string[self.pos]

	def readLine(self):
		try:
			lineend_pos= self.string.index("\n",self.pos)
		except ValueError:
			lineend_pos = self.len
		prev_pos,self.pos = self.pos, lineend_pos+1
		return self.string[prev_pos:lineend_pos]
		
	def isWhitespace(self):
		return False if self.pos>=self.len else self.isWhiteSpaceChar(self.string[self.pos])
		
	def nextChar(self,step=1):
		#print(self.string[self.pos:self.pos+step])
		self.pos = self.pos+step
		
	def readChars(self,size=1):
		string=self.string[self.pos:self.pos+size]
		self.pos = self.pos+step
	
	def readNumber(self):
		self.skip_whitespaces()
		string_number=""
		while self.pos<self.len:
			c=self.getChar()
			if c in "0123456789":
				string_number+=c
				self.nextChar()
			else:
				return int(string_number)
		
	def readToken(self):
		string=""
		while not self.isWhitespace() and self.pos<self.len:
			string += self.getChar()
			self.nextChar()
		#print string
		return string

	def expectString(self,string):
		if self.string[self.pos:self.pos+len(string)]!=string:
			raise Exception("file syntax error")
		self.nextChar(len(string))

	def acceptString(self,string):
		if self.string[self.pos:self.pos+len(string)]==string:
			self.nextChar(len(string))
			return True
		return False

	def isString(self,string,case_sensitive=True):
		return self.string[self.pos:self.pos+len(string)]==string if case_sensitive else self.string[self.pos:self.pos+len(string)].lower()==string.lower()
		
		
class Step:
	def __init__(self,type,to_x,to_y,from_x=None,from_y=None,capture=None):
		pass

#color: "w"/"b"
def readStep(input_file,color):
	#read step notation
	type='P'
	input_file.skip_whitespaces()
	#read notation string - until next whitespace
	capture = False
	dis_file=None
	dis_rank=None
	trg_file=None
	trg_rank=None
	king_castling=False;
	queen_castling=False;
	token = input_file.readToken()
	#capture - not interesting
	if 'x' in token or ":" in token :
		capture = True
		token=token.replace("x","")
		token=token.replace(":","")
	#check or checkmate - not interesting
	if '+' in token or "#" in token:
		token=token.replace("+","")
		token=token.replace("#","")
	if token == "O-O":
		king_castling=True;
		type='K'
	elif token == "O-O-O":
		queen_castling=True;
		type='K'
	else:
		#normal move
		if token[-4:]=="e.p.":
			#en passage - not supported yet
			raise Exception("en passage - not supported yet")
		#last 2 chars: target file, rank 
		trg_file=token[-2]
		trg_rank=token[-1]
		token=token[:-2] #cut target field
		
		#first char: type (or omitted if pawn)
		if len(token)>0:
			c1=token[0]
			if c1 in "QKNBR":
				#other move
				type=c1
				token = token[1:] #cut piece identification

		#remaining chars: disambiguation
		if len(token)==1:
			if token[0] in string.digits:
				dis_rank=token[0]
			elif token[0] in string.ascii_lowercase:
				dis_file=token[0]
		elif len(token)==2:
			dis_file=token[0]
			dis_rank=token[1]
		elif len(token)!=0:
			raise Exception("token error")
	
	if queen_castling:
		trg_file = "c"
		trg_rank == 0 if color == "w" else 7
	elif king_castling:
		trg_file = "g"
		trg_rank == 0 if color =="w" else 7

#	print type,trg_file,trg_rank,dis_file,dis_rank,capture
	# transform a..h,1..8 to 0..7,0..7
	files = ["a","b","c","d","e","f","g","h"]

	if trg_file != None:trg_file=files.index(trg_file)
	if trg_rank != None:trg_rank = int(trg_rank)-1
	if dis_file!=None:dis_file=files.index(dis_file)
	if dis_rank!=None:dis_rank = int(dis_rank)-1
	if capture == None:capture = False

	if queen_castling or king_castling:
		move = Castling(Piece(color,type), trg_file, trg_rank)
	else:
		move = Move(Piece(color,type), trg_file, trg_rank, capture)
	move.from_x = dis_file
	move.from_y = dis_rank
	
	return move
	
class PGNFile:

	class End:
		def __init__(self):
			pass
			
	def __init__(self, filename):
		self.input_file = TokenFile(filename)
	
	def TestEnd(self):
		self.input_file.skip_whitespaces()
		if self.input_file.acceptString("1-0"):
			return "w"
		if self.input_file.acceptString("0-1"):
			return "b"
		if self.input_file.acceptString("1/2-1/2"):
			return "d"
		return None
	
	
	def ReadGame(self):
		try:
			step_ex=0
			moves = []
			self.input_file.skip_whitespaces()
			#skip tags
			while self.input_file.getChar()=="[":
				print self.input_file.readLine()
				self.input_file.skip_whitespaces()
			while True:
				#read step
				if self.TestEnd()!=None:break
				step=self.input_file.readNumber()
				if step==None:
					break
				step_ex = step_ex+1
				if step!=step_ex:
					raise Exception("file step mismatch @ step"+step_ex+1)
				#read . (dot)
				self.input_file.expectString(".")
				#print str(step_ex),":",
				moves.append(readStep(self.input_file,"w"))
				#print moves[-1].toString(),
				if self.TestEnd()!=None:break
				moves.append(readStep(self.input_file,"b"))
				#print moves[-1].toString(),
			
		except TokenFile.EndOfFile:
			print "PGNFile.End"
			raise PGNFile.End()
			pass

		print "read",step_ex,"steps"
			
		return moves
		
		
		
		
		#test: collect all valid moves
		
def MakeCode(game_steps):
	#generate code
	sum_bits=0
	n=Decimal(0)
	for (range,index) in reversed(game_steps):
		assert range>index
		n=n*range
		n=n+index
		sum_bits = sum_bits + math.log(range,2)
	#print as binary
	print "code=",n
	bits=""

	ctx = getcontext()
	assert ctx.prec > len(n.as_tuple().digits) + 2

	while n>0:
		if n % Decimal(2)==1:
			bits="1"+bits
			n = n - 1
		else:
			bits="0"+bits
		n = n / 2

	print "bits=",len(bits),"theoretical=",sum_bits,"avg bit/move",float(len(bits))/len(game_steps)

	return bits

def ProcessPGN(file_name):
	pgn_file = PGNFile(file_name)
	game = 1
	while True:
		game_desc=[] # list of tuples(number of possible steps, players step index in possible step list)
		log_string=""

		try:
			moves = pgn_file.ReadGame()
		except PGNFile.End:
			break

		print "GAME ",game,
		SetupTable()
		
		PrintTable()
		log_string+=LogTable(0)
		#for each move: look for possible moves, make the move
		side = True #True:white False:black
		continous = True
		verbose = False
		step=0
		for move in moves:
			step = step + 1
			color = "w" if side else "b"
			piece = move.piece
			possible_moves = []
			#find pieces on table
			for y in range(0,8):
				for x in range(0,8):
					if table[x][y]!=None and table[x][y].Color == color:
						for pmove in GeneralMove(x,y):
							possible_moves.append([x,y,pmove])
						
			
			if verbose:print "step",step,"players move: ",move.toString(),"possible moves",len(possible_moves)

			matching_moves=[]
			move_index=matching_move_index=0
			for [x,y,pmove] in possible_moves:
				if move.Match(pmove) and (move.from_x==None or move.from_x==x) and (move.from_y==None or move.from_y==y):
					if verbose:print "found move",pmove.piece.toString()+'abcdefgh'[x]+str(y+1),pmove.toString()
					matching_moves.append([x,y,pmove])
					matching_move_index = move_index
				move_index = move_index + 1
					
			if len(matching_moves) != 1:
				PrintTable()
				print "Possible moves:"
				for [x,y,pmove] in possible_moves:print pmove.toString(),
				print
				print "Matching moves:"
				for [x,y,pmove] in matching_moves:print pmove.toString(),
				print
				
				logfile=open(file_name+"."+str(game)+".tbl","w")
				logfile.write(log_string)
				logfile.close()

				raise Exception("Bad move in step",step/2,move.toString())
			else:
				DoMove(matching_moves[0][0],matching_moves[0][1],matching_moves[0][2])
				
			if False and verbose:
				PrintTable()
				
			game_desc.append((len(possible_moves),matching_move_index))
					
			log_string+=LogTable(step)
			
			try:
				if not continous:
					cont = raw_input("Continue? ")
					if cont=="n":break
					if cont== "a":
						continous = True
			except:
				pass
			side = not side
		
		#all moves processed
		if verbose:
			PrintTable()
		
		logfile=open(file_name+"."+str(game)+".tbl","w")
		logfile.write(log_string)
		logfile.close()

		print game_desc
		binary = MakeCode(game_desc)

		bin_file=open(file_name+"."+str(game)+".bin","w")
		bin_file.write(binary)
		bin_file.close()
		print binary
		game = game + 1

	#all games processed

def ProcessBIN(file_name):
	binary_str=TokenFile(file_name).readLine()
	pos_value = Decimal(1)
	value = Decimal(0)
	for pos in range(len(binary_str)-1,-1,-1):
		value += pos_value if binary_str[pos]=="1" else Decimal(0)
		pos_value *= Decimal(2)
	
	SetupTable();
	game_desc = []
	
	print "code=",value
	log_string=""
	step = 0
	log_string+=LogTable(step);
	
	color ="b"
	while value != 0:
		color = "w" if color =="b" else "b"
		possible_moves = []
		#find pieces on table
		for y in range(0,8):
			for x in range(0,8):
				if table[x][y]!=None and table[x][y].Color == color:
					for pmove in GeneralMove(x,y):
						possible_moves.append([x,y,pmove])

		step_range = len(possible_moves)
		index = value % step_range
		game_desc.append((int(step_range),int(index)))
		value -= index
		value = value / step_range
		
		int_index = int(index)
		assert Decimal(int_index) == index
		DoMove(possible_moves[int_index][0],possible_moves[int_index][1],possible_moves[int_index][2])
		step += 1
		log_string+=LogTable(step);
	print game_desc

	game = 1
	logfile=open(file_name+"."+str(game)+".tbl","w")
	logfile.write(log_string)
	logfile.close()
	
	
if False:
	test_moves=[]
	test_moves+=GeneralMove(4,0)
	test_moves+=GeneralMove(4,7)
				
	for move in test_moves:print move.toString(),
	print
	
	DoMove(4,0,test_moves[1])
	PrintTable()

setcontext(Context(prec=300))

filename = sys.argv[1].strip().replace("\\","/")
if filename[-4:]==".pgn":
	ProcessPGN(filename)
elif sys.argv[1][-4:]==".bin":
	ProcessBIN(filename)

