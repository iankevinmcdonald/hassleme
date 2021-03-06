#!/usr/bin/perl -w -I../perllib -I../commonlib/perllib
#
# hassleme.cgi:
# Website for hassleme.
#
# Copyright (c) 2005 Chris Lightfoot. All rights reserved.
# Email: chris@ex-parrot.com; WWW: http://www.ex-parrot.com/~chris/
#

use strict;

use CGI qw(-no_xhtml);
use mySociety::CGIFast;
use Data::Dumper;
use HTML::Entities qw(encode_entities);
use IO::Pipe;
use HTML::Entities;
use Net::DNS;
use FindBin;

use Hassle;
use mySociety::Config;

BEGIN {
    mySociety::Config::set_file("$FindBin::Bin/../conf/general");
}

sub _ {
    # TODO - this is the function that will become the stub function for il18n and l10n
    return @_;
}

sub hassle_header {
    my ($q, $title) = @_;
    my $fn = lc($q->param('fn'));
    $fn ||= 'home';
    my $header_title = "HassleMe";
    if ($title) {
        $header_title .= " - $title";
    }
    print
        $q->header(-type => 'text/html; charset=utf-8'),
        $q->start_html(-title=>$header_title,
                       -style=>{-src=>'/hassleme.css'},
#                       -script=>{-language=>'JAVASCRIPT',
#                                 -src=>'yellowFade.js'}
                       );

    my $staging = mySociety::Config::get('HM_STAGING') ? 1 : 0;
    if ($staging) {
        print $q->div( { style=>'background-color: red; text-align: center; padding: 1em; color: white;' },
            "This is a test site for developers only, you want",
            $q->a({href=>'http://www.hassleme.co.uk'}, "www.hassleme.co.uk")
        );
    }

    print $q->h1($q->a({href=>'/'},"HassleMe"),
#                 $q->span({-id=>'betaTest'},
#                        'Beta Test'),
                 $q->span({-id=>'slogan'},
                          _("Because sometimes in life,<br>you just need to be nagged...")),
                 );
    print _('<div id="w"><div id="content">');
    if ($title) {
        print $q->h2($title);
    }
}

sub hassle_intro {
    print <<EOF;
<div id="intro">
<p><strong>Not eating enough fruit?</strong> Forgot to feed the fish again?
Need a little help keeping your New Year's resolutions? <br>Tell us what to
hassle you about, and we'll nag you via email at <strong>semi-unpredictable intervals</strong>.
<br>HassleMe is unique because you <strong>never quite know</strong> when your
reminder will come along.</p>
</div>
EOF
}

sub hassle_form {
    my ($q) = @_;

    $q->delete('fn');

    print $q->div({id=>'createHassleBox'},
              $q->start_form(-name => 'createHassleForm',
                             -action => '/',    # XXX
                             -method => 'POST',
                             -enctype => 'application/x-www-form-urlencoded',
                             -accept_charset => 'UTF-8'),
              $q->hidden(-name => 'fn',
                         -value => 'home'),
              $q->hidden(-name => 'f'),
              $q->h2('Set up a hassle now!'),
              $q->p(
                    'Hassle me <b>roughly</b> every ',
                    $q->textfield(-name => 'freq', -size => 3),
#                    $q->popup_menu(-name => 'units',
#                                   -values => ['days','hours','minutes']),
#                        $q->br(),
#                    ', reminding me to:',
                    'days, reminding me to:',
                    $q->textarea(
                                 -style => 'width: 25em;',
                                 -name => 'what', -cols => 25, -rows => 3),
                    ),
              $q->p(
                    'Send the emails to: ',
                    $q->textfield(-name => 'email', -size => 25),
                    ),
              $q->ul(
                    $q->li("We'll send you a confirmation email when you sign up."),
                    $q->li("If you add more than one email address (separated by commas or semicolons) we'll pick one person at random for each hassle &mdash; good for offices!"),
                    ),
              $q->p(
                    'Can we make the text of this hassle <a href="/hassles">publicly visible</a>?',
                    $q->br(),
                    $q->radio_group(-name=>'public',
                                    -values=>['true','false'],
                                    -default=>'false',
                                    -labels=>{'true'=>'Yes','false'=>'No'}),
                    ),
              $q->submit(-value => 'Set up this hassle now >>'),
              $q->end_form(),
              );

    hassle_recent($q);
}

