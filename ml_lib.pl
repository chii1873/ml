# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml_lib.pl
#  - ���쌠�\��    (c)1997-2009 Perl Script Laboratory
#  - �A  ��  ��    info@psl.ne.jp (http://www.psl.ne.jp/)
# ---------------------------------------------------------------
# �����p�ɂ������Ă̒���
#   �����̃V�X�e���̓t���[�E�G�A�ł��B
#   �����̃V�X�e���́A�u���p�K��v�����ǂ݂̏ゲ���p���������B
#     http://www.psl.ne.jp/info/copyright.html
# ---------------------------------------------------------------
# ���̃X�N���v�g�͋��ʃ��C�u�����ł��B
use strict;
use vars qw($q %FORM %CONF %login);
use Fcntl qw(:flock);
use POSIX qw(SEEK_SET);

sub base64_decode {

    my $str = shift;
    my $res = "";

    $str =~ tr|A-Za-z0-9+=/||cd;
    if (length($str) % 4) {
        error("�f�R�[�h�Ώۂ̕����񂪕s���ł��B");
    }
    $str =~ s/=+$//;
    $str =~ tr|A-Za-z0-9+/| -_|;
    while ($str =~ /(.{1,60})/gs) {
	my $len = chr(32 + length($1) * 3 / 4);
	$res .= unpack("u", $len . $1 );
    }
    $res;
}

sub base64_encode {

    my($subject) = @_;
    my($str, $padding);
    while ($subject =~ /(.{1,45})/gs) {
        $str .= substr(pack('u', $1), 1);
        chop($str);
    }
    $str =~ tr|` -_|AA-Za-z0-9+/|;
    $padding = (3 - length($subject) % 3) % 3;
    $str =~ s/.{$padding}$/'=' x $padding/e if $padding;
    $str;

}

sub clean_tempfile {

    my $now = time;
    opendir(DIR, "temp") or error("temp�f�B���N�g�����J���܂���ł����B: $!");
    foreach my $file(grep(!/^\.\.?/, readdir(DIR))) {
        unlink("temp/$file") if (stat("temp/$file"))[10] < $now - 7200;
    }

}

sub comma {

    my($num) = @_;
    1 while $num =~ s/(.*\d)(\d\d\d)/$1,$2/;
    $num;
}

sub crypt_passwd {

    my $passwd = shift;
    my $salt;
    my @salt = ('0'..'9','A'..'Z','a'..'z','.','/');
    foreach (1..8) { $salt .= $salt[rand(@salt)] };
    crypt($passwd,
     index(crypt('a', '$1$a$'), '$1$a$') == 0 ? '$1$'.$salt.'$' : $salt);

}

sub crypt_passwd_is_valid {

    my($plain_passwd, $crypt_passwd) = @_;
    return 0 if $plain_passwd eq '' or $crypt_passwd eq '';
    return crypt($plain_passwd, $crypt_passwd) eq $crypt_passwd ? 1 : 0;

}

sub date_f {

    my($time, $mode) = @_;
    my($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($time);
    $mon++;
    $year += 1900;
    $sec  = sprintf("%02d", $sec);
    $min  = sprintf("%02d", $min);
    $hour = sprintf("%02d", $hour);
    $mon  = sprintf("%02d", $mon);
    $mday = sprintf("%02d", $mday);
    my $week = (qw(Sun Mon Tue Wed Thu Fri Sat))[$wday];
    "$year/$mon/$mday($week) $hour:$min:$sec";

}

sub date_header_f {

    my($time) = @_;
    my($sec,$min,$hour,$mday,$mon,$year,$wday) = gmtime($time + 32400);
    $year += 1900;
    $sec  = sprintf("%02d", $sec);
    $min  = sprintf("%02d", $min);
    $hour = sprintf("%02d", $hour);
    my $week = (qw(Sun Mon Tue Wed Thu Fri Sat))[$wday];
    $mon  = (qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec))[$mon];
    "$week, $mday $mon $year $hour:$min:$sec +0900";

}

sub decoding {

    my($q) = @_;
    my %FORM;
    my $buf;

    if ($q) {
        foreach my $name($q->param()) {
            foreach my $each($q->param($name)) {
                if (defined($FORM{$name})) {
                    $FORM{$name} = join('|||', $FORM{$name}, $each);
                } else {
                    $FORM{$name} = $each;
                }
            }
        }
        if (keys %FORM == 1 and $FORM{keywords}) {
            $FORM{$FORM{keywords}} = 1;
            delete $FORM{keywords};
        } else {
            foreach my $key(qw(cancel chg chg2 confirm del
             export export_done export_getfile import
             import_confirm import_done list logout mail
             mailstr mod mod2 post prechg prereg reg reg2
             send setup setup_done)) {
                $FORM{$key} = 1 if exists $FORM{$key} and $FORM{$key} eq '';
            }
        }
    } else {
        if ($ENV{REQUEST_METHOD} eq "POST") {
            read(STDIN, $buf, $ENV{CONTENT_LENGTH});
        } else {
            $buf = $ENV{QUERY_STRING};
        }
        foreach (split(/&/,$buf)) {
            if (!/=/) { $_ .= "=1"; }
            my($name, $value) = split(/=/);
            $value =~ tr/+/ /;
            $name  =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
            $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
            $value =~ s/\r//g;

            if (defined($FORM{$name})) {
                $FORM{$name} = join('|||', $FORM{$name}, $value);
            } else {
                $FORM{$name} = $value;
            }
        }

    }

    %FORM;
}

sub email_chk {

    my($email, %opt) = @_;
    $opt{str} ||= "���[���A�h���X";
    my @msg;

    if ($opt{required}) {
        $email or push(@msg, $opt{str}.'����͂��Ă��������B');
    }
    if ($email && $email !~ /^[-_.!*a-zA-Z0-9\/&+%\#]+\@[-_.a-zA-Z0-9]+\.(?:[a-zA-Z]{2,4})$/) {
        push(@msg, $opt{str}.'������������܂���B');
    }

    return wantarray ? (lc($email), @msg) : lc($email);

}

sub email_dupl_check {

    my $email = shift;

    opendir(DIR, "member")
     or error("member�f�B���N�g�����J���܂���ł����B: $!");
    foreach my $file(grep(/\.cgi$/, readdir(DIR))) {
        open(R, "member/$file")
         or error("�����o�[�f�[�^�t�@�C�����J���܂���ł����B: $!");
        my($email_) = (split(/\t/, <R>))[2];
        if ($email eq $email_) {
            error("���̃A�h���X( $email )�͂��łɓo�^����Ă��܂��B");
        }
        close(R);
    }
    closedir(DIR);

}

sub enc_b64 {

    my($subject) = @_;
    my($str, $padding);
    while ($subject =~ /(.{1,45})/gs) {
        $str .= substr(pack('u', $1), 1);
        chop($str);
    }
    $str =~ tr|` -_|AA-Za-z0-9+/|;
    $padding = (3 - length($subject) % 3) % 3;
    $str =~ s/.{$padding}$/'=' x $padding/e if $padding;
    "=?ISO-2022-JP?B?$str?=";

}

