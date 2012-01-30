//
// PokerStars.g
//
// This is an antlr3 grammar to build a AST from a PokerStars 
// history file.
//
grammar PokerStars;

options {
  language = Python;
  output = AST; 
  ASTLabelType=CommonTree;
}


tokens {
  GAME;
  INFO;
  CARDS;
  PLAYER;
  ACTION;
  SMALLBLIND;
  BIGBLIND;
  BUTTON;
  POST;
  DEAL;
  FOLD;
  BET;
  RAISE;
  CHECK;
  CALL;
  MUCK;
  COLLECT;
  RETURN;
  SHOW;
  SUMMARY;
  SEATS;
  BLINDS;
}

@lexer::members {
    inPlayerId = False
    numChars = 0
    playerIds = {}
    
    # Work around bug in Python code generator
    class SEATANDCHIPS_return:
       pass;
       
    # Keep track of player id 
    def addPlayerId( self, p ):
      self.playerIds[p] = p
}

   
   
// Lexer specs
//
// We don't try to achieve too much in the lexer, it provides a 
// simple first pass tokenising that significantly simplifies the
// token parsing stage.

//
// A further complication is that the player names aren't delimited 
// in anyway so we need some context-sensitive logic to parse them
// properly.
//



fragment DIGIT: '0'..'9' ;
fragment ALPHANUM: 'a'..'z' | 'A'..'Z' | DIGIT | '#' | ':';
fragment ANY: . ;

PLAYERID
@init {  
  num = 0 
  partial = "" 
}
 : 
   {self.inPlayerId}?=> '\n' (char='\u0020'..'\ufffd' {
            num = num + 1
            if num > 12:
              self.inPlayerId=False # we should signal failure here because the player id is unknown
            partial += unichr($char)
            #if ( self.playerIds[partial] ):
            #  self.inPlayerId=False
       } )+ ;

