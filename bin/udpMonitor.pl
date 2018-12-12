#!/usr/bin/perl
#syslogMonitor.pl
# Source: http://www.thegeekstuff.com/2010/07/perl-tcp-udp-socket-programming/

# Marcel Zoller, 2018
# This is not used for normal operation.
# It simulates a simple UDP receiver like Loxone Miniserver is.
# For debugging, send UDP packages to this server instead of the Miniserver and see the UDP communication.
use IO::Socket::INET;
use utf8;
use Encode;
use Time::Piece;
use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;
use LWP::Simple;
use Net::Ping;



# flush after every write
$| = 1;


# Konfig LoxBerry auslesen
my %pcfg;
my %miniservers;
tie %pcfg, "Config::Simple", "$lbpconfigdir/pluginconfig.cfg";
$UDP_Port = %pcfg{'MAIN.LB_UDP_Port'};
$SetClock = %pcfg{'MAIN.setclock'};
%miniservers = LoxBerry::System::get_miniservers();
$LOX_Name = $miniservers{1}{Name};
$LOX_IP = $miniservers{1}{IPAddress};
$LOX_User = $miniservers{1}{Admin};
$LOX_PW = $miniservers{1}{Pass};



my ($socket,$received_data);
my ($peeraddress,$peerport);


# Datum und Uhrzeit zusammenbauen
my $t = my $t = localtime;
$mdy    = $t->dmy(".");
$hms    = $t->hms;
$datumtime = "$mdy $hms";
#print $datumtime;

$UDP_Port2 = $UDP_Port+1;



#UDP Reciver PORT for EDP Port
$socket = new IO::Socket::INET (
	LocalPort => $UDP_Port,
	Proto => 'udp'
) or die "ERROR in Socket Creation UDP port : $!\n";

#UDP Sender PORT for Watchdog
$sock = IO::Socket::INET->new(
    Proto    => 'udp',
    PeerPort => $UDP_Port2,
    PeerAddr => '127.0.0.1',
) or die "Could not create socket watchdog prt: $!\n";

print "\nUDP-Moniter by Marcel Zoller 2018 - V3.3 / Listening on port $UDP_Port\n";


