#!/usr/bin/perl
# ---------------------------------------------------------------
#  - システム名    疑似メーリングリスト (Web Mailing List)
#  - バージョン    0.31
#  - 公開年月日    2009/6/22
#  - スクリプト名  ml.cgi
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
    open(STDERR, ">&STDOUT");
}
use strict;
use vars qw(%FORM %CONF);
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());

menu();

sub menu {

    my $ga;
    if ($CONF{enable_get_archive}) {
        $ga = <<'STR';
<td><b><a href="ml_getarc.cgi">アーカイブ取得</a></b></td>
<td>過去の投稿記事を取り寄せることができます。</td></tr>
STR
    }
    my $ep;
    if ($CONF{enable_post}) {
        $ep = <<'STR';
<td><b><a href="ml_post.cgi">新規投稿</a></b></td>
<td>新規記事の投稿ができます。</td></tr>
<td>No.<input name=res size=4>へ<input type=submit value=返信></td>
<td>指定した投稿番号への返信ができます。</td></tr>
STR
    }

    printhtml("menu.html", ga=>$ga, ep=>$ep);
    exit;

}