TOURNAMENT: {not self.inPlayerId}?=>'Tournament' ;
POKERSTARSGAME: {not self.inPlayerId}?=>'PokerStars Game' ;
COMMA: {not self.inPlayerId}?=>',' ;
COLON: {not self.inPlayerId}?=>':' ;
DASH: {not self.inPlayerId}?=>'-' ;
HASH: {not self.inPlayerId}?=>'#' ;
PIPE: {not self.inPlayerId}?=>'|' ;
PERIOD: {not self.inPlayerId}?=>'.' ;
QUOT: {not self.inPlayerId}?=>'\'' ;
PLUS: {not self.inPlayerId}?=>'+' ;
BO: {not self.inPlayerId}?=>'(' ;
BC: {not self.inPlayerId}?=>')' ;
FOLDS: {not self.inPlayerId}?=>'folds' ;
BETS: {not self.inPlayerId}?=>'bets' ;
RAISES: {not self.inPlayerId}?=>'raises' ;
CALLS: {not self.inPlayerId}?=>'calls' ;
CHECKS: {not self.inPlayerId}?=>'checks' ;
TO: {not self.inPlayerId}?=>'to' ;
LEVEL: {not self.inPlayerId}?=>'Level';
SBO: {not self.inPlayerId}?=>'[' ;
SBC: {not self.inPlayerId}?=>']' ;
DOLLARS: {not self.inPlayerId}?=>'$' ;
SLASH: {not self.inPlayerId}?=>'/' ;
HOLDEMNL: {not self.inPlayerId}?=>'Hold\'em No Limit';
AEST: {not self.inPlayerId}?=>'AEST' ;
ET: {not self.inPlayerId}?=>'ET' ;
USD: {not self.inPlayerId}?=>'USD' ;
AUD: {not self.inPlayerId}?=>'AUD' ;
NINEMAX: {not self.inPlayerId}?=>'9-max';
SIXMAX: {not self.inPlayerId}?=>'6-max' ;
NUMERAL:{not self.inPlayerId}?=> ('I' | 'V' | 'X' )+ ;
POSTS: {not self.inPlayerId}?=>'posts' ;
ISBUTTON: {not self.inPlayerId}?=>'is the button' ;
TABLE: {not self.inPlayerId}?=>'Table' ;
UNCALLED: {not self.inPlayerId}?=>'Uncalled bet' ;
RETURNEDTO: {not self.inPlayerId}?=>'returned to' ;
COLLECTED: {not self.inPlayerId}?=>'collected' ; 
FROMPOT: {not self.inPlayerId}?=>'from pot' ;
SHOWS: {not self.inPlayerId}?=>'shows' ;
MUCKS: {not self.inPlayerId}?=>'mucks hand' ;
NOSHOW: {not self.inPlayerId}?=>'doesn\'t show hand' ;
DEALTTO: {not self.inPlayerId}?=>'Dealt to' ;
HOLECARDS: {not self.inPlayerId}?=>'*** HOLE CARDS ***' { self.inPlayerId = True} ;
FLOP: {not self.inPlayerId}?=>'*** FLOP ***' ;
TURN: {not self.inPlayerId}?=>'*** TURN ***' ;
RIVER: {not self.inPlayerId}?=>'*** RIVER ***' ;
SHOWDOWN: {not self.inPlayerId}?=>'*** SHOW DOWN ***' ;
SUMMARY: {not self.inPlayerId}?=>'*** SUMMARY ***' ;
BUTTON: {not self.inPlayerId}?=>'button';
SMALLBLIND: {not self.inPlayerId}?=>'small blind' ;
BIGBLIND: {not self.inPlayerId}?=>'big blind' ;
FOLDEDBF: {not self.inPlayerId}?=>'folded before Flop' ;
FOLDEDONFL: {not self.inPlayerId}?=>'folded on the Flop';
FOLDEDONT: {not self.inPlayerId}?=>'folded on the Turn';
FOLDRIVER: {not self.inPlayerId}?=>'folded on the River' ;
NOBET: {not self.inPlayerId}?=>'didn\'t bet' ;
TOTALPOT: {not self.inPlayerId}?=>'Total pot' ;
MUCKED: {not self.inPlayerId}?=>'mucked' ;
SHOWED: {not self.inPlayerId}?=>'showed' ;
ANDWON: {not self.inPlayerId}?=>'and won' ;
WITH: {not self.inPlayerId}?=>'with' ;
RAKE: {not self.inPlayerId}?=>'Rake';
BOARD: {not self.inPlayerId}?=>'Board' ;

WHITESPACE: {not self.inPlayerId}?=>' '+ { $channel = HIDDEN; } ;
NL: {not self.inPlayerId}?=>( '\n' | '\r' )+ ;

SEATANDCHIPS returns [playerId, stack, seatNum]: {not self.inPlayerId}?=>'\nSeat ' snum+=DIGIT+ ':' (options {greedy=false;} : id+=('\u0020'..'\ufffd' )+ ) ' (' chips+=DIGIT+ ' in chips)' 
  {
    $playerId = $id
    $stack = $chips
    $seatNum = $snum
    self.addPlayerId( $id )
  }
  ;

SEAT: {not self.inPlayerId}?=>'Seat' ;

NUMBER: {not self.inPlayerId}?=>DIGIT+ ;
ID: {not self.inPlayerId}?=>'#' NUMBER ;
TEXT: {not self.inPlayerId}?=>ALPHANUM+ ;



/*
maximum payer id length = 12
*/


// Parser specs
// 
// Mostly straight forward, the only trick here is use new line characters
// to disambiguate some clauses.

// Top level rules
game: 
   heading 
   tableSummary 
   player+
   blinds*
   holeAction 
   flopAction? 
   turnAction? 
   riverAction? 
   showdownAction? 
   gameSummary
   -> ^( GAME heading tableSummary ^(SEATS player+) ^(BLINDS blinds*) 
         holeAction flopAction? turnAction? riverAction?  showdownAction? gameSummary )
   ;
  
// Simple and token rules
timezone: AEST | ET ;      // TODO: flesh these out
currency: USD | AUD;      // TODO: flesh these out
type: HOLDEMNL ;    // TODO: Add more supported types
levelNum: NUMERAL ;
dateTime:  
   NUMBER SLASH! NUMBER SLASH! NUMBER  NUMBER COLON! NUMBER COLON! NUMBER timezone
   ;
