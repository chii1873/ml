#!/usr/bin/perl
# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml_reg.cgi
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
#    open(STDERR, ">&STDOUT");
}
use strict;
use vars qw(%FORM %CONF);
require 'jcode.pl';
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());
umask 0;

%FORM = decoding();

cancel() if $FORM{cancel};
prereg() if $FORM{prereg};
reg2() if $FORM{reg2};
reg() if $FORM{reg};
display_form();

sub display_form {

    printhtml("prereg_form.html");
    exit;

}

sub prereg {

    ($FORM{email}, my @msg_) = email_chk($FORM{email}, str=>"���[���A�h���X",
     required=>1);
    error(@msg_) if @msg_;

    file_lock();
    opendir(DIR, "member")
     or error("member�f�B���N�g�����J���܂���ł����B: $!");
    foreach my $file(grep(/\.cgi$/, readdir(DIR))) {
        open(R, "member/$file")
         or error("�����o�[�f�[�^�t�@�C�����J���܂���ł����B: $!");
        my($email) = (split(/\t/, <R>))[2];
        if ($FORM{email} eq $email) {
            error("���̃A�h���X( $email )�͂��łɓo�^����Ă��܂��B");
        }
        close(R);
    }
    closedir(DIR);

    srand(time|$$);
    my $key;
    while (1) {
        $key = '';
        foreach (1..12) { $key .= ('a'..'z','A'..'Z',0..9)[rand(62)]; }
        last unless -e "temp/$key";
    }
    open(W, "> temp/$key.cgi")
     or error("�e���|�����t�@�C���� temp �f�B���N�g����ɍ쐬�ł��܂���".
              "�ł����Btemp �f�B���N�g�������݂��邩�Atemp �f�B���N�g���ւ�".
              "�������݌��������邩���m�F���������B: $!");
    print W $FORM{email};
    close(W);
    file_unlock();

    my($reg_subject,$reg_mailstr) = get_mailstr("prereg");
    $reg_subject =~ s/##title##/$CONF{title}/g;
    $reg_mailstr =~ s/##title##/$CONF{title}/g;
    $reg_mailstr =~ s/##key##/$key/g;
    $reg_mailstr =~ s/##email##/$FORM{email}/g;
    $reg_mailstr =~ s/##k_email##/$CONF{k_email}/g;
    $reg_mailstr =~ s/##ml_dir##/$CONF{ml_dir}/g;
    sendmail($FORM{email}, $CONF{k_email}, $reg_subject, $reg_mailstr);

    printhtml("prereg_done.html");
    exit;

}

sub reg {

    if ($FORM{key} =~ /\W/) {
        error("�s���ȉ��o�^�L�[���w�肳��Ă��܂��B");
    }

    file_lock();
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("���o�^�f�[�^�t�@�C�����J���܂���ł����B: $!");
        chomp(my $email = <R>);
        $FORM{email} = $email;
#        if ($email ne $FORM{email}) {
#            error("���[���A�h���X���Ⴂ�܂��B");
#        }
    } else {
        error("�w�肳�ꂽ���o�^�L�[�͑��݂��܂���ł����B")
    }
    file_unlock();

    printhtml("reg_form.html", key=>$FORM{key}, email=>$FORM{email});
    exit;

}

sub reg2 {

    if ($FORM{key} =~ /\W/) {
        error("�s���ȉ��o�^�L�[���w�肳��Ă��܂��B");
    }

    file_lock();
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("���o�^�f�[�^�t�@�C�����J���܂���ł����B: $!");
        chomp(my $email = <R>);
        if ($email ne $FORM{email}) {
            error("���[���A�h���X���Ⴂ�܂��B");
        }
    } else {
        error("�w�肳�ꂽ���o�^�L�[�͑��݂��܂���ł����B")
    }

    email_dupl_check($FORM{email});

    my $memcnt = get_memcnt();

    srand(time|$$);
    my $now = time;
    my $passwd;
    foreach (1..8) { $passwd .= (0..9)[rand(10)]; }
    open(W,"> member/$memcnt.cgi");
    print W join("\t", $memcnt,$passwd,$FORM{email},$now,$now), "\n";
    close(W);

    my($reg_subject,$reg_mailstr) = get_mailstr("reg");
    $reg_subject =~ s/##([^#]+)##/$CONF{$1}/g;
    $reg_mailstr =~ s/##id##/$memcnt/g;
    $reg_mailstr =~ s/##passwd##/$passwd/g;
    $reg_mailstr =~ s/##([^#]+)##/$CONF{$1}/g;
    sendmail($FORM{email}, $CONF{k_email}, $reg_subject, $reg_mailstr);

    if ($CONF{send_intro}) {
        my($subject,$mailstr) = get_mailstr("intro");
        $subject =~ s/##([^#]+)##/$CONF{$1}/g;
        $mailstr =~ s/##([^#]+)##/$CONF{$1}/g;
        sendmail($FORM{email}, $CONF{k_email}, $subject, $mailstr);
    }

    unlink("temp/$FORM{key}.cgi");
    file_unlock();

    printhtml("reg_done.html");
    exit;

}

sub cancel {

    if ($FORM{key} =~ /\W/) {
        error("�s���ȉ��o�^�L�[���w�肳��Ă��܂��B");
    }

    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("���o�^�f�[�^�t�@�C�����J���܂���ł����B: $!");
        chomp(my $email = <R>);
        if ($email ne $FORM{email}) {
            error("���[���A�h���X���Ⴂ�܂��B");
        }
    } else {
        error("�w�肳�ꂽ���o�^�L�[�͑��݂��܂���ł����B")
    }
    unlink("temp/$FORM{key}.cgi");

    printhtml("reg_cancel.html");
    exit;

}
