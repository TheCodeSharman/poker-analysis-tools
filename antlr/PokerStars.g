//
// PokerStars.g
//
// This is an antlr3 grammar to build a AST from a PokerStars 
// history file.
//
// We use a combined grammar here because the complexity doesn't
// justify splitting the grammar into multiple files.
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
    inPlayerId = 0
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
fragment ALPHANUM: 'a'..'z' | 'A'..'Z' | DIGIT;

TOURNAMENT: 'Tournament' ;
POKERSTARSGAME: 'PokerStars Game' ;
SEAT: 'Seat' ;
COMMA: ',' ;
COLON: ':' ;
DASH: '-' ;
HASH: '#' ;
PIPE: '|' ;
PERIOD: '.' ;
QUOT: '\'' ;
PLUS: '+' ;
BO: '(' ;
BC: ')' ;
INCHIPS: 'in chips' ;
FOLDS: 'folds' ;
BETS: 'bets' ;
RAISES: 'raises' ;
CALLS: 'calls' ;
CHECKS: 'checks' ;
TO: 'to' ;
LEVEL: 'Level';
SBO: '[' ;
SBC: ']' ;
DOLLARS: '$' ;
SLASH: '/' ;
HOLDEMNL: 'Hold\'em No Limit';
AEST: 'AEST' ;
ET: 'ET' ;
USD: 'USD' ;
AUD: 'AUD' ;
NINEMAX: '9-max';
SIXMAX: '6-max' ;
NUMERAL: 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI' | 'VII' | 'VIII' | 'VIIII' 
  | 'X' | 'XI' | 'XII' | 'XIII' | 'XIIII' | 'XV' | 'XVI' | 'XVII' | 'XVIII'
  | 'XVIIII' | 'XX' | 'XXI' | 'XXII' | 'XXIII' | 'XXIIII' | 'XXV' | 'XXVI' ;
POSTS: 'posts' ;
ISBUTTON: 'is the button' ;
TABLE: 'Table' ;
UNCALLED: 'Uncalled bet' ;
RETURNEDTO: 'returned to' ;
COLLECTED: 'collected' ; 
FROMPOT: 'from pot' ;
SHOWS: 'shows' ;
MUCKS: 'mucks hand' ;
NOSHOW: 'doesn\'t show hand' ;
DEALTTO: 'Dealt to' ;
HOLECARDS: '*** HOLE CARDS ***' ;
FLOP: '*** FLOP ***' ;
TURN: '*** TURN ***' ;
RIVER: '*** RIVER ***' ;
SHOWDOWN: '*** SHOW DOWN ***' ;
SUMMARY: '*** SUMMARY ***' ;
BUTTON: 'button';
SMALLBLIND: 'small blind' ;
BIGBLIND: 'big blind' ;
FOLDEDBF: 'folded before Flop' ;
FOLDEDONFL: 'folded on the Flop';
FOLDEDONT: 'folded on the Turn';
FOLDRIVER: 'folded on the River' ;
NOBET: 'didn\'t bet' ;
TOTALPOT: 'Total pot' ;
MUCKED: 'mucked' ;
SHOWED: 'showed' ;
ANDWON: 'and won' ;
WITH: 'with' ;
RAKE: 'Rake';
BOARD: 'Board' ;

WHITESPACE: ' '+ { $channel = HIDDEN; } ;
NL: ( '\n' | '\r' )+ ;

NUMBER: DIGIT+ ;

TEXT: ALPHANUM+ ;

ID: '#' NUMBER ;
//PLAYERID: {self.inPlayerId}?=> ('\u0020'..'\ufffd')+ ;


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

playerId: TEXT+  ;

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

player: SEAT seat=NUMBER COLON id=playerId BO stack=NUMBER INCHIPS BC NL -> ^( PLAYER $seat $id $stack ) ; 

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

   