money: DOLLARS! NUMBER PERIOD! NUMBER ;

tableId: QUOT! NUMBER NUMBER QUOT! ;
fees: money PLUS! money currency ;

playerId :  PLAYERID ;

dealtCards: SBO TEXT+ SBC -> ^(CARDS TEXT+ ) ; // We parse the card details in a subsequent phase to make it easier
levelDetails: LEVEL! levelNum! BO! NUMBER SLASH! NUMBER BC! ;

// Possible player betting actions: TODO: is there a reraise ? 
action: 
    FOLDS -> FOLD
  | BETS amount=NUMBER -> ^( BET $amount )
  | RAISES ramount=NUMBER TO amount=NUMBER -> ^( RAISE $ramount $amount )
  | CALLS amount=NUMBER -> ^( CALL $amount )
  | CHECKS -> CHECK
  ;

player: s=SEATANDCHIPS NL -> ^( PLAYER $s ) ; 

heading: POKERSTARSGAME id=ID COLON TOURNAMENT tid=ID COMMA f=fees t=type DASH lvl=levelDetails DASH dt=dateTime SBO dtg=dateTime SBC  NL
   -> ^(INFO $id $tid $f $t $lvl $dt $dtg )
   ;

tableSize: NINEMAX | SIXMAX
   ;

tableSummary: 
   TABLE id=tableId  sz=tableSize SEAT button=ID ISBUTTON NL 
   -> ^( TABLE $id $sz $button )
   ;

blindType: POSTS! SMALLBLIND | POSTS! BIGBLIND
   ;

blinds: 
   id=playerId COLON t=blindType amount=NUMBER NL
   -> ^( POST $t $id $amount) 
   ;

playerAction: 
   id=playerId COLON act=action NL 
   -> ^( ACTION $id $act )
   ;
    
handType: ( TEXT | COMMA) + ;
    
betSummary: 
     UNCALLED BO amount=NUMBER BC RETURNEDTO id=playerId NL -> ^(RETURN $id $amount )
   | id=playerId COLLECTED amount=NUMBER FROMPOT NL -> ^(COLLECT $id $amount)
   | id=playerId COLON 
    ( SHOWS deal=dealtCards BO handType BC -> ^(SHOW $id $deal )
    | MUCKS
    | NOSHOW) NL
   ; 

holeAction: 
   HOLECARDS NL DEALTTO id=playerId deal=dealtCards NL playerAction+ betSummary* 
   -> ^( DEAL $id $deal playerAction+ betSummary*  )
   ;

flopAction: FLOP deal=dealtCards NL playerAction+ betSummary*
   -> ^( FLOP $deal playerAction+ betSummary* )
   ;

turnAction: TURN dealtCards deal=dealtCards NL playerAction+ betSummary*  
   -> ^( TURN $deal playerAction+ betSummary*  )
   ;

riverAction: RIVER dealtCards deal=dealtCards NL playerAction+ betSummary*
   -> ^( RIVER $deal playerAction+ betSummary*  )
   ;

showdownAction: SHOWDOWN NL betSummary+
   -> ^( SHOWDOWN betSummary+ )
   ;
  
playerSummary: 
  SEAT NUMBER COLON playerId  
  (BO BUTTON BC | BO SMALLBLIND BC | BO BIGBLIND BC )?  
  ( FOLDEDBF  (BO NOBET BC)?
  | FOLDEDONFL (BO NOBET BC)?
  | FOLDEDONT (BO NOBET BC)?
  | FOLDRIVER (BO NOBET BC)?
  | COLLECTED BO NUMBER BC
  | MUCKED dealtCards 
  | SHOWED dealtCards ANDWON BO NUMBER BC WITH handType 
  )
  ;
  
gameSummary:
   SUMMARY NL TOTALPOT total=NUMBER PIPE RAKE rake=NUMBER (NL BOARD dealtCards)? (NL playerSummary)+ 
   -> ^( SUMMARY $total $rake )
   ;

   