#!/usr/bin/perl
# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml_post.cgi
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
use vars qw($q %FORM %CONF %login);
use CGI;
require 'jcode.pl';
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());
umask 0;

$CONF{enable_post} or error('���ݓ��e�@�\�͂ł��Ȃ��ݒ�ɂȂ��Ă��܂��B');

%FORM = decoding($ENV{CONTENT_TYPE} =~ m#multipart/form-data#
 ? ($q = new CGI) : undef);
@FORM{qw(id passwd)} = idpw_decode($FORM{idpw}) if $FORM{idpw};
@login{qw(id email)} = passwd_check();

post() if $FORM{post};
confirm() if $FORM{confirm};
form();

sub form {

    file_lock();

    my $type_dsp;
    my $res_date;
    my $res_from;
    my $res_subject;
    my $res_mailbody;

    if ($FORM{res}) {
        if ($FORM{res} =~ /\D/) {
            error("�������̋L���ԍ��͔��p�����Ŏw�肵�Ă��������B");
        }
        my $res_s = int($FORM{res}/100);
        unless (-e "post/$res_s/$FORM{res}.cgi") {
            error("�Y������ԐM���̋L��(No.$FORM{res})�͂���܂���ł����B");
        }
        open(R, "post/$res_s/$FORM{res}.cgi")
         or error("���e�f�[�^�t�@�C�����J�����Ƃ��ł��܂���ł����B: $!");
        chomp($res_date = <R>);
        chomp($res_from = <R>);
        chomp($res_subject = <R>);
        $res_subject =~ s/Subject: +(.*)$/$1/i;
        my $res_subject_org = $res_subject;
        if ($res_subject =~ /^re: *\D*/i) {
            $res_subject =~ s/^re: */Re\^2: /i;
        } elsif ($res_subject =~ /^re\^(\d*): */i) {
            my $resno = $1 + 1;
            $res_subject =~ s/^re\^(\d*): */Re\^$resno: /i;
        } else {
            $res_subject = 'Re: ' . $res_subject;
        }

        $res_mailbody = join("", <R>);
        $res_mailbody =~ s/\n+$//;
        $res_mailbody =~ s/\n/\n> /g;
        $res_mailbody = "$res_date\n$res_from �ւ̕ԐM\n\n> $res_mailbody";

        $type_dsp = "No.$FORM{res}: $res_subject_org �ւ̕ԐM";
    } else {
        $type_dsp = "�V�K���e";
    }

    open(R,"sign/$login{id}.cgi");
    my $signiture = join("", <R>);
    close(R);

    printhtml("post_form.html", res=>$FORM{res},type_dsp=>$type_dsp,
     email=>$login{email}, res_subject => html_output_escape($res_subject),
     res_mailbody => html_output_escape($res_mailbody),
     signiture => html_output_escape($signiture),
     attach_begin =>($CONF{enable_attachment} ? "" : "<!--"),
     attach_end =>($CONF{enable_attachment} ? "" : "-->"),
     attach_list => join("<br>\n", map { qq{<input type=file name="file$_" size=50>} } (1..$CONF{attachment})),
     attachment_sizemax_dsp => ($CONF{attachment_sizemax} ? "$CONF{attachment_sizemax}kb/�t�@�C��" : "�����Ȃ�"),
     attachment_ext_dsp => ($CONF{attachment_ext} ? $CONF{attachment_ext} : "�����Ȃ�"),
    );
    exit;

}

sub confirm {

    if ($FORM{res} =~ /\D/) {
        error("�������̋L���ԍ��͔��p�����Ŏw�肵�Ă��������B");
    }

    $FORM{subject} =~ s/^\s*(.*)\s*$/$1/;
    $FORM{subject} = "(����)" if $FORM{subject} eq '';
    if ($FORM{mailbody} eq '') {
        error("���[���{���������w�肳��Ă��܂���B");
    }

    foreach (qw(subject mailbody signiture type)) {
        $FORM{$_} =~ s/\n+$/\n/;
        $FORM{"${_}_dsp"} = $FORM{$_} = html_output_escape($FORM{$_});
    }
    my $mailbody_dsp = "$FORM{mailbody}\n$FORM{signiture}";

    my $attach_dsp;
    my $temp = time . $$;
    if ($CONF{enable_attachment}) {
        foreach my $i(1..$CONF{attachment}) {
            if ($FORM{"file$i"}) {
                my $stream = get_file_stream($q, "file$i");
                my($filename) = $FORM{"file$i"} =~ m#([^/]+)$#;
                if ($CONF{attachment_sizemax}) {
                    if (length($stream) > $CONF{attachment_sizemax} * 1024) {
                        error("$filename�̃t�@�C���T�C�Y��$CONF{attachment_sizemax}kb�𒴂��Ă��܂��B");
                    }
                }
                file_save($stream, "temp", "$temp-$filename", split(/\W+/, $CONF{attachment_ext}));
                $attach_dsp .= "$filename<br>";
            }
        }
    }

    printhtml("post_confirm.html",
     (map { $_ => $FORM{$_} } qw(res subject mailbody signiture type_dsp
     subject_dsp)),
     ua=>$ENV{HTTP_USER_AGENT}, remote_host=>remote_host(),
     attach_dsp => $attach_dsp,
     mailbody_dsp=>$mailbody_dsp, temp=>$temp,
     attach_begin =>($CONF{enable_attachment} ? "" : "<!--"),
     attach_end =>($CONF{enable_attachment} ? "" : "-->"),
    );
    exit;


}

