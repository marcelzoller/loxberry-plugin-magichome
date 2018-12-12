#!/usr/bin/perl


##########################################################################
# LoxBerry-Module
##########################################################################
use CGI;
use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;
  
# Die Version des Plugins wird direkt aus der Plugin-Datenbank gelesen.
my $version = LoxBerry::System::pluginversion();

# Loxone Miniserver Select Liste Variable
our $MSselectlist;

# Mit dieser Konstruktion lesen wir uns alle POST-Parameter in den Namespace R.
my $cgi = CGI->new;
$cgi->import_names('R');
# Ab jetzt kann beispielsweise ein POST-Parameter 'form' ausgelesen werden mit $R::form.

# Create my logging object
my $log = LoxBerry::Log->new ( 
	name => 'HTTP Settup',
	filename => "$lbplogdir/magichome.log",
	append => 1
	);
LOGSTART "Magic Home htmlauth start";
 
 
# Wir Übergeben die Titelzeile (mit Versionsnummer), einen Link ins Wiki und das Hilfe-Template.
# Um die Sprache der Hilfe brauchen wir uns im Code nicht weiter zu kümmern.
LoxBerry::Web::lbheader("Magic Home WiFi Plugin V$version", "http://www.loxwiki.eu/MagicHome/Zoller", "help.html");
  
# Wir holen uns die Plugin-Config in den Hash %pcfg. Damit kannst du die Parameter mit $pcfg{'Section.Label'} direkt auslesen.
my %pcfg;
tie %pcfg, "Config::Simple", "$lbpconfigdir/pluginconfig.cfg";

# Alle Miniserver aus Loxberry config auslesen
%miniservers = LoxBerry::System::get_miniservers();

 

# Wir initialisieren unser Template. Der Pfad zum Templateverzeichnis steht in der globalen Variable $lbptemplatedir.

my $template = HTML::Template->new(
    filename => "$lbptemplatedir/index.html",
    global_vars => 1,
    loop_context_vars => 1,
    die_on_bad_params => 0,
	associate => $cgi,
);
  

# Sprachdatei laden
my %L = LoxBerry::Web::readlanguage($template, "language.ini");
  


##########################################################################
# Process form data
##########################################################################
if ($cgi->param("save")) {
	# Data were posted - save 
	&save;
}

$R::stop if 0; # Prevent errors
if ( $R::stop ) 
{
	&stop;
}
R::start if 0; # Prevent errors
if ( $R::start ) 
{
	&start;
}
R::restart if 0; # Prevent errors
if ( $R::restart ) 
{
	&restart;
}
R::reset if 0; # Prevent errors
if ( $R::reset ) 
{
	&reset;
}	

	

# print "LB UDP Port: " . %pcfg{'MAIN.LB_UDP_Port'} . "</i><br>\n";
my $LB_UDP = %pcfg{'MAIN.LB_UDP_Port'};
my $miniserver = %pcfg{'MAIN.MINISERVER'};
my $SERVICE = %pcfg{'MAIN.UDP_Server_runnig'};
# my $UDPPORT = %pcfg{'MAIN.UDP_Port'};
my $AUTOSTART = %pcfg{'MAIN.autostart'};
# my $UDPSENDINTER = %pcfg{'MAIN.UDP_SEND_Intervall'};
my $SETCLOCK = %pcfg{'MAIN.setclock'};
# my $HTTPSENDINTER = %pcfg{'MAIN.HTTP_TEXT_SEND_Intervall'};



%miniservers = LoxBerry::System::get_miniservers();
#print "Anzahl deiner Miniserver: " . keys(%miniservers);

##########################################################################
# Fill Miniserver selection dropdown
##########################################################################
for (my $i = 1; $i <=  keys(%miniservers);$i++) {
	if ("MINISERVER$i" eq $miniserver) {
		$MSselectlist .= '<option selected value="'.$i.'">'.$miniservers{$i}{Name}."</option>\n";
	} else {
		$MSselectlist .= '<option value="'.$i.'">'.$miniservers{$i}{Name}."</option>\n";
	}
}