sub error {

    my $errmsg = join("", map { "<li>$_\n" } map { html_output_escape($_) } @_);
    printhtml("error.html", errmsg=>$errmsg);
    exit;

}

sub error_admin {

    my $errmsg = join("", map { "<li>$_\n" } map { html_output_escape($_) } @_);
    printhtml("error_admin.html", errmsg=>$errmsg);
    exit;

}

sub file_lock {

    open(LOCK, ">./lock")
     or error("�t�@�C�����b�N���ł��܂���ł����B: $!");
    flock(LOCK, LOCK_EX);
    undef;

}

sub file_save {

    my %extlist = map { $_ => 1 } qw(jpg gif jpeg html shtml htm pdf);
    my($stream, $filepath, $filename, @extra_extlist) = @_;
    %extlist = map { $_ => 1 } @extra_extlist if @extra_extlist;
    $stream or return;

    $filename =~ s#.*[\\/]([^\\/]+)$#$1#;
    my($ext) = $filename =~ /\.([^\.]+)$/;
    unless ($extlist{lc($ext)}) {
        error("�A�b�v���[�h�ł���t�@�C���́A".
         join(" ", sort keys %extlist).
         " �̊g���q�������̂Ɍ����Ă��܂��B");
    }
    open(W, "> $filepath/$filename")
     or error("$filepath/$filename �̏������݂Ɏ��s���܂����B: $!");
    print W $stream;
    close(W);

}

sub file_unlock {

}

sub get_cookie {

    my($cookie_name) = @_;
    my $cookie_data;
    error('�N�b�L�[�����w�肵�Ă��������B') if !$cookie_name;
    foreach (split(/; /, $ENV{HTTP_COOKIE})) {
        my($name, $value) = split(/=/);
        if ($name eq $cookie_name) {
            $cookie_data = $value;
            last;
        }
    }

    wantarray
     ? split(/\!\!\!/, $cookie_data) : (split(/\!\!\!/, $cookie_data))[0];

}