sub post {

    file_lock();

    my $remote_host = remote_host();

    open(R, "ml_postcnt.txt")
     or error("���e�ԍ��t�@�C�� ml_postcnt.txt ���J���܂���ł����B: $!");
    chomp(my $postcnt = <R>);
    close(R);
    $postcnt ||= 1;
    while (1) {
        my $post_s = int($postcnt/100);
        last unless -e "post/$post_s/$postcnt.cgi";
        $postcnt++;
    }
    open(W, "> ml_postcnt.txt")
     or error("���e�ԍ��̏������݂��ł��܂���ł����B: $!");
    print W $postcnt;
    close(W);

    open(W, "> sign/$login{id}.cgi")
     or error("�����t�@�C�� sign/$login{id}.cgi �֏������݂ł��܂���ł����B: $!");
    print W $FORM{signiture};
    close(W);

    open(R,"member/$login{id}.cgi")
     or error("�����o�[�t�@�C�� member/$login{id}.cgi ���J���܂���ł����B: $!");
    (undef,undef,my $from) = split(/\t/, <R>);
    close(R);

    my $post_s = int($postcnt/100);
    mkdir("post/$post_s", 0777) unless -d "post/$post_s";
    mkdir("post/attach/$post_s", 0777) unless -d "post/attach/$post_s";
    my $date_header_f = date_header_f(time);

    $FORM{mailstr} .= "\n$FORM{signiture}";
    my $maillogstr = $FORM{mailbody};
    if ($CONF{add_ml_header}) {
        my $ml_header = $CONF{ml_header};
        $ml_header = '' if $ml_header eq "\n";
        $FORM{mailbody} = "$ml_header$FORM{mailbody}";
    }
    if ($CONF{add_ml_footer}) {
        my $ml_footer = $CONF{ml_footer};
        $ml_footer =~ s/##idpw##/__idpw__/g;
        $ml_footer =~ s/##id##/__id__/g;
        $ml_footer =~ s/##passwd##/__passwd__/g;
        $ml_footer =~ s/##ml_cnt##/$postcnt/g;
        $ml_footer =~ s/##([^#]+)##/$CONF{$1}/g;
        $FORM{mailbody} .= "\n" unless $FORM{mailbody} =~ /(\r\n|\r|\n)$/;
        $FORM{mailbody} .= $ml_footer;
    }
    open(W, "> post/$post_s/$postcnt.cgi")
     or error("���e�t�@�C���̏������݂��ł��܂���ł����B: $!");
    print W qq{Date: $date_header_f\n};
    print W qq{From: $from\n};
    print W qq{Subject: $FORM{subject}\n};
    print W qq{X-Sender-Remote-Host: $remote_host\n};
    print W qq{X-Sender-User-Agent: $ENV{HTTP_USER_AGENT}\n};
    print W qq{\n};
    print W $maillogstr;
    close(W);

    my %attachment;
    if ($CONF{enable_attachment}) {
        opendir(DIR, "temp") or error("temp�f�B���N�g�����J���܂���ł����B: $!");
        foreach (grep(/^$FORM{temp}-/, readdir(DIR))) {
            mkdir("post/attach/$post_s/$postcnt", 0777)
             unless -d "post/attach/$post_s/$postcnt";
            my($filename) = /^$FORM{temp}-(.*)$/;
            open(R, "temp/$_") or error("temp/$_���J���܂���ł����B: $!");
            $attachment{$filename} = join("", <R>);
            open(W, "> post/attach/$post_s/$postcnt/$filename")
             or error("�Y�t�t�@�C���̏������݂��ł��܂���ł����B: $!");
            print W $attachment{$filename};
            close(W);
            close(R);
        }
    }

    printhtml("post_done.html");

    $| = 1;
    exit if my $pid = fork;
    close(STDOUT);
    close(STDERR);

    if ($CONF{subject_prefix} ne '') {
        $CONF{subject_prefix} =~ s/(#+)/sprintf("%0".length($1)."d",$postcnt)/e;
        $FORM{subject} = "$CONF{subject_prefix} $FORM{subject}";
    }
    sendmail2($from, $FORM{subject}, $FORM{mailbody}, {
        "X-Sender-Remote-Host" => $remote_host,
        "X-Sender-User-Agent" => $ENV{HTTP_USER_AGENT},
    }, { %attachment },);
    exit;

}