while(1)
{
# Create my logging object
my $log = LoxBerry::Log->new ( 
	name => 'syslogMonitor',
	filename => "$lbplogdir/magichome_udpMonitor.log",
	append => 1
	);
LOGSTART "MagicHome demand UDPMonitor start";

my $filename = 'return.log';
system ("echo leer>return.log");

# read operation on the socket
$socket->recv($recieved_data,10000);
$peer_address = $socket->peerhost();
$peer_port = $socket->peerport();
$recieved_data = decode('iso-8859-1',encode('utf-8', $recieved_data));

#print $recieved_data;
#print "\n";



# Deamon Watchdog 
if(index($recieved_data,"TEST")!=-1){
	print "WATCHDOG REV: TEST\n";
	LOGDEB "WATCHDOG REV: $recieved_data";
	$sock->send('TEST') or die "Send error: $!\n";
	print "WATCHDOG SEND: TEST\n";
	LOGDEB "WATCHDOG SEND: TEST";
}

print "$recieved_data   $datumtime \n"; 
LOGINF "RECIVED DATE: $recieved_data   $datumtime"; 



# Ab hier wird das UDP Protokoll auseinander genommen von der Loxone	
my @splitestate = split(':', $recieved_data);
$MagicHome_IP = $splitestate[0];
$MagicHome_Befehl = $splitestate[1];
$MagicHome_Befehl2 = $splitestate[2];
$MagicHome_Befehl3 = $splitestate[3];

print "MagicHome IP: $MagicHome_IP\n";
print "MagicHome Befehl: $MagicHome_Befehl\n";
print "MagicHome Befehl2: $MagicHome_Befehl2\n";
LOGINF "MagicHome IP: $MagicHome_IP";
LOGINF "MagicHome Befehl: $MagicHome_Befehl";
LOGINF "MagicHome Befehl2: $MagicHome_Befehl2";
LOGINF "MagicHome Befehl3: $MagicHome_Befehl3";



if(index($MagicHome_Befehl,"on")!=-1){
	#print ">>>>>>  FOUND ON <<<<<<<\n";
	LOGDEB "Befehl --on";
	LOGDEB "python -m flux_led $MagicHome_IP --on";
	system ("python -m flux_led $MagicHome_IP --on>$filename 2>&1");
	$res = result($filename); 
	
}  elsif(index($MagicHome_Befehl,"off")!=-1){
	#print ">>>>>>  FOUND OFF <<<<<<<\n";
	LOGDEB "Befehl --off";
	LOGDEB "python -m flux_led $MagicHome_IP --off";
	system("python -m flux_led $MagicHome_IP --off>$filename 2>&1");
	$res = result($filename); 

} elsif(index($MagicHome_Befehl,"all_on")!=-1){
	#print ">>>>>>  FOUND OFF <<<<<<<\n";
	LOGDEB "Befehl --ALL off";
	LOGDEB "python -m flux_led -sS --off";
	system ("python -m flux_led -sS --off>$filename 2>&1");
	$res = result($filename); 

} elsif(index($MagicHome_Befehl,"all_off")!=-1){
	#print ">>>>>>  FOUND OFF <<<<<<<\n";
	LOGDEB "Befehl --ALL off";
	LOGDEB "python -m flux_led -sS --off";
	system ("python -m flux_led -sS --off>$filename 2>&1");
	$res = result($filename); 

} elsif(index($MagicHome_Befehl,"#")!=-1){
	#print ">>>>>>  FOUND Color # <<<<<<<\n";
	LOGDEB "Befehl # Color";
	$red = hex(substr($MagicHome_Befehl,1,2));
	$green = hex(substr($MagicHome_Befehl,3,2));
	$blue = hex(substr($MagicHome_Befehl,5,2));
	
	#print "$red,$green,$blue\n";
	LOGDEB "RGB: $red,$green,$blue"; 
	
	if(index($MagicHome_Befehl2,"on")!=-1){
		#print "python -m flux_led $MagicHome_IP -c $red,$green,$blue --on\n";
		LOGDEB "Befehl --on";
		LOGDEB "python -m flux_led $MagicHome_IP -c $red,$green,$blue --on";
		system ("python -m flux_led $MagicHome_IP -c $red,$green,$blue --on>$filename 2>&1");
		$res = result($filename); 
		
	} elsif(index($MagicHome_Befehl2,"off")!=-1){
		#print "python -m flux_led $MagicHome_IP -c $red,$green,$blue --off\n";
		LOGDEB "Befehl --off";
		LOGDEB "python -m flux_led $MagicHome_IP -c $red,$green,$blue --off";
		system ("python -m flux_led $MagicHome_IP -c $red,$green,$blue --off>$filename 2>&1");
		$res = result($filename); 
		
	} else {
		#print "python -m flux_led $MagicHome_IP -c $red,$green,$blue\n";
		LOGDEB "python -m flux_led $MagicHome_IP -c $red,$green,$blue";
		system ("python -m flux_led $MagicHome_IP -c $red,$green,$blue>$filename 2>&1");
		$res = result($filename); 
		
	}
} elsif(index($MagicHome_Befehl,"W")!=-1){
	#print ">>>>>>  FOUND WarmeWhite <<<<<<<\n";
	LOGDEB "Befehl W";
	$warmwhite = substr($MagicHome_Befehl,1,3);
	
	# print "WW: $warmwhite\n";
	LOGDEB "WW: $warmwhite"; 
	
	if(index($MagicHome_Befehl2,"on")!=-1){
		# print "python -m flux_led $MagicHome_IP -w $warmwhite --on\n";
		LOGDEB "Befehl --on";
		LOGDEB "python -m flux_led $MagicHome_IP -w $warmwhite --on";
		system ("python -m flux_led $MagicHome_IP -w $warmwhite --on>$filename 2>&1");
		$res = result($filename); 
		
	} elsif(index($MagicHome_Befehl2,"off")!=-1){
		# print "python -m flux_led $MagicHome_IP -w $warmwhite --off\n";
		LOGDEB "Befehl --off";
		LOGDEB "python -m flux_led $MagicHome_IP -w $warmwhite --off";
		system ("python -m flux_led $MagicHome_IP -w $warmwhite --off>$filename 2>&1");
		$res = result($filename); 
		
	} else {
		# print "python -m flux_led $MagicHome_IP -w $warmwhite\n";
		LOGDEB "python -m flux_led $MagicHome_IP -w $warmwhite";
		system ("python -m flux_led $MagicHome_IP -w $warmwhite>$filename 2>&1");
		$res = result($filename); 
		
	}
	
} elsif(index($MagicHome_Befehl,"P")!=-1){
	#print ">>>>>>  FOUND WarmeWhite <<<<<<<\n";
	LOGDEB "Befehl PATTERN";
	$pattern = substr($MagicHome_Befehl,1,3);
	$pattern = $pattern+36;
	
	print "Pattern: $pattern\n";
	LOGDEB "Pattern: $pattern"; 
	LOGDEB "Speed: $MagicHome_Befehl2\%";
	
	if(index($MagicHome_Befehl3,"on")!=-1){
		print "python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2 --on\n";
		LOGDEB "Befehl --on";
		LOGDEB "python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2 --on";
		system ("python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2 --on>$filename 2>&1");
		$res = result($filename); 
		
	} elsif(index($MagicHome_Befehl3,"off")!=-1){
		# print "python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2 --off\n";
		LOGDEB "Befehl --off";
		LOGDEB "python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2 --off";
		system ("python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2 --off>$filename 2>&1");
		$res = result($filename); 
		
	} else {
		# print "python -m flux_led $MagicHome_IP - -p $pattern $MagicHome_Befehl2\n";
		LOGDEB "python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2";
		system ("python -m flux_led $MagicHome_IP -p $pattern $MagicHome_Befehl2>$filename 2>&1");
		$res = result($filename); 
		
	}
	
}

# Sync/Set Clock von allen Magic Home Geräten im Netzwerk
if($SetClock =="1"){
	LOGDEB "Set Clock Magic Home\n";
	system("python -m flux_led -s --setclock>$filename");
	$res = result($filename); 
	}
	
LOGEND "Operation finished sucessfully.";
}

$socket->close();

##########################################################################
# Result File Return 0 = no Error / 1 = Error
##########################################################################
sub result
{
	my ($filename) = @_;
	my $answer;
	open(my $fh, '<:encoding(UTF-8)', $filename)
		or die "Could not open file '$filename' $!";
 
	while (my $row = <$fh>) {
	  chomp $row;
	  print "$row\n";
	  if(index($row,"Err")!=-1){
		LOGERR "$row";
		$answer = 1;
	  } elsif(index($row,"Unable to connect")!=-1){
		LOGERR "$row";
		$answer = 1;
	  } elsif(index($row,"is not in range")!=-1){
		LOGERR "$row";
		$answer = 1;
	  } else {
		LOGDEB "$row";
		$answer = 0;
	  } 
	}

	return $answer;	 
}	