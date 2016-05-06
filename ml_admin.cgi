#!/usr/bin/perl
# ---------------------------------------------------------------
#  - �V�X�e����    �^�����[�����O���X�g (Web Mailing List)
#  - �o�[�W����    0.31
#  - ���J�N����    2009/6/22
#  - �X�N���v�g��  ml_admin.cgi
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
use vars qw($q %FORM %CONF %login);
use CGI;
require 'jcode.pl';
require 'ml_conf.pl';
require 'ml_lib.pl';
%CONF = (setver(), conf());
umask 0;

%FORM = decoding($ENV{CONTENT_TYPE} =~ m#multipart/form-data#
 ? ($q = new CGI) : undef);
admin_passwd_check();

post() if $FORM{post};
confirm() if $FORM{confirm};
chpasswd() if $FORM{chpasswd};
chpasswd2() if $FORM{chpasswd2};
logout() if $FORM{logout};
mail() if $FORM{mail};
mailstr() if $FORM{mailstr};
mailstr_done() if $FORM{mailstr_done};
mod2() if $FORM{mod2};
mod() if $FORM{mod};
member_export() if $FORM{export};
member_export_done() if $FORM{export_done};
member_export_getfile() if $FORM{export_getfile};
member_import() if $FORM{import};
member_import_confirm() if $FORM{import_confirm};
member_import_done() if $FORM{import_done};
member_list() if $FORM{list};
reg() if $FORM{reg};
reg2() if $FORM{reg2};
setup() if $FORM{setup};
setup_done() if $FORM{setup_done};
admin_menu();


sub admin_menu {

    printhtml("admin_menu.html");
    exit;

}

sub admin_passwd_check {

    unless (get_cookie('PSL_ML_ADMIN')) {
        login_admin() unless $FORM{passwd};
        open(R, "ml_admin_passwd.cgi")
         or error("�Ǘ��p�p�X���[�h�t�@�C�����J���܂���ł����B: $!");
        chomp(my $passwd = <R>);
        close(R);
        if ($passwd eq "") {
            open(W, "> ml_admin_passwd.cgi")
             or error("�Ǘ��p�p�X���[�h�t�@�C���֏������݂ł��܂���ł����B: $!");
            print W $passwd = crypt_passwd("12345");
            close(W);
        }
        unless (crypt_passwd_is_valid($FORM{passwd}, $passwd)) {
            error("�p�X���[�h���Ⴂ�܂��B");
        }
        if ($FORM{do_cache}) {
            set_cookie('PSL_ML_ADMIN_CACHE', 30 * 86400, $FORM{passwd});
        }
    }
    set_cookie('PSL_ML_ADMIN',"", "login");
    clean_tempfile();

}

