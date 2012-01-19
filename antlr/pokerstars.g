//
// PokerStars.g
//
// This is an antlr3 grammar to build a AST from a PokerStars 
// history file.
//
// We use a combined grammar here because the complexity doesn't
// justify splitting the grammar into multiple files.
//
grammar pokerstars;

options {
  language = Python;
  output = AST; 
  ASTLabelType=CommonTree;
}

tokens {
  GAME;
  INFO;
  TABLE;
  CARDS;
  NINEMAX;
  SIXMAX;
  HOLDEMNL;
  PLAYER;
  ACTION;
  SMALLBLIND;
  BIGBLIND;
  BUTTON;
  POST;
  DEAL;
  FLOP;
  TURN;
  RIVER;
  SHOWDOWN;
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

// Lexer specs
//
// We don't try to achieve too much in the lexer, it provides a 
// simple first pass tokenising that significantly simplifies the
// token parsing stage.
fragment DIGIT: '0'..'9' ;
fragment ALPHA: 'a'..'z' | 'A'.. 'Z'  ;
fragment ALPHANUM: ALPHA | DIGIT ;

WHITESPACE: ' '+ { $channel = HIDDEN; } ;
NL: ( '\n' | '\r' )+ ;
NUMBER: DIGIT+ ;
TOKEN: ALPHANUM* ;
ID: '#' NUMBER ;

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
timezone: 'AEST' | 'ET' ;      // TODO: flesh these out
currency: 'USD' | 'AUD' ;      // TODO: flesh these out
type: 'Hold\'em No Limit' -> HOLDEMNL
   ;    // TODO: Add more supported types
levelNum: 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI' | 'VII' | 'VIII' | 'VIIII' 
  | 'X' | 'XI' | 'XII' | 'XIII' | 'XIIII' | 'XV' | 'XVI' | 'XVII' | 'XVIII'
  | 'XVIIII' | 'XX' | 'XXI' | 'XXII' | 'XXIII' | 'XXIIII' | 'XXV' | 'XXVI' ;
dateTime:  
   NUMBER '/'! NUMBER '/'! NUMBER  NUMBER ':'! NUMBER ':'! NUMBER timezone
   ;
money: '$'! NUMBER '.'! NUMBER ;

tableId: '\''! NUMBER NUMBER '\''! ;
fees: money '+'! money currency ;

playerId: TOKEN+ ; // Just to make things difficult some player names have white space 
                   // in their names! Work around this we simply collect adjacent TOKEN's
                   
dealtCards: '[' TOKEN+ ']' -> ^(CARDS TOKEN+ ) ; // We parse the card details in a subsequent phase to make it easier
levelDetails: 'Level'! levelNum! '('! NUMBER '/'! NUMBER ')'! ;

// Possible player betting actions: TODO: is there a reraise ? 
action: 
    'folds' -> FOLD
  | 'bets' amount=NUMBER -> ^( BET $amount )
  | 'raises' ramount=NUMBER 'to' amount=NUMBER -> ^( RAISE $ramount $amount )
  | 'calls' amount=NUMBER -> ^( CALL $amount )
  | 'checks' -> CHECK
  ;

player: 'Seat' seat=NUMBER ':' id=playerId '(' stack=NUMBER ' in chips)' NL -> ^( PLAYER $seat $id $stack ) ; 

heading: 'PokerStars Game' id=ID ':' 'Tournament' tid=ID ',' f=fees t=type '-' lvl=levelDetails '-' dt=dateTime '[' dtg=dateTime ']'  NL
   -> ^(INFO $id $tid $f $t $lvl $dt $dtg )
   ;

tableSize:
     '9-max' -> NINEMAX
   | '6-max' -> SIXMAX
   ;

tableSummary: 
   'Table' id=tableId  sz=tableSize' Seat #' button=NUMBER ' is the button' NL 
   -> ^( TABLE $id $sz $button )
   ;

blindType:
     'posts small blind' -> SMALLBLIND 
   | 'posts big blind' -> BIGBLIND
   ;

blinds: 
   id=playerId ':' t=blindType amount=NUMBER NL
   -> ^( POST $t $id $amount) 
   ;

playerAction: 
   id=playerId ':' act=action NL 
   -> ^( ACTION $id $act )
   ;
    
handType: ( TOKEN | ',') + ;
    
betSummary: 
     'Uncalled bet' '(' amount=NUMBER ')' 'returned to' id=playerId NL -> ^(RETURN $id $amount )
   | id=playerId 'collected' amount=NUMBER 'from pot' NL -> ^(COLLECT $id $amount)
   | id=playerId ':' 
    ( 'shows' deal=dealtCards '(' handType ')' -> ^(SHOW $id $deal )
    | 'mucks hand'
    | 'doesn\'t show hand') NL
   ; 

holeAction: 
   '*** HOLE CARDS ***' NL 'Dealt to' id=playerId deal=dealtCards NL playerAction+ betSummary* 
   -> ^( DEAL $id $deal playerAction+ betSummary*  )
   ;

flopAction: '*** FLOP ***' deal=dealtCards NL playerAction+ betSummary*
   -> ^( FLOP $deal playerAction+ betSummary* )
   ;

turnAction: '*** TURN ***' dealtCards deal=dealtCards NL playerAction+ betSummary*  
   -> ^( TURN $deal playerAction+ betSummary*  )
   ;

riverAction: '*** RIVER ***' dealtCards deal=dealtCards NL playerAction+ betSummary*
   -> ^( RIVER $deal playerAction+ betSummary*  )
   ;

showdownAction: '*** SHOW DOWN ***' NL betSummary+
   -> ^( SHOWDOWN betSummary+ )
   ;
  
playerSummary: 
  'Seat' NUMBER ':' playerId  
  ('(button)' | '(small blind)' | '(big blind)' )?  
  ( 'folded before Flop'
  | 'folded on the Flop'
  | 'folded on the Turn'
  | 'folded on the River' '(didn\'t bet)'?
  | 'collected' '('NUMBER ')'
  | 'mucked' dealtCards 
  | 'showed' dealtCards 'and' 'won' '(' NUMBER ')' 'with' handType 
  )
  ;
  
gameSummary:
   '*** SUMMARY ***' NL 'Total pot' total=NUMBER '|' 'Rake' rake=NUMBER (NL 'Board' dealtCards)? (NL playerSummary)+ 
   -> ^( SUMMARY $total $rake )
   ;