sub hassle_recent {
    my ($q) = @_;

        print <<EOF;
<div id="exampleHasslesBox">
<h2>Example Hassles</h2>
<ul>
<li><b>Go to the gym</b> roughly every 4 days</li>
<li><b>Write an entry in my diary</b> roughly every 3 days</li>
<li><b>Call your mother</b> roughly every 7 days</li>
<li><b>Go to the theatre</b> roughly every 21 days</li>
<li><b>Spend 5 hours doing something for <a href="http://www.mysociety.org/helpus/">mySociety</a></b> roughly every 28 days</li>
<li><b>Practice the piano</b> roughly every 3 days</li>
<li><b>Go for a walk in the park</b> roughly every 10 days</li>
</ul>
<p align="right"><a href="/hassles">Read lots of hassles</a></p>
<!--
<h2>Recently on HassleMe</h2>
<ul>People asked to be sent these hassles:
<li><a href="/hassleme.cgi?fn=home&f=1&freq=14&what=Go+to+the+theatre&public=false&email=">Go to the theatre every 14 days</a></li>
<li><a href="/hassleme.cgi?fn=home&f=1&freq=4&what=Go+to+the+gym&public=false&email=">Go to the gym every 4 days</a></li>
<li><a href="/hassleme.cgi?fn=home&f=1&freq=7&what=Call+your+mother&public=false&email=">Call your mother every 7 days</a></li>
</ul>
-->
</div>

<!--
<div id="news">
<h2>Upcoming Features</h2>
<ul>
<li>Get hassled via <acronym title="Instant Messaging services like AIM, ICQ, MSN Messenger, Jabber, Google Talk">IM</acronym>.</li>
<li>Specify time in hours, days, weeks and months.</li>
<li>Translation into other languages.</li>
<li>Other cool stuff!</li>
</ul>
</div>
-->

EOF

}

sub hassle_footer {
    my ($q) = @_;
    print <<EOF;

</div></div>

<p id="footer">
<a href="http://digg.com/software/HassleMe_nags_you_because_your_mother_can_t_do_everything">Digg this!</a> |
<a href="/faq">FAQ</a> |
<a href="/privacy">Privacy and cookies</a> |
Derived from <a href="http://www.mysociety.org/2005/03/17/the-management-power-of-evil/">Hasslebot</a>, a
<a href="http://www.mysociety.org/">mySociety</a> tool that reminds us to post
things on our <a href="http://www.mysociety.org/blog/">blog</a><br>
</p>

EOF

    if ($ENV{'SERVER_NAME'} eq 'www.hassleme.co.uk') {
        print <<EOF;
           <!-- Google Analytics -->
           <script type="text/javascript">

             var _gaq = _gaq || [];
             _gaq.push(['_setAccount', 'UA-660910-8']);
             _gaq.push (['_gat._anonymizeIp']);
             _gaq.push(['_trackPageview']);

             (function() {
               var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
               ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
               var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
             })();

           </script>
            <!-- End Google Analytics Tag -->
EOF
    }

    print $q->end_html();
}