$template->param( LB_UDP => $LB_UDP);
$template->param( LOXLIST => $MSselectlist);
#$template->param( LOGDATEI => "/admin/system/tools/logfile.cgi?logfile=plugins/$lbpplugindir/magichome.log&header=html&format=template");
$template->param( UDP_MONITOR => "/admin/system/tools/logfile.cgi?logfile=plugins/$lbpplugindir/magichome_udpMonitor.log&header=html&format=template");
# $template->param( UDPPORT => $UDPPORT);
# $template->param( WEBSITE => "http://$ENV{HTTP_HOST}/plugins/$lbpplugindir/index.cgi");
# $template->param( PNAME => "Magic Home");
# $template->param( LBIP => "172.16.200.66");

if ($SERVICE == 1) {
	$template->param( SERVER => '<span style="color:green">running</span>');
	} 
elsif ($SERVICE == 0) {
	$template->param( SERVER => '<span style="color:red">stop</span>');
	} 
else  {
	$template->param( SERVER => '<span style="color:red">stop</span>');
	}
	
if ($AUTOSTART == 1) {
		$template->param( AUTOSTART => "checked");
		$template->param( AUTOSTARTYES => "selected");
		$template->param( AUTOSTARTNO => "");
	} else {
		$template->param( AUTOSTART => " ");
		$template->param( AUTOSTARTYES => "");
		$template->param( AUTOSTARTNO => "selected");
	} 
if ($SETCLOCK == 1) {
		$template->param( SETCLOCK => "checked");
		$template->param( SETCLOCKYES => "selected");
		$template->param( SETCLOCKNO => "");
	} else {
		$template->param( SETCLOCK => " ");
		$template->param( SETCLOCKYES => "");
		$template->param( SETCLOCKNO => "selected");
	} 

  
 
  
# Nun wird das Template ausgegeben.
print $template->output();
  
# Schlussendlich lassen wir noch den Footer ausgeben.
LoxBerry::Web::lbfooter();

LOGEND "MagicHome Setting finish.";

##########################################################################
# Save data
##########################################################################
sub save 
{

	# We import all variables to the R (=result) namespace
	$cgi->import_names('R');
	
	LOGDEB "UDP Port: $R::UDP_Port";
	LOGDEB "LX Miniserver: $R::miniserver";
	

	if ($R::LB_UDP != "") {
			# print "LB_UDP:$R::LB_UDP<br>\n";
			$pcfg{'MAIN.LB_UDP_Port'} = $R::LB_UDP;
		} 
	if ($R::miniserver != "") {
			#print "miniserver:$R::miniserver<br>\n";
			$pcfg{'MAIN.MINISERVER'} = "MINISERVER".$R::miniserver;
		} 
	if ($R::AUTOSTART == "1") {
			LOGDEB "Autostart: $R::AUTOSTART";
			$pcfg{'MAIN.autostart'} = "1";
		} else{
			LOGDEB "Autostart: $R::AUTOSTART";
			$pcfg{'MAIN.autostart'} = "0";
		}
		
	if ($R::SETCLOCK== "1") {
			LOGDEB "SetClock: $R::SETCLOCK";
			$pcfg{'MAIN.setclock'} = "1";
		} else{
			LOGDEB "SetClock: $R::SETCLOCK";
			$pcfg{'MAIN.setclock'} = "0";
		}
	
	tied(%pcfg)->write();
	LOGDEB "Setting: SAVE!!!!";
	#	print "SAVE!!!!";	
	return;
	
}


##########################################################################
# Start Deamen
##########################################################################
sub start 
{
	#print "Start\n";
	LOGDEB "UDP-Server start";
	$pcfg{'MAIN.UDP_Server_runnig'} = 1;
	
	tied(%pcfg)->write();
	#LOGDEB "Setting: SAVE!!!!";
	#	print "SAVE!!!!";	
	
	system ("perl '$lbpbindir/magichome-control.pl' start &");
	
	return;	
}

##########################################################################
# Stop Deamen
##########################################################################
sub stop
{
	#print "Stop\n";
	LOGDEB "UDP-Server stop";
	$pcfg{'MAIN.UDP_Server_runnig'} = 0;
	
	tied(%pcfg)->write();
	#LOGDEB "Setting: SAVE!!!!";
	#	print "SAVE!!!!";	
	
	system ("perl '$lbpbindir/magichome-control.pl' stop &");
	
	return;	
}	

##########################################################################
# RESTART Deamen
##########################################################################
sub restart
{
	#print "Stop\n";
	LOGDEB "UDP-Server restart";
	
	system ("perl '$lbpbindir/magichome-control.pl' restart &");
	
	return;	
}
