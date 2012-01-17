tree grammar pokerstars_walk;

options {
  language = Python;
  tokenVocab = pokerstars;
  ASTLabelType = CommonTree;
}

@header {
  from parser.data import *
  import datetime
}

game: 
  ^( GAME 
     ^(INFO id=ID tid=ID fees type levelDetails dt=dateTime dtg=dateTime ))
  {
    h = Hand()
    h.gameType = $type.type
    return h
  };
    
type returns [type]
  : HOLDEMNL { $type=Hand.HoldEmNoLimit } ;
  
levelDetails returns [small,big]: sb=NUMBER bb=NUMBER
{ 
    $small = $sb.text
    $big = $bb.text
} ;

dateTime returns [dt]: d=NUMBER m=NUMBER y=NUMBER h=NUMBER min=NUMBER s=NUMBER tz=timezone
   {
     $dt = datetime.datetime( $y.text, $m.text, $d.text, $h.text, $min.text, $s.text, $tz.text )
   };
  
timezone returns [tz]:
   'AEST' { $tz = datetime.tzinfo.utcoffset( 10 ) }
  | 'ET'  { $tz = datetime.tzinfo.utcoffset( 0 ) }
  ;
  
fees returns [byin, curr] :
  buyin=money fee=money currency
  {
    $byin = Money( $buyin.text, $currency.text )
    $curr = Money( $fee.text, $currency.text )
  };
 
 money: d=NUMBER c=NUMBER { return d*100+c; };
 currency: 
     'USD' { return Money.USD; }
   | 'AUD' { return Money.AUD; }
  ;