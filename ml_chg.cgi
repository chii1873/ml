#!/usr/bin/perl
# ---------------------------------------------------------------
#  - システム名    疑似メーリングリスト (Web Mailing List)
#  - バージョン    0.31
#  - 公開年月日    2009/6/22
#  - スクリプト名  ml_chg.cgi
#  - 著作権表示    (c)1997-2009 Perl Script Laboratory
#  - 連  絡  先    info@psl.ne.jp (http://www.psl.ne.jp/)
# ---------------------------------------------------------------
# ご利用にあたっての注意
#   ※このシステムはフリーウエアです。
#   ※このシステムは、「利用規約」をお読みの上ご利用ください。
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

    ($FORM{email}, my @msg_) = email_chk($FORM{email}, str=>"メールアドレス",
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
     or error("テンポラリファイルが temp ディレクトリ上に作成できません".
              "でした。temp ディレクトリが存在するか、temp ディレクトリへの".
              "書き込み権限があるかご確認ください。: $!");
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
        error("不正な仮登録キーが指定されています。");
    }

    file_lock();
    my($id, $email);
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("仮登録データファイルが開けませんでした。: $!");
        ($id, $email) = split(/\t/, <R>);
        if ($id ne $login{id}) { error("IDが違います。"); }
        $FORM{email} = $email;
#        if ($email ne $FORM{email}) {
#            error("メールアドレスが違います。");
#        }
    } else {
        error("指定された仮登録キーは存在しませんでした。")
    }
    file_unlock();

    printhtml("chg_form.html", key=>$FORM{key}, email=>$FORM{email},
     email_org=>$login{email});
    exit;

}

sub chg2 {

    if ($FORM{key} =~ /\W/) {
        error("不正な仮登録キーが指定されています。");
    }

    file_lock();
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("仮登録データファイルが開けませんでした。: $!");
        my($id,$email) = split(/\t/, <R>);
        if ($id ne $login{id}) { error("IDが違います。"); }
        if ($email ne $FORM{email}) {
            error("メールアドレスが違います。");
        }
    } else {
        error("指定された仮登録キーは存在しませんでした。")
    }

    email_dupl_check($FORM{email});

    open(R,"member/$login{id}.cgi")
     or error("メンバーデータファイルが開けませんでした。: $!");
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
        error("不正な仮登録キーが指定されています。");
    }

    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("仮登録データファイルが開けませんでした。: $!");
        my($id,$email) = split(/\t/, <R>);
        if ($id ne $login{id}) { error("IDが違います。"); }
        if ($email ne $FORM{email}) {
            error("メールアドレスが違います。");
        }
    } else {
        error("指定された仮登録キーは存在しませんでした。")
    }
    unlink("temp/$FORM{key}.cgi");

    printhtml("chg_cancel.html");
    exit;

}