sub as_ml {

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

    my $post_s = int($postcnt/100);
    mkdir("post/$post_s", 0777) unless -d "post/$post_s";
    mkdir("post/attach/$post_s", 0777) unless -d "post/attach/$post_s";
    my $date_header_f = date_header_f(time);

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
    print W qq{From: $CONF{k_email}\n};
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

    if ($CONF{subject_prefix} ne '') {
        $CONF{subject_prefix} =~ s/(#+)/sprintf("%0".length($1)."d",$postcnt)/e;
        $FORM{subject} = "$CONF{subject_prefix} $FORM{subject}";
    }

    return %attachment;

}

sub chpasswd {

    printhtml("admin_chpasswd.html");
    exit;

}

sub chpasswd2 {

    if ($FORM{passwd} eq '') {
        error('�V�����p�X���[�h�����͂���Ă��܂���B');
    }
    if ($FORM{passwd} =~ /\W/) {
        error('�p�X���[�h�͔��p�p�����݂̂Ŏw�肵�Ă��������B');
    }
    if ($FORM{passwd} ne $FORM{passwd2}) {
        error('���͂��ꂽ2�̃p�X���[�h������ł���܂���B');
    }
    if (length($FORM{passwd}) > 8) {
        error('�p�X���[�h�͔��p�p����8�����ȓ��Ŏw�肵�Ă��������B');
    }

    open(W, "> ml_admin_passwd.cgi")
     or error("�p�X���[�h�t�@�C���ւ̏����o���Ɏ��s���܂����B: $!");
    print W crypt_passwd($FORM{passwd});
    close(W);

    if (get_cookie("PSL_ML_ADMIN_CACHE")) {
        set_cookie("PSL_ML_ADMIN_CACHE", 30 * 86400, $FORM{passwd});
    }

    printhtml("admin_chpasswd2.html");
    exit;

}

sub confirm {

    $FORM{subject} =~ s/^\s*(.*)\s*$/$1/;
    $FORM{subject} = "(����)" if $FORM{subject} eq '';
    if ($FORM{mailbody} eq '') {
        error("���[���{���������w�肳��Ă��܂���B");
    }
    foreach (qw(subject mailbody signiture type)) {
        $FORM{$_} =~ s/\n+$/\n/;
        $FORM{$_} = html_output_escape($FORM{$_});
    }

    my $mailbody_dsp = "$FORM{mailbody}\n$FORM{signiture}";
    my $remote_host = remote_host();

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

    printhtml("admin_confirm.html",
     remote_host => $remote_host, mailbody_dsp => $mailbody_dsp,
     as_ml_dsp => ($FORM{as_ml} ? "���[�����O���X�g�̓��e�Ƃ��đ��M����"
     : "�ʏ�̂����������[���Ƃ��đ��M����"),
     temp => $temp,
     ua => $ENV{HTTP_USER_AGENT},
     (map { $_ => html_output_escape($FORM{$_}) } qw(as_ml subject mailbody signiture)),
     attach_begin =>($CONF{enable_attachment} ? "" : "<!--"),
     attach_end =>($CONF{enable_attachment} ? "" : "-->"),
     attach_dsp =>($attach_dsp||"&nbsp;"),
    );
    exit;

}

sub del {

    unlink("member/$FORM{id}.cgi","sign/$FORM{id}.cgi");

    print "Location: $CONF{ml_dir}/ml_admin.cgi?list&p=$FORM{p}&s=$FORM{s}\n\n";
    exit;

}

sub logout {

    clean_tempfile();

    set_cookie('PSL_ML_ADMIN');
    printhtml("admin_logout.html");
    exit;

}

sub mail {

    open(R,"sign/admin.cgi");
    my $signiture = join("", <R>);
    close(R);

    printhtml("admin_mail.html", signiture=>html_output_escape($signiture),
     attach_begin =>($CONF{enable_attachment} ? "" : "<!--"),
     attach_end =>($CONF{enable_attachment} ? "" : "-->"),
     attach_list => join("<br>\n", map { qq{<input type=file name="file$_" size=50>} } (1..$CONF{attachment})),
     attachment_sizemax_dsp => ($CONF{attachment_sizemax} ? "$CONF{attachment_sizemax}kb/�t�@�C��" : "�����Ȃ�"),
     attachment_ext_dsp => ($CONF{attachment_ext} ? $CONF{attachment_ext} : "�����Ȃ�"),
    );
    exit;

}

sub mailstr {

    my %mailstrname = (
        prereg => "���o�^",
        reg => "�o�^����",
        prechg => "���ύX",
        intro => "�o�^������",
    );
    unless ($mailstrname{$FORM{mailstr}}) {
        error("���[�����͂��w�肷�镶���񂪕s���ł��B");
    }

    open(R, "tmpl/mail_$FORM{mailstr}.txt")
     or error("���[�����̓f�[�^�t�@�C�����J���܂���ł����B: $!");
    chomp(my $subject = <R>);
    my $body =  join("", <R>);
    close(R);

    printhtml("admin_mailstr.html", mailstrname=>$mailstrname{$FORM{mailstr}},
     mailstr=>$FORM{mailstr},
     subject=>html_output_escape($subject),
     body=>html_output_escape($body),
    );
    exit;

}

sub mailstr_done {

    my %mailstrname = (
        prereg => "���o�^",
        reg => "�o�^����",
        prechg => "���ύX",
        intro => "�o�^������",
    );

    unless (-e "tmpl/mail_$FORM{mailstr_done}.txt") {
        error("���[�����C�A�E�g�t�@�C���̎w�肪�s���ł��B");
    }
    open(W, "> tmpl/mail_$FORM{mailstr_done}.txt")
     or error("���[�����̓f�[�^�t�@�C�����J���܂���ł����B: $!");
    print W $FORM{subject}, "\n", $FORM{body};
    close(W);

    printhtml("admin_mailstr_done.html",
     mailstrname=>$mailstrname{$FORM{mailstr_done}},);
    exit;

}

sub member_export {

    printhtml("admin_member_export.html");
    exit;

}

sub member_export_done {

    opendir(DIR, "member")
     or error("member�f�B���N�g�����J���܂���ł����B: $!");
    my $list;
    foreach my $file(sort grep(/^\d{4}\.cgi$/, readdir(DIR))) {
        open(R, "member/$file") or error("member/$file���J���܂���ł����B: $!");
        chomp( my $data = <R> );
        my($id, $passwd, $email, $reg_date, $last_update) = split(/\t/, $data);
        $reg_date = get_datetime($reg_date) if $reg_date;
        $last_update = get_datetime($last_update) if $last_update;
        $list .= join("\t", $id, $passwd, $email, $reg_date, $last_update)."\n";
    }

    my $temp =sprintf("%s%s%s%s%s%s", split(/\D+/, get_datetime(time)));
    open(W, "> temp/ml_memberdata$temp.cgi") or error("temp/ml_memberdata$temp.cgi�֏������݂ł��܂���ł����B: $!");
    print W $list;
    close(W);

    printhtml("admin_member_export_done.html", temp=>$temp);
    exit;

}

sub member_export_getfile {

    my($temp) = $FORM{export_getfile} =~ m#^(\d{14})$#;
    error("�s���ȃt�@�C���w��ł��B") unless $temp;
    open(R, "temp/ml_memberdata$temp.cgi")
     or error("temp/ml_memberdata$temp.cgi���J���܂���ł����B: $!");
    my @data = <R>;
    close(R);

    print qq|Content-type: application/octet-stream; name="ml_memberdata$temp.txt"\n|;
    print qq|Content-Disposition: filename="ml_memberdata$temp.txt"\n\n|;
    print @data;
    exit;

}

sub member_import {

    printhtml("admin_member_import.html");
    exit;

}

sub member_import_confirm {

    opendir(DIR, "member")
     or error("member�f�B���N�g�����J���܂���ł����B: $!");
    my %email;
    my %id;
    my $id_max;
    foreach my $file(sort grep(/^\d{4}\.cgi$/, readdir(DIR))) {
        open(R, "member/$file") or error("member/$file���J���܂���ł����B: $!");
        chomp( my $data = <R> );
        my($id, $passwd, $email) = split(/\t/, $data);
        $email{$email} = $id;
        $id{$id} = 1;
        $id_max = $id if $id_max <= $id;
    }

    my %email_exists;
    my $linecnt;
    my $stream;
    my $list;
    my $new = 0;
    my $mod = 0;
    foreach my $line(split(/\r\n|\r|\n/, get_file_stream($q, "file"))) {
        $linecnt++;
        my($id, $passwd, $email, $reg_date, $last_update) = split(/\t/, $line);
        $id ||= sprintf("%04d", ++$id_max);
        ($email, my @msg) = email_chk($email,
         str=>"$linecnt�s��: ���[���A�h���X(=$email)", required=>1);
        error(@msg) if @msg;
        error("$linecnt�s��: ���[���A�h���X(=$email)���d�����Ă��܂��B")
         if $email_exists{$email}++;
        if ($email{$email} and $email{$email} ne $id) {
            error("$linecnt�s��: �ʂ�ID�œo�^����Ă��郁�[���A�h���X(=$email)�͎g�p�ł��܂���B");
        }
        if ($reg_date and $reg_date =~ /^\d{4}[-\/]\d{1,2}[-\/]\d{1,2} \d{1,2}[-\/]\d{1,2}[-\/]\d{1,2}/) {
            error("$linecnt�s��: �o�^����(=$reg_date)�̌`��������������܂���B");
        }
        if ($last_update and $last_update =~ /^\d{4}[-\/]\d{1,2}[-\/]\d{1,2} \d{1,2}[-\/]\d{1,2}[-\/]\d{1,2}/) {
            error("$linecnt�s��: �X�V����(=$last_update)�̌`��������������܂���B");
        }
        $stream .= join("\t", $id, $passwd, $email, $reg_date, $last_update)."\n";
        my $mode = $id{$id} ? "<font color=red>�X�V</font>" : "<font color=green>�V�K</font>";
        $id{$id} ? $mod++ : $new++;

        next if $linecnt > 50;
        $reg_date ||= "(�o�^��)";
        $last_update = "(�o�^��)";
        $list .= <<STR;
<tr><td>$mode</td><td>$id</td><td>$passwd</td><td>$email</td>
<td>$reg_date</td><td>$last_update</td></tr>
STR
    }

    my $temp = time . $$;
    file_save($stream, "temp", "members$temp.txt", "txt");

    printhtml("admin_member_import_confirm.html",
     new=>$new, mod=>$mod, list=>$list, temp=>$temp,
    );
    exit;

}

sub member_import_done {

    use Time::Local;

    ($FORM{temp}) = $FORM{temp} =~ /^(\d+)$/;
    $FORM{temp} or errror("temp(=$FORM{temp})�̒l������������܂���B");

    my $last_update = time;
    open(R, "temp/members$FORM{temp}.txt")
     or errror("�ꎞ�t�@�C�����J���܂���ł����B: $!");
    while (<R>) {
        chomp;
        my($id, $passwd, $email, $reg_date) = split(/\t/);
        open(W, ">member/$id.cgi")
         or error("id=$id�̃����o�[�f�[�^���������߂܂���ł����B: $!");
        print W join("\t", $id, $passwd, $email,
         ($reg_date ? get_epoch($reg_date) : $last_update), $last_update);
        close(W);
    }

    printhtml("admin_member_import_done.html");
    exit;

}

sub member_list {

    my $page_disp = 15;

    file_lock();

    opendir(DIR, "member")
     or error("member�f�B���N�g�����J���܂���ł����B: $!");
    my @files = sort(grep(/\.cgi/, readdir(DIR)));

    if ($FORM{s}) {
        my @files2;
        if ($FORM{s} =~ /[<>:;()'"#$&]/) {
            error("����������ɂ̓��[���A�h���X�Ɋ܂߂邱�Ƃ��ł��Ȃ���������w�肷�邱�Ƃ͂ł��܂���B");
        }
        foreach (@files) {
            open(R, "member/$_") or error("member/$_���J���܂���ł����B: $!");
            my($n,$n,$email) = split(/\t/, <R>);
            push(@files2, $_) if $email =~ /\Q$FORM{s}\E/i;
        }
        @files = @files2;
    }
    my $cnt_all = @files;

    my $p = $FORM{p};
    my $prev;
    if ($FORM{p}) {
        my $prev_p = $FORM{p} - $page_disp;
        $prev = "<a href=ml_admin.cgi?list&p=$prev_p&s=$FORM{s}>&lt;&lt; �߂�</a>";
    } else {
        $prev = "<font color=#999999>&lt;&lt; �߂�</font>";
    }
    my $next;
    if ($FORM{p} + $page_disp <= $cnt_all) {
        my $next_p = $FORM{p} + $page_disp;
        $next = "<a href=ml_admin.cgi?list&p=$next_p&s=$FORM{s}>�i�� &gt;&gt;</a>";
    } else {
        $next = "<font color=#999999>�i�� &gt;&gt;</font>";
    }
    my $page_c = $FORM{p} / $page_disp + 1;
    my $page_all = int($cnt_all / $page_disp) + ($cnt_all % $page_disp ? 1 : 0);
    my $page = "$page_c �y�[�W / �S $page_all �y�[�W ( $cnt_all �� )"
     if $page_all;

    my $list;
    my $cnt;
    foreach (@files) {
        next if $p-- > 0;
        last if ++$cnt > $page_disp;
        open(R, "member/$_")
         or error("�����o�[�f�[�^�t�@�C�����J���܂���ł����B: $!");
        my ($id,$passwd,$email,$reg_date,$last_update) = split(/\t/, <R>);
        $reg_date = date_f($reg_date);
        $list .= <<HTML;
<tr><td>$id</td><td>$passwd</td>
<td><a href=mailto:$email>$email</a></td>
<td>$reg_date</td>
<td><a href=ml_admin.cgi?mod&id=$id&p=$FORM{p}&s=$FORM{s}>�C��/�ύX</a></td></tr>

HTML
    }
    file_unlock();

    printhtml("admin_member_list.html",
     prev=>$prev, next=>$next, page=>$page, list=>$list,
     (map { $_=>$FORM{$_} } qw(s)),
    );
    exit;

}

sub mod {

    if ($FORM{id} =~ /\D/) {
        error("ID�͔��p�����݂̂Ŏw�肵�Ă��������B");
    }

    file_lock();
    open(R, "member/$FORM{id}.cgi")
     or error("member/$FORM{id}.cgi ���J���܂���ł����B: $!");
    my ($id,$passwd,$email,$reg_date,$last_update) = split(/\t/, <R>);
    close(R);
    file_unlock();
    chomp($last_update);
    $reg_date = date_f($reg_date);
    $last_update = date_f($last_update);

    printhtml("admin_mod.html", id=>$id, passwd=>$passwd, email=>$email,
     reg_date=>$reg_date, last_update=>$last_update,
     (map { $_=>$FORM{$_} } qw(p id)),
    );
    exit;

}

sub mod2 {

    if ($FORM{id} =~ /\D/) {
        error("ID�͔��p�����݂̂Ŏw�肵�Ă��������B");
    }

    del() if $FORM{del};

    file_lock();

    open(R, "member/$FORM{id}.cgi")
     or error("member/$FORM{id}.cgi ���J���܂���ł����B: $!");
    my ($id,$passwd,$email,$reg_date,$last_update) = split(/\t/, <R>);
    close(R);
    open(W, ">member/$FORM{id}.cgi")
     or error("member/$FORM{id}.cgi �ɏ������݂ł��܂���ł����B: $!");
    print W join("\t",$id,$FORM{passwd},$FORM{email},$reg_date,time), "\n";
    close(W);

    file_unlock();

    print "Location: $CONF{ml_dir}/ml_admin.cgi?list&p=$FORM{p}&s=$FORM{s}\n\n";
    exit;

}

sub post {

    open(W, "> sign/admin.cgi")
     or error("�����t�@�C�� sign/admin.cgi �֏������݂ł��܂���ł����B: $!");
    print W $FORM{signiture};
    close(W);

    $FORM{mailbody} .= "\n$FORM{signiture}";
    my %attachment;
    %attachment = as_ml() if $FORM{as_ml};

    printhtml("admin_post.html");

    $| = 1;
#    exit if my $pid = fork;
#    close(STDOUT);
#    close(STDERR);

    sendmail2($CONF{k_email}, $FORM{subject}, $FORM{mailbody}, {
        "X-Sender-Remote-Host" => remote_host(),
        "X-Sender-User-Agent" => $ENV{HTTP_USER_AGENT},
    }, { %attachment });
    exit;

}

sub reg {

    printhtml("admin_reg.html", p=>$FORM{p});
    exit;

}

sub reg2 {

    my @msg;
    if ($FORM{id} ne "") {
        $FORM{id} =~ /^\d{4}$/
         or push(@msg, "ID�͔��p����4�P�^�Ŏw�肵�Ă��������B");
         ($FORM{id}) = $FORM{id} =~ /^(\d{4})$/;
         if (-e "member/$FORM{id}.cgi") {
             error("ID=$FORM{id}�͂��łɓo�^����Ă��܂��B");
         }
    }
    if ($FORM{passwd} eq "") {
        push(@msg, "�p�X���[�h���w�肵�Ă��������B");
    } elsif ($FORM{passwd} =~ /\W/) {
        push(@msg, "�p�X���[�h�͔��p�p�����Ŏw�肵�Ă��������B");
    }
    ($FORM{email}, my @msg_) = email_chk($FORM{email},
     opt=>"�z�M��A�h���X", require=>1);
    push(@msg, @msg_) if @msg_;

    error(@msg) if @msg;

    email_dupl_check($FORM{email});

    $FORM{id} ||= get_memcnt();

    file_lock();

    my $now = time;
    open(W, ">member/$FORM{id}.cgi")
     or error("member/$FORM{id}.cgi �ɏ������݂ł��܂���ł����B: $!");
    print W join("\t",@FORM{qw(id passwd email)},$now,$now), "\n";
    close(W);

    file_unlock();

    printhtml("admin_reg2.html", reg_date=> date_f($now),
     map { $_ => $FORM{$_} } qw(id passwd email p)
    );
    exit;

}

sub setup {

    my %conf = map { $_ => html_output_escape($CONF{$_}) } keys %CONF;
    $CONF{ml_dir} ||= "http://$ENV{SERVER_NAME}$ENV{REQUEST_URI}";
    $CONF{ml_dir} =~ s#/ml_admin\.cgi$##;
    $CONF{mainpage} ||= "$CONF{ml_dir}/ml.cgi";
    $CONF{sendmail} ||= "/usr/sbin/sendmail";

    printhtml("admin_setup.html",
     (map { $_.":1" => ($CONF{$_} == 1 ? "checked" : ""),
     $_.":0" => ($CONF{$_} == 0 ? "checked" : "") }
     qw(send_intro enable_get_archive enable_post enable_attachment
     add_ml_header add_ml_footer)),
     (map { "attachment:".$_ => ($CONF{attachment} == $_ ? "selected" : "") } (1..5)),
     (map { $_ => $conf{$_} } qw(k_email fromname title subject_prefix mainpage_info
     attachment_sizemax attachment_ext sendmail ml_dir mainpage home
     ml_header ml_footer)),
    );
    exit;


}

sub setup_done {

    my @msg;
    ($FORM{k_email}, my @msg_) = email_chk($FORM{k_email},
     str=>"�Ǘ��l��E-mail�A�h���X", required=>1);
    push(@msg, @msg_) if @msg_;
    if ($FORM{title} eq "") {
        push(@msg, "���̃��[�����O���X�g�̃^�C�g�����w�肵�Ă��������B");
    }
    $FORM{send_intro} ||= 0;
    $FORM{enable_get_archive} ||= 0;
    $FORM{enable_post} ||= 0;
    $FORM{add_ml_header} ||= 0;
    $FORM{add_ml_footer} ||= 0;
    if ($FORM{sendmail} eq "") {
        push(@msg, "sendmail�R�}���h�̃p�X���w�肵�Ă��������B");
    } elsif (!-e $FORM{sendmail}) {
        push(@msg, "�w�肳�ꂽ�ꏊ��sendmail�R�}���h������܂���B");
    }

    setup_mkconf(%FORM);

    printhtml("admin_setup_done.html");
    exit;

}

sub setup_mkconf {

    my %conf = @_;

    my $updated = get_datetime(time);
    $conf{page_disp_admin} = 15;

    open(W, "> ml_conf.pl")
     or error("ml_conf.pl�t�@�C���ɏ������݂ł��܂���ł����B: $!");
    print W <<STR;

### �V�X�e���ݒ�t�@�C�� ml_conf.pl
### �X�V�����F$updated
### �����̃t�@�C���͎�����������܂��̂Œ��ڕҏW���Ȃ��ł��������B

sub conf {

    my \%conf;

    \$conf{_updated} = q{$updated};

STR

    foreach (qw(k_email fromname title subject_prefix mainpage_info send_intro enable_get_archive enable_post enable_attachment attachment attachment_sizemax attachment_ext  add_ml_header add_ml_footer sendmail ml_dir mainpage home ml_header ml_footer page_disp_admin)) {
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