sub get_datetime {

    my $time = shift;
    my($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($time);
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900,++$mon,$mday,$hour,$min,$sec);

}

sub get_datetime_for_cookie {

    my($time) = @_;
    my($sec,$min,$hour,$mday,$mon,$year,$wday) = gmtime(time + $time);
    sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
     (qw(Sun Mon Tue Wed Thu Fri Sat))[$wday],
     $mday, (qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec))[$mon],
     $year+1900, $hour, $min, $sec);

}

sub get_epoch {

    use Time::Local;
    my($y,$m,$d,$h,$mi,$s) = split(/\D+/, shift);
    return timelocal($s,$mi,$h,$d,$m-1,$y-1900);

}

sub get_file_stream {

    my($q,$param) = @_;
    my $stream;

    if (ref $q->uploadInfo($q->param($param))) {
        my $ctype = $q->uploadInfo($q->param($param))->{'Content-Type'};
        if ($ctype =~ /macbinary/) {
            my $len;
            seek($q->param($param), 83, SEEK_SET);
            read($q->param($param), $len, 4);
            $len = unpack "%N", $len;
            seek($q->param($param), 128, SEEK_SET);
            read($q->param($param), $stream, $len);
        } else {
            my $buf;
            $stream .= $buf while read($q->param($param),$buf,1024);
        }
    }
    $stream;

}

sub get_mailstr {

    my $name = shift;
    open(R, "tmpl/mail_$name.txt")
     or error("���[���e���v���[�g�t�@�C�����J���܂���ł����B: $!");
    chomp(my $subject = <R>);
    my $mailstr = join("", <R>);
    close(R);

    return $subject, $mailstr;

}

sub get_memcnt {

    open(R, "ml_memcnt.txt")
     or error("ml_memcnt.txt ���J���܂���ł����B: $!");
    chomp(my $memcnt = <R>);
    close(R);

    $memcnt ||= 1001;
    while (1) {
        last unless -e "member/$memcnt.cgi";
        $memcnt++;
    }

    open(W, "> ml_memcnt.txt")
     or error("ml_memcnt.txt �֏������݂ł��܂���ł����B: $!");
    print W $memcnt;
    close(W);

    return $memcnt;

}

sub h {

	return html_output_escape($_[0]);

}

sub html_output_escape {

    my $str = shift;
    $str =~ s/&/&amp;/g;
    $str =~ s/>/&gt;/g;
    $str =~ s/</&lt;/g;
    $str =~ s/"/&quot;/g;
    $str =~ s/'/&#39;/g;
    $str;

}

