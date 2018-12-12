#!/usr/bin/perl

use warnings;
use strict;
use CGI;
use LoxBerry::Log;

our $cgi = CGI->new;
$cgi->import_names('R');

#Übergabeparameter
my $param1 = $ARGV[0];

# Init logfile
my $log = LoxBerry::Log->new ( name => 'Service Control', filename => "$lbplogdir/magichome_service_control.log", stdout => 0, addtime => 0 );
LOGSTART "Magic Home Controller";

my %pcfg;
tie %pcfg, "Config::Simple", "$lbpconfigdir/pluginconfig.cfg";
 


if ( $param1 eq 'stop') {
	#print "STOP\n>";
	LOGINF "Service STOP";
	killhost();
	
	# Save Config
	$pcfg{'MAIN.UDP_Server_runnig'} = 0;
	
	tied(%pcfg)->write();
	LOGDEB "Setting: SAVE!!!!";
	exit(0);
}
if ( $param1 eq 'start') {
	#print "Start\n";
	LOGINF "Service START";
	killhost();
	starthost();
	
	# Save Config
	$pcfg{'MAIN.UDP_Server_runnig'} = 1;
	
	tied(%pcfg)->write();
	LOGDEB "Setting: SAVE!!!!";
	
	exit(0);
}

if ( $param1 eq 'restart') {
	#print "Restart\n";
	LOGINF "Service RESTART";
	killhost();
	# Save Config
	$pcfg{'MAIN.UDP_Server_runnig'} = 0;
	
	tied(%pcfg)->write();
	LOGDEB "Setting: SAVE!!!!";
	
	starthost();
	# Save Config
	$pcfg{'MAIN.UDP_Server_runnig'} = 1;
	
	tied(%pcfg)->write();
	LOGDEB "Setting: SAVE!!!!";
	exit(0);
}

#killhost();
#starthost();


sub starthost
{
	#system ("su - loxberry -c \'$lbpbindir/udpMonitor.pl\' > /dev/null 2>&1 &");
	system ("perl '$lbpbindir/udpMonitor.pl\' > /dev/null 2>&1 &");
	#print "perl '$lbpbindir/udoMonitor.pl\' > /dev/null 2>&1 &";
	LOGDEB "perl '$lbpbindir/udpMonitor.pl\' > /dev/null 2>&1 &";
}

sub killhost
{
	my @output = qx { pkill -f "udpMonitor.pl" };
	#print "@output";
	LOGDEB "@output";
}