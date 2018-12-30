#!/usr/bin/perl

# Einbinden von Module
use CGI;
use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;
use IO::Socket::INET;
use LWP::Simple;
use Net::Ping;


print "Content-type: text/html\n\n";

# Konfig auslesen
my %pcfg;
my %miniservers;
tie %pcfg, "Config::Simple", "$lbpconfigdir/pluginconfig.cfg";
$UDP_Port = %pcfg{'MAIN.UDP_Port'};
#$UDP_Send_Enable = %pcfg{'MAIN.UDP_Send_Enable'};
$HTTP_TEXT_Send_Enable = %pcfg{'MAIN.HTTP_TEXT_Send_Enable'};
$MINISERVER = %pcfg{'MAIN.MINISERVER'};
%miniservers = LoxBerry::System::get_miniservers();


# Miniserver konfig auslesen
#print "\n".substr($MINISERVER, 10, length($MINISERVER))."\n";
$i = substr($MINISERVER, 10, length($MINISERVER));
$LOX_Name = $miniservers{$i}{Name};
$LOX_IP = $miniservers{$i}{IPAddress};
$LOX_User = $miniservers{$i}{Admin};
$LOX_PW = $miniservers{$i}{Pass};

#print "Miniserver\@".$LOX_Name."<br>";
#print $LOX_IP."<br>";
#print $LOX_User."<br>";
#print $LOX_PW."<br>";

# Mit dieser Konstruktion lesen wir uns alle POST-Parameter in den Namespace R.
my $cgi = CGI->new;
$cgi->import_names('R');
# Ab jetzt kann beispielsweise ein POST-Parameter 'form' ausgelesen werden mit $R::form.


# Create my logging object
my $log = LoxBerry::Log->new ( 
	name => 'cronjob',
	filename => "$lbplogdir/magichome_status.log",
	append => 1
	);
LOGSTART "MagicHome status start";

my $filename = 'status.log';
system ("echo leer>status.log");

# POST request
$MagicHome_IP = $R::ip;
# $MagicHome_IP = "172.16.200.79";

# Wenn keine POST, dann alle Magic Home Controller abfragen
if($MagicHome_IP==""){
	# Magic Home Status IP 
	LOGDEB "python magichome.py -sSi";
	system ("python magichome.py  -sSi>$filename 2>&1");
} else {
	# Magic Home Status IP 
	LOGDEB "python magichome.py $MagicHome_IP -i";
	system ("python magichome.py $MagicHome_IP  -i>$filename 2>&1");
}

# open file
open(my $fh, '<:encoding(UTF-8)', $filename)
	or die "Could not open file '$filename' $!";

