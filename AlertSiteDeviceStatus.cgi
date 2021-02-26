#!/usr/bin/perl
use strict;
use HTTP::Request::Common;
use LWP::UserAgent;
use warnings;
use Data::Dumper;

my $REST_SERVER = 'https://www.alertsite.com/restapi';  # Base path
my $LOGIN = 'pearl.caller@wolfshac.com';                      # AlertSite account login
my $PASSWORD = 'Password456';                            # AlertSite account password
my $ua = LWP::UserAgent->new;
$ua->agent('AlertSite REST Client/1.0');
my ($POST_XML, $req, $resp, $cookie, $session, $OBJCUST, $DEVICE);
my $POST_XML_LOGIN = << "POST_XML_LOGIN";  # Request body
<Login> <Login>$LOGIN</Login> <Password>$PASSWORD</Password> </Login>

POST_XML_LOGIN

$req = HTTP::Request->new(POST => "$REST_SERVER/user/login");
$req->content_type('text/xml');
$req->content($POST_XML_LOGIN);

print "Content-type: text/html\n\n";
print "<html><head>\n";
print "</head><body>\n";

$resp = $ua->request($req);            # Send request
$cookie = $resp->header('Set-Cookie'); # Save cookie

($session) = $resp->content =~ m|<SessionID>(\w+)</SessionID>|;
($OBJCUST) = $resp->content =~ m|<ObjCust>(\w+)</ObjCust>|;

my $POST_XML = << "POST_XML";             # Request body
<List>
   <TxnHeader>
      <Request>
          <Login>_LOGIN_</Login>
          <SessionID>_SESSION_</SessionID> </Request>
   </TxnHeader>
   <Source></Source>
</List>
POST_XML

# Set Login and Session ID from login request response

$POST_XML =~ s/_LOGIN_/$LOGIN/;
$POST_XML =~ s/_SESSION_/$session/;

# Set up HTTP request to list devices and include the cookie from login.
# Use text/xml and raw POST data to conform to existing REST API.

$req = HTTP::Request->new(POST => "$REST_SERVER/devices/list");
$req->header(Cookie => $cookie);
$req->content_type('text/xml');
$req->content($POST_XML);

$resp = $ua->request($req);
$DEVICE = 606458;                           # Device ID from List Device run
$POST_XML = << "POST_XML";                 # Request body
<Status>
   <TxnHeader>
      <Request>
          <Login>_LOGIN_</Login>
          <SessionID>_SESSION_</SessionID>
          <ObjCust>_OBJCUST_</ObjCust>
          <ObjDevice>_OBJDEVICE_</ObjDevice>
      </Request>
   </TxnHeader>
   <Source></Source>
</Status>
POST_XML

# Set Login and Session ID from login request response
# Set Customer Object ID and Device ID from list request response

$POST_XML =~ s/_LOGIN_/$LOGIN/;
$POST_XML =~ s/_SESSION_/$session/;
$POST_XML =~ s/_OBJCUST_/$OBJCUST/;
$POST_XML =~ s/_OBJDEVICE_/$DEVICE/;

# Set up HTTP request to list devices and include the cookie from login.
# Use text/xml and raw POST data to conform to existing REST API.

$req = HTTP::Request->new(POST => "$REST_SERVER/devices/status");
$req->header(Cookie => $cookie);
$req->content_type('text/xml');
$req->content($POST_XML);

$resp = $ua->request($req);
my $newstr = $resp->as_string;

$newstr =~ s/%20/\ /ig;
$newstr =~ s/<\//\&/ig;
$newstr =~ s/</|/ig;
$newstr =~ s/>/=/ig;

my @NewArray = split /\&/, $newstr;
my $Cntr=0;
my $InCnt=0;
my $MyLocNum;
my $MyCurCode;
my $CurLocation;
my $CurLocName;
my $CurStatus;
my @BigFatArray;

foreach my $newLine (@NewArray) {
    my @InnerArray = split /\|/, $newLine;
    my @SepInArray = split /\=/, $InnerArray[1];
    if (($SepInArray[1] ne "") && ($Cntr > 10) && ($SepInArray[0] ne "Device")) {
        if ($SepInArray[0] eq "ObjLocation") {
            $CurLocation = $SepInArray[1];
        } elsif ($SepInArray[0] eq "Location") {
            $CurLocName = $SepInArray[1];
        } elsif ($SepInArray[0] eq "LastStatusCode") {
            $CurStatus = $SepInArray[1];
        } elsif ($SepInArray[0] eq "DtLastStatus") {
            $BigFatArray[$InCnt] = $CurLocName . "|" . $CurLocation . "|" . $CurStatus . "|" . $SepInArray[1];
            $InCnt+=1;
        }
    }
    $Cntr+=1;
}
print "Array Format: <b>Location_Name</b> | <b>Location_Number</b> | <b>Current_Status</b> | <b>Last_Checked</b><p>";
print "<table border=1><tr><td><b>Location<td align=right><b>Loc ID<td align=right><b>Status<td align=right><b>Last Checked\n";
foreach my $Entry (@BigFatArray) {
    my @InnerListArray = split /\|/, $Entry;
    if ($InnerListArray[2] eq "0") {
       print "<tr><td><font color=green>" . $InnerListArray[0] . "<td align=right>" . $InnerListArray[1] . "<td align=right><font color=green>";
    } else {
       print "<tr><td><font color=red><b>" . $InnerListArray[0] . "<td align=right>" . $InnerListArray[1] . "<td align=right><font color=red><b>";
    }
    print $InnerListArray[2] . "<td>" . $InnerListArray[3];
}
print "</table></body><p>\n";

print "<script src=\"src/index.js\"></script>\n";

print "</html>\n";

