#!/usr/bin/perl
# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml.cgi
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
use vars qw(%FORM %CONF);
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());

menu();

sub menu {

    my $ga;
    if ($CONF{enable_get_archive}) {
        $ga = <<'STR';
<td><b><a href="ml_getarc.cgi">�A�[�J�C�u�擾</a></b></td>
<td>�ߋ��̓��e�L�������񂹂邱�Ƃ��ł��܂��B</td></tr>
STR
    }
    my $ep;
    if ($CONF{enable_post}) {
        $ep = <<'STR';
<td><b><a href="ml_post.cgi">�V�K���e</a></b></td>
<td>�V�K�L���̓��e���ł��܂��B</td></tr>
<td>No.<input name=res size=4>��<input type=submit value=�ԐM></td>
<td>�w�肵�����e�ԍ��ւ̕ԐM���ł��܂��B</td></tr>
STR
    }

    printhtml("menu.html", ga=>$ga, ep=>$ep);
    exit;

}
