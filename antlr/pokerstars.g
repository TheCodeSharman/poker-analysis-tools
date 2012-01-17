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
game: heading tableSummary player+ blinds holeAction flopAction? turnAction? riverAction? showdownAction? gameSummary ;
  
// Simple and token rules
timezone: 'AEST' | 'ET' ;      // TODO: flesh these out
currency: 'USD' | 'AUD' ;      // TODO: flesh these out
type: 'Hold\'em No Limit' ;    // TODO: Add more supported types
levelNum: 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI' | 'VII' | 'VIII' | 'VIIII' 
  | 'X' | 'XI' | 'XII' | 'XIII' | 'XIIII' | 'XV' | 'XVI' | 'XVII' | 'XVIII'
  | 'XVIIII' | 'XX' | 'XXI' | 'XXII' | 'XXIII' | 'XXIIII' | 'XXV' | 'XXVI' ;
dateTime:  NUMBER '/' NUMBER '/' NUMBER  NUMBER ':' NUMBER ':' NUMBER timezone ;
money: '$' NUMBER '.' NUMBER ;

tableId: '\'' NUMBER  NUMBER '\'' ;
fees: money '+' money  currency ;

playerId: TOKEN+ ; // Just to make things difficult some player names have white space 
                   // in their names! Work around this we simply collect adjacent TOKEN's
                   
dealtCards: '[' TOKEN+ ']' ; // We parse the card details in a subsequent phase to make it easier
levelDetails: 'Level'  levelNum  '(' NUMBER '/' NUMBER ')' ;

// Possible player betting actions: TODO: is there a reraise ? 
action: 'folds' | 'bets' NUMBER | 'raises' NUMBER 'to' NUMBER | 'calls' NUMBER | 'checks' ;

player:  'Seat'  NUMBER ':'  playerId  '(' NUMBER ' in chips)' NL ; 

heading: 'PokerStars Game' ID ':' 'Tournament' ID ',' fees type '-' levelDetails '-' dateTime '[' dateTime ']'  NL ;

tableSummary: 'Table'  tableId  ( '9-max' | '6-max' ) ' Seat #' NUMBER ' is the button' NL ;

blinds: playerId ':' 'posts small blind' NUMBER NL playerId ':' 'posts big blind' NUMBER NL ;

playerAction: playerId ':'  action NL ;
    
handType: ( TOKEN | ',') + ;
    
betSummary: 
     'Uncalled bet' '(' NUMBER ')' 'returned to'  playerId NL 
   | playerId  'collected'  NUMBER  'from pot' NL 
   | playerId ':' 
    ( 'shows' dealtCards '(' handType ')'
    | 'mucks hand'
    | 'doesn\'t show hand') NL
   ; 

holeAction: '*** HOLE CARDS ***' NL 'Dealt to'  playerId  dealtCards NL playerAction+ betSummary* ;

flopAction: '*** FLOP ***'  dealtCards NL playerAction+ betSummary* ;

turnAction: '*** TURN ***'  dealtCards  dealtCards NL playerAction+ betSummary* ;

riverAction: '*** RIVER ***'  dealtCards  dealtCards NL playerAction+ betSummary* ; 

showdownAction: '*** SHOW DOWN ***' NL betSummary+ ;
  
foldSummary: ( 'folded before Flop' | 'folded on the Flop' | 'folded on the Turn' | 'folded on the River')  ( '(didn\'t bet)')? ;
  
playerSummary: 
  'Seat'  NUMBER ':'  playerId  ('(button)'  | '(small blind)'  | '(big blind)' )?  
  ( foldSummary 
  | 'collected'  '(' NUMBER ')' 
  | 'mucked' dealtCards
  | 'showed' dealtCards 'and' 'won' '(' NUMBER ')' 'with' handType 
  )
  ;
  
gameSummary: '*** SUMMARY ***' NL 'Total pot'  NUMBER  '|'  'Rake'  NUMBER (NL 'Board'  dealtCards)? (NL playerSummary)+ ;