while (my $q = new mySociety::CGIFast()) {
#    $q->autoEscape(0);
    my $fn = lc($q->param('fn'));
    $fn ||= 'home';
    my %fns = map { $_ => 1 } qw(home confirm unsubscribe faq hassles privacy);
    $fn = 'home' if (!exists($fns{$fn}));

    my $created = undef;

    if ($fn eq 'home') {
        my $emails = $q->param('email');
        my $freq = $q->param('freq');
        my $units = $q->param('units');
        my $what = $q->param('what');
        my $public = lc($q->param('public'));

        my @errors = ( );

        if ($q->param('f')) {
            if (!defined($freq) || $freq eq '') {
                push(@errors, "Please tell us how often you want to be hassled");
            } elsif ($freq !~ /^[1-9]\d*$/) {
                push(@errors, "Number of days should be a number, like '7'");
            } elsif ($freq > 3650) {
                push(@errors, "Surely you want to be hassled more than once every ten years?");
            }

            if (defined($public)) {
                if ($public ne 'true' && $public ne 'false') {
                    push(@errors, "Marking a hassle publicly visible should be either 'true' or 'false'.");
                }
            } else {
                $public = 'false';
            }

            if (!defined($what) || $what =~ /^\s*$/) {
                push(@errors, 'Please tell us what you want to be hassled about');
            }

#            if (!defined($units) || $units eq '') {
#                push(@errors, "Please select hours or days");
#            } elsif ($units !~ /(days|hours)/) {
#                push(@errors, "Sorry, you can only specify hours or days");
#            }

            my @emails;
            if (!$emails) {
                push(@errors, "Please enter an email address or addresses");
            } else {
                $emails =~ s/\s//mg;
                my %e;
                @emails = grep { ++$e{$_}; $e{$_} == 1 } split('[,;]', $emails);
                push(@errors, grep { defined($_) } map { Hassle::is_valid_email($_) } @emails);
            }

            if (!@errors) {
                # Actually create it.
                my $hassle_id = dbh()->selectrow_array("select nextval('hassle_id_seq')");

                # TODO - funky arithmetic to modify the frequency
                # depending on unit of time used (days = no change,
                # hours, weeks, etc = change).

                # strip out newlines in $what or emails get borked Subject: lines

                $what =~ s/[\r\n]+/ /g;

                # remove the capacity for spammers to put vast
                # quantities of text in a hassle

                my $what_preview = $what;
                my $preview_length = 512;
                if (length($what) > $preview_length) {
                    $what_preview = substr($what_preview, 0, $preview_length - 3) . '...';
                }

                my $t0 = time();
                dbh()->do('
                        insert into hassle (id, frequency, what, public, ipaddr)
                        values (?, ?, ?, ?, ?)', {},
                        $hassle_id, $freq, $what, $public, $q->remote_host());

                my @printable_emails = map { encode_entities($_) } @emails;
                foreach my $email (@emails) {
                    my $recipient_id = dbh()->selectrow_array("select nextval('recipient_id_seq')");
                    dbh()->do('
                              insert into recipient (id, hassle_id, email)
                              values (?, ?, ?)', {},
                              $recipient_id, $hassle_id, $email);
                    dbh()->commit();

                    my $confirmurl = mySociety::Config::get('WEBURL') . "/C/" . token($recipient_id);

                    my $t1 = time();
                    my $result = sendmail($email, "Please confirm you want to be hassled to \"$what_preview\"",
                             <<EOF,

Hello,

Someone (hopefully you) has asked for this email address to be hassled roughly every $freq days to:

$what_preview

If you want to be hassled about this, please click on the link below:
    $confirmurl

If your email program does not let you click on this link, just copy and paste it into your web browser and hit return.

If you have changed your mind and don't want us to nag you, then do nothing - your message will expire and be deleted.

Any other questions? Please email team\@hassleme.co.uk and we'll get back to you as soon as we can.

Thanks!

--The HassleMe Team

EOF
                            );
                    my $dt = time() - $t1;
                    warn "sending email to <$email> about hassle #$hassle_id took ${dt}s"
                        if ($dt > 30);
                    if ($result == mySociety::EmailUtil::EMAIL_SUCCESS) {
                        ;
                    } elsif ($result == mySociety::EmailUtil::EMAIL_SOFT_ERROR) {
                        push @errors, "Your email to $email didn't work, but it looks like it might be worth trying again later ('soft error').";
                    } else {
                        push @errors, "The email computers say that they cannot pass on a message to $email - are you sure this is the right address? ('hard error')";
                    }
                }

                my $dt = time() - $t0;
                warn "creating hassle #$hassle_id took ${dt}s"
                    if ($dt > 30);

                $q->delete('what','freq','public');

                $created = 1;
                my $printable_emails = join(', ',@printable_emails);

                my $singular_or_plural = (@printable_emails == 1
                                          ? 'a confirmation email'
                                          : 'confirmation emails');

                hassle_header($q,'Now check your email!');
                print $q->div({-id=>'message'},
                            $q->ul(
                                   $q->li("We've sent $singular_or_plural to <em>$printable_emails</em>; you'll need to click on the link in the email before we can hassle you."),
                                   $q->li("If you're using <acronym title='Web-based email systems like Oddpost, Gmail, MSN Hotmail, or Yahoo! Mail'>webmail</acronym>, you might want to check your <em>Spam</em>, <em>Junk</em> or <em>Bulk Mail</em> folders."),
                                   $q->li("<strong>Since you're here, why not set up another hassle (or two)?</strong>")));
            }
        } else {
            hassle_header($q);
        }

        $q->param('f', 1);

        if (@errors) {
            hassle_header($q);
            print $q->h3("Sorry, that didn't work."),
                  $q->ul({-id=>'errors'},
                    $q->li([
                            map { encode_entities($_) } @errors
                        ])
                    );
        }
        unless ($created || @errors) {
            hassle_intro();
        }

        if ($created) {
            print '<p><a href="/">Set up another hassle</a>.</p>';
        } else {
            hassle_form($q);
        }

    } elsif ($fn eq 'confirm') {
        my $token = $q->param('token');
        my $id = check_token($token);
        if (defined($id)) {
            dbh()->do('update recipient set confirmed = true where id = ?',
                        {}, $id);
            dbh()->commit();
            hassle_header($q,'Confirmed!');
            print <<EOF;
<div id="donatemessage">
<p>
Well done - we'll now hassle you as per your request.
</p>
<p>
If you like this service, <a href="http://www.mysociety.org/donate/">please donate</a>!
</p>
<p><a href="http://www.mysociety.org/donate/"><img src="/waving.jpg" alt=""></a></p>
<p>
We're a registered non-profit running in the UK, and we need your help
to run services like this. For more info see
<a href="http://www.mysociety.org">http://www.mysociety.org</a>.
</p>
</div>
<p>
<a href="/">Set up another hassle</a>
</p>
EOF
        } else {
                hassle_header($q,'Oops!');
                print $q->p({-id=>'errors'},
                            "Sorry. We couldn't understand the link you've followed."
                            );
                hassle_form($q);
        }
    } elsif ($fn eq 'unsubscribe') {
        my $token = $q->param('token');
        my $id = check_token($token);
        if (defined($id)) {
            dbh()->do('delete from recipient where id = ?',
                        {}, $id);
            dbh()->commit();
            hassle_header($q,'Stopped!');
            print $q->div({-id=>'donatemessage'},
                    <<EOF
                    <p>Thanks! We'll stop hassling you about that, starting now.</p>

                    <p>If HassleMe has been useful to you, please donate to the non-profit
                    which runs it.</p>

                    <p><a href="http://www.mysociety.org/donate">Donate</a>.</p>
EOF
                );
        } else {
            hassle_header($q,'Oops!');
            print $q->p({-id=>'errors'},
                    "Sorry. We couldn't understand the link you've followed."
                );
        }
        hassle_form($q);
    } elsif ($fn eq 'hassles') {
        my $longest = $q->param('longest') ? 1 : 0;

        if ($longest) {
            hassle_header($q, 'Longest hassles');
        } else {
            hassle_header($q,'Publicly visible hassles');
        }

        if ($longest) {
            print <<EOF;
            <div id="message">
                <p>Below are 100 things which users of HassleMe have asked to be unpredictably
                reminded of. You may like to see instead <a href="/hassles">100 random hassles</a>.
                <p><a href="/">Set up your own hassle!</a></p>
            </div>
EOF
            } else {
            print <<EOF;
            <div id="message">
                <p>Below are 100 things which users of HassleMe have asked to be unpredictably
                reminded of. <a href="/hassles">Reload the page</a> for another 100.
                <strong>Warning!</strong> There may be strong language within hassles, that's just the way people are. Don't read them if that bothers you.</p>
                <p><a href="/">Set up your own hassle!</a></p>
            </div>
EOF
        }
        my $sth;
        if ($longest) {
            $sth = dbh()->prepare("select what, frequency, whencreated from hassle, recipient where recipient.hassle_id = hassle.id and public and confirmed order by frequency desc limit 100");
        } else {
            $sth = dbh()->prepare("select what, frequency, whencreated from hassle, recipient where recipient.hassle_id = hassle.id and public and confirmed order by random() limit 100");
        }

        $sth->execute;
        print '<table border="0" width="100%"><tr><td width="50%">';
        my $odd = 0;
        my $x = "<b>foo</b>";
        while (my @row = $sth->fetchrow_array) {
            my ($what, $frequency, $whencreated) = @row;
            print "<b>" . CGI::escapeHTML($what) . "</b> roughly every " . $frequency . " " . ($frequency > 1 ? "days" : "day");
            print "</td></tr><tr><td width=\"50%\">" if ($odd);
            print "</td><td width=\"50%\">" if (!$odd);
            print "\n";
            $odd = 1 - $odd;
        }
        print '</td></tr></table>';
        if ($longest) {
            print <<EOF;
            <div id="message">
                <p>You may like to see <a href="/hassles">100 random hassles</a>.
                <p><a href="/">Set up your own hassle!</a></p>
            </div>
EOF
        } else {
        print <<EOF;
            <div id="message">
                <p><a href="/hassles">Reload the page</a> for another 100, or
                see the <a href="/hassles/longest">longest hassles</a>.
                </p>
                <p><a href="/">Set up your own hassle!</a></p>
            </div>
EOF
        }
    } elsif ($fn eq 'faq') {
                hassle_header($q,'Frequently Asked Questions');
                print <<EOF;
<dl>

<dt>Something's not working &mdash; who do I tell?</dt>

<dd>Please email <a
href="mailto:etienne\@mysociety.org">etienne\@mysociety.org</a> with a
short description of what page you were on; what <em>should</em> have
happened; what <em>actually</em> happened; and roughly what time the
error occured. Thanks!</dd>

<dt>What is this site?</dt>

<dd>HassleMe is a tool which nags you. It nags you via email about things
you know you should be doing, but which you'll forget.</dd>

<dt>How often does it nag?</dt>

<dd>You set up a rough frequency, but it actually nags you at random times
within certain parameters. It keeps you on your toes.</dd>

<dt>Why do you think it'll work?</dt>

<dd>mySociety's developer <a href="http://www.ex-parrot.com/~chris/">Chris
Lightfoot</a> built a little program called
<a href="http://www.mysociety.org/?p=16">Hasslebot</a>, to encourage the
developers and volunteers at mySociety to post frequently to our blog, letting
people know what mySociety was up to. Despite the fact that it shouldn't work,
it did.</dd>

<dt>How do I cancel a hassle?</dt>

<dd>Every time we hassle you there will be a link that you can
click to cancel it.</dd>

<dt>If I give you my email address, will you send me spam?<dt>

<dd><b>No!</b> We will only ever send you email when someone
(hopefully you) uses this website to set up a hassle (i.e. we'll send
you a "please confirm this hassle" email), and to carry out the actual
hassling (i.e. the regular nagging emails telling you to go the gym,
write to your mother, etc.). We won't sell your email address to
anyone, and we won't send you spam &mdash; ever.</dd>

<dt>Who are you?</dt>

<dd>This site was built by <a
href="http://www.ex-parrot.com/~chris/">Chris Lightfoot</a> and <a
href="http://ejhp.net/">Etienne Pollard</a> in two afternoons before
and after Christmas 2005 as a mySociety 'back of the envelope'
project. Chris was a full-time employee of mySociety and spent his
days running much more serious sites like <a
href="http://www.writetothem.com/">WriteToThem.com</a>. <a
href="http://www.mysociety.org/">mySociety</a> is a charitable
organisation which has grown out of the community of volunteers who
built sites like <a
href="http://www.theyworkforyou.com/">TheyWorkForYou.com</a>. Our
primary mission is to build internet projects which give people
simple, tangible benefits in the civic and community aspects of their
lives. Our first project was <a
href="http://www.writetothem.com/">WriteToThem.com</a>, where you can
write to any of your elected representatives, for free, and our more
recent sites include <a
href="http://www.pledgebank.com/">PledgeBank.com</a> and <a
href="http://www.placeopedia.com/">Placeopedia.com</a>.</dd>

EOF

    } elsif ($fn eq 'privacy') {
                hassle_header($q,'Privacy, cookies, and third party services');
                print <<EOF;

                <p><strong>Our use of your data, cookies, and external services: what you should know, and how to opt out if you want to.</strong></p>

                <p>Summary: We care a lot about our users’ privacy. We provide details below, and we try our hardest to look after the private data that we hold. Like many other websites, we sometimes use cookies to help us make our websites better. These tools are very common and used by many other sites, but they do have privacy implications, and as a charity concerned with socially positive uses of the internet, we think it’s important to explain them in full. If you don’t want to share your browsing activities on mySociety’s sites with other companies, you can adjust your usage or install opt-out browser plugins.

                <h3>Measuring website usage (Google Analytics)</h3>

                We use Google Analytics to collect information about how people use this site. We do this to make sure it’s meeting its users’ needs and to understand how we could do it better. Google Analytics stores information such as what pages you visit, how long you are on the site, how you got here, what you click on, and information about your web browser. IP addresses are masked (only a portion is stored) and personal information is only reported in aggregate. We do not allow Google to use or share our analytics data for any purpose besides providing us with analytics information, and we recommend that any user of Google Analytics does the same.

                <p>If you’re unhappy with data about your visit to be used in this way, you can install the <a href="http://tools.google.com/dlpage/gaoptout">official browser plugin for blocking Google Analytics</a>.

                <p>The cookies set by Google Analytics are as follows:

                <table>
                <tr><th scope="col">Name</th><th scope="col">Typical Content</th><th scope="col">Expires</th></tr>
                <tr><td>__utma</td><td>Unique anonymous visitor ID</td><td>2 years</td></tr>
                <tr><td>__utmb</td><td>Unique anonymous session ID</td><td>30 minutes</td></tr>
                <tr><td>__utmz</td><td>Information on how the site was reached (e.g. direct or via a link/search/advertisement)</td><td>6 months</td></tr>
                <tr><td>__utmx</td><td>Which variation of a page you are seeing if we are testing different versions to see which is best</td><td>2 years</td></tr>
                </table>

                <h4>Google’s Official Statement about Analytics Data</h4>

                <p>“This website uses Google Analytics, a web analytics service provided by Google, Inc. (“Google”).  Google Analytics uses “cookies”, which are text files placed on your computer, to help the website analyze how users use the site. The information generated by the cookie about your use of the website (including your IP address) will be transmitted to and stored by Google on servers in the United States . Google will use this information for the purpose of evaluating your use of the website, compiling reports on website activity for website operators and providing other services relating to website activity and internet usage.  Google may also transfer this information to third parties where required to do so by law, or where such third parties process the information on Google’s behalf. Google will not associate your IP address with any other data held by Google.  You may refuse the use of cookies by selecting the appropriate settings on your browser, however please note that if you do this you may not be able to use the full functionality of this website.  By using this website, you consent to the processing of data about you by Google in the manner and for the purposes set out above.”</p>

                <p><a href="http://www.mysociety.org/privacy-online/">More general information on how third party services work</a></p>

                <h2>Credits</h2>

                <p>Bits of wording taken from the <a href="http://gov.uk/help/cookies">gov.uk cookies page</a> (under the Open Government Licence).
EOF
    }
    hassle_footer($q);
}
