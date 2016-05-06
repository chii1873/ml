#!/usr/bin/perl
# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml_chg.cgi
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
use vars qw(%FORM %CONF %login);
require 'jcode.pl';
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());
umask 0;

%FORM = decoding();

@login{qw(id email)} = passwd_check();

cancel() if $FORM{cancel};
prechg() if $FORM{prechg};
chg2() if $FORM{chg2};
chg() if $FORM{chg};
display_form();

sub display_form {

    printhtml("prechg_form.html", email=>$login{email});
    exit;

}

sub prechg {

    ($FORM{email}, my @msg_) = email_chk($FORM{email}, str=>"���[���A�h���X",
     required=>1);
    error(@msg_) if @msg_;

    file_lock();
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
    print W "$login{id}\t$FORM{email}";
    close(W);
    file_unlock();

    my($chg_subject,$chg_mailstr) = get_mailstr("prechg");
    $chg_subject =~ s/##title##/$CONF{title}/g;
    $chg_mailstr =~ s/##title##/$CONF{title}/g;
    $chg_mailstr =~ s/##key##/$key/g;
    $chg_mailstr =~ s/##email##/$FORM{email}/g;
    $chg_mailstr =~ s/##k_email##/$CONF{k_email}/g;
    $chg_mailstr =~ s/##ml_dir##/$CONF{ml_dir}/g;
    sendmail($FORM{email}, $CONF{k_email}, $chg_subject, $chg_mailstr);

    printhtml("prechg_done.html");
    exit;

}

sub chg {

    if ($FORM{key} =~ /\W/) {
        error("�s���ȉ��o�^�L�[���w�肳��Ă��܂��B");
    }

    file_lock();
    my($id, $email);
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("���o�^�f�[�^�t�@�C�����J���܂���ł����B: $!");
        ($id, $email) = split(/\t/, <R>);
        if ($id ne $login{id}) { error("ID���Ⴂ�܂��B"); }
        $FORM{email} = $email;
#        if ($email ne $FORM{email}) {
#            error("���[���A�h���X���Ⴂ�܂��B");
#        }
    } else {
        error("�w�肳�ꂽ���o�^�L�[�͑��݂��܂���ł����B")
    }
    file_unlock();

    printhtml("chg_form.html", key=>$FORM{key}, email=>$FORM{email},
     email_org=>$login{email});
    exit;

}

sub chg2 {

    if ($FORM{key} =~ /\W/) {
        error("�s���ȉ��o�^�L�[���w�肳��Ă��܂��B");
    }

    file_lock();
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("���o�^�f�[�^�t�@�C�����J���܂���ł����B: $!");
        my($id,$email) = split(/\t/, <R>);
        if ($id ne $login{id}) { error("ID���Ⴂ�܂��B"); }
        if ($email ne $FORM{email}) {
            error("���[���A�h���X���Ⴂ�܂��B");
        }
    } else {
        error("�w�肳�ꂽ���o�^�L�[�͑��݂��܂���ł����B")
    }

    email_dupl_check($FORM{email});

    open(R,"member/$login{id}.cgi")
     or error("�����o�[�f�[�^�t�@�C�����J���܂���ł����B: $!");
    my($n,$passwd,$n,$reg_date,$last_update) = split(/\t/,<R>,3);
    close(R);
    open(W,"> member/$login{id}.cgi");
    print W join("\t", $login{id},$passwd,$FORM{email},$reg_date,time), "\n";
    close(W);

    unlink("temp/$FORM{key}.cgi");
    file_unlock();

    printhtml("chg_done.html");
    exit;

}

sub cancel {

    if ($FORM{key} =~ /\W/) {
        error("�s���ȉ��o�^�L�[���w�肳��Ă��܂��B");
    }

    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("���o�^�f�[�^�t�@�C�����J���܂���ł����B: $!");
        my($id,$email) = split(/\t/, <R>);
        if ($id ne $login{id}) { error("ID���Ⴂ�܂��B"); }
        if ($email ne $FORM{email}) {
            error("���[���A�h���X���Ⴂ�܂��B");
        }
    } else {
        error("�w�肳�ꂽ���o�^�L�[�͑��݂��܂���ł����B")
    }
    unlink("temp/$FORM{key}.cgi");

    printhtml("chg_cancel.html");
    exit;

}
