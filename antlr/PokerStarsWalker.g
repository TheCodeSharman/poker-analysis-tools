tree grammar PokerStarsWalker;

options {
  language = Python;
  tokenVocab = PokerStars;
  ASTLabelType = CommonTree;
}

@header {
  from parser.data import *
  import datetime
  from pytz import timezone
}

game returns [ hand ]
  @init { 
     h = Hand() 
     preflop = BettingRound()
     h.rounds.append( preflop )
     $hand = h
  } : 
  ^( GAME 
     ^(INFO id=ID tid=ID fees type levelDetails dt=dateTime dtg=dateTime )  
     ^(TABLE tableId tsize=tableSize button=NUMBER )  
        {
           h.numOfSeats = $tsize.size
           h.gameType = $type.type
        }
     ^( SEATS  (player { h.addPlayer( $player.pyr ) })+ )     
     ^( BLINDS (blinds { h.addActions( preflop, [ $blinds.bl ] ) } )* )    
     holeAction 
        {
           h.addActions( preflop, $holeAction.actions )
           h.addWinnings( $holeAction.win )
           h.addKnownCards( $holeAction.deadcards )
        }       
     (streetAction
        {
           betRound = $streetAction.round
           h.addActions( betRound, $streetAction.actions )
           h.addWinnings( $streetAction.win )
           h.addKnownCards( $streetAction.deadcards )
           h.rounds.append( betRound )
        })*
     (showdownAction
        {
           h.addWinnings( $showdownAction.win )
           h.addKnownCards( $showdownAction.deadcards )
        })?
     gameSummary
        {
           h.totalPot = $gameSummary.pot
           h.rake = $gameSummary.rake
        } )
   ;
 
tableSize returns [ size ]: 
    SIXMAX { $size = 6 }
   | NINEMAX { $size = 9 }
   ;
   
type returns [type]
  : HOLDEMNL { $type=Hand.HoldEmNoLimit } ;
  
levelDetails returns [small,big]: sb=NUMBER bb=NUMBER
  { 
    $small = $sb.text
    $big = $bb.text
  };

dateTime returns [dt]: y=NUMBER m=NUMBER d=NUMBER h=NUMBER min=NUMBER s=NUMBER tz=timezone
  {
    $dt = datetime.datetime( int($y.text), int($m.text), int($d.text), 
        int($h.text), int($min.text), int($s.text), 0, $tz.tz )
  };
  
timezone returns [tz]:
   'AEST' { $tz = timezone('Australia/Tasmania') }
  | 'ET'  { $tz = timezone('UTC') }
  ;
  
fees returns [byin, curr] :
  buyin=money fee=money currency
  {
    $byin = Money( $buyin.cents, $currency.curr )
    $curr = Money( $fee.cents, $currency.curr )
  };
 
money returns [ cents ]: d=NUMBER c=NUMBER 
  { 
    $cents = $d.text*100 + $c.text 
  };
  
 currency returns [ curr ]: 
     'USD' { $curr = Money.USD }
   | 'AUD' { $curr = Money.AUD }
  ;
  
tableId returns [id] : a=NUMBER b=NUMBER { $id = $a.text + ' ' + $b.text } ;

playerId returns [id] : ts+=TOKEN+ 
  { 
    $id = ""
    for t in $ts:
      $id+=" "+t.text
  };

player returns [ pyr ] : 
  ^( PLAYER st=NUMBER playerId stack=NUMBER ) 
  {
    $pyr = Player( $playerId.id )
    $pyr.initialStack = int( $stack.text )
    $pyr.seat = int( $st.text )
  };
  
blindType: SMALLBLIND | BIGBLIND ;    
    
blinds returns [ bl ]  :
  ^( POST blindType playerId NUMBER )
  {
    a = Action()
    a.action = Action.Post
    a.bet = int($NUMBER.text)
    $bl = [ $playerId.id, a ]
  };

deal returns [ cards ] : ^(CARDS cds+=TOKEN+ ) 
  { 
    $cards = []
    for c in $cds:
      $cards.append( Card( c.text ) )
  };
    
action returns [ act ] :
     FOLD
     { 
       $act = Action()
       $act.action = Action.Fold
     }     
  |  ^( BET NUMBER )
     {
       $act = Action()
       $act.action= Action.Bet
       $act.bet = Money( int( $NUMBER.text ) )
     }
  |  ^( RAISE NUMBER ram=NUMBER )
     {
       $act = Action()
       $act.action= Action.Raise
       $act.bet = Money( int( $ram.text ) )
     }
  |  ^( CALL NUMBER )
     {
       $act = Action()
       $act.action= Action.Call
       $act.bet = Money( int( $NUMBER.text ) )
     }
  |  CHECK
     {
       $act = Action()
       $act.action= Action.Check
       $act.bet = Money( 0 )
     }
   ;
   
playerAction returns [ pact ] :
  ^( ACTION playerId action )
  {
    $pact = [ $playerId.id, $action.act ]
  }
   ;
   
betSummary returns [ pid, cards, win ] :
    ^( RETURN playerId NUMBER ) 
    { 
       $pid = $playerId.id
       $cards = None
       $win = int( $NUMBER.text )
    } 
  | ^( COLLECT playerId NUMBER )
    { 
       $pid = $playerId.id
       $cards = None
       $win = int( $NUMBER.text )
    } 
  | ^( SHOW playerId deal)
    {
       $pid = $playerId.id
       $cards = $deal.cards
    };
    
holeAction returns [ actions, deadcards, win ] :
  ^( DEAL playerId deal acts+=playerAction+ bets+=betSummary* )
  {
    $actions = $acts
    $deadcards = [ [$playerId.id, $deal.cards] ]
    $win = []
    if $bets:
      for b in $bets:
        if b.cards:
          $deadcards.append( [b.pid, b.cards] )
        if b.win:
          $win.append( [b.pid, b.win] )
  };
  
streetAction returns [ round, actions, deadcards, win ] :
  ^( (FLOP | TURN | RIVER ) deal acts+=playerAction+ bets+=betSummary* )
  {
    $round = BettingRound()
    $round.cards = $deal.cards
    $actions = $acts
    $deadcards = []
    $win = []
    if $bets:
      for b in $bets:
        if b.cards:
         $deadcards.append( [b.pid, b.cards] )
        if b.win:
         $win.append( [b.pid, b.win] )
  };
   
showdownAction returns [ deadcards, win ] :
  ^( SHOWDOWN bets+=betSummary* )
  {
    $deadcards = []
    $win = []
    if $bets:
	    for b in $bets:
	      if b.cards:
	        $deadcards.append( [b.pid, b.cards] )
	      if b.win:
	        $win.append( [b.pid, b.win] )
  };
  
 gameSummary returns [ pot, rake ] :
  ^( SUMMARY p=NUMBER r=NUMBER )
  {
      $pot = int(p.text)
      $rake = int(r.text)
  };