#!/usr/bin/perl
# ---------------------------------------------------------------
#  - システム名    疑似メーリングリスト (Web Mailing List)
#  - バージョン    0.31
#  - 公開年月日    2009/6/22
#  - スクリプト名  ml_reg.cgi
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

    ($FORM{email}, my @msg_) = email_chk($FORM{email}, str=>"メールアドレス",
     required=>1);
    error(@msg_) if @msg_;

    file_lock();
    opendir(DIR, "member")
     or error("memberディレクトリが開けませんでした。: $!");
    foreach my $file(grep(/\.cgi$/, readdir(DIR))) {
        open(R, "member/$file")
         or error("メンバーデータファイルが開けませんでした。: $!");
        my($email) = (split(/\t/, <R>))[2];
        if ($FORM{email} eq $email) {
            error("このアドレス( $email )はすでに登録されています。");
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
     or error("テンポラリファイルが temp ディレクトリ上に作成できません".
              "でした。temp ディレクトリが存在するか、temp ディレクトリへの".
              "書き込み権限があるかご確認ください。: $!");
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
        error("不正な仮登録キーが指定されています。");
    }

    file_lock();
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("仮登録データファイルが開けませんでした。: $!");
        chomp(my $email = <R>);
        $FORM{email} = $email;
#        if ($email ne $FORM{email}) {
#            error("メールアドレスが違います。");
#        }
    } else {
        error("指定された仮登録キーは存在しませんでした。")
    }
    file_unlock();

    printhtml("reg_form.html", key=>$FORM{key}, email=>$FORM{email});
    exit;

}

sub reg2 {

    if ($FORM{key} =~ /\W/) {
        error("不正な仮登録キーが指定されています。");
    }

    file_lock();
    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("仮登録データファイルが開けませんでした。: $!");
        chomp(my $email = <R>);
        if ($email ne $FORM{email}) {
            error("メールアドレスが違います。");
        }
    } else {
        error("指定された仮登録キーは存在しませんでした。")
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
        error("不正な仮登録キーが指定されています。");
    }

    if (-e "temp/$FORM{key}.cgi") {
        open(R, "temp/$FORM{key}.cgi")
         or error("仮登録データファイルが開けませんでした。: $!");
        chomp(my $email = <R>);
        if ($email ne $FORM{email}) {
            error("メールアドレスが違います。");
        }
    } else {
        error("指定された仮登録キーは存在しませんでした。")
    }
    unlink("temp/$FORM{key}.cgi");

    printhtml("reg_cancel.html");
    exit;

}