# Ausgabe aller Magic Home Device	
while (my $row = <$fh>) {
  chomp $row;
  # print "$row<br>"; 
  
  if(index($row,"Err")!=-1){
	print "ERROR<br>";
	LOGERR "$row";
  } elsif(index($row,"timed")!=-1){
	print "TIMEOUT<br>";
	LOGERR "$row";
  } elsif(index($row,"raw state")!=-1){
	# print "STATUS<br>";
	LOGDEB "$row";
	
	my @splitestate = split('raw state:', $row);
	
	my @splitestate1 = split('\[', $splitestate[0]);
	#print "$splitestate1[1]<br>";
	my @splitestate2 = split('\]', $splitestate1[1]);
	$IP=$splitestate2[0];
	print "<b>IP\@$IP</b><br>";
	
	$rawdata = $splitestate[1];
	chop($rawdata);
	#print "$rawdata<br>";

	my @splitestate = split(',', $rawdata);
		
	if($splitestate[0]==0x81){
		# response from a 5-channel LEDENET controller:
        #pos  0  1  2  3  4  5  6  7  8  9 10 11 12 13
        #    81 25 23 61 21 06 38 05 06 f9 01 00 0f 9d
        #     |  |  |  |  |  |  |  |  |  |  |  |  |  |
        #     |  |  |  |  |  |  |  |  |  |  |  |  |  checksum
        #     |  |  |  |  |  |  |  |  |  |  |  |  color mode (f0 colors were set, 0f whites, 00 all were set)
        #     |  |  |  |  |  |  |  |  |  |  |  cold-white
        #     |  |  |  |  |  |  |  |  |  |  <don't know yet>
        #     |  |  |  |  |  |  |  |  |  warmwhite
        #     |  |  |  |  |  |  |  |  blue
        #     |  |  |  |  |  |  |  green
        #     |  |  |  |  |  |  red
        #     |  |  |  |  |  speed: 0f = highest f0 is lowest
        #     |  |  |  |  <don't know yet>
        #     |  |  |  preset pattern
        #     |  |  off(24)/on(23)
        #     |  type
        #     msg head
        #
		if($splitestate[2]==0x24) {
			print "Light\@0<br>";}
		elsif ($splitestate[2]==0x23) {
			print "Light\@1<br>";}
		else {
			print "Light\@0<br>";}
		$pattern = $splitestate[3]-36;
		if($pattern=>60) {$pattern=0;}
		print "Pattern\@$pattern<br>";
		print "Speed\@$splitestate[5]<br>";
		$red = $splitestate[6];
		$green = $splitestate[7];
		$blue = $splitestate[8];
		print "Red\@$red<br>";
		print "Green\@$green<br>";
		print "Blue\@$blue<br>";
		$redp = int($red/2.55);
		$greenp = int((int($green/2.55))*1000);
		$bluep = int((int($blue/2.55))*1000000);
		$rgb = $bluep+$greenp+$redp;
		print "RGB\@$rgb<br>";
		print "Warmwhite\@$splitestate[9]<br>";
		print "Coldwhite\@$splitestate[11]<br>";
	}        	
	elsif($splitestate[0]==0x66){
	# typical response:
        #pos  0  1  2  3  4  5  6  7  8  9 10
        #    66 01 24 39 21 0a ff 00 00 01 99
        #     |  |  |  |  |  |  |  |  |  |  |
        #     |  |  |  |  |  |  |  |  |  |  checksum
        #     |  |  |  |  |  |  |  |  |  warmwhite
        #     |  |  |  |  |  |  |  |  blue
        #     |  |  |  |  |  |  |  green 
        #     |  |  |  |  |  |  red
        #     |  |  |  |  |  speed: 0f = highest f0 is lowest
        #     |  |  |  |  <don't know yet>
        #     |  |  |  preset pattern             
        #     |  |  off(24)/on(23)
        #     |  type
        #     msg head
        #
		if($splitestate[2]==0x24) {
			print "Light\@0<br>";}
		elsif ($splitestate[2]==0x25) {
			print "Light\@1<br>";}
		else {
			print "Light\@0<br>";}
		$pattern = $splitestate[3]-36;
		if($pattern=>60) {$pattern=0;}
		print "Pattern\@$pattern<br>";
		print "Speed\@$splitestate[5]<br>";
		$red = $splitestate[6];
		$green = $splitestate[7];
		$blue = $splitestate[8];
		print "Red\@$red<br>";
		print "Green\@$green<br>";
		print "Blue\@$blue<br>";
		$redp = int($red/2.55);
		$greenp = int((int($green/2.55))*1000);
		$bluep = int((int($blue/2.55))*1000000);
		$rgb = $bluep+$greenp+$redp;
		print "RGB\@$rgb<br>";
		print "Warmwhite\@$splitestate[9]<br>";
	} else {
		# Fehler, Type nicht bekannt!
		LOGERR "Request unbekannt";
		LOGERR "Rawdate :$rawdata";
		print "ERROR<br>";
		print "Light\@0<br>";
		print "Pattern\@0<br>";
		print "Speed\@0<br>";
		print "Red\@0<br>";
		print "Green\@0<br>";
		print "Blue\@0<br>";
		print "RGB\@000000000<br>";
		print "Warmwhite\@0<br>";
		}
  } else {
	print "ERROR<br>";
	LOGERR "$row";
  } 
}	

	


# We start the log. It will print and store some metadata like time, version numbers
  
# Now we really log, ascending from lowest to highest:
# LOGDEB "This is debugging";                 # Loglevel 7
# LOGINF "Infos in your log";                 # Loglevel 6
# LOGOK "Everything is OK";                   # Loglevel 5
# LOGWARN "Hmmm, seems to be a Warning";      # Loglevel 4
# LOGERR "Error, that's not good";            # Loglevel 3
# LOGCRIT "Critical, no fun";                 # Loglevel 2
# LOGALERT "Alert, ring ring!";               # Loglevel 1
# LOGEMERGE "Emergency, for really really hard issues";   # Loglevel 0
  
LOGEND "Operation finished sucessfully.";
