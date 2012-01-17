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
  };
    
type: HOLDEMNL { return Hand.HoldEmNoLimit } ;
  
levelDetails: sb=NUMBER bb=NUMBER { return [ $sb.text, $bb.text ] } ;

dateTime: d=NUMBER m=NUMBER y=NUMBER h=NUMBER min=NUMBER s=NUMBER tz=timezone
   {
     return datetime.datetime( $y.text, $m.text, $d.text, $h.text, $min.text, $s.text, $tz.text )
   };
  
timezone:
   'AEST' { return datetime.tzinfo.utcoffset( 10 ) }
  | 'ET'  { return datetime.tzinfo.utcoffset( 0 ) }
  ;
  
fees:
  buyin=money fee=money currency
  {
    return [ Money( $buyin.text, $currency.text ), Money( $fee.text, $currency.text ) ]
  };
 
 money: d=NUMBER c=NUMBER { return d*100+c; };
 currency: 
     'USD' { return Money.USD; }
   | 'AUD' { return Money.AUD; }
  ;