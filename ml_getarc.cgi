#!/usr/bin/perl
# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml_getarc.cgi
#  - ���쌠�\��    (c)1997-2009 Perl Script Laboratory
#  - �A  ��  ��    info@psl.ne.jp (http://www.psl.ne.jp/)
# ---------------------------------------------------------------
# �����p�ɂ������Ă̒���
#   �����̃V�X�e���̓t���[�E�G�A�ł��B
#   �����̃V�X�e���́A�u���p�K��v�����ǂ݂̏ゲ���p���������B
#     http://www.psl.ne.jp/info/copyright.html
# ---------------------------------------------------------------
BEGIN {
#    print "Content-type: text/html\n\n";
    open(STDERR, ">&STDOUT");
}
use strict;
use vars qw(%FORM %CONF %login);
require 'jcode.pl';
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());
umask 0;

$CONF{enable_get_archive}
 or error('���݃A�[�J�C�u�̎擾�͂ł��Ȃ��ݒ�ɂȂ��Ă��܂��B');

%FORM = decoding();

@login{qw(id email)} = passwd_check();

list() if $FORM{list};
send_arc() if $FORM{send};
display_form();

sub display_form {

    printhtml("getarc_form.html");
    exit;

}

sub list {

    my @list = parse_no($FORM{arc_no});
    if (@list > 20) { error("�w�肵�����e�ԍ��̐���20�𒴂��Ă��܂��B"); }

    file_lock();

    my $cnt;
    my $list;
    foreach (@list) {
        my $dir_s = int($_/100);
        next unless -e "post/$dir_s/$_.cgi";
        $cnt++;
        open(R, "post/$dir_s/$_.cgi")
         or error("$_�Ԃ̓��e�f�[�^�t�@�C�����J���܂���ł����B: $!");
        chomp(my $date = <R>);
        chomp(my $from = <R>);
        chomp(my $subject = <R>);
        close(R);
        my $attach = "&nbsp;";
        if (-d "post/attach/$dir_s/$_") {
            opendir(DIR, "post/attach/$dir_s/$_") or error($!);
            $attach = "��" if grep(!/^\.\.?/, readdir(DIR));
        }
        $date =~ s/^Date: +(.*)$/$1/;
        $from =~ s/^From: +(.*)$/$1/;
        $subject =~ s/^Subject: +(.*)$/$1/;
        $list .= <<STR;
<tr><td align=right>$_</td><td>$subject</td><td>$from</td>
<td align=center>$attach</td><td>$date</td></tr>
STR
    }

    printhtml("getarc_list.html", cnt=>($cnt||0), list=>$list, arc_no=>$FORM{arc_no});
    exit;

}

sub send_arc {

    my @list = parse_no($FORM{arc_no});
    if (@list > 20) { error("�w�肵�����e�ԍ��̐���20�𒴂��Ă��܂��B"); }

    file_lock();

    my @spool;
    foreach my $no(@list) {
        my $dir_s = int($no/100);
        next unless -e "post/$dir_s/$no.cgi";
        open(R, "post/$dir_s/$no.cgi")
         or error("$_�Ԃ̓��e�f�[�^�t�@�C�����J���܂���ł����B: $!");
        chomp(my $date = <R>);
        chomp(my $from = <R>);
        chomp(my $subject = <R>);
        chomp(my $remote_host = <R>);
        chomp(my $user_agent = <R>);
        my $mailstr = join("", <R>);
        $mailstr =~ s/^[\r\n]+//;
        close(R);
        $date =~ s/^Date: +(.*)$/$1/;
        $from =~ s/^From: +(.*)$/$1/;
        $subject =~ s/^Subject: +(.*)$/$1/;
        $remote_host =~ s/^X-Sender-Remote-Host: +(.*)$/$1/;
        $user_agent =~ s/^X-Sender-User-Agent: +(.*)$/$1/;
        if ($CONF{subject_prefix} ne '') {
            my $subject_prefix0 = $CONF{subject_prefix};
            $subject_prefix0 =~ s/(#+)/sprintf("%0".length($1)."d",$no)/e;
            $subject = "$subject_prefix0 $subject";
        }
        open(R, "member/$login{id}.cgi")
         or error_log("member/$login{id}.cgi ���J���܂���ł����B: $!");
        (undef,$login{passwd}) = split(/\t/, <R>);
        close(R);
        if ($CONF{add_ml_header}) {
            my $ml_header = $CONF{ml_header};
            $ml_header = '' if $ml_header eq "\n";
            $mailstr = "$ml_header$mailstr";
        }
        if ($CONF{add_ml_footer}) {
            my $ml_footer = $CONF{ml_footer};
            $ml_footer =~ s/##idpw##/__idpw__/g;
            $ml_footer =~ s/##id##/__id__/g;
            $ml_footer =~ s/##passwd##/__passwd__/g;
            $ml_footer =~ s/##ml_cnt##/$no/g;
            $ml_footer =~ s/##([^#]+)##/$CONF{$1}/g;
            $mailstr .= "\n" unless $mailstr =~ /(\r\n|\r|\n)$/;
            $mailstr .= $ml_footer;
        }
        my %add_header;
        if ($remote_host ne '') {
            $add_header{"X-Sender-Remote-Host"} = $remote_host;
        }
        if ($user_agent ne '') {
            $add_header{"X-Sender-User-Agent"} = $user_agent;
        }
        my %attachment;
        if (-d "post/attach/$dir_s/$no") {
            opendir(DIR, "post/attach/$dir_s/$no")
             or error("�Y�t�t�@�C���p�f�B���N�g�����J���܂���ł����B: $!");
            foreach my $file(grep(!/^\.\.?/, readdir(DIR))) {
                open(R, "post/attach/$dir_s/$no/$file")
                 or error("�Y�t�t�@�C�����J���܂���ł����B: $!");
                $attachment{$file} = join("", <R>);
                close(R);
            }
        }
        push(@spool, [$login{email},$from,$subject,$mailstr,$date,{%add_header},{%attachment}]);

    }

    printhtml("getarc_done.html");

    $| = 1;
    exit if my $pid = fork;
    close(STDOUT);
    close(STDERR);

    foreach (@spool) { sendmail(@{$_}); }
    exit;

}

sub parse_no {

    my ($arc_no) = @_;
    my @list;

    my @msg;
    $arc_no = zen_to_han($arc_no);
    $arc_no =~ s/\s+//g;
    push(@msg,"���e�ԍ����w�肵�Ă��������B") if $arc_no eq '';
    if ($arc_no =~ /[^0-9,\- ]/) {
        push(@msg,"���e�ԍ��̎w��ɂ͔��p�����A�n�C�t��(-)�A�J���}(,)".
                  "�ȊO�̕������g�����Ƃ͂ł��܂���B");
    }
    foreach (split(/,/, $arc_no)) {
        my($s,$e) = split(/\-/);
        if ($e and $s > $e) { push(@msg,"$_ �͊Ԉ�����w��ł��B"); }
        $e ||= $s;
        foreach my $no($s..$e) { push(@list, $no); }
    }
    error(@msg) if @msg;

    @list;
}
