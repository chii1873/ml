function set_passwd () {
    var charset = new Array("0","1","2","3","4","5","6","7","8","9");
    var passwd = "";
    for (i = 0; i < 8; i++) {
        var r = Math.floor(Math.random() * 10);
        passwd = passwd + charset[r];
    }
    document.myform.passwd.value = passwd;
}

function delconfirm() {

    if (confirm("このメンバーのデータを削除します。よろしいですか?")) {
        document.myform.del.value="1";
        document.myform.submit();
    }

}
