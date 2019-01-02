#!/usr/bin/perl

# Einbinden von Module
use IO::Socket;
use IO::Socket::Timeout;
use strict;
use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;

# Konfig auslesen
my %pcfg;
tie %pcfg, "Config::Simple", "$lbpconfigdir/pluginconfig.cfg";
my $UDP_Port = %pcfg{'MAIN.LB_UDP_Port'};
my $UDP_Port2 = $UDP_Port+1;
my $autostart = $pcfg{'MAIN.autostart'};

my $socket;
my $sock;
my $recieved_data;
my $peer_address;
my $peer_port;
my $peeraddress;
my $peerport;


#UDP Listener PORT
$socket = new IO::Socket::INET (
LocalPort => $UDP_Port2,
Proto => 'udp'
) or die "Could not create socket: $!\n";
IO::Socket::Timeout->enable_timeouts_on($socket);

#UDP Sender PORT
$sock = IO::Socket::INET->new(
    Proto    => 'udp',
    PeerPort => $UDP_Port,
    PeerAddr => '127.0.0.1',
) or die "Could not create socket: $!\n";

$sock->send('WATCHDOG') or die "Send error: $!\n";


#Timeout 10s recevie data
eval {
  local $SIG{ALRM} = sub { die 'Timed Out'; };
  alarm 10;
  $socket->recv($recieved_data,1024);
  print "\nReceived data $recieved_data \n \n";
  
  $pcfg{'MAIN.UDP_Server_runnig'} = 1;
  tied(%pcfg)->write();
  exit;
  alarm 0;
};
# alarm 0;

# AUTOSTART nach einem neustart oder abstutz!
# Start Deamen neu und prüfe noch einmal.
if($autostart == 1){
	LOGERR "Autostart";
	system ("perl '$lbpbindir/magichome-control.pl' start &");

	$sock->send('WATCHDOG') or die "Send error: $!\n";


	#Timeout 10s recevie data
	eval {
	  local $SIG{ALRM} = sub { die 'Timed Out'; };
	  alarm 10;
	  $socket->recv($recieved_data,1024);
	  print "\nReceived data $recieved_data \n \n";
	  
	  $pcfg{'MAIN.UDP_Server_runnig'} = 1;
	  tied(%pcfg)->write();
	  exit;
	  alarm 0;
	};
}
alarm 0;

print "ALARM!!!  UDP-Deamen not work.\n";
$pcfg{'MAIN.UDP_Server_runnig'} = 0;
tied(%pcfg)->write();