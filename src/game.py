
class Piece:
    LEGAL_PIECES = [
        'Pawn',
        'Knight',
        'Rook',
        'Bishop',
        'Queen',
        'King']

    def __init__(self, name, x_pos, y_pos):
        if name not in LEGAL_PIECES:
            raise Exception("Piece does not have a legal name")
        if x_pos < 0 or y_pos < 0:
            raise Exception("Position must be a non-negative number")
        self.name = name
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.moved = 0
        self.passant_victim = None

    def __eq__(self, other):
        return self.name == other.name and \
                self.x_pos == other.xpos and \
                self.y_pos == other.ypos

    def __ne__(self, other):
        return not self.__eq__(other)

class Board:
    def __init__(self, x_size = 8, y_size = 8):
        self.x_size = x_size
        self.y_size = y_size

class Move:
    def __init__(self, piece, x_dest, y_dest, castle_rook=None,\
            take=False, check_passant=False, is_passant=False):
        self.piece = piece
        self.x_dest = x_dest
        self.y_dest = y_dest
        self.castle_rook = castle_rook
        self.take = take
        self.check_passant = check_passant
        self.is_passant=is_passant

class Game:
    white = 0
    black = 1
    '''
    p1_init: Array of pieces for white
    p2_init: Array of pieces for black
    board: Board object
    '''
    def __init__(self, board, p1_init, p2_init, turn=white):
        self.board = board
        self.w_pos = []
        self.b_pos = []
        w_king_count = 0
        b_king_count = 0

        for p in p1_init:
            if p.name == 'King':
                w_king_count += 1
            if not self.__is_open(p.x_pos, p.y_pos, can_take=False):
                raise Exception("Illegal initial position")
            self.w_pos.append(p)
        if not w_king_count == 1:
            raise Exception("Both players must have a king")

        for p in p2_init:
            if p.name == 'King':
                b_king_count += 1
            if self.__is_open(p.x_pos, p.y_pos, can_take=False):
                raise Exception("Illegal initial position")
            self.b_pos.append(p)
        if not b_king_count == 1:
            raise Exception("Both players must have a king")

        self.turn = turn

    '''
    Return all possible moves for the current player as a list of move objects 
    '''
    def get_legal_moves(self):
        cur_pieces = self.w_pos if self.turn == white else self.b_pos
        moves = []

        for p in cur_pieces:
            if p.name == 'Pawn':
                moves.extend(self.__pawn_moves(p))
            elif p.name == 'Bishop':
                moves.extend(self.__bishop_moves(p))
            elif p.name == 'Rook':
                moves.extend(self.__rook_moves(p))
            elif p.name == 'Queen':
                moves.extend(self.__bishop_moves(p))
                moves.extend(self.__rook_moves(p))
            elif p.name == 'King':
                # Time to start checking for checks
                pass
                
    '''
    Make the given move
    '''
    def make_move(self, move):
        opponent = black if turn == white else white
        if move.is_passant:
            victim = move.piece.passant_victim
            self.__remove_at(opponent, victim.x_pos, victim.y_pos)
            self.piece.x_pos = x_dest
            self.piece.y_pos = y_dest

        elif move.castle_rook:
            
            

            


    '''
    Return a list of all possible pawn moves for the given pawn
    '''
    def __pawn_moves(self, pawn):
        moves = []
        if turn == white:
            if self.__is_open(pawn.x_pos, pawn.y_pos + 1, can_take=False):
                moves.append(Move(pawn, pawn.x_pos, pawn.y_pos + 1))
            if self.__is_takable(pawn.x_pos - 1, pawn.y_pos + 1):
                moves.append(Move(pawn, pawn.x_pos - 1, pawn.y_pos + 1, take=True))
            if self.__is_takable(pawn.x_pos + 1, pawn.y_pos + 1):
                moves.append(Move(pawn, pawn.x_pos + 1, pawn.y_pos + 1, take=True))
            if pawn.moved == 0:
                if self.__is_open(pawn.x_pos, pawn.y_pos + 2, can_take=False):
                    moves.append(Move(pawn, pawn.x_pos, pawn.y_pos + 2))

        else:
            if self.__is_open(pawn.x_pos, pawn.y_pos - 1, can_take=False):
                moves.append(Move(pawn, pawn.x_pos, pawn.y_pos - 1))
            if self.__is_takable(pawn.x_pos - 1, pawn.y_pos - 1):
                moves.append(Move(pawn, pawn.x_pos - 1, pawn.y_pos - 1, take=True))
            if self.__is_takable(pawn.x_pos + 1, pawn.y_pos - 1):
                moves.append(Move(pawn, pawn.x_pos + 1, pawn.y_pos - 1, take=True))
            if pawn.moved == 0:
                if self.__is_open(pawn.x_pos, pawn.y_pos + 2, can_take=False):
                    moves.append(Move(pawn, pawn.x_pos, pawn.y_pos + 2))
        return moves

    '''
    Return a list of all possible bishop moves for the given bishop
    '''
    def __bishop_moves(self, bishop):
        moves = []
        distance = 1
        can_move = self.__is_open(bishop.x_pos + distance, bishop.y_pos + distance)
        while can_move:
            if can_move < 0:
                moves.append(Move(bishop, bishop.x_pos + distance, bishop.y_pos + distance, take=True))
                break
            moves.append(Move(bishop, bishop.x_pos + distance, bishop.y_pos + distance))
            distance += 1
            can_move = self.__is_open(bishop.x_pos + distance, bishop.y_pos + distance)

        distance = 1
        can_move = self.__is_open(bishop.x_pos + distance, bishop.y_pos - distance)
        while can_move:
            if can_move < 0:
                moves.append(Move(bishop, bishop.x_pos + distance, bishop.y_pos - distance, take=True))
                break
            moves.append(Move(bishop, bishop.x_pos + distance, bishop.y_pos - distance))
            distance += 1
            can_move = self.__is_open(bishop.x_pos + distance, bishop.y_pos - distance)

        distance = 1
        can_move = self.__is_open(bishop.x_pos - distance, bishop.y_pos + distance)
        while can_move:
            if can_move < 0:
                moves.append(Move(bishop, bishop.x_pos - distance, bishop.y_pos + distance, take=True))
                break
            moves.append(Move(bishop, bishop.x_pos - distance, bishop.y_pos + distance))
            distance += 1
            can_move = self.__is_open(bishop.x_pos - distance, bishop.y_pos + distance)

        distance = 1
        can_move = self.__is_open(bishop.x_pos - distance, bishop.y_pos - distance)
        while can_move:
            if can_move < 0:
                moves.append(Move(bishop, bishop.x_pos - distance, bishop.y_pos - distance, take=True))
                break
            moves.append(Move(bishop, bishop.x_pos - distance, bishop.y_pos - distance))
            distance += 1
            can_move = self.__is_open(bishop.x_pos - distance, bishop.y_pos - distance)
        return moves

    '''
    Returns a list of all possible rook moves for a given rook
    '''
    def __rook_moves(self, rook):
        moves = []
        distance = 1
        can_move = self.__is_open(rook.x_pos + distance, rook.y_pos)
        while can_move:
            if can_move < 0:
                moves.append(Move(rook, rook.x_pos + distance, rook.y_pos, take=True))
                break
            moves.append(Move(rook, rook.x_pos + distance, rook.y_pos))
            distance += 1
            can_move = self.__is_open(rook.x_pos + distance, rook.y_pos)

        distance = 1
        can_move = self.__is_open(rook.x_pos - distance, rook.y_pos)
        while can_move:
            if can_move < 0:
                moves.append(Move(rook, rook.x_pos - distance, rook.y_pos, take=True))
                break
            moves.append(Move(rook, rook.x_pos - distance, rook.y_pos))
            distance += 1
            can_move = self.__is_open(rook.x_pos - distance, rook.y_pos)

        distance = 1
        can_move = self.__is_open(rook.x_pos, rook.y_pos + distance)
        while can_move:
            if can_move < 0:
                moves.append(Move(rook, rook.x_pos, rook.y_pos + distance, take=True))
                break
            moves.append(Move(rook, rook.x_pos, rook.y_pos + distance))
            distance += 1
            can_move = self.__is_open(rook.x_pos, rook.y_pos + distance)

        distance = 1
        can_move = self.__is_open(rook.x_pos, rook.y_pos - distance)
        while can_move:
            if can_move < 0:
                moves.append(Move(rook, rook.x_pos, rook.y_pos - distance, take=True))
                break
            moves.append(Move(rook, rook.x_pos, rook.y_pos - distance))
            distance += 1
            can_move = self.__is_open(rook.x_pos, rook.y_pos - distance)
        return moves

    '''
    Returns true if making a given move leads to check
    '''
    def __is_check(self, move):




    '''
    Remove the given players piece at the given position
    '''
    def __remove_at(self, player, x_pos, y_pos):
        victim = -1
        if player == white:
            for i, piece in enumerate(self.w_pos):
                if piece.xpos == x_pos and piece.y_pos == y_pos:
                    victim = i
                    break
            self.w_pos.pop(victim)
        else:
            for i, piece in enumerate(self.b_pos):
                if piece.xpos == x_pos and piece.y_pos == y_pos:
                    victim = i
                    break
            self.b_pos.pop(victim)

    '''
    Return true if there is an opponenet piece at the given location. Else
    return false
    '''
    def __is_takeable(self, x_cor, y_cor):
        if x_cor < 0 or x_cor >= self.board.x_size or y_cor < 0 or y_cor >= self.board.y_size:
            return False
        w_taken = any([p.x_pos == x_cor and p.y_pos == y_cor \
                        for p in self.w_pos])
        b_taken = any([p.x_pos == x_cor and p.y_pos == y_cor \
                        for p in self.b_pos])
        return (self.turn == white and b_taken) or (self.turn == black and w_taken)

    '''
    Return 0 if the position is not open or if the position is occupied by the opponent and can_take is false,
    1 if the position is truely open, and -1 if the postion is occupied by the opponent and can_take is true 
    ''' 
    def __is_open(self, x_cor, y_cor, can_take=True):
        if x_cor < 0 or x_cor >= self.board.x_size or y_cor < 0 or y_cor >= self.board.y_size:
            return 0

        w_taken = any([p.x_pos == x_cor and p.y_pos == y_cor \
                        for p in self.w_pos])
        b_taken = any([p.x_pos == x_cor and p.y_pos == y_cor \
                        for p in self.b_pos])
        if not p1_taken and not p2_taken:
            return 1
        if can_take and ((self.turn == white and b_taken) or (self.turn == black and w_taken)):
            return -1
        return 0

    
        
