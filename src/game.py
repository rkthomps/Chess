
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
            take=False, check_passant=False, is_passant=False, \
            promote_to=None):
        self.piece = piece
        self.x_dest = x_dest
        self.y_dest = y_dest
        self.castle_rook = castle_rook
        self.take = take
        self.check_passant = check_passant
        self.is_passant=is_passant
        self.promote_to=promote_to

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
    Return all legal moves. A legal move is constituted as a possible move such
    that after the move is made, the player that made the move is not in check
    '''
    def get_legal_moves(self):
        possible = self.get_possible_moves
        legal_moves = []
        for move in possible:
            if not self.__self_check(move):
                legal_moves.append(move)
        return legal_moves

    '''
    Return all possible moves for the current player as a list of move objects.
    Note. This method does not check if a move leads to the king being in
    check. See get_legal_moves
    '''
    def __get_possible_moves(self, turn=self.turn):
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
                moves.extend(self.__king_moves(p))
            elif p.name == 'Knight':
                moves.extend(self.__knight_moves(p))
            else:
                raise Exception('Piece not recognized')
                
    '''
    Make the given move
    '''
    def make_move(self, move):
        opponent = black if self.turn == white else white
        if move.is_passant:
            victim = move.piece.passant_victim
            self.__remove_at(opponent, victim.x_pos, victim.y_pos)
            move.piece.x_pos = x_dest
            move.piece.y_pos = y_dest
            move.piece.moved += 1
            move.piece.passant_victim = None

        elif move.castle_rook:
            king = self.get_king(turn)
            move_left = move.castle_rook.x_pos < king.x_pos
            if move_left:
                king.x_pos -= 2
                move.castle_rook.x_pos = king.x_pos + 1
            else:
                king.x_pos += 2
                move.castle_rook.x_pos = king.x_pos - 1
            king.moved += 1
            move.castle_rook += 1

        else:
            # Checking whether a passant is possible on the next turn
            if move.piece.name == 'Pawn' and \
                    abs(move.piece.y_dest - move.piece.y_pos) == 2:
                opp_pieces = w_pos if opponent == white else b_pos
                for p in opp_pieces:
                    if p.name == 'Pawn' and \
                            abs(p.x_pos - move.piece.x_dest) == 1 and \
                            p.y_pos - move.piece.y_dest == 0:
                        p.passant_victim = move.piece

            if take:
                self.__remove_at(opponent, move.x_dest, move.y_dest)
            move.piece.x_pos = move.x_dest
            move.piece.y_pos = move.y_dest
            if promote_to:
                move.piece.name = promote_to
            move.piece.moved += 1
        self.turn = opponent


    '''
    Return a list of all possible pawn moves for the given pawn.
    '''
    def __pawn_moves(self, pawn):
        moves = []
        check_takes = []
        check_moves = []
        y_dir = 1 if self.turn == white else -1
        execute_passant = False

        capture = False
        if pawn.moved == 0:
            check_moves.append((pawn.x_pos + 2 * y_dir, pawn.y_pos, capture))
        check_moves.append((pawn.x_pos, pawn.y_pos + 1 * y_dir, capture))
        capture = True
        check_takes.append((pawn.x_pos + 1, pawn.y_pos + 1 * y_dir, capture))
        check_takes.append((pawn.x_pos - 1, pawn.y_pos + 1 * y_dir, capture))

        for x_dest, y_dest, cap in check_moves:
            can_take = self.__is_open(x_dest, y_dest, can_take=cap)
            if (not can_take) or (cap and can_take >= 0):
                continue
            if cap:
                capture = True
            else:
                capture = False
            promotions = self.__check_promo(pawn, x_dest, y_dest, capture)
            if promotions:
                moves.extend(promotions)
                continue
            passant = self.__check_passant(pawn, x_dest, y_dest, capture)
            if passant:
                moves.append(passant)
                execute_passant = True
            else:
                moves.append(Move(pawn, x_dest, y_dest, take=capture))
           
        if not execute_passant:
            pawn.passant_victim = None
        return moves
    
    '''
    Check if moving a pawn results in the ability for the pawn to be
    promoted. Return an array of moves accounting for the different types
    of promotions
    '''
    def __check_promo(self, pawn, x_dest, y_dest, take):
        possible_promotions = [
            'Queen',
            'Bishop',
            'Rook'
            'Knight']

        moves = []
        crit_pawn_y_pos = self.board.y_size - 1 if self.turn == white else 0
        if y_dest == crit_pawn_y_pos: 
            moves.extend([Move(pawn, x_dest, y_dest, take=take, \
                    promote_to=p) for p in possible_promotions])
        return moves

    '''
    Checks if a pawn that is currently eligible for a passant is being advanced
    one square
    '''
    def __check_passant(self, pawn, x_dest, y_dest, take):
        if pawn.passant_victim and x_dest == x_pos:
            return Move(pawn, x_dest, y_dest, is_passant=True)
        return None

    '''
    Return a list of all possible bishop moves for the given bishop
    '''
    def __bishop_moves(self, bishop):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for x_dir, y_dir in directions:
            distance = 1
            x_dest = bishop.x_pos + distance * x_dir
            y_dest = bishop.y_pos + distance * y_dir)

            can_move = self.__is_open(x_dest, y_dest)
            while can_move:
                if can_move < 0:
                    moves.append(Move(bishop, x_dest, y_dest, take=True))
                    break
                moves.append(Move(bishop, x_dest, y_dest)) 
                distance += 1
                can_move = self.__is_open(x_dest, y_dest)
        return moves

    '''
    Returns a list of all possible rook moves for a given rook
    '''
    def __rook_moves(self, rook):
        moves = []
        directions = [(1, 1), (1, -1), (0, 1), (0, -1)]

        for x_change, direc in directions:
            distance = 1
            x_dest = rook.x_pos + distance * direc * x_change
            y_dest = rook.y_pos + distance * direc * (1 - x_change)
            can_move = self.__is_open(x_dest, y_dest)

            while can_move:
                if can_move < 0:
                    moves.append(Move(bishop, x_dest, y_dest, take=True))
                    break
                moves.append(Move(bishop, x_dest, y_dest)) 
                distance += 1
                can_move = self.__is_open(x_dest, y_dest)
        return moves

    '''
    Returns a list of all possible king moves for a given king
    '''
    def __king_moves(self, king):
        moves = []
        for x_change in range(-1, 2):
            for y_change in range(-1, 2):
                if x_change == 0 and y_change == 0:
                    continue
                x_dest = king.x_pos + x_change
                y_dest = king.y_pos + y_change
                can_move = self.__is_open(x_dest, y_dest)
                if can_move == 0:
                    continue
                if can_move < 0:
                    moves.append(Move(king, x_dest, y_dest, take=True))
                else:
                    moves.append(Move(king, x_dest, y_dest))
        return moves

    '''
    Returns a list of all possible knight moves for a given knight
    '''
    def __knight_moves(self, knight):
        moves = []
        x_turn = 1
        y_turn = 0
        turns = [x_turn, y_turn]
        general_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for gx, gy in general_directions:
            for turn in turns:
                x_dest = knight.x_pos + gx + gx * turn
                y_dest = knight.y_pos + gy + gy * (1 - turn)
                can_move = self.__is_open(x_dest, y_dest)
                if can_move == 0:
                    continue
                if can_move < 0:
                    moves.append(Move(knight, x_dest, y_dest, take=True))
                else:
                    moves.append(Move(knight, x_dest, y_dest))
        return moves
         
    '''
    Checks is a current player is in check
    '''
    def in_check(self, player=self.turn):
        opponent = black if player == white else white
        opp_pos_moves = self.get_possible_moves(opponent)
        king_piece = self.__get_king(player)
        for move in opp_pos_moves:
            if move.take and move.x_dest == king_piece.x_pos and \
                    move.y_dest == king_piece.y_pos:
                return True
        return False

    '''
    Returns true if making a given move leads to check
    '''
    def __self_check(self, move):
        game_copy = Game(self.board, w_pos, b_pos, turn=self.turn)
        game_copy.make_move(move)
        return game_copy.in_check(self.turn)

    '''
    Return the king of the given player
    '''
    def __get_king(self, player=self.turn):
        if player == white:
            for p in self.w_pos:
                if p.name == 'King':
                    return p
        else:
            for p in self.b_pos:
                if p.name == 'King'
                    return p
        raise Exception("No king exists for player", player)
        return None


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

    
        
