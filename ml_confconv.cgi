#!/usr/bin/perl
# ---------------------------------------------------------------
#  - システム名    疑似メーリングリスト 設定ファイル変換プログラム
#  - バージョン    -
#  - 公開年月日    2009/6/22
#  - スクリプト名  ml_confconv.cgi
#  - 著作権表示    (c)1997-2009 Perl Script Laboratory
#  - 連  絡  先    info@psl.ne.jp (http://www.psl.ne.jp/)
# ---------------------------------------------------------------
# ご利用にあたっての注意
#   ※このシステムはフリーウエアです。
#   ※このシステムは、「利用規約」をお読みの上ご利用ください。
#     http://www.psl.ne.jp/info/copyright.html
# ---------------------------------------------------------------
BEGIN {
    print "Content-type: text/html\n\n";
    open(STDERR, ">&STDOUT");
}
use CGI;
require 'jcode.pl';
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());
umask 0;

%FORM = decoding();

done() if $FORM{done};
confirm();

sub confirm {

    printhtml("confconv_confirm.html");
    exit;

}

sub done {

    unless (-e "ml_conf_org.pl") {
        error("ml_conf_org.plが見つかりませんでした。");
    }
    eval {
        require "ml_conf_org.pl";
        conf();
        $ml_header = ml_header();
        $ml_footer = ml_footer();
        ($prereg_subject, $prereg_mailstr) = prereg_mailstr();
        ($prechg_subject, $prechg_mailstr) = prechg_mailstr();
        ($reg_subject, $reg_mailstr) = reg_mailstr();
    };
    error("旧設定ファイルの読み込み時にエラーがありました。: $@") if $@;

    open(W, ">tmpl/mail_prereg.txt")
     or error("tmpl/mail_prereg.txtに書き込みできませんでした。: $!");
    print W "$prereg_subject\n$prereg_mailstr";
    close(W);

    open(W, ">tmpl/mail_prechg.txt")
     or error("tmpl/mail_prechg.txtに書き込みできませんでした。: $!");
    print W "$prechg_subject\n$prechg_mailstr";
    close(W);

    open(W, ">tmpl/mail_reg.txt")
     or error("tmpl/mail_reg.txtに書き込みできませんでした。: $!");
    print W "$reg_subject\n$reg_mailstr";
    close(W);

    setup_mkconf(
	k_email            => $k_email,
	title              => $title,
	subject_prefix     => $subject_prefix,
	mainpage_info      => $mainpage_info,
	send_intro         => $send_intro,
	enable_get_archive => $enable_get_archive,
	enable_post        => $enable_post,
	enable_attachment  => 0,
	attachment         => 1,
	attachment_sizemax => 1024,
	attachment_ext     => "jpg,png,gif,txt,doc,ppt,xls",
	add_ml_header      => $add_ml_header,
	add_ml_footer      => $add_ml_footer,
	sendmail           => $sendmail,
	ml_dir             => $ml_dir,
	mainpage           => $mainpage,
	home               => $home,
	ml_header          => $ml_header,
	ml_footer          => $ml_footer,
	page_disp_admin    => 15,
    );

    printhtml("confconv_done.html");
    exit;

}

sub setup_mkconf {

    my %conf = @_;

    my $updated = get_datetime(time);
    $conf{page_disp_admin} = 15;

    open(W, "> ml_conf.pl")
     or error("ml_conf.plファイルに書き込みできませんでした。: $!");
    print W <<STR;

### システム設定ファイル ml_conf.pl
### 更新日時：$updated
### ※このファイルは自動生成されますので直接編集しないでください。

sub conf {

    my \%conf;

    \$conf{_updated} = q{$updated};

STR

    foreach (qw(k_email title subject_prefix mainpage_info send_intro enable_get_archive enable_post enable_attachment attachment attachment_sizemax attachment_ext  add_ml_header add_ml_footer sendmail ml_dir mainpage home ml_header ml_footer page_disp_admin)) {
        print W <<STR;
    chomp(\$conf{$_} = <<'_${_}_str_');
$conf{$_}
_${_}_str_
STR
    }

    print W <<'STR';

    return %conf;

}

1;
STR

    close(W);

}
