
### �V�X�e���ݒ�t�@�C�� ml_conf.pl
### �X�V�����F2006-06-18 20:35:19
### �����̃t�@�C���͎�����������܂��̂Œ��ڕҏW���Ȃ��ł��������B

sub conf {

    my %conf;

    $conf{_updated} = q{2006-06-18 20:35:19};

    chomp($conf{k_email} = <<'_k_email_str_');
mail@add.re.ss
_k_email_str_
    chomp($conf{title} = <<'_title_str_');
Web���[�����O���X�g
_title_str_
    chomp($conf{subject_prefix} = <<'_subject_prefix_str_');
[test-ml:#]
_subject_prefix_str_
    chomp($conf{mainpage_info} = <<'_mainpage_info_str_');
<!-- ### ���C���y�[�W�̏Љ �������� ### -->
<div align=center>
<table border=0 cellpadding=5 cellspacing=0 bgcolor=#ffffcc>
<tr><td>
���̃V�X�e���́AWeb��Ń��[�����O���X�g�̂悤�ȋ@�\���������邽�߂̂��̂ł��B�ʏ�̃��[�����O���X�g�Ƒ�����@���قȂ�܂��̂ŁA������@�̐������悭���ǂ݂ɂȂ�����ł����p���������B
</td></tr></table></div>
<!-- ### ���C���y�[�W�̏Љ �����܂� ### -->

_mainpage_info_str_
    chomp($conf{send_intro} = <<'_send_intro_str_');
0
_send_intro_str_
    chomp($conf{enable_get_archive} = <<'_enable_get_archive_str_');
1
_enable_get_archive_str_
    chomp($conf{enable_post} = <<'_enable_post_str_');
1
_enable_post_str_
    chomp($conf{enable_attachment} = <<'_enable_attachment_str_');
0
_enable_attachment_str_
    chomp($conf{attachment} = <<'_attachment_str_');
1
_attachment_str_
    chomp($conf{attachment_sizemax} = <<'_attachment_sizemax_str_');
1024
_attachment_sizemax_str_
    chomp($conf{attachment_ext} = <<'_attachment_ext_str_');
jpg,png,gif,txt,doc,ppt,xls
_attachment_ext_str_
    chomp($conf{add_ml_header} = <<'_add_ml_header_str_');
0
_add_ml_header_str_
    chomp($conf{add_ml_footer} = <<'_add_ml_footer_str_');
1
_add_ml_footer_str_
    chomp($conf{sendmail} = <<'_sendmail_str_');
/usr/sbin/sendmail
_sendmail_str_
    chomp($conf{ml_dir} = <<'_ml_dir_str_');
_ml_dir_str_
    chomp($conf{mainpage} = <<'_mainpage_str_');
_mainpage_str_
    chomp($conf{home} = <<'_home_str_');
http://test.psl.ne.jp/
_home_str_
    chomp($conf{ml_header} = <<'_ml_header_str_');

_ml_header_str_
    chomp($conf{ml_footer} = <<'_ml_footer_str_');

--------------------------------------------------------------------
��##title##  ##ml_dir##/ml.cgi��
�����̓��e�ɕԐM����ɂ͉��L�փA�N�Z�X��
##ml_dir##/ml_post.cgi?res=##ml_cnt##&idpw=##idpw##
�����̃��[�����O���X�g�ɐV�K���e����ɂ͉��L�փA�N�Z�X��
##ml_dir##/ml_post.cgi?&idpw=##idpw##

_ml_footer_str_
    chomp($conf{page_disp_admin} = <<'_page_disp_admin_str_');
15
_page_disp_admin_str_

    return %conf;

}

1;