sub idpw_encode {

    my($id,$passwd) = @_;

    unless (@idpw::list) {
        @idpw::list = (0..9,"a".."z","A".."Z",",");
        @idpw::rev{@idpw::list} = reverse @idpw::list;
    }
    my $k = base64_encode(join("", map {$idpw::rev{$_}} reverse split(//,"$id,$passwd")));
    $k =~ s/(\W)/"%".unpack("H2", $1)/ge;
    return $k;

}

sub idpw_decode {

    my $k = shift;

    unless (@idpw::list) {
        @idpw::list = (0..9,"a".."z","A".."Z",",");
        @idpw::rev{@idpw::list} = reverse @idpw::list;
    }
    $k =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('H2', $1)/eg;
    return split(/,/, join("", reverse map {$idpw::rev{$_}} split(//, base64_decode($k))));

}

sub login {

    my %opt = @_;

    my $values;
    foreach (keys %FORM) {
        next if $_ eq 'id' or $_ eq 'passwd';
        $values .= qq|<input type=hidden name=$_ value="$FORM{$_}">\n|;
    }
    my($id, $passwd) = get_cookie("PSL_ML_CACHE");
    my $do_cache = $id ? "checked" : "";

    printhtml("login.html", id=>$id, passwd=>$passwd, do_cache=>$do_cache,
     values => $values, location=>$ENV{SCRIPT_NAME},
    );
    exit;

}

sub login_admin {

    my %opt = @_;

    my $values;
    foreach (keys %FORM) {
        next if $_ eq 'id' or $_ eq 'passwd';
        $values .= qq|<input type=hidden name=$_ value="$FORM{$_}">\n|;
    }

    my $passwd = get_cookie("PSL_ML_ADMIN_CACHE");
    my $do_cache = ($passwd ? "checked" : "");

    printhtml("login_admin.html", passwd=>$passwd, do_cache=>$do_cache,
     values => $values, location=>$ENV{SCRIPT_NAME},
    );
    exit;

}

sub passwd_check {

    my($id,$passwd,$email,$null);
    if (($id) = get_cookie('PSL_ML') and !$FORM{id}) {
        open(R, "member/$id.cgi")
         or error("�Y������ID ( $id ) �͑��݂��܂���ł����B");
        $email = (split("\t", <R>))[2];
    } else {
        login() unless $id = $FORM{id};
        if ($id =~ /\W/) {
            error("ID�ɂ͔��p�p�����ȊO�̕������g�����Ƃ͂ł��܂���B");
        }
        open(R, "member/$id.cgi")
         or error("�Y������ID ( $id ) �͑��݂��܂���ł����B");
        ($null, $passwd, $email) = split("\t", <R>);
        if ($passwd ne $FORM{passwd}) {
            error("�p�X���[�h���Ⴂ�܂��B");
        }
        if ($FORM{do_cache}) {
            set_cookie('PSL_ML_CACHE', 30 * 86400, @FORM{qw(id passwd)});
        }
    }
    set_cookie('PSL_ML',"", $id);
    ($id, $email);

}

sub printhtml {

    my($filename, %tr) = @_;
    $filename or die("printhtml: �g�p����html�t�@�C�����w�肵�Ă��������B");

#die(map {"$_=>$tr{$_}\n" } keys %tr);
    open(R, "tmpl/$filename")
     or die("printhtml: $filename ���J���܂���ł����B $!");
    my $htmlstr = join("", <R>);
    close(R);

    foreach (qw(header header_admin footer)) {
        open(R, "tmpl/_$_.html")
         or die("printhtml: _$_.html ���J���܂���ł����B $!");
        my $htmlstr_ = join("", <R>);
        close(R);
        $htmlstr =~ s/<!-- $_ -->/$htmlstr_/g;
    }
    $htmlstr =~ s/##conf:([^#]+)##/$CONF{$1}/g;
    $htmlstr =~ s/##prod:([^#]+)##/$CONF{$1}/g;
#    jcode::convert(\$htmlstr, "euc", "sjis");
    foreach my $key(keys %tr) {
#        jcode::convert(\$tr{$key}, "euc", "sjis");
        $htmlstr =~ s/##$key##/$tr{$key}/g;
    }
#    jcode::convert(\$htmlstr, "sjis", "euc");
    print "Content-type: text/html; charset=Shift_JIS\n\n$htmlstr";

}

sub remote_host {

    if ($ENV{REMOTE_HOST} eq $ENV{REMOTE_ADDR} or $ENV{REMOTE_HOST} eq '') {
        gethostbyaddr(pack('C4',split(/\./,$ENV{REMOTE_ADDR})),2)
         or $ENV{REMOTE_ADDR};
    } else {
        $ENV{REMOTE_HOST};
    }
}

sub sendmail {

    my($mailto, $from, $subject, $mailstr, $date, $headers, $attachment) = @_;

    jcode::convert(\$subject,'jis');
    jcode::convert(\$mailstr,'jis');
    $subject = enc_b64($subject) if $subject =~ /[^\t\n\x20-\x7e]/;
    if ($from eq $CONF{k_email} and $CONF{fromname} ne "") {
        my $fromname = $CONF{fromname};
        jcode::convert(\$fromname, 'jis', 'sjis');
        $fromname = enc_b64($fromname) if $fromname =~ /[^\t\n\x20-\x7e]/;
        $from = qq|"$fromname" <$from>|;
    }

    my $add_header;
    foreach my $header(keys %$headers) {
        if ($headers->{$header} =~ /[^\t\n\x20-\x7e]/) {
            $headers->{$header} = enc_b64($headers->{$header});
        }
        $add_header .= qq{$header: $headers->{$header}\n};
    }

    $mailstr =~ s/__idpw__/idpw_encode(@login{qw(id passwd)})/eg;
    $mailstr =~ s/__id__/$login{id}/g;
    $mailstr =~ s/__passwd__/$login{passwd}/g;

    if (keys %$attachment) {
        my $boundary;
        foreach (1..12) { $boundary .= ('0'..'9','a'..'f')[rand(16)]; }
        $mailstr = <<STR;
To: $mailto
From: $from
Subject: $subject
MIME-Version: 1.0
${add_header}Content-Transfer-Encoding: 7bit
Mime-Version: 1.0
Content-Type: multipart/mixed; boundary="$boundary"


--$boundary
Content-type: text/plain; charset=ISO-2022-JP

$mailstr
STR

        foreach my $filename(keys %$attachment) {
            my $attachdata = base64_encode($attachment->{$filename});
            $mailstr .= <<STR;
--$boundary
Content-Type: application/octet-stream; name="$filename"
Content-Disposition: attachment;
 filename="$filename"
Content-Transfer-Encoding: base64

$attachdata
STR
        }
        $mailstr .= "--$boundary--\n";

    } else {
        $mailstr = <<STR;
To: $mailto
From: $from
Subject: $subject
${add_header}Content-Transfer-Encoding: 7bit
Mime-Version: 1.0
Content-Type: text/plain; charset=ISO-2022-JP

$mailstr
STR
    }

    open(SEND, "|$CONF{sendmail} -t 1>/dev/null 2>/dev/null")
     || error("$mailto �ւ̑��M�Ɏ��s���܂����B: $!");
    print SEND $mailstr;
    close(SEND);

}

sub sendmail2 {

    my ($from, $subject, $mailstr, $headers, $attachment) = @_;

    jcode::convert(\$subject,'jis');
    jcode::convert(\$mailstr,'jis');
    $subject = enc_b64($subject) if $subject =~ /[^\t\n\x20-\x7e]/;
    if ($CONF{fromname} ne "") {
        my $fromname = $CONF{fromname};
        jcode::convert(\$fromname, 'jis', 'sjis');
        $fromname = enc_b64($fromname) if $fromname =~ /[^\t\n\x20-\x7e]/;
        $from = qq|"$fromname" <$from>|;
    }

    my $add_header;
    foreach my $header(keys %$headers) {
        if ($headers->{$header} =~ /[^\t\n\x20-\x7e]/) {
            $headers->{$header} = enc_b64($headers->{$header});
        }
        $add_header .= qq{$header: $headers->{$header}\n};
    }

    if (keys %$attachment) {
        my $boundary;
        foreach (1..12) { $boundary .= ('0'..'9','a'..'f')[rand(16)]; }
        $mailstr = <<STR;
From: $from
Subject: $subject
MIME-Version: 1.0
${add_header}Content-Transfer-Encoding: 7bit
Mime-Version: 1.0
Content-Type: multipart/mixed; boundary="$boundary"


--$boundary
Content-type: text/plain; charset=ISO-2022-JP

$mailstr
STR

        foreach my $filename(keys %$attachment) {
            my $attachdata = base64_encode($attachment->{$filename});
            $mailstr .= <<STR;
--$boundary
Content-Type: application/octet-stream; name="$filename"
Content-Disposition: attachment;
 filename="$filename"
Content-Transfer-Encoding: base64

$attachdata
STR
        }
        $mailstr .= "--$boundary--\n";

    } else {
        $mailstr = <<STR;
From: $from
Subject: $subject
${add_header}Content-Transfer-Encoding: 7bit
Mime-Version: 1.0
Content-Type: text/plain; charset=ISO-2022-JP

$mailstr
STR
    }

    opendir(DIR, "member")
     or error_log("member�f�B���N�g���̓ǂݏo�����ł��܂���ł����B: $!");
    foreach my $file(grep(/\.cgi$/, readdir(DIR))) {
        open(R, "member/$file")
         or error_log("member/$file ���J���܂���ł����B: $!");
        my($id,$passwd,$email) = split(/\t/, <R>);
        close(R);
        my $mailstr0 = $mailstr;
        $mailstr0 =~ s/__idpw__/idpw_encode($id,$passwd)/eg;
        $mailstr0 =~ s/__id__/$id/g;
        $mailstr0 =~ s/__passwd__/$passwd/g;
        open(SEND, "|$CONF{sendmail} -t 1>/dev/null 2>/dev/null")
         or error_log("$email �ւ̑��M�Ɏ��s���܂����B: $!");
        print SEND "To: $email\n$mailstr0";
       close(SEND);
    }
    closedir(DIR);

}

sub set_cookie {

    my($cookie_name, $expire, @cookie_data) = @_;
    my($cookie_data) = join('!!!', @cookie_data);
    $expire = "expires=". get_datetime_for_cookie($expire) . "; "
     if $expire;
    print "Set-Cookie: $cookie_name=$cookie_data; $expire\n";

}

sub setver {

    ### ���̃T�u���[�`�����̐ݒ�͕ύX���Ȃ��ł��������B ###
    return (
        prod_name => 'Web Mailing List',
        version   => '0.31',
        a_email   => 'info@psl.ne.jp',
        a_url     => 'http://www.psl.ne.jp/',
    );
}

sub zen_to_han {

     my($str) = @_;
     my $from = '�O�P�Q�R�S�T�U�V�W�X';
     jcode::convert(\$from, 'euc');
     jcode::convert(\$str, 'euc');
     jcode::tr($from, '0123456789');
     jcode::convert(\$str, 'sjis');
     $str;
}

1;
