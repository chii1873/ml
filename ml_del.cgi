#!/usr/bin/perl
# ---------------------------------------------------------------
#  - システム名    疑似メーリングリスト (Web Mailing List)
#  - バージョン    0.31
#  - 公開年月日    2009/6/22
#  - スクリプト名  ml_del.cgi
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

del() if $FORM{del};
confirm();

sub confirm {

    printhtml("del_confirm.html", email=>$login{email});
    exit;

}

sub del {

    unlink("member/$login{id}.cgi", "sign/$login{id}.cgi");
    set_cookie("PSL_ML");

    printhtml("del_done.html");
    exit;

